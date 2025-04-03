import aiosqlite
import asyncio
from pathlib import Path
from typing import Optional
from contextlib import asynccontextmanager

class DatabaseManager:
    _instance: Optional['DatabaseManager'] = None
    _lock = asyncio.Lock()

    def __init__(self, db_path: str = "data/schedule.db"):
        self.db_path = db_path
        self._connection: Optional[aiosqlite.Connection] = None
        
    @classmethod
    async def get_instance(cls, db_path: str = "data/schedule.db") -> 'DatabaseManager':
        if not cls._instance:
            async with cls._lock:
                if not cls._instance:
                    cls._instance = cls(db_path)
                    await cls._instance.init()
        return cls._instance

    async def init(self):
        """データベースの初期化とテーブル作成を行う"""
        # データベースディレクトリの作成
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)

        async with self.connect() as conn:
            await conn.executescript('''
                CREATE TABLE IF NOT EXISTS schedules (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    creator_id INTEGER NOT NULL,
                    channel_id INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    confirmed_date TIMESTAMP,
                    reminder_sent BOOLEAN DEFAULT FALSE
                );

                CREATE TABLE IF NOT EXISTS schedule_dates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    schedule_id TEXT NOT NULL,
                    date TIMESTAMP NOT NULL,
                    FOREIGN KEY (schedule_id) REFERENCES schedules(id),
                    UNIQUE(schedule_id, date)
                );

                CREATE TABLE IF NOT EXISTS votes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    schedule_id TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    date TIMESTAMP NOT NULL,
                    vote_status TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    FOREIGN KEY (schedule_id) REFERENCES schedules(id),
                    UNIQUE(schedule_id, user_id, date)
                );

                CREATE INDEX IF NOT EXISTS idx_schedule_dates_schedule_id 
                ON schedule_dates(schedule_id);
                
                CREATE INDEX IF NOT EXISTS idx_votes_schedule_id 
                ON votes(schedule_id);
                
                CREATE INDEX IF NOT EXISTS idx_votes_user_id 
                ON votes(user_id);
                
                CREATE INDEX IF NOT EXISTS idx_schedules_status 
                ON schedules(status);
            ''')

    @asynccontextmanager
    async def connect(self):
        """データベース接続のコンテキストマネージャー"""
        if self._connection is None:
            self._connection = await aiosqlite.connect(self.db_path)
            self._connection.row_factory = aiosqlite.Row
        
        try:
            yield self._connection
        except Exception as e:
            await self._connection.rollback()
            raise e

    @asynccontextmanager
    async def transaction(self):
        """トランザクション管理のコンテキストマネージャー"""
        async with self.connect() as conn:
            async with conn.cursor() as cur:
                await conn.execute("BEGIN")
                try:
                    yield cur
                    await conn.commit()
                except Exception as e:
                    await conn.rollback()
                    raise e

    async def close(self):
        """データベース接続のクローズ"""
        if self._connection is not None:
            await self._connection.close()
            self._connection = None
