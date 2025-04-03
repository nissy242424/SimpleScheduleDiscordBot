"""
Main entry point for the Discord Schedule Bot.
"""
import asyncio
import os
import signal
import sys
import discord
from discord.ext import commands

from simple_schedule_bot.core.config import config
from simple_schedule_bot.core.logger import logger
from simple_schedule_bot.db.database import DatabaseManager

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
        # Initialize database
        logger.logger.info("Initializing database...")
        self.db = await DatabaseManager.get_instance(config.DB_PATH)
        
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

    async def close(self):
        """Cleanly shut down the bot and close all resources."""
        logger.logger.info("Closing database connection...")
        if hasattr(self, 'db'):
            await self.db.close()
        
        logger.logger.info("Closing bot connection...")
        await super().close()

async def main():
    """Main entry point."""
    bot = ScheduleBot()
    
    async def shutdown():
        """Perform a clean shutdown."""
        try:
            logger.logger.info("Starting shutdown process...")
            
            # 1. まずWebSocket接続を終了してkeep-alive-handlerを停止
            logger.logger.info("Closing bot connection...")
            await bot.close()
            
            # 2. 残りのタスクを処理（keep-alive-handler以外）
            loop = asyncio.get_running_loop()
            pending = [t for t in asyncio.all_tasks(loop) 
                      if t is not asyncio.current_task() and
                      not t.done() and
                      not t.cancelled()]
            
            if pending:
                logger.logger.info(f"Cancelling {len(pending)} pending tasks...")
                for task in pending:
                    task.cancel()
                
                # タイムアウト付きで待機
                try:
                    await asyncio.wait(pending, timeout=5.0)
                except (asyncio.CancelledError, Exception) as e:
                    logger.log_error(e, "Task cancellation error")
            
            # 3. データベース接続を安全にクローズ
            if hasattr(bot, 'db'):
                logger.logger.info("Closing database connection...")
                try:
                    await bot.db.close()
                    # データベースマネージャーのクリーンアップ
                    DatabaseManager._instance = None
                    bot.db = None
                except Exception as e:
                    logger.log_error(e, "Database shutdown error")
            
            # 4. ログハンドラーのクリーンアップ
            for handler in logger.logger.handlers[:]:
                try:
                    logger.logger.removeHandler(handler)
                    handler.close()
                except Exception as e:
                    logger.log_error(e, "Logger cleanup error")
            
            logger.logger.info("Shutdown completed successfully")
            
        except Exception as e:
            logger.log_error(e, "Shutdown error")
            return 1
        return 0

    try:
        # シグナルハンドラの設定
        def signal_handler():
            """Handle termination signals."""
            asyncio.create_task(shutdown())
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Windowsでのシグナルハンドリング
        if os.name == 'nt':
            import win32api
            def win_handler(type):
                signal_handler()
                return True
            win32api.SetConsoleCtrlHandler(win_handler, True)
        else:
            # Unix系OSでのシグナルハンドリング
            for sig in (signal.SIGINT, signal.SIGTERM):
                loop.add_signal_handler(sig, signal_handler)
        
        # ボットの起動
        logger.logger.info("Starting bot...")
        try:
            await bot.start(config.DISCORD_TOKEN)
        except KeyboardInterrupt:
            logger.logger.info("Received keyboard interrupt")
        finally:
            exit_code = await shutdown()
            if exit_code != 0:
                sys.exit(exit_code)
    
    except Exception as e:
        logger.log_error(e, "Bot startup error")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
