"""
Ping command implementation for testing bot responsiveness.
"""
import discord
from discord import app_commands
from discord.ext import commands

from ..core.logger import logger

class PingCog(commands.Cog):
    """Ping command for checking bot latency."""
    
    def __init__(self, bot: commands.Bot):
        """Initialize the cog with bot instance."""
        self.bot = bot
    
    @app_commands.command(
        name="ping",
        description="Botの応答時間を確認します"
    )
    async def ping(self, interaction: discord.Interaction):
        """Ping command to check bot latency."""
        # Log the command execution
        logger.log_command("ping", f"{interaction.user} (ID: {interaction.user.id})")
        
        # Calculate and send the latency
        latency = round(self.bot.latency * 1000)
        await interaction.response.send_message(
            f"Pong! 🏓 ({latency}ms)",
            ephemeral=True
        )

async def setup(bot: commands.Bot):
    """Set up the Ping cog."""
    await bot.add_cog(PingCog(bot))
