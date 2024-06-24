import dotenv

dotenv.load_dotenv(dotenv.find_dotenv())
env_vars = dotenv.dotenv_values()

HF_TOKEN_WRITE = env_vars["HF_TOKEN_WRITE"]
LLM_REPO_NAME = env_vars["LLM_REPO_NAME"]
G_SHEET_ID = env_vars["G_SHEET_ID"]