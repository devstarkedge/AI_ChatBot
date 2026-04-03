from .memory_store import get_memory

def build_prompt(user_id, message):
    history = get_memory(user_id)

    prompt = ""

    for chat in history:
        prompt += f"User: {chat['user']}\nAssistant: {chat['bot']}\n"

    prompt += f"User: {message}\nAssistant:"
    return prompt