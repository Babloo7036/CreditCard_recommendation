from groq import Groq
import uuid
import logging
import os

logger = logging.getLogger(__name__)

class CreditCardAgent:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.sessions = {}
        self.questions = [
            "What is your monthly income in INR?",
            "How much do you spend monthly on fuel in INR?",
            "How much do you spend monthly on travel in INR?",
            "How much do you spend monthly on groceries in INR?",
            "How much do you spend monthly on dining in INR?",
            "What benefits are you looking for? (e.g., cashback, travel rewards, dining)",
            "Do you have any existing credit cards? If yes, please list them, or say 'none'.",
            "What is your credit score? (Enter a number or 'unknown')"
        ]

    def start_session(self):
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {"step": 0, "answers": {}}
        logger.info(f"Started new session: {session_id}")
        return session_id

    def validate_answer(self, step, answer):
        try:
            if step == 0:  # Income
                return float(answer) > 0, "Income must be a positive number."
            elif step in [1, 2, 3, 4]:  # Spending
                return float(answer) >= 0, "Spending must be a non-negative number."
            elif step == 5:  # Benefits
                return len(answer.strip()) > 0, "Please specify a benefit."
            elif step == 6:  # Existing cards
                return answer.strip().lower() == "none" or len(answer.strip()) > 0, "Please list cards or say 'none'."
            elif step == 7:  # Credit score
                if answer.lower() == "unknown":
                    return True, ""
                return int(answer) >= 300 and int(answer) <= 900, "Credit score must be between 300 and 900 or 'unknown'."
        except ValueError:
            return False, "Invalid input format."
        return True, ""

    def get_next_question(self, session_id):
        if session_id not in self.sessions:
            return "Invalid session."
        step = self.sessions[session_id]["step"]
        if step < len(self.questions):
            return self.questions[step]
        return "All questions answered. Ready to get recommendations?"

    def process_answer(self, session_id, answer):
        if session_id not in self.sessions:
            return "Invalid session."
        
        step = self.sessions[session_id]["step"]
        if step >= len(self.questions):
            return "No more questions."

        is_valid, error_message = self.validate_answer(step, answer)
        if not is_valid:
            prompt = f"The user provided an invalid answer: '{answer}'. Error: {error_message}. Politely ask them to provide a valid answer for: {self.questions[step]}"
            response = self.client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content

        # answers
        keys = ["income", "spending_fuel", "spending_travel", "spending_groceries", "spending_dining", "benefits", "existing_cards", "credit_score"]
        self.sessions[session_id]["answers"][keys[step]] = answer
        self.sessions[session_id]["step"] += 1

        return self.get_next_question(session_id)

    def get_user_data(self, session_id):
        if session_id in self.sessions:
            return self.sessions[session_id]["answers"]
        return None