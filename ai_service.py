import os
import google.generativeai as genai
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class AIService:
    def __init__(self):
        # Initialize Gemini
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        if self.gemini_key:
            genai.configure(api_key=self.gemini_key)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.gemini_model = None
            print("Gemini API Key missing")

        # Initialize Groq
        self.groq_key = os.getenv("GROQ_API_KEY")
        if self.groq_key:
            self.groq_client = Groq(api_key=self.groq_key)
        else:
            self.groq_client = None
            print("Groq API Key missing")

    def chat_gemini(self, message):
        if not self.gemini_model:
            return "Gemini API Key is not configured."
        try:
            response = self.gemini_model.generate_content(message)
            return response.text
        except Exception as e:
            return f"Gemini Error: {str(e)}"

    def chat_groq(self, message, model="llama-3.3-70b-versatile"):
        if not self.groq_client:
            return "Groq API Key is not configured."
        try:
            completion = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": message}],
                model=model,
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"Groq Error: {str(e)}"

    def ask(self, message, provider="gemini"):
        if provider == "gemini":
            return self.chat_gemini(message)
        elif provider == "groq":
            return self.chat_groq(message)
        else:
            return "Invalid AI provider selected."

# Singleton instance
ai_service = AIService()
