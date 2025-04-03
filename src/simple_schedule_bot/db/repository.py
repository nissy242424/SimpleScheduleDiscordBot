from datetime import datetime
from typing import List, Optional, Dict, Tuple

from ..models.schedule import Schedule, ScheduleDate, Vote, ScheduleStatus, VoteStatus
from .database import DatabaseManager

class ScheduleRepository:
    def __init__(self, db: DatabaseManager):
        self.db = db

    async def create_schedule(self, schedule: Schedule) -> str:
        """スケジュールを作成"""
        async with self.db.transaction() as cur:
            # スケジュールの保存
            await cur.execute(
                """
                INSERT INTO schedules (
                    id, title, description, creator_id, channel_id,
                    status, created_at, confirmed_date, reminder_sent
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    schedule.id, schedule.title, schedule.description,
                    schedule.creator_id, schedule.channel_id, schedule.status.value,
                    schedule.created_at, schedule.confirmed_date,
                    schedule.reminder_sent
                )
            )

            # 候補日時の保存
            for date in schedule.dates:
                await cur.execute(
                    "INSERT INTO schedule_dates (schedule_id, date) VALUES (?, ?)",
                    (schedule.id, date.date)
                )

        return schedule.id

    async def get_schedule(self, schedule_id: str) -> Optional[Schedule]:
        """スケジュールを取得"""
        async with self.db.connect() as conn:
            # スケジュール本体の取得
            cursor = await conn.execute(
                "SELECT * FROM schedules WHERE id = ?",
                (schedule_id,)
            )
            schedule_row = await cursor.fetchone()
            
            if not schedule_row:
                return None

            # 候補日時の取得
            cursor = await conn.execute(
                "SELECT * FROM schedule_dates WHERE schedule_id = ? ORDER BY date",
                (schedule_id,)
            )
            date_rows = await cursor.fetchall()

            # 投票の取得
            cursor = await conn.execute(
                "SELECT * FROM votes WHERE schedule_id = ?",
                (schedule_id,)
            )
            vote_rows = await cursor.fetchall()

            # Schedule オブジェクトの構築
            dates = [
                ScheduleDate(
                    id=row['id'],
                    schedule_id=row['schedule_id'],
                    date=datetime.fromisoformat(row['date'])
                )
                for row in date_rows
            ]

            votes: Dict[int, Dict[datetime, Vote]] = {}
            for row in vote_rows:
                user_id = row['user_id']
                date = datetime.fromisoformat(row['date'])
                
                if user_id not in votes:
                    votes[user_id] = {}
                
                votes[user_id][date] = Vote(
                    id=row['id'],
                    schedule_id=row['schedule_id'],
                    user_id=user_id,
                    date=date,
                    vote_status=VoteStatus(row['vote_status']),
                    created_at=datetime.fromisoformat(row['created_at'])
                )

            return Schedule(
                id=schedule_row['id'],
                title=schedule_row['title'],
                description=schedule_row['description'],
                creator_id=schedule_row['creator_id'],
                channel_id=schedule_row['channel_id'],
                status=ScheduleStatus(schedule_row['status']),
                created_at=datetime.fromisoformat(schedule_row['created_at']),
                confirmed_date=datetime.fromisoformat(schedule_row['confirmed_date']) if schedule_row['confirmed_date'] else None,
                reminder_sent=bool(schedule_row['reminder_sent']),
                dates=dates,
                votes=votes
            )

    async def update_vote(self, vote: Vote) -> None:
        """投票を更新"""
        async with self.db.transaction() as cur:
            await cur.execute(
                """
                INSERT INTO votes (
                    schedule_id, user_id, date, vote_status, created_at
                ) VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(schedule_id, user_id, date)
                DO UPDATE SET vote_status = ?, created_at = ?
                """,
                (
                    vote.schedule_id, vote.user_id, vote.date,
                    vote.vote_status.value, vote.created_at,
                    vote.vote_status.value, vote.created_at
                )
            )

    async def confirm_schedule(self, schedule_id: str, confirmed_date: datetime) -> None:
        """スケジュールを確定"""
        async with self.db.transaction() as cur:
            await cur.execute(
                """
                UPDATE schedules
                SET status = ?, confirmed_date = ?
                WHERE id = ?
                """,
                (ScheduleStatus.CONFIRMED.value, confirmed_date, schedule_id)
            )

    async def cancel_schedule(self, schedule_id: str) -> None:
        """スケジュールをキャンセル"""
        async with self.db.transaction() as cur:
            await cur.execute(
                "UPDATE schedules SET status = ? WHERE id = ?",
                (ScheduleStatus.CANCELLED.value, schedule_id)
            )

    async def get_active_schedules(self) -> List[Schedule]:
        """アクティブなスケジュールを全て取得"""
        async with self.db.connect() as conn:
            cursor = await conn.execute(
                "SELECT id FROM schedules WHERE status = ?",
                (ScheduleStatus.ACTIVE.value,)
            )
            rows = await cursor.fetchall()

            schedules = []
            for row in rows:
                schedule = await self.get_schedule(row['id'])
                if schedule:
                    schedules.append(schedule)

            return schedules

    async def update_reminder_sent(self, schedule_id: str, sent: bool = True) -> None:
        """リマインダー送信状態を更新"""
        async with self.db.transaction() as cur:
            await cur.execute(
                "UPDATE schedules SET reminder_sent = ? WHERE id = ?",
                (sent, schedule_id)
            )
