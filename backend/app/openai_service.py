import asyncio
import logging
from openai import AsyncOpenAI
from .config import settings
from .models import SymptomCheckRequest

logger = logging.getLogger(__name__)

class OpenAIService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.max_retries = 3
        self.base_delay = 1  # seconds

    async def analyze_symptoms(self, symptom_data: SymptomCheckRequest) :
        # Create the prompt for symptom analysis
        prompt = self._create_analysis_prompt(symptom_data)
        
        for attempt in range(self.max_retries):
            try:
                response = await self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "system",
                            "content": """You are a medical AI assistant. Analyze the provided symptoms and give a professional medical assessment. 
                            Always include:
                            1. Possible conditions based on symptoms
                            2. Severity assessment
                            3. Recommended next steps
                            4. When to seek immediate medical attention
                            
                            IMPORTANT: This is for informational purposes only and should not replace professional medical advice."""
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    max_tokens=1000,
                    temperature=0.3
                )
                
                analysis = response.choices[0].message.content
                logger.info(f"Symptom analysis completed successfully")
                return analysis
                
            except Exception as e:
                logger.error(f"OpenAI API error (attempt {attempt + 1}): {e}")
                
                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    delay = self.base_delay * (2 ** attempt)
                    await asyncio.sleep(delay)
                else:
                    # Final attempt failed, return error message
                    return self._get_fallback_response()

    def _create_analysis_prompt(self, symptom_data: SymptomCheckRequest) -> str:
        prompt = f"""
        Please analyze the following patient symptoms:

        Patient Information:
        - Age: {symptom_data.age} years
        - Sex: {symptom_data.sex}
        - Symptoms: {symptom_data.symptoms}
        - Duration: {symptom_data.duration}
        - Severity (1-10): {symptom_data.severity}
        - Additional Notes: {symptom_data.additional_notes or 'None'}

        Please provide a comprehensive analysis including:
        1. Possible medical conditions
        2. Severity assessment
        3. Recommended next steps
        4. When to seek immediate medical attention
        5. General health recommendations

        Format your response in a clear, structured manner.
        """
        return prompt

    def _get_fallback_response(self) -> str:
        return """I apologize, but I'm currently unable to analyze your symptoms due to a technical issue. 

        Please consider:
        1. Contacting a healthcare provider for professional medical advice
        2. Visiting an emergency room if symptoms are severe
        3. Trying again later

        This is for informational purposes only and should not replace professional medical advice."""

    async def health_check(self) -> bool:
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            return True
        except Exception as e:
            logger.error(f"OpenAI health check failed: {e}")
            return False

# Create OpenAI service instance
openai_service = OpenAIService() 