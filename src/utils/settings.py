import os
from dotenv import load_dotenv

# https://github.com/theskumar/python-dotenv


load_dotenv(verbose=True)

# Note: KeyError if the environment variable not found

LLM_MODEL_NAME = os.environ["LLM_MODEL_NAME"]
LLM_API_BASE = os.environ["LLM_API_BASE"]

SEARCH_ENDPOINT = os.environ["SEARCH_ENDPOINT"]
SEARCH_API_KEY = os.environ["SEARCH_API_KEY"]

# logging settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
