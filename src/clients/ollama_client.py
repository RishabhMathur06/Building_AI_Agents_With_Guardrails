"""
Handles communication with locally-running models.
"""
import ollama
from typing import List, Dict, Any, Optional
from ..config import Config
import asyncio

class OllamaClient:
    """
    Client for interacting with Ollama-hosted local models.
    
    This client provides a unified interface for:
    - Fast inference with lightweight models (Gemma 2)
    - Security/compliance checks with specialized models (Llama Guard 3)
    """

    def __init__(self, base_url: Optional[str]=None):
        """
        Initialize Ollama client.
        
        Args:
            base_url: Ollama server URL (defaults to config value)
        """
        self.base_url = base_url or Config.OLLAMA_BASE_URL
        self.client = ollama.Client(host=base_url)

        if Config.VERBOSE:
            print(f"Ollama client initialized at: {self.base_url}")

    def generate(
            self,
            model: str,
            prompt: str,
            system: Optional[str] = None,
            temperature: float = 0.7,
            max_tokens: int = 1024,
            **kwargs
    ) -> str:
        """
        Generate a completion using an Ollama model.
        
        Args:
            model: Model name (e.g., 'gemma2:2b', 'llama-guard3:8b')
            prompt: User prompt/query
            system: System message to set context (optional)
            temperature: Sampling temperature (0.0 = deterministic, 1.0 = creative)
            max_tokens: Maximum tokens in response
            **kwargs: Additional parameters for ollama.generate()
        
        Returns:
            str: Model's text response
        """
        try:
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})

            # Calling Ollama API
            response = self.client.chat(
                model=model,
                messages=messages,
                options={
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    **kwargs
                }
            )

            return response['message']['content']
        
        except Exception as e:
            print(f"ERROR in Ollama generation with model: {model}: {e}")
            raise

    async def generate_async(
            self,
            model: str,
            prompt: str,
            system: Optional[str] = None,
            temperature: float = 0.7,
            max_tokens: int = 1024,
            **kwargs
    ) -> str:
        """
        Asynchronous version of generate() for parallel guardrail execution.
        
        This is crucial for Layer 1 guardrails which run concurrently.
        
        Args:
            Same as generate()
        
        Returns:
            str: Model's text response
        """
        return await asyncio.to_thread(
            self.generate,
            model,
            prompt,
            system,
            temperature,
            max_tokens,
            **kwargs
        )
    
    def check_model_availability(self, model: str) -> bool:
        """
        Check if a model is available locally.
        
        Args:
            model: Model name to check
        
        Returns:
            bool: True if model is available, False otherwise
        """
        try:
            models = self.client.list()
            available_models =  [m['name'] for m in models.get('models', [])]
            return model in available_models
        except Exception as e:
            print(f"ERROR checking model availability: {e}")
            return False
        
    def pull_model(self, model:str):
        """
        Pull/download a model if not available locally.
        
        Args:
            model: Model name to pull (e.g., 'gemma2:2b')
        """
        try:
            print(f"Fetching Model: {model}... This may take few minutes.")
            self.client.pull(model)
            print(f"Model: {model} downloaded successfully!")
        except Exception as e:
            print(f"ERROR pulling model {model}: {e}")
            raise

# Instance for global access.
ollama_client = OllamaClient()