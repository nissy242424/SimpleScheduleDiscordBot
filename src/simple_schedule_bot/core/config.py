"""
Configuration management for the Discord Schedule Bot.
Handles loading and accessing environment variables and settings.
"""
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

class Config:
    """環境変数と設定の管理"""
    
    def __init__(self):
        """Initialize configuration."""
        # Load environment variables from .env file
        env_path = Path(".") / ".env"
        load_dotenv(env_path)
        
        # Required settings
        self.DISCORD_TOKEN: str = self._get_required("DISCORD_BOT_TOKEN")
        
        # Optional settings with defaults
        self.COMMAND_PREFIX: str = os.getenv("COMMAND_PREFIX", "/")
        self.DB_PATH: str = os.getenv("DB_PATH", "data/schedule.db")
        self.MAX_DATES: int = int(os.getenv("MAX_DATES", "10"))
        self.REMINDER_CHECK_INTERVAL: int = int(os.getenv("REMINDER_CHECK_INTERVAL", "60"))
    
    def _get_required(self, key: str) -> str:
        """Get a required environment variable."""
        value = os.getenv(key)
        if value is None:
            raise ValueError(f"Required environment variable '{key}' is not set")
        return value

# Global configuration instance
config = Config()
