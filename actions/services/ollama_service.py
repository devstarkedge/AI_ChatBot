import requests
import re

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "phi3"


def clean_response(response):

    # Remove unwanted system leakage
    bad_patterns = [
        "You are",
        "Instruction",
        "Assistant:",
        "Bot:",
        "User:",
        "---",
    ]

    for pattern in bad_patterns:
        if pattern in response:
            response = response.split(pattern)[0]

    response = response.strip()

    #  Remove extra new lines
    response = response.replace("\n", " ").strip()

    #  Extract first complete sentence
    sentences = re.split(r'(?<=[.!?]) +', response)

    if sentences and len(sentences[0].split()) > 2:
        response = sentences[0]

    # fallback if no punctuation
    words = response.split()
    if len(words) > 15:
        response = " ".join(words[:15])

    return response.strip()


def generate_response(prompt):
    try:
        res = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.6,   
                    "num_predict": 35    
                }
            },
            timeout=30
        )

        res.raise_for_status()
        data = res.json()

        response = data.get("response", "").strip()

        #  clean response
        response = clean_response(response)

        # Reject bad outputs
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