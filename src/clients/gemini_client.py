"""
Gemini API Client for Cloud-Based Powerful Reasoning
Handles communication with Google's Gemini models for complex tasks
"""

# Importing dependencies.
from google import genai
from google.genai import types
from typing import List, Optional, Any, Dict
from ..config import Config
import asyncio
import json

class GeminiClient:
    """
    Client for interacting with Google Gemini API.
    """ 
    def __init__(self, api_key: Optional[str]=None):
        """
        Initializes the gemini client.

        Args:
            api_key: Gemini API Key
        """
        self.api_key = api_key or Config.GEMINI_API_KEY

        if not self.api_key:
            raise ValueError("Gemini API key not found. Please set api key in .env file first.")
        
        self.client = genai.Client(api_key=api_key)

        if Config.VERBOSE:
            print("Gemini client initialized successfully.")

    def generate(
            self,
            prompt: str,
            model: Optional[str] = None,
            system_instruction: Optional[str] = None,
            temperature: float = 0.7,
            max_output_tokens: int = 2048,
            **kwargs
    ) -> str:
        """
        Generate a completion using gemini model.

        Args:
            prompt: User prompt/query
            model: Model name (defaults to Config.MODEL_POWERFUL)
            system_instruction: System instruction to set behavior
            temperature: Controls randomness
            max_output_tokens: Maximum tokens in response

        Returns:
            str: Model's text response
        """
        try:
            model = model or Config.MODEL_POWERFUL

            # Building generation configurations.
            config = types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_output_tokens,
                system_instruction=system_instruction,
                **kwargs
            )

            # Generate response.
            response = self.client.models.generate_content(
                model=model,
                contents=prompt,
                config=config
            )

            return response.text

        except Exception as e:
            print(f"ERROR in generating response with model {model} : {e}")
            raise

    async def generate_async(
            self,
            prompt: str,
            model: Optional[str]=None,
            system_instruction: Optional[str]=None,
            temperature: float=0.7,
            max_output_tokens: int=2048,
            **kwargs
    ) -> str:
        """
        Asynchronous version of generate() for parallel execution.
        
        Args:
            Same as generate()
        
        Returns:
            str: Model's text response
        """
        return await asyncio.to_thread(
            self.generate,
            prompt,
            model,
            system_instruction,
            temperature,
            max_output_tokens,
            **kwargs
        )

    def generate_json(
            self,
            prompt: str,
            model: Optional[str]=None,
            system_instruction: Optional[str]=None,
            **kwargs
    ) -> Dict[str, Any]:
        """
        Generate structured JSON output (useful for guardrail decisions).
        
        Args:
            prompt: User prompt requesting JSON output
            model: Model name
            system_instruction: System instruction
            **kwargs: Additional parameters
        
        Returns:
            dict: Parsed JSON response
        """
        json_prompt = f"{prompt}\n\nRespond ONLY with valid JSON formatting and no other additional text."

        response_text = self.generate(
            prompt=json_prompt,
            model=model,
            system_instruction=system_instruction,
            temperature=0.1, # Lower temperature for structured output
            **kwargs
        )

        # Extract JSON from the response
        response_text = response_text.strip()

        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]

        return json.loads(response_text.strip())
    
# Instance for global access.
gemini_client = GeminiClient()