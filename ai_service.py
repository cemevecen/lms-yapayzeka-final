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
            self.gemini_model = genai.GenerativeModel(
                model_name='gemini-flash-latest',
                system_instruction="Sen gelişmiş bir AI Eğitim Asistanısın. Profesyonel, yapıcı ve eğitici yanıtlar vermelisin."
            )
        else:
            self.gemini_model = None

        # Initialize Groq
        self.groq_key = os.getenv("GROQ_API_KEY")
        if self.groq_key:
            self.groq_client = Groq(api_key=self.groq_key)
        else:
            self.groq_client = None

    def chat_gemini(self, message, temp=0.7, tokens=2048):
        if not self.gemini_model:
            return "Gemini API Key is not configured."
        try:
            config = genai.types.GenerationConfig(
                temperature=temp,
                top_p=0.9,
                max_output_tokens=tokens,
            )
            response = self.gemini_model.generate_content(message, generation_config=config)
            return response.text
        except Exception as e:
            return f"Gemini Error: {str(e)}"

    def chat_groq(self, message, model="llama-3.3-70b-versatile", temp=0.7, tokens=2048):
        if not self.groq_client:
            return "Groq API Key is not configured."
        try:
            completion = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "Sen gelişmiş bir AI Eğitim Asistanısın. Profesyonel ve eğitici yanıtlar vermelisin."},
                    {"role": "user", "content": message}
                ],
                model=model,
                temperature=temp,
                max_tokens=tokens,
                top_p=0.9
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"Groq Error: {str(e)}"

    def ask(self, message, provider="gemini", temp=0.7, tokens=2048):
        if provider == "gemini":
            return self.chat_gemini(message, temp=temp, tokens=tokens)
        elif provider == "groq":
            return self.chat_groq(message, temp=temp, tokens=tokens)
        else:
            return "Invalid AI provider selected."

# Singleton instance
ai_service = AIService()
