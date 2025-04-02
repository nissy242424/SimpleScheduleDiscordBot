# コマンドシステム

## コマンドの基本

### プレフィックスコマンド
従来のプレフィックスを使用したコマンドシステムです。

```python
@bot.command()
async def hello(ctx):
    """あいさつを返すコマンド"""
    await ctx.send(f'こんにちは、{ctx.author.name}さん！')

@bot.command()
async def ping(ctx):
    """Botの応答速度を確認するコマンド"""
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')
```

### スラッシュコマンド
Discordの新しいインタラクションシステムを使用したコマンドです。

```python
@bot.tree.command()
@app_commands.describe(user="メンションするユーザー")
async def greet(interaction: discord.Interaction, user: discord.Member):
    """指定したユーザーにあいさつします"""
    await interaction.response.send_message(f'こんにちは、{user.mention}さん！')
```

## コマンドの高度な使用法

### 引数の処理
```python
@bot.command()
async def echo(ctx, *, message: str):
    """メッセージを繰り返すコマンド"""
    await ctx.send(message)

@bot.command()
async def add(ctx, a: int, b: int):
    """2つの数値を足し算するコマンド"""
    result = a + b
    await ctx.send(f'{a} + {b} = {result}')
```

### コマンドグループ
```python
@bot.group()
async def math(ctx):
    """数学関連コマンドグループ"""
    if ctx.invoked_subcommand is None:
        await ctx.send('サブコマンドを指定してください')

@math.command()
async def add(ctx, a: int, b: int):
    """足し算"""
    await ctx.send(f'{a} + {b} = {a + b}')

@math.command()
async def multiply(ctx, a: int, b: int):
    """掛け算"""
    await ctx.send(f'{a} × {b} = {a * b}')
```

### エラーハンドリング
```python
@bot.command()
async def divide(ctx, a: int, b: int):
    """割り算を行うコマンド"""
    try:
        result = a / b
        await ctx.send(f'{a} ÷ {b} = {result}')
    except ZeroDivisionError:
        await ctx.send('0で割ることはできません')
    except ValueError:
        await ctx.send('有効な数値を入力してください')

@divide.error
async def divide_error(ctx, error):
    """divide コマンドのエラーハンドラ"""
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('2つの数値を入力してください')
    elif isinstance(error, commands.BadArgument):
        await ctx.send('有効な数値を入力してください')
```

## 高度な機能

### クールダウン
```python
@bot.command()
@commands.cooldown(1, 60, commands.BucketType.user)
async def daily(ctx):
    """1日1回実行できるコマンド"""
    await ctx.send('デイリーボーナスを受け取りました！')

@daily.error
async def daily_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        remaining = round(error.retry_after)
        await ctx.send(f'このコマンドは{remaining}秒後に使用できます')
```

### 権限チェック
```python
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    """メンバーをキックするコマンド"""
    await member.kick(reason=reason)
    await ctx.send(f'{member.name}をキックしました')

@bot.command()
@commands.has_role('Admin')
async def admin_only(ctx):
    """管理者専用コマンド"""
    await ctx.send('このコマンドは管理者のみ使用できます')
```

### カスタムチェック
```python
def is_in_channel(channel_id):
    async def predicate(ctx):
        return ctx.channel.id == channel_id
    return commands.check(predicate)

@bot.command()
@is_in_channel(123456789)
async def channel_specific(ctx):
    """特定のチャンネルでのみ使用可能なコマンド"""
    await ctx.send('このコマンドは指定されたチャンネルでのみ使用できます')
```

## スラッシュコマンドの応用

### オプション付きコマンド
```python
@bot.tree.command()
@app_commands.describe(
    text="変換するテキスト",
    style="変換スタイル"
)
@app_commands.choices(style=[
    app_commands.Choice(name="大文字", value="upper"),
    app_commands.Choice(name="小文字", value="lower")
])
async def convert(
    interaction: discord.Interaction,
    text: str,
    style: str
):
    """テキストを変換します"""
    result = text.upper() if style == "upper" else text.lower()
    await interaction.response.send_message(f'変換結果: {result}')
```

### コマンドグループ
```python
@app_commands.guild_only()
class AdminCommands(app_commands.Group):
    """管理者用コマンドグループ"""
    
    @app_commands.command()
    @app_commands.describe(
        member="対象ユーザー",
        reason="理由"
    )
    async def warn(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str
    ):
        """ユーザーに警告を送信します"""
        await interaction.response.send_message(
            f'{member.mention}に警告を送信しました\n理由: {reason}'
        )

# グループの登録
bot.tree.add_command(AdminCommands(name="admin"))
```

## ベストプラクティス

### 1. コマンド設計
- 直感的なコマンド名
- 適切なヘルプメッセージ
- 明確な引数の説明

### 2. エラー処理
- ユーザーフレンドリーなエラーメッセージ
- 適切な例外処理
- 入力値の検証

### 3. パフォーマンス
- 重い処理の非同期実行
- キャッシュの活用
- 適切なクールダウン設定

### 4. セキュリティ
- 適切な権限チェック
- 入力値のサニタイズ
- レート制限の実装

## 次のステップ
- [インタラクティブ機能](../03_interactive_features/01_message_components.md)でボタンやメニューの実装方法を学ぶ
