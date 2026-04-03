from .memory_store import get_memory

def build_prompt(user_id, message):
    history = get_memory(user_id)

    msg = message.lower()

    #  Decide response style
    if any(word in msg for word in ["joke", "story", "explain", "detail", "tell me about"]):
        style = "long"
    else:
        style = "short"

    #  Dynamic system prompt
    if style == "short":
        system_prompt = """
You are a chill chatbot.

Rules:
- Max 1 sentence
- Max 10 words
- Casual tone
- No explanation
"""
    else:
        system_prompt = """
You are a friendly chatbot.

Rules:
- Give slightly detailed response (2-4 lines)
- Still casual tone
- No AI-like language
"""

    prompt = system_prompt + "\n"

    for chat in history:
        prompt += f"User: {chat['user']}\nBot: {chat['bot']}\n"

    prompt += f"User: {message}\nBot:"

    return prompt