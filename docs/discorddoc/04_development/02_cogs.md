# Cogsによるモジュール化

## Cogsの基本

### Cogsとは
Cogsは、Botの機能をモジュール化するための仕組みです。関連する機能をまとめて管理し、コードの整理と再利用を容易にします。

### 基本的なCog構造
```python
from discord.ext import commands

class BasicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.__class__.__name__}が読み込まれました')
        
    @commands.command()
    async def hello(self, ctx):
        """基本的なコマンド"""
        await ctx.send('Hello!')

async def setup(bot):
    await bot.add_cog(BasicCog(bot))
```

## Cogの機能

### イベントリスナー
```python
class EventsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
            
        if 'hello' in message.content.lower():
            await message.channel.send('こんにちは！')
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = member.guild.system_channel
        if channel is not None:
            await channel.send(f'{member.mention}さん、ようこそ！')
```

### コマンドグループ
```python
class MathCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.group()
    async def math(self, ctx):
        """数学関連コマンドグループ"""
        if ctx.invoked_subcommand is None:
            await ctx.send('サブコマンドを指定してください')
    
    @math.command()
    async def add(self, ctx, a: int, b: int):
        """足し算"""
        await ctx.send(f'{a} + {b} = {a + b}')
    
    @math.command()
    async def multiply(self, ctx, a: int, b: int):
        """掛け算"""
        await ctx.send(f'{a} × {b} = {a * b}')
```

### エラーハンドリング
```python
class ErrorHandlerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send('権限が不足しています')
        elif isinstance(error, commands.CommandNotFound):
            await ctx.send('コマンドが見つかりません')
        else:
            await ctx.send(f'エラーが発生しました: {str(error)}')
```

## 高度な使用方法

### 状態管理
```python
class StateCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.counter = 0
        
    @commands.command()
    async def count(self, ctx):
        """カウンターをインクリメント"""
        self.counter += 1
        await ctx.send(f'現在のカウント: {self.counter}')
        
    def cog_unload(self):
        """Cogがアンロードされる時の処理"""
        print(f'最終カウント: {self.counter}')
```

### データベース操作
```python
class DatabaseCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()  # データベース接続
        
    @commands.command()
    async def save(self, ctx, key: str, *, value: str):
        """データを保存"""
        try:
            self.db.set(key, value)
            await ctx.send(f'{key}を保存しました')
        except Exception as e:
            await ctx.send(f'エラー: {str(e)}')
            
    def cog_unload(self):
        """データベース接続のクリーンアップ"""
        self.db.close()
```

### スラッシュコマンド
```python
class SlashCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.hybrid_command()
    @app_commands.describe(
        user="ターゲットユーザー",
        message="送信するメッセージ"
    )
    async def send(self, ctx, user: discord.Member, *, message: str):
        """ユーザーにメッセージを送信"""
        try:
            await user.send(message)
            await ctx.send(f'{user.name}にメッセージを送信しました', ephemeral=True)
        except discord.Forbidden:
            await ctx.send('メッセージを送信できませんでした')
```

## Cogの管理

### コグのロード/アンロード
```python
class ManagementCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    @commands.is_owner()
    async def load(self, ctx, extension):
        """Cogをロード"""
        try:
            await self.bot.load_extension(f'cogs.{extension}')
            await ctx.send(f'{extension}をロードしました')
        except Exception as e:
            await ctx.send(f'エラー: {str(e)}')
    
    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx, extension):
        """Cogをアンロード"""
        try:
            await self.bot.unload_extension(f'cogs.{extension}')
            await ctx.send(f'{extension}をアンロードしました')
        except Exception as e:
            await ctx.send(f'エラー: {str(e)}')
    
    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, extension):
        """Cogをリロード"""
        try:
            await self.bot.reload_extension(f'cogs.{extension}')
            await ctx.send(f'{extension}をリロードしました')
        except Exception as e:
            await ctx.send(f'エラー: {str(e)}')
```

## ベストプラクティス

### 1. 構造化
- 関連する機能をまとめる
- 適切な粒度でCogを分割
- 明確な責任範囲の設定

### 2. エラー処理
- Cog固有のエラーハンドリング
- グローバルエラーハンドラとの連携
- 適切なエラーメッセージ

### 3. リソース管理
- 適切な初期化と後処理
- メモリリークの防止
- 接続のクリーンアップ

### 4. 依存関係
- 循環参照の回避
- 適切なインジェクション
- モジュール間の疎結合

## 次のステップ
- [エラーハンドリングとログ](03_error_handling.md)でエラー処理の詳細を学ぶ
