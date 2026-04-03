memory = {}
MAX_HISTORY = 3


def get_memory(user_id):
    return memory.get(user_id, [])


def add_to_memory(user_id, user_msg, bot_msg):
    if user_id not in memory:
        memory[user_id] = []

    #  Clean bot response before saving
    if "Bot:" in bot_msg:
        bot_msg = bot_msg.split("Bot:")[-1].strip()

    memory[user_id].append({
        "user": user_msg,
        "bot": bot_msg
    })

    # Keep last N messages
    memory[user_id] = memory[user_id][-MAX_HISTORY:]