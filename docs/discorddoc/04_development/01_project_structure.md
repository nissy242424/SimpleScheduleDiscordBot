# プロジェクト構造

## 基本的なプロジェクト構造

### 推奨されるディレクトリ構造
```
my_bot/
├── .env                    # 環境変数
├── .gitignore             # Gitの除外ファイル設定
├── README.md              # プロジェクトの説明
├── requirements.txt       # 依存パッケージリスト
├── main.py               # メインのBotファイル
├── config.py             # 設定ファイル
├── cogs/                 # コグディレクトリ
│   ├── __init__.py
│   ├── admin.py         # 管理者コマンド
│   ├── general.py       # 一般コマンド
│   └── events.py        # イベントハンドラ
├── utils/               # ユーティリティ関数
│   ├── __init__.py
│   ├── database.py     # データベース操作
│   └── helpers.py      # ヘルパー関数
└── data/               # データ保存ディレクトリ
    ├── config.json     # ボット設定
    └── database.db     # SQLiteデータベース
```

## 主要なファイルの内容

### main.py
```python
import os
from discord.ext import commands
import discord
from config import TOKEN

# Bot初期化
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# コグのロード
async def load_extensions():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')

# Bot起動時の処理
@bot.event
async def on_ready():
    print(f'{bot.user} としてログインしました')
    await bot.tree.sync()  # スラッシュコマンドの同期

# メイン処理
async def main():
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)

# Botの実行
if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
```

### config.py
```python
import os
from dotenv import load_dotenv

# 環境変数のロード
load_dotenv()

# 設定値
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = os.getenv('GUILD_ID')
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///data/database.db')

# Bot設定
PREFIX = '!'
OWNER_IDS = [
    int(id_) for id_ in os.getenv('OWNER_IDS', '').split(',')
    if id_
]

# その他の設定
COOLDOWN_RATE = 3
COOLDOWN_PER = 10
```

### cogs/admin.py
```python
from discord.ext import commands
import discord

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def clear(self, ctx, amount: int = 5):
        """指定した数のメッセージを削除"""
        await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f'{amount}件のメッセージを削除しました', delete_after=5)
    
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        """メンバーをキック"""
        await member.kick(reason=reason)
        await ctx.send(f'{member.name}をキックしました')

async def setup(bot):
    await bot.add_cog(Admin(bot))
```

### utils/database.py
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL

# データベースエンジンの作成
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def get_session():
    """データベースセッションを取得"""
    return Session()

class Database:
    def __init__(self):
        self.session = get_session()
    
    def close(self):
        """セッションを閉じる"""
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
```

## モジュール分割の方針

### 1. コグによる機能分割
- 関連する機能をコグとしてグループ化
- 各コグは単一の責任を持つ
- コグ間の依存関係を最小限に

### 2. ユーティリティ関数
- 共通で使用する関数をutils/に配置
- データベース操作をデータアクセス層として分離
- ヘルパー関数の適切な分類

### 3. 設定管理
- 環境変数による設定
- JSONファイルによる動的設定
- 定数の集中管理

## コード品質の維持

### 1. コーディング規約
- PEP 8に準拠
- 一貫性のある命名規則
- 適切なコメントとドキュメント

### 2. エラー処理
- 例外の適切な捕捉
- ログ記録の実装
- エラーメッセージの標準化

### 3. テスト
- ユニットテストの作成
- モックの使用
- CI/CDの導入

## スケーラビリティ

### 1. データベース設計
- 適切なテーブル設計
- インデックスの最適化
- キャッシュの活用

### 2. 非同期処理
- 重い処理の非同期化
- バックグラウンドタスク
- レート制限の実装

### 3. モジュール性
- プラグイン方式の採用
- 設定の外部化
- 依存関係の管理

## メンテナンス

### 1. ログ記録
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('discord_bot')
```

### 2. バックアップ
- データベースのバックアップ
- 設定ファイルの管理
- ログのローテーション

### 3. 監視
- エラー監視
- パフォーマンス監視
- 使用状況の追跡

## 次のステップ
- [Cogsによるモジュール化](02_cogs.md)でコグの詳細な使用方法を学ぶ
