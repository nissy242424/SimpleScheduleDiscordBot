"""
Schedule command implementation for managing schedules.
"""
import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timezone
from typing import List, Optional
import re

from ..core.logger import logger
from ..db.repository import ScheduleRepository
from ..models.schedule import Schedule, ScheduleStatus

class ScheduleCreateModal(discord.ui.Modal, title="スケジュール作成"):
    """Modal for creating a new schedule."""
    
    title_input = discord.ui.TextInput(
        label="タイトル",
        placeholder="スケジュールのタイトルを入力",
        min_length=1,
        max_length=100,
        required=True,
    )
    
    description_input = discord.ui.TextInput(
        label="説明",
        placeholder="スケジュールの説明を入力（任意）",
        max_length=1000,
        required=False,
        style=discord.TextStyle.paragraph,
    )
    
    dates_input = discord.ui.TextInput(
        label="候補日時",
        placeholder="YYYY-MM-DD HH:MM\n複数の場合は1行に1つ入力",
        style=discord.TextStyle.paragraph,
        required=True,
    )

    def __init__(self, repository: ScheduleRepository):
        super().__init__()
        self.repository = repository
        self.datetime_pattern = re.compile(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$')

    def validate_dates(self, dates_str: str) -> tuple[bool, str, Optional[List[datetime]]]:
        """Validate date strings and convert to datetime objects."""
        dates = []
        now = datetime.now(timezone.utc)
        
        # Split input into lines and remove empty lines
        date_strings = [line.strip() for line in dates_str.split('\n') if line.strip()]
        
        if not date_strings:
            return False, "少なくとも1つの候補日時を入力してください。", None
            
        if len(date_strings) > 10:
            return False, "候補日時は最大10個までです。", None
            
        for date_str in date_strings:
            # Check format
            if not self.datetime_pattern.match(date_str):
                return False, f"日時のフォーマットが不正です: {date_str}\n正しい形式: YYYY-MM-DD HH:MM", None
                
            try:
                # Convert to datetime
                date = datetime.strptime(date_str, '%Y-%m-%d %H:%M')
                date = date.replace(tzinfo=timezone.utc)
                
                # Check if date is in the future
                if date <= now:
                    return False, f"過去の日時は指定できません: {date_str}", None
                    
                dates.append(date)
            except ValueError as e:
                return False, f"無効な日時です: {date_str}\n{str(e)}", None
                
        return True, "", dates

    async def on_submit(self, interaction: discord.Interaction):
        """Handle form submission."""
        try:
            # Validate dates
            is_valid, error_message, dates = self.validate_dates(str(self.dates_input))
            if not is_valid:
                await interaction.response.send_message(
                    f"エラー: {error_message}",
                    ephemeral=True
                )
                return

            # Create schedule
            schedule = Schedule.create(
                title=str(self.title_input),
                description=str(self.description_input) if self.description_input.value else None,
                creator_id=interaction.user.id,
                channel_id=interaction.channel_id,
                dates=dates
            )

            # Save to database
            await self.repository.create_schedule(schedule)

            # Send response
            embed = discord.Embed(
                title="スケジュール作成完了",
                description=f"**{schedule.title}**\n" + \
                          (f"{schedule.description}\n\n" if schedule.description else "\n") + \
                          "**候補日時:**\n" + \
                          "\n".join([f"• {date.date.strftime('%Y-%m-%d %H:%M')}" for date in schedule.dates]),
                color=discord.Color.green()
            )
            
            await interaction.response.send_message(embed=embed)
            
            # Log the command execution
            logger.log_command(
                "schedule create",
                f"{interaction.user} (ID: {interaction.user.id}) created schedule: {schedule.id}"
            )

        except Exception as e:
            logger.error(f"Error in schedule creation: {str(e)}")
            await interaction.response.send_message(
                "スケジュールの作成中にエラーが発生しました。",
                ephemeral=True
            )

class ScheduleCog(commands.Cog):
    """Schedule management commands."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = bot.db  # DatabaseManager instance
        self.repository = ScheduleRepository(self.db)
    
    @app_commands.command(
        name="schedule",
        description="スケジュールの作成・管理を行います"
    )
    @app_commands.describe(
        action="実行するアクション（create/list/cancel）"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="作成", value="create"),
        app_commands.Choice(name="一覧", value="list"),
        app_commands.Choice(name="キャンセル", value="cancel"),
    ])
    async def schedule(
        self,
        interaction: discord.Interaction,
        action: str
    ):
        """Schedule command main handler."""
        logger.log_command(
            "schedule",
            f"{interaction.user} (ID: {interaction.user.id}) called {action}"
        )

        if action == "create":
            modal = ScheduleCreateModal(self.repository)
            await interaction.response.send_modal(modal)
        else:
            await interaction.response.send_message(
                f"Action '{action}' は現在実装されていません。",
                ephemeral=True
            )

async def setup(bot: commands.Bot):
    """Set up the Schedule cog."""
    await bot.add_cog(ScheduleCog(bot))
