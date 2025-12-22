"""
Configuration module for Agentic Guardrails System
Centralizes all model selection, API keys, and system settings
"""

# Importing dependencies.
import os
from pathlib import Path
from dotenv import load_dotenv

# Loading environment variables.
load_dotenv()

class Config:
    # ----API Configuration----
    GEMINI_API_KEY : str = os.getenv("GEMINI_API_KEY", "")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    # ----Model Selection----
    # Role specific model selection based on cost/performance trade-off

    ## Fast, lightweight models for simple tasks.
    ## Use Cases: 
    ##  - Topical Filtering
    ##  - Quick Classification
    MODEL_FAST : str = os.getenv("MODEL_FAST", "gemma2:2b")

    ## Guarding Models for security.
    ## Use Cases: 
    ##  - Threat Detection
    ##  - Compliance Checking
    ##  - Content Moderating
    MODEL_GUARD : str = os.getenv("MODEL_GUARD", "llama-guard3:8b")

    ## Complexing reasoning models.
    ## Use cases
    ##  - Reasoning
    ##  - Hallucination Detection
    ##  - Evaluation
    MODEL_POWERFUL : str = os.getenv("MODEL_POWERFUL", "gemini-2.5-flash")

    # ----Data Configuration----
    DATA_DIR : Path = Path("data")

    # ----System Settings----
    # Timeout for LLM API calls.
    LLM_TIMEOUT: int = 30

    # Maximum retries for failed API calls.
    MAX_RETRIES: int = 3

    # Enable verbose logging.
    VERBOSE: bool = True

    @classmethod
    def validate(cls) -> bool:
        """
        Validates that all required configuration is present.
        
        Returns:
            bool: True if configuration is valid, False otherwise
        """
        if not cls.GEMINI_API_KEY:
            print("WARNING: GEMINI_API_KEY not found in .env file.")
            print("Please set it in .env file.")
            return False
        
        # Creating data directory if doesn't exists.
        cls.DATA_DIR.mkdir(exist_ok=True)

        return True
    
    @classmethod
    def print_config(cls):
        print("\n" + "="*60)
        print("AGENTIC GUARDRAILS SYSTEM - Configuration")
        print("="*60)
        print(f"\n MODEL SELECTION:")
        print(f"   |- Fast/Routing:         {cls.MODEL_FAST} (Ollama - Local)")
        print(f"   |- Security/Compliance:  {cls.MODEL_GUARD} (Ollama - Local)")
        print(f"   |- Core Reasoning        {cls.MODEL_POWERFUL} (GEMINI API- Cloud)")
        print(f"\n API Endpoints:")
        print(f"   |- Ollama:  {cls.OLLAMA_BASE_URL}")
        print(f"   |- Gemini:  {'✓ Configured' if cls.GEMINI_API_KEY else '✗ Not configured'}")
        print(f"\n System Settings:")
        print(f"   |- Data Directory: {cls.DATA_DIR}")
        print(f"   |- LLM Timeout:    {cls.LLM_TIMEOUT}s")
        print(f"   |- Max Retries:    {cls.MAX_RETRIES}")
        print("="*60 + "\n")

# Validate configurations on import.
if __name__ != "__main__":
    Config.validate()