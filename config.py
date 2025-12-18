import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    def __init__(self):
        self.MCP_SERVER_URL = "https://vipfapwm3x.us-east-1.awsapprunner.com/mcp"
        self.GROQ_API_KEY = os.getenv("GROQ_API_KEY")
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.model = "llama-3.1-8b-instant"


settings = Config()
