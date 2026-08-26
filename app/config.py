"""
Application Configurations and Environment Settings
"""
import os

LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "MOCK_SECRET")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "MOCK_ACCESS_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./yuedpao_chatbot.db")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
