"""
Logging configuration and utilities for the Discord Schedule Bot.
"""
import logging
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

class Logger:
    """ログ管理クラス"""
    
    def __init__(self):
        """Initialize logger."""
        self.logger = logging.getLogger("discord_schedule_bot")
        
        if not self.logger.handlers:
            self.setup()
    
    def setup(self):
        """ログ設定の初期化"""
        self.logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # File handler with rotation
        file_handler = RotatingFileHandler(
            filename=log_dir / "bot.log",
            maxBytes=1024 * 1024,  # 1MB
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setFormatter(logging.Formatter(
            "[%(asctime)s] %(levelname)s: %(message)s"
        ))
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter(
            "[%(asctime)s] %(levelname)s: %(message)s"
        ))
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def log_command(self, cmd: str, user: str):
        """コマンド実行のログを記録"""
        self.logger.info(f"Command executed: {cmd} by {user}")
    
    def log_error(self, error: Exception, context: str = ""):
        """エラーログを記録"""
        if context:
            self.logger.error(f"Error in {context}: {str(error)}")
        else:
            self.logger.error(f"Error occurred: {str(error)}")

# Global logger instance
logger = Logger()
