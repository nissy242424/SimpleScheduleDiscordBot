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
from ..models.schedule import Schedule, ScheduleStatus, VoteStatus
from ..views import CalendarView

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
            # カレンダーViewを表示
            calendar_view = CalendarView()
            await interaction.response.send_message(
                "日付を選択してください",
                view=calendar_view
            )
        else:
            if action == "list":
                # アクティブなスケジュールを取得
                schedules = await self.repository.get_active_schedules()
                
                if not schedules:
                    await interaction.response.send_message(
                        "アクティブなスケジュールはありません。",
                        ephemeral=True
                    )
                    return
                
                # Embedを作成
                embed = discord.Embed(
                    title="アクティブなスケジュール一覧",
                    color=discord.Color.blue()
                )
                
                for schedule in schedules:
                    # 作成者情報を取得
                    creator = await self.bot.fetch_user(schedule.creator_id)
                    creator_name = creator.display_name if creator else "Unknown"
                    
                    # 候補日時と投票状況を文字列化
                    date_votes = []
                    for date in schedule.dates:
                        vote_counts = schedule.get_vote_count(date.date)
                        date_str = date.date.strftime('%Y-%m-%d %H:%M')
                        vote_str = f"(⭕:{vote_counts[VoteStatus.CIRCLE]} 🔺:{vote_counts[VoteStatus.TRIANGLE]} ❌:{vote_counts[VoteStatus.CROSS]})"
                        date_votes.append(f"・{date_str} {vote_str}")
                    
                    # スケジュール情報をフィールドとして追加
                    field_value = f"**説明**: {schedule.description or '説明なし'}\n" + \
                                f"**作成者**: {creator_name}\n\n" + \
                                "**候補日時**:\n" + "\n".join(date_votes)
                    
                    embed.add_field(
                        name=f"📅 {schedule.title}",
                        value=field_value,
                        inline=False
                    )
                
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message(
                    f"Action '{action}' は現在実装されていません。",
                    ephemeral=True
                )

async def setup(bot: commands.Bot):
    """Set up the Schedule cog."""
    await bot.add_cog(ScheduleCog(bot))
