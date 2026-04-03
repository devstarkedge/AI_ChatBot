from typing import Text, Dict, Any, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import random
# import os
from dotenv import load_dotenv

#  AI services
from .services.ollama_service import generate_response
from .utils.prompt_builder import build_prompt
from .utils.memory_store import add_to_memory, get_memory

load_dotenv()

USE_FAKE_AI = False  


class ActionSmartReply(Action):

    def name(self) -> Text:
        return "action_smart_reply"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_text = tracker.latest_message.get("text", "")
        intent = tracker.latest_message.get("intent", {}).get("name")
        sender_id = tracker.sender_id

        text = user_text.lower().strip()

        #  Safety
        if intent == "risky_question":
            dispatcher.utter_message(text="I can’t help with that 😅")
            return []

        #  Tone variation
        tone_prefix = random.choice(["", "", "hmm… "])

        #  SMART TOPIC DETECTION
        topic = None

        if any(word in text for word in ["code", "programming", "react", "node", "js"]):
            topic = "coding"

        elif any(word in text for word in ["hungry", "hugry", "food", "eat", "khana", "bhook"]):
            topic = "food"

        elif any(word in text for word in ["gym", "fitness", "workout", "exercise"]):
            topic = "fitness"

        elif intent == "mood_unhappy":
            topic = "emotion"

        elif "life" in text:
            topic = "life"

        #  QUICK HUMAN-LIKE REPLIES
        if text in ["nothing", "nothing much", "nm", "kuch nahi"]:
            ai_reply = random.choice([
                "haha same 😄",
                "just chilling huh 😄",
                "relaxed day 👀"
            ])

        elif "how are you" in text:
            ai_reply = random.choice([
                "I’m good 😄 what about you?",
                "doing well! what’s up?",
                "pretty good 👀 how’s your day?"
            ])

        elif text in ["yes", "yeah", "yup"]:
            ai_reply = random.choice([
                "nice 👍",
                "got it 😄",
                "okay cool"
            ])

        elif text in ["no", "nope"]:
            ai_reply = random.choice([
                "alright 😄",
                "no worries",
                "okay 👍"
            ])

        #  FOOD / HUNGER LOGIC
        elif topic == "food":
            ai_reply = random.choice([
                "you should grab something tasty 😄 maybe pizza, burger or something healthy?",
                "bhook lagi hai? 😄 try something light or your favorite food",
                "go eat something 😄 food makes everything better"
            ])

        #  FITNESS LOGIC
        elif topic == "fitness":
            ai_reply = random.choice([
                "fitness is great 🔥 even a small workout helps",
                "you into gym? 💪 consistency is key",
                "start with simple exercises 😄 don't overthink"
            ])

        #  INTENT BASED
        elif intent == "greet":
            ai_reply = random.choice([
                "Hey! 😊",
                "Hi 👀",
                "Hello 😄"
            ])

        elif intent == "casual_talk":
            ai_reply = random.choice([
                "Just chilling 😄 what about you?",
                "Talking to you 😎",
                "Nothing much… what’s going on?"
            ])

        elif intent == "ask_name":
            ai_reply = "I’m your AI buddy 😄"

        elif intent == "ask_help":
            ai_reply = "Of course 👍 what do you need help with?"

        elif intent == "ask_personal":
            ai_reply = random.choice([
                "I enjoy good conversations 😄",
                "I’m just here to chat and vibe"
            ])

        elif intent == "ask_opinion":
            ai_reply = random.choice([
                "Hmm… depends 🤔 what do you think?",
                "That’s interesting… I’d say it varies"
            ])

        elif intent == "mood_great":
            ai_reply = random.choice([
                "That’s nice 😄",
                "love that 🔥",
                "good to hear that"
            ])

        elif intent == "mood_unhappy":
            ai_reply = random.choice([
                "That sounds tough 😔 wanna talk?",
                "I get that… I’m here"
            ])

        elif intent == "continue_conversation":
            ai_reply = random.choice([
                "yeah?",
                "hmm 👀",
                "go on…"
            ])

        elif intent == "bot_challenge":
            ai_reply = "maybe 😄 but I feel real enough right?"

        elif intent == "user_check":
            ai_reply = "yeah I’m here 👀"

        elif intent == "goodbye":
            ai_reply = "alright 🙂 catch you later"

        #  AI FALLBACK 
        else:
            if USE_FAKE_AI:
                ai_reply = "hmm interesting 👀 tell me more"
            else:
                prompt = build_prompt(sender_id, user_text)
                ai_reply = generate_response(prompt, user_text)

        #  MEMORY SAVE
        add_to_memory(sender_id, user_text, ai_reply)

        #  Tone apply
        ai_reply = tone_prefix + ai_reply

        dispatcher.utter_message(text=ai_reply)

        return []