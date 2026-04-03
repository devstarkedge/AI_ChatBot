import requests
import re

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "phi3"


def clean_response(response, allow_long=False):

    bad_patterns = ["You are", "Instruction", "Assistant:", "Bot:", "User:", "---"]

    for pattern in bad_patterns:
        if pattern in response:
            response = response.split(pattern)[0]

    response = response.strip().replace("\n", " ")

    #  Short mode
    if not allow_long:
        sentences = re.split(r'(?<=[.!?]) +', response)
        if sentences:
            response = sentences[0]

        words = response.split()
        if len(words) > 15:
            response = " ".join(words[:15])

    return response.strip()


def generate_response(prompt, user_text):
    try:
        msg = user_text.lower()

        #  Decide response length
        allow_long = any(word in msg for word in [
            "joke", "story", "explain", "detail", "tell me"
        ])

        res = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.6,
                    "num_predict": 80 if allow_long else 35
                }
            },
            timeout=30
        )

        res.raise_for_status()
        data = res.json()

        response = data.get("response", "").strip()

        #  Clean response
        response = clean_response(response, allow_long)

        #  Reject garbage output
        if (
            not response
            or len(response) < 3
            or "You are" in response
            or "Instruction" in response
        ):
            return "hmm 😄"

        return response

    except requests.exceptions.Timeout:
        return "thoda slow ho gaya 😅 try again"

    except Exception as e:
        print("[OLLAMA ERROR]", e)
        return "something went wrong 😅"