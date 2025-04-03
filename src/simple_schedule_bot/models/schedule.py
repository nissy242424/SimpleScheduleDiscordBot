from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional, Dict
import uuid

class VoteStatus(str, Enum):
    CIRCLE = "⭕"
    TRIANGLE = "🔺"
    CROSS = "❌"

class ScheduleStatus(str, Enum):
    ACTIVE = "active"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"

@dataclass
class Vote:
    id: Optional[int]
    schedule_id: str
    user_id: int
    date: datetime
    vote_status: VoteStatus
    created_at: datetime

    @classmethod
    def create(cls, schedule_id: str, user_id: int, date: datetime, vote_status: VoteStatus) -> 'Vote':
        return cls(
            id=None,
            schedule_id=schedule_id,
            user_id=user_id,
            date=date,
            vote_status=vote_status,
            created_at=datetime.now(timezone.utc)
        )

@dataclass
class ScheduleDate:
    id: Optional[int]
    schedule_id: str
    date: datetime

    @classmethod
    def create(cls, schedule_id: str, date: datetime) -> 'ScheduleDate':
        return cls(
            id=None,
            schedule_id=schedule_id,
            date=date
        )

@dataclass
class Schedule:
    id: str
    title: str
    description: Optional[str]
    creator_id: int
    channel_id: int
    status: ScheduleStatus
    created_at: datetime
    confirmed_date: Optional[datetime]
    reminder_sent: bool
    dates: List[ScheduleDate]
    votes: Dict[int, Dict[datetime, Vote]]

    @classmethod
    def create(cls, title: str, description: Optional[str], creator_id: int, channel_id: int, dates: List[datetime]) -> 'Schedule':
        schedule_id = str(uuid.uuid4())
        return cls(
            id=schedule_id,
            title=title,
            description=description,
            creator_id=creator_id,
            channel_id=channel_id,
            status=ScheduleStatus.ACTIVE,
            created_at=datetime.now(timezone.utc),
            confirmed_date=None,
            reminder_sent=False,
            dates=[ScheduleDate.create(schedule_id, date) for date in dates],
            votes={}
        )

    def add_vote(self, user_id: int, date: datetime, status: VoteStatus) -> None:
        """ユーザーの投票を追加または更新"""
        if user_id not in self.votes:
            self.votes[user_id] = {}
        
        self.votes[user_id][date] = Vote.create(
            schedule_id=self.id,
            user_id=user_id,
            date=date,
            vote_status=status
        )

    def get_vote_count(self, date: datetime) -> Dict[VoteStatus, int]:
        """指定された日付の投票集計"""
        counts = {status: 0 for status in VoteStatus}
        for user_votes in self.votes.values():
            if date in user_votes:
                counts[user_votes[date].vote_status] += 1
        return counts

    def confirm_date(self, date: datetime) -> None:
        """日程を確定する"""
        self.status = ScheduleStatus.CONFIRMED
        self.confirmed_date = date
