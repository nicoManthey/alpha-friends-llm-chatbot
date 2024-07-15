import os

# Attempt to load environment variables from .env file if present, for local development
try:
    import dotenv

    dotenv.load_dotenv(dotenv.find_dotenv())
except ImportError:
    # dotenv not installed, likely in production
    pass

# Access environment variables directly, works both locally and in hosted environments
HF_TOKEN_WRITE = os.getenv("HF_TOKEN_WRITE")
LLM_REPO_NAME = os.getenv("LLM_REPO_NAME")
G_SHEET_ID = os.getenv("G_SHEET_ID")
GOOGLE_SHEETS = os.getenv("GOOGLE_SHEETS")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL_NAME = os.getenv("GROQ_MODEL_NAME")
