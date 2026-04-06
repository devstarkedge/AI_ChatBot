from typing import Text, Dict, Any, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import random
import asyncio

# Custom modules
from .services.ollama_service import generate_response
from .utils.prompt_builder import build_prompt
from .utils.memory_store import add_to_memory


class ActionSmartReply(Action):
    """
    Custom Rasa action to generate AI-based smart replies
    using Ollama LLM with memory + prompt engineering.
    """

    def name(self) -> Text:
        """
        Unique action name (must match domain.yml)
        """
        return "action_smart_reply"

    async def simulate_typing_delay(self, text: str):
        """
        Simulates human-like typing delay based on message length
        """
        words = len(text.split())

        # Short replies - quick response
        if words <= 3:
            await asyncio.sleep(0.8)

        # Medium replies - moderate delay
        elif words <= 10:
            await asyncio.sleep(1.5)

        # Long replies - longer delay
        else:
            await asyncio.sleep(2.0)

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        """
        Main execution function triggered by Rasa
        """

        try:
            # Get latest user message
            user_text = tracker.latest_message.get("text", "").strip()

            # Unique user/session ID
            sender_id = tracker.sender_id

            # Ignore empty input
            if not user_text:
                return []

            # Build structured prompt (context + memory + user input)
            prompt = build_prompt(sender_id, user_text)

            # Generate AI response using Ollama
            ai_reply = await generate_response(prompt, user_text)

            # Fallback if AI fails or returns empty
            if not ai_reply:
                ai_reply = random.choice([
                    "hmm 👀",
                    "tell me more 😄",
                    "interesting 👀"
                ])

            # Fetch last bot messages to avoid repetition
            last_bot_messages = [
                e.get("text") for e in tracker.events
                if e.get("event") == "bot"
            ]

            # Prevent duplicate responses (last 2 messages)
            if ai_reply in last_bot_messages[-2:]:
                return []

            # Simulate typing delay for better UX
            await self.simulate_typing_delay(ai_reply)

            # Store conversation in memory (for context awareness)
            add_to_memory(sender_id, user_text, ai_reply)

            # Send final response to user
            dispatcher.utter_message(text=ai_reply)

            return []

        except Exception as e:
            # Log error for debugging
            print("[ACTION ERROR]", e)

            # Graceful fallback message
            dispatcher.utter_message(
                text="something went wrong 😅"
            )

            return []