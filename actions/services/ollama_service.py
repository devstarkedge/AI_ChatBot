import aiohttp
import re
import random
import asyncio

# Ollama API configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3:8b"

# Global session (reuse connection for performance)
session = None


async def get_session():
    """
    Returns a reusable aiohttp session.
    Creates a new one only if not exists or closed.
    """
    global session
    if session is None or session.closed:
        session = aiohttp.ClientSession()
    return session


def clean_response(response: str, allow_long: bool = False) -> str:
    """
    Cleans LLM output:
    - Removes prompt leakage
    - Limits length
    - Formats response
    """
    if not response:
        return ""

    # Remove unwanted patterns (prompt leaks)
    bad_patterns = ["You are", "Instruction", "Assistant:", "Bot:", "User:", "---"]
    for pattern in bad_patterns:
        if pattern in response:
            response = response.split(pattern)[0]

    # Normalize line breaks
    response = response.replace("\r", "\n").strip()

    if not allow_long:
        # SHORT MODE → chat-like responses

        # Take only first line
        response = response.split("\n")[0]

        # Cut at punctuation or emojis
        response = re.split(r'[.!?]|😊|😄|😎|👀', response)[0]

        # Limit to 10 words
        words = response.split()
        response = " ".join(words[:10])

    else:
        # LONG MODE → explanation responses

        lines = response.split("\n")

        # Keep max 3 lines
        response = "\n".join(lines[:3])

    return response.strip()


async def generate_response(prompt: str, user_text: str) -> str:
    """
    Generates AI response using Ollama.
    Handles:
    - Short vs long response detection
    - API call
    - Cleaning
    - Error handling
    """
    try:
        msg = user_text.lower()

        # Keywords for long responses
        long_keywords = [
            "explain", "detail", "in detail", "describe",
            "tell me about", "what is", "how does", "guide"
        ]

        # Keywords for short responses
        short_keywords = [
            "short", "brief", "in short", "quick", "one line"
        ]

        # Decide response type
        if any(k in msg for k in short_keywords):
            allow_long = False
        elif any(k in msg for k in long_keywords):
            allow_long = True
        else:
            allow_long = False  # default chat mode

        # Get reusable session
        session = await get_session()

        # Call Ollama API
        async with session.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,        # creativity
                    "top_p": 0.9,             # randomness control
                    "repeat_penalty": 1.2,    # reduce repetition
                    "num_predict": 120 if allow_long else 20,  # length control
                    "stop": ["User:", "Bot:"]  # stop unwanted patterns
                }
            },
            timeout=aiohttp.ClientTimeout(total=20)
        ) as res:

            # Handle non-200 response
            if res.status != 200:
                print(f"[OLLAMA ERROR] Status: {res.status}")
                return fallback_reply()

            # Parse JSON safely
            try:
                data = await res.json()
            except Exception:
                text = await res.text()
                print("[OLLAMA ERROR] Invalid JSON:", text)
                return fallback_reply()

            # Extract response
            response = data.get("response", "").strip()

        # Clean AI output
        response = clean_response(response, allow_long)

        # Validate response
        if not response or len(response) < 3:
            return fallback_reply()

        return response

    # Handle timeout
    except asyncio.TimeoutError:
        print("[OLLAMA ERROR] Timeout")
        return "slow response 😅 try again"

    # Handle unexpected errors
    except Exception as e:
        print("[OLLAMA ERROR]", e)
        return fallback_reply()


def fallback_reply():
    """
    Returns safe fallback responses
    when AI fails
    """
    return random.choice([
        "hmm 😄",
        "interesting 👀",
        "tell me more 😄"
    ])