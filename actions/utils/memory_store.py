# In-memory storage for user conversations
memory = {}

# Maximum number of chat exchanges to keep per user
MAX_HISTORY = 6


def get_memory(user_id):
    """
    Retrieve conversation history for a user.

    Args:
        user_id (str): Unique user/session identifier

    Returns:
        List[Dict]: List of past conversations
    """
    return memory.get(user_id, [])


def add_to_memory(user_id, user_msg, bot_msg):
    """
    Store a new conversation entry for a user.

    Args:
        user_id (str): Unique user/session identifier
        user_msg (str): User's message
        bot_msg (str): Bot's response
    """

    # Initialize memory for new user
    if user_id not in memory:
        memory[user_id] = []

    # Append new conversation pair
    memory[user_id].append({
        "user": user_msg,
        "bot": bot_msg
    })

    # Trim history to last N conversations (sliding window)
    memory[user_id] = memory[user_id][-MAX_HISTORY:]