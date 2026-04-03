import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "tinyllama"


def clean_response(response):
    # remove system leakage
    if "You are" in response:
        response = response.split("User:")[-1]

    # remove tags
    for tag in ["User:", "Assistant:", "Bot:", "BoT:"]:
        if tag in response:
            response = response.split(tag)[-1]

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
                    "temperature": 0.4,
                    "num_predict": 80
                }
            },
            timeout=30
        )

        res.raise_for_status()
        data = res.json()

        response = data.get("response", "").strip()

        #  clean properly
        response = clean_response(response)

        if not response or len(response) < 5:
            return "I didn't understand that clearly. Can you try again?"

        return response

    except requests.exceptions.Timeout:
        return "I'm a bit slow right now 😅 try again."

    except Exception as e:
        print("[OLLAMA ERROR]", e)
        return "Something went wrong while generating response."