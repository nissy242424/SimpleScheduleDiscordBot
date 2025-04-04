"""
Calendar view implementation for schedule creation.
"""
from datetime import datetime, timezone
import calendar
from typing import List, Optional

import discord
from discord.ui import Button, Select, View

from ..db.repository import ScheduleRepository
from .modals import ScheduleCreateModal


class DateButton(Button):
    """日付を表すボタン"""
    def __init__(self, date: datetime, parent_view: 'CalendarView', row: int):
        """
        Args:
            date: ボタンが表す日付
            parent_view: 親のCalendarView
            row: ボタンの行位置
        """
        self.date = date
        self.parent_view = parent_view
        
        # 過去の日付かどうか
        is_past = date.date() < datetime.now(timezone.utc).date()
        # 選択済みかどうか
        is_selected = date in [d.replace(hour=0, minute=0, second=0, microsecond=0) 
                             for d in parent_view.selected_dates]
        
        # スタイル設定
        style = discord.ButtonStyle.success if is_selected else discord.ButtonStyle.secondary
        
        # 曜日に応じた色設定（土曜日は青、日曜日は赤）
        label = str(date.day)
        if date.weekday() == 5:  # 土曜日
            label = f"💙{date.day}"
        elif date.weekday() == 6:  # 日曜日
            label = f"❤️{date.day}"
        
        super().__init__(
            label=label,
            style=style,
            disabled=is_past,
            row=row
        )

    async def callback(self, interaction: discord.Interaction):
        """ボタンクリック時のコールバック"""
        await self.parent_view.handle_date_select(interaction, self.date)


class MonthSelect(Select):
    """月選択セレクトメニュー"""
    def __init__(self, parent_view: 'CalendarView'):
        """
        Args:
            parent_view: 親のCalendarView
        """
        self.parent_view = parent_view
        
        # 現在の月から3ヶ月分のオプションを生成
        current = datetime.now(timezone.utc)
        options = []
        
        for i in range(3):
            target_date = datetime(
                year=current.year + ((current.month + i - 1) // 12),
                month=((current.month + i - 1) % 12) + 1,
                day=1,
                tzinfo=timezone.utc
            )
            options.append(
                discord.SelectOption(
                    label=f"{target_date.year}年{target_date.month}月",
                    value=f"{target_date.year}-{target_date.month}",
                    default=(i == 0)
                )
            )
        
        super().__init__(
            placeholder="月を選択",
            options=options,
            row=0
        )

    async def callback(self, interaction: discord.Interaction):
        """月選択時のコールバック"""
        year, month = map(int, self.values[0].split('-'))
        self.parent_view.current_year = year
        self.parent_view.current_month = month
        await self.parent_view.update_calendar(interaction)


class CalendarView(View):
    """カレンダービュー"""
    def __init__(self):
        super().__init__()
        
        # 現在の年月を設定
        now = datetime.now(timezone.utc)
        self.current_year = now.year
        self.current_month = now.month
        
        # 選択された日付のリスト
        self.selected_dates: List[datetime] = []
        
        # 月選択メニューを追加
        self.add_item(MonthSelect(self))
        
        # 確定ボタンを追加
        self.add_item(
            Button(
                label="確定",
                style=discord.ButtonStyle.primary,
                custom_id="confirm",
                row=4
            )
        )
        
        # カレンダーを構築
        self.build_calendar()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """インタラクションのチェック"""
        if interaction.data.get("custom_id") == "confirm":
            # 日付が選択されているかチェック
            if not self.selected_dates:
                await interaction.response.send_message(
                    "少なくとも1つの日付を選択してください。",
                    ephemeral=True
                )
                return False
            
            # モーダルを表示
            modal = ScheduleCreateModal(
                ScheduleRepository(interaction.client.db),
                self.selected_dates
            )
            await interaction.response.send_modal(modal)
            return True
        
        return True

    def build_calendar(self):
        """カレンダーのボタングリッドを構築"""
        # 曜日ヘッダー（日〜土）
        weekdays = ["日", "月", "火", "水", "木", "金", "土"]
        
        # カレンダーの日付を取得
        cal = calendar.monthcalendar(self.current_year, self.current_month)
        
        # ボタンを配置（最大6行）
        current_row = 1  # 0行目は月選択用
        
        for week in cal:
            for day in week:
                if day != 0:
                    date = datetime(
                        year=self.current_year,
                        month=self.current_month,
                        day=day,
                        tzinfo=timezone.utc
                    )
                    self.add_item(DateButton(date, self, current_row))
            current_row += 1

    async def handle_date_select(self, interaction: discord.Interaction, date: datetime):
        """日付選択時の処理
        
        Args:
            interaction: インタラクション
            date: 選択された日付
        """
        # 00:00に設定
        date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # 既に選択されていれば解除
        if date in self.selected_dates:
            self.selected_dates.remove(date)
        else:
            # 最大選択数チェック
            if len(self.selected_dates) >= 10:
                await interaction.response.send_message(
                    "最大10件まで選択可能です",
                    ephemeral=True
                )
                return
            
            self.selected_dates.append(date)
        
        # カレンダーを更新
        await self.update_calendar(interaction)

    async def update_calendar(self, interaction: discord.Interaction):
        """カレンダーの表示を更新"""
        # 既存のボタンを削除
        self.clear_items()
        
        # 月選択メニューを再追加
        self.add_item(MonthSelect(self))
        
        # カレンダーを再構築
        self.build_calendar()
        
        # 選択済み日付リストを構築
        selected_dates_str = "\n".join(
            [f"・{date.strftime('%Y-%m-%d')}" for date in sorted(self.selected_dates)]
        )
        
        if not selected_dates_str:
            selected_dates_str = "選択された日付はありません"
        
        # メッセージを更新
        await interaction.response.edit_message(
            content=f"**選択された日付:**\n{selected_dates_str}",
            view=self
        )
