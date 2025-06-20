from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("API_KEY")
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL")
BASE_URL = os.getenv("BASE_URL")

MODEL_NAME = "mistralai/devstral-small:free"

print("MCP_SERVER_URL:", MCP_SERVER_URL)