# Botの初期化とIntents

## Intentsシステム

### Intentsとは
Intentsは、BotがDiscordから受け取るイベントを制御するシステムです。必要なイベントのみを受信することで、パフォーマンスを最適化し、効率的なBot運用が可能になります。

### Intentsの種類

#### 標準Intents（デフォルトで有効）
```python
intents = discord.Intents.default()
```

含まれる主なIntents:
- Guilds
- Guild Messages
- Direct Messages
- Guild Message Reactions
- Direct Message Reactions
- Guild Voice States

#### 特権Intents（明示的な有効化が必要）
- `members`: サーバーメンバー関連のイベント
- `presences`: ユーザーステータス関連のイベント
- `message_content`: メッセージ内容の取得

```python
# 特権Intentsの有効化例
intents = discord.Intents.default()
intents.members = True
intents.presences = True
intents.message_content = True
```

## Botの初期化

### 基本的な初期化
```python
import discord
from discord.ext import commands

# Intentの設定
intents = discord.Intents.default()
intents.message_content = True

# Botのインスタンス化
bot = commands.Bot(
    command_prefix='!',     # コマンドプレフィックス
    intents=intents,       # Intents設定
    description='Bot説明'   # Bot説明（ヘルプコマンドで表示）
)
```

### 高度な初期化オプション
```python
bot = commands.Bot(
    command_prefix=['!', '?'],  # 複数のプレフィックス
    case_insensitive=True,      # 大文字小文字を区別しない
    strip_after_prefix=True,    # プレフィックス後の空白を削除
    help_command=None,          # デフォルトのヘルプコマンドを無効化
    intents=intents,
    activity=discord.Game(name="!help") # 「〜をプレイ中」の表示
)
```

## イベントの設定

### 基本的なイベント
```python
@bot.event
async def on_ready():
    print(f'{bot.user} としてログインしました')
    print(f'Bot ID: {bot.user.id}')

@bot.event
async def on_connect():
    print('Discord WebSocketに接続しました')

@bot.event
async def on_disconnect():
    print('Discord WebSocketから切断されました')
```

### エラーハンドリング
```python
@bot.event
async def on_error(event, *args, **kwargs):
    print(f'エラーが発生しました: {event}')
    import traceback
    traceback.print_exc()

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('コマンドが見つかりません')
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send('権限が不足しています')
    else:
        await ctx.send(f'エラーが発生しました: {error}')
```

## アプリケーションコマンド（スラッシュコマンド）

### グローバルコマンドの登録
```python
@bot.tree.command()
async def hello(interaction: discord.Interaction):
    """あいさつを返します"""
    await interaction.response.send_message(f'こんにちは、{interaction.user.name}さん！')
```

### サーバー固有コマンドの登録
```python
@bot.tree.command()
@app_commands.guilds(GUILD_ID)  # 特定のサーバーにのみ登録
async def server_hello(interaction: discord.Interaction):
    """サーバー専用のあいさつを返します"""
    await interaction.response.send_message(
        f'こんにちは、{interaction.guild.name}の{interaction.user.name}さん！'
    )
```

## コグの使用

### コグの基本構造
```python
class BasicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('BasicCogが読み込まれました')

    @commands.command()
    async def hello(self, ctx):
        await ctx.send('こんにちは！')

async def setup(bot):
    await bot.add_cog(BasicCog(bot))
```

### コグの読み込み
```python
async def load_extensions():
    await bot.load_extension('cogs.basic')
    # または複数のコグを一度に読み込む
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')

# Botの起動時にコグを読み込む
async def main():
    await load_extensions()
    await bot.start(TOKEN)
```

## ベストプラクティス

### 1. Intentsの最適化
- 必要なIntentsのみを有効化
- 特権Intentsの使用は最小限に

### 2. エラーハンドリング
- グローバルエラーハンドラの実装
- ユーザーフレンドリーなエラーメッセージ

### 3. コードの構造化
- 機能ごとにコグを分割
- 設定の外部ファイル化
- 環境変数の使用

### 4. セキュリティ
- トークンの安全な管理
- 権限の適切な設定
- 入力値の検証

## 次のステップ
- [イベントシステム](02_events.md)でイベントの詳細を学ぶ
- [コマンドシステム](03_commands.md)でコマンドの実装方法を学ぶ
