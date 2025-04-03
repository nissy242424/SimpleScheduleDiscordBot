"""
Main entry point for the Discord Schedule Bot.
"""
import asyncio
import discord
from discord.ext import commands

from simple_schedule_bot.core.config import config
from simple_schedule_bot.core.logger import logger

class ScheduleBot(commands.Bot):
    """Discord Schedule Bot main class"""
    
    def __init__(self):
        """Initialize the bot with required intents and settings."""
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        super().__init__(
            command_prefix=config.COMMAND_PREFIX,
            intents=intents,
            help_command=None  # カスタムヘルプコマンドを使用予定
        )
    
    async def setup_hook(self):
        """Bot setup hook - called before the bot starts."""
        # Load command cogs
        await self.load_extension("simple_schedule_bot.commands.ping")
        await self.load_extension("simple_schedule_bot.commands.schedule")
        
        # Sync commands with Discord
        logger.logger.info("Syncing commands...")
        await self.tree.sync()
        logger.logger.info("Commands synced successfully")
    
    async def on_ready(self):
        """Called when the bot is ready and connected."""
        logger.logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        logger.logger.info("------")
    
    async def on_command_error(self, ctx, error):
        """Global error handler for command errors."""
        if isinstance(error, commands.errors.CommandNotFound):
            return
        
        error_message = str(error)
        logger.log_error(error, f"Command: {ctx.command}")
        
        await ctx.send(f"エラーが発生しました: {error_message}")

def main():
    """Main entry point."""
    bot = ScheduleBot()
    
    try:
        logger.logger.info("Starting bot...")
        asyncio.run(bot.start(config.DISCORD_TOKEN))
    except KeyboardInterrupt:
        logger.logger.info("Shutting down...")
    except Exception as e:
        logger.log_error(e, "Bot startup")
        raise

if __name__ == "__main__":
    main()
