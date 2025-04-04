"""
Modal dialogs for schedule management.
"""
import discord
from typing import List
from datetime import datetime

from ..core.logger import logger
from ..db.repository import ScheduleRepository
from ..models.schedule import Schedule, ScheduleStatus, VoteStatus

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

    def __init__(self, repository: ScheduleRepository, selected_dates: List[datetime]):
        super().__init__()
        self.repository = repository
        self.selected_dates = selected_dates

    async def on_submit(self, interaction: discord.Interaction):
        """Handle form submission."""
        try:
            if not self.selected_dates:
                await interaction.response.send_message(
                    "エラー: 少なくとも1つの候補日を選択してください。",
                    ephemeral=True
                )
                return

            # Create schedule
            schedule = Schedule.create(
                title=str(self.title_input),
                description=str(self.description_input) if self.description_input.value else None,
                creator_id=interaction.user.id,
                channel_id=interaction.channel_id,
                dates=self.selected_dates
            )

            # Save to database
            await self.repository.create_schedule(schedule)

            # Send response
            embed = discord.Embed(
                title="スケジュール作成完了",
                description=f"**{schedule.title}**\n" + \
                          (f"{schedule.description}\n\n" if schedule.description else "\n") + \
                          "**候補日時:**\n" + \
                          "\n".join([f"• {date.date.strftime('%Y-%m-%d %H:%MM')}" for date in schedule.dates]),
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
