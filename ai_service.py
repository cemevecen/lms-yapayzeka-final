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
            # Using Gemini 2.0 Flash for speed and intelligence
            self.gemini_model = genai.GenerativeModel(
                model_name='gemini-2.0-flash',
                system_instruction="Sen gelişmiş bir AI Eğitim Asistanısın. Öğrencilere ve eğitmenlere akademik konularda, ders planlamada ve içerik üretiminde yardımcı olursun. Yanıtların profesyonel, yapıcı ve eğitici olmalıdır."
            )
        else:
            self.gemini_model = None

        # Initialize Groq
        self.groq_key = os.getenv("GROQ_API_KEY")
        if self.groq_key:
            self.groq_client = Groq(api_key=self.groq_key)
        else:
            self.groq_client = None

    def chat_gemini(self, message):
        if not self.gemini_model:
            return "Gemini API Key is not configured."
        try:
            # Optimized generation config
            config = genai.types.GenerationConfig(
                temperature=0.7,
                top_p=0.9,
                top_k=40,
                max_output_tokens=2048,
            )
            response = self.gemini_model.generate_content(message, generation_config=config)
            return response.text
        except Exception as e:
            return f"Gemini Error: {str(e)}"

    def chat_groq(self, message, model="llama-3.3-70b-versatile"):
        if not self.groq_client:
            return "Groq API Key is not configured."
        try:
            completion = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "Sen gelişmiş bir AI Eğitim Asistanısın. Profesyonel ve eğitici yanıtlar vermelisin."},
                    {"role": "user", "content": message}
                ],
                model=model,
                temperature=0.7,
                max_tokens=2048,
                top_p=0.9
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
