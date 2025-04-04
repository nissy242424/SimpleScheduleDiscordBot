import pytest
from datetime import datetime, timedelta, timezone
from simple_schedule_bot.models.schedule import (
    Schedule,
    ScheduleDate,
    Vote,
    VoteStatus,
    ScheduleStatus
)

class TestSchedule:
    @pytest.fixture
    def sample_dates(self):
        now = datetime.now(timezone.utc)
        return [
            now + timedelta(days=1),
            now + timedelta(days=2),
            now + timedelta(days=3)
        ]

    def test_schedule_creation(self, sample_dates):
        """基本的なスケジュール作成のテスト"""
        schedule = Schedule.create(
            title="テスト予定",
            description="テストの説明",
            creator_id=123456789,
            channel_id=987654321,
            dates=sample_dates
        )

        assert schedule.title == "テスト予定"
        assert schedule.description == "テストの説明"
        assert schedule.creator_id == 123456789
        assert schedule.channel_id == 987654321
        assert schedule.status == ScheduleStatus.ACTIVE
        assert not schedule.reminder_sent
        assert len(schedule.dates) == 3
        assert isinstance(schedule.dates[0], ScheduleDate)
        assert schedule.votes == {}

    def test_add_vote(self, sample_dates):
        """投票追加のテスト"""
        schedule = Schedule.create(
            title="テスト予定",
            description="テストの説明",
            creator_id=123456789,
            channel_id=987654321,
            dates=sample_dates
        )

        user_id = 111222333
        schedule.add_vote(user_id, sample_dates[0], VoteStatus.CIRCLE)

        assert user_id in schedule.votes
        assert sample_dates[0] in schedule.votes[user_id]
        assert schedule.votes[user_id][sample_dates[0]].vote_status == VoteStatus.CIRCLE

        # 同じユーザーが別の投票を上書き
        schedule.add_vote(user_id, sample_dates[0], VoteStatus.CROSS)
        assert schedule.votes[user_id][sample_dates[0]].vote_status == VoteStatus.CROSS

    def test_get_vote_count(self, sample_dates):
        """投票集計のテスト"""
        schedule = Schedule.create(
            title="テスト予定",
            description="テストの説明",
            creator_id=123456789,
            channel_id=987654321,
            dates=sample_dates
        )

        # 複数ユーザーの投票を追加
        user_votes = [
            (111, VoteStatus.CIRCLE),
            (222, VoteStatus.CIRCLE),
            (333, VoteStatus.TRIANGLE),
            (444, VoteStatus.CROSS)
        ]

        for user_id, status in user_votes:
            schedule.add_vote(user_id, sample_dates[0], status)

        counts = schedule.get_vote_count(sample_dates[0])
        assert counts[VoteStatus.CIRCLE] == 2
        assert counts[VoteStatus.TRIANGLE] == 1
        assert counts[VoteStatus.CROSS] == 1

    def test_confirm_date(self, sample_dates):
        """スケジュール確定のテスト"""
        schedule = Schedule.create(
            title="テスト予定",
            description="テストの説明",
            creator_id=123456789,
            channel_id=987654321,
            dates=sample_dates
        )

        confirm_date = sample_dates[0]
        schedule.confirm_date(confirm_date)

        assert schedule.status == ScheduleStatus.CONFIRMED
        assert schedule.confirmed_date == confirm_date

class TestVoteStatus:
    def test_vote_status_values(self):
        """投票状態の値テスト"""
        assert VoteStatus.CIRCLE == "⭕"
        assert VoteStatus.TRIANGLE == "🔺"
        assert VoteStatus.CROSS == "❌"

    def test_vote_status_comparison(self):
        """投票状態の比較テスト"""
        status = VoteStatus.CIRCLE
        assert status == VoteStatus.CIRCLE
        assert status != VoteStatus.TRIANGLE
        assert status != VoteStatus.CROSS
        assert status in VoteStatus

class TestScheduleStatus:
    def test_schedule_status_values(self):
        """スケジュール状態の値テスト"""
        assert ScheduleStatus.ACTIVE == "active"
        assert ScheduleStatus.CONFIRMED == "confirmed"
        assert ScheduleStatus.CANCELLED == "cancelled"

    def test_schedule_status_transitions(self):
        """スケジュール状態遷移のテスト"""
        schedule = Schedule.create(
            title="テスト予定",
            description="テストの説明",
            creator_id=123456789,
            channel_id=987654321,
            dates=[datetime.now(timezone.utc)]
        )

        assert schedule.status == ScheduleStatus.ACTIVE
        schedule.confirm_date(datetime.now(timezone.utc))
        assert schedule.status == ScheduleStatus.CONFIRMED
