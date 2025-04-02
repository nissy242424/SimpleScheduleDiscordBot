# イベントシステム

## イベントの基本

### イベントとは
イベントは、Discordで発生する様々なアクションを捕捉するための仕組みです。ユーザーのメッセージ、参加、退出など、サーバー上で起こる様々な動作に対して反応することができます。

### イベントの種類

#### メッセージ関連
```python
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if message.content.startswith('こんにちは'):
        await message.channel.send('こんにちは！')

    # コマンドの処理を行うために必要
    await bot.process_commands(message)

@bot.event
async def on_message_delete(message):
    # メッセージが削除された時の処理
    print(f'メッセージが削除されました: {message.content}')

@bot.event
async def on_message_edit(before, after):
    # メッセージが編集された時の処理
    print(f'編集前: {before.content}')
    print(f'編集後: {after.content}')
```

#### メンバー関連
```python
@bot.event
async def on_member_join(member):
    # メンバーが参加した時の処理
    channel = member.guild.system_channel
    if channel is not None:
        await channel.send(f'{member.mention}さん、ようこそ！')

@bot.event
async def on_member_remove(member):
    # メンバーが退出した時の処理
    channel = member.guild.system_channel
    if channel is not None:
        await channel.send(f'{member.name}さんが退出しました')

@bot.event
async def on_member_update(before, after):
    # メンバーの情報が更新された時の処理
    if before.nick != after.nick:
        print(f'ニックネームが変更されました: {before.nick} → {after.nick}')
```

#### リアクション関連
```python
@bot.event
async def on_reaction_add(reaction, user):
    # リアクションが追加された時の処理
    if str(reaction.emoji) == '👍':
        await reaction.message.channel.send(f'{user.name}さんがいいねしました！')

@bot.event
async def on_reaction_remove(reaction, user):
    # リアクションが削除された時の処理
    print(f'{user.name}がリアクションを削除しました')
```

#### ボイス関連
```python
@bot.event
async def on_voice_state_update(member, before, after):
    # ボイスチャンネルの状態が変更された時の処理
    if before.channel is None and after.channel is not None:
        # ボイスチャンネルに参加
        print(f'{member.name}が{after.channel.name}に参加しました')
    elif before.channel is not None and after.channel is None:
        # ボイスチャンネルから退出
        print(f'{member.name}が{before.channel.name}から退出しました')
```

#### サーバー関連
```python
@bot.event
async def on_guild_join(guild):
    # Botが新しいサーバーに参加した時の処理
    print(f'新しいサーバーに参加しました: {guild.name}')

@bot.event
async def on_guild_remove(guild):
    # Botがサーバーから削除された時の処理
    print(f'サーバーから削除されました: {guild.name}')
```

## エラーハンドリング

### グローバルエラーハンドラ
```python
@bot.event
async def on_error(event, *args, **kwargs):
    """すべてのイベントで発生したエラーを処理"""
    import traceback
    import sys
    
    error = sys.exc_info()
    # エラー情報をログに記録
    traceback.print_exception(*error)

@bot.event
async def on_command_error(ctx, error):
    """コマンド実行時のエラーを処理"""
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('コマンドが見つかりません')
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send('このコマンドを実行する権限がありません')
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('必要な引数が不足しています')
    else:
        await ctx.send(f'エラーが発生しました: {str(error)}')
```

## イベントの使用例

### メッセージフィルター
```python
@bot.event
async def on_message(message):
    # NGワードをフィルタリング
    ng_words = ['NGワード1', 'NGワード2']
    
    if any(word in message.content for word in ng_words):
        await message.delete()
        await message.channel.send(f'{message.author.mention} 不適切な表現は使用できません')
    
    await bot.process_commands(message)
```

### 自動役職付与
```python
@bot.event
async def on_member_join(member):
    # 新規メンバーに自動で役職を付与
    role = discord.utils.get(member.guild.roles, name='メンバー')
    if role is not None:
        await member.add_roles(role)
        
    # 参加メッセージを送信
    channel = member.guild.system_channel
    if channel is not None:
        embed = discord.Embed(
            title='メンバー参加',
            description=f'{member.mention}さんがサーバーに参加しました！',
            color=discord.Color.green()
        )
        await channel.send(embed=embed)
```

### リアクションロール
```python
@bot.event
async def on_raw_reaction_add(payload):
    # リアクションに応じて役職を付与
    if payload.message_id != ROLE_MESSAGE_ID:  # 特定のメッセージのみ対象
        return

    guild = bot.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id)

    role_emojis = {
        '🔴': 'Red Team',
        '🔵': 'Blue Team',
        '🟢': 'Green Team'
    }

    if str(payload.emoji) in role_emojis:
        role = discord.utils.get(guild.roles, name=role_emojis[str(payload.emoji)])
        if role is not None:
            await member.add_roles(role)
```

## ベストプラクティス

### 1. エラー処理
- 適切なエラーハンドリングの実装
- エラーログの記録
- ユーザーフレンドリーなエラーメッセージ

### 2. パフォーマンス
- 重い処理は非同期で実行
- キャッシュの活用
- 必要最小限のイベント購読

### 3. セキュリティ
- 入力値の検証
- 権限チェック
- レート制限の実装

### 4. コード整理
- イベントハンドラの分割
- コグの活用
- 共通処理の関数化

## 次のステップ
- [コマンドシステム](03_commands.md)でコマンドの実装方法を学ぶ
