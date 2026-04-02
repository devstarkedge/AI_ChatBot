from typing import Text, Dict, Any, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import random
import os
from dotenv import load_dotenv

load_dotenv()

USE_FAKE_AI = True

# Memory store
user_memory = {}


class ActionSmartReply(Action):

    def name(self) -> Text:
        return "action_smart_reply"

    def run(self, dispatcher, tracker, domain):

        user_text = tracker.latest_message.get("text", "")
        intent = tracker.latest_message.get("intent", {}).get("name")
        sender_id = tracker.sender_id

        text = user_text.lower().strip()

        memory = user_memory.get(sender_id, {
            "history": [],
            "last_intent": None,
            "mood": None,
            "topic": None
        })

        #  Safety
        if intent == "risky_question":
            dispatcher.utter_message(text="I can’t help with that 😅")
            return []

        #  Natural tone 
        tone_prefix = random.choice([
            "",
            "",
            "hmm… "
        ])

        #  Topic detection 
        if "code" in text or "programming" in text:
            memory["topic"] = "coding"
        elif intent == "mood_unhappy":
            memory["topic"] = "emotion"
        elif "life" in text:
            memory["topic"] = "life"

        #  Mood tracking
        if intent == "mood_great":
            memory["mood"] = "happy"
        elif intent == "mood_unhappy":
            memory["mood"] = "sad"

        #  Special cases FIRST 

        # Neutral replies
        if text in ["nothing", "nothing much", "nm", "kuch nahi"]:
            ai_reply = random.choice([
                "haha same 😄",
                "fair enough 😄 just chilling?",
                "okay 😄 relaxed day huh",
            ])

        # How are you
        elif "how are you" in text:
            ai_reply = random.choice([
                "I’m good 😄 what about you?",
                "doing well! what’s up?",
                "pretty good 👀 how’s your day going?",
            ])

        # Yes / No handling
        elif text in ["yes", "yeah", "yup"]:
            ai_reply = random.choice([
                "nice 👍",
                "got it 😄",
                "okay cool",
            ])

        elif text in ["no", "nope"]:
            ai_reply = random.choice([
                "alright 😄",
                "no worries",
                "okay 👍",
            ])

        #  Intent-based replies

        elif intent == "greet":
            ai_reply = random.choice([
                "Hey! 😊",
                "Hi 👀",
                "Hello 😄",
            ])

        elif intent == "casual_talk":
            ai_reply = random.choice([
                "Just chilling 😄 what about you?",
                "Talking to you 😎",
                "Nothing much… what’s going on?",
            ])

        elif intent == "ask_name":
            ai_reply = "I’m your AI buddy 😄"

        elif intent == "ask_help":
            ai_reply = "Of course 👍 what do you need help with?"

        elif intent == "ask_personal":
            ai_reply = random.choice([
                "I enjoy good conversations 😄",
                "I’m just here to chat and vibe",
            ])

        elif intent == "ask_opinion":
            ai_reply = random.choice([
                "Hmm… depends 🤔 what do you think?",
                "That’s interesting… I’d say it varies",
            ])

        elif intent == "mood_great":
            ai_reply = random.choice([
                "That’s nice 😄",
                "love that 🔥",
                "good to hear that",
            ])

        elif intent == "mood_unhappy":
            ai_reply = random.choice([
                "That sounds tough 😔 wanna talk?",
                "I get that… I’m here",
            ])

        elif intent == "continue_conversation":
            ai_reply = random.choice([
                "yeah?",
                "hmm 👀",
                "go on…",
            ])

        elif intent == "bot_challenge":
            ai_reply = "maybe 😄 but I feel real enough right?"

        elif intent == "user_check":
            ai_reply = "yeah I’m here 👀"

        elif intent == "goodbye":
            ai_reply = "alright 🙂 catch you later"

        else:
            #  Smart fallback
            if memory["topic"] == "coding":
                ai_reply = "oh you're into coding 👀 what are you building?"
            elif memory["topic"] == "emotion":
                ai_reply = "that sounds important… tell me more"
            elif memory["topic"] == "life":
                ai_reply = "life gets confusing 😅 what’s going on?"
            else:
                ai_reply = random.choice([
                    "hmm 🤔",
                    "ohh 👀",
                    "interesting…",
                ])

        #  Smart continuation 
        if memory["last_intent"] == intent and random.random() > 0.7:
            ai_reply += random.choice([
                " btw you mentioned this earlier",
                "",
            ])

        #  Add tone
        ai_reply = tone_prefix + ai_reply

        #  Save memory
        memory["history"].append({"user": user_text, "bot": ai_reply})
        memory["last_intent"] = intent

        user_memory[sender_id] = memory

        dispatcher.utter_message(text=ai_reply)

        return []