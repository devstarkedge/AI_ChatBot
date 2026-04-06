from .memory_store import get_memory


def build_prompt(user_id, message):
    """
    Builds a structured prompt for LLM using:
    - Conversation memory
    - Personality definition
    - Response style rules (short/long)
    """

    # Fetch past conversation history for this user
    history = get_memory(user_id)

    # Normalize message for keyword detection
    msg = message.lower()

    # Detect whether response should be long or short
    if any(word in msg for word in ["joke", "story", "explain", "detail", "tell me about"]):
        style = "long"
    else:
        style = "short"

    # Define AI personality (human-like WhatsApp tone)
    personality = """
You are chatting like a real human on WhatsApp.

Personality:
- Chill
- Friendly
- Slightly witty
- Uses emojis sometimes
"""

    # Define response rules based on style
    if style == "short":
        # Short chat replies
        system_prompt = """
Reply like a WhatsApp chat.

STRICT RULES:
- Only ONE line
- No line breaks
- Max 10–12 words
- Casual human tone
- No multiple sentences
"""
    else:
        # Long explanatory replies
        system_prompt = """
Reply like WhatsApp.

STRICT:
- 2 to 4 lines
- Explain clearly

- Simple human tone
- No robotic language
"""

    # Combine personality + system rules
    prompt = personality + system_prompt + "\n"

    # Inject conversation history (memory)
    for chat in history:
        prompt += f"User: {chat['user']}\nBot: {chat['bot']}\n"

    # Add current user message
    prompt += f"User: {message}\nBot:"

    # Return final prompt for LLM
    return prompt