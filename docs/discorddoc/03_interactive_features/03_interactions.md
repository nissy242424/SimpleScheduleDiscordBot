# インタラクション処理

## インタラクションの基本

### インタラクションとは
インタラクションは、ユーザーがBotのUI要素（ボタン、セレクトメニュー、モーダルなど）と対話する際に発生するイベントです。

### 基本的な応答方法
```python
@bot.tree.command()
async def example(interaction: discord.Interaction):
    # 即時応答
    await interaction.response.send_message("これは即時応答です")
    
    # 遅延応答
    await interaction.response.defer()
    await asyncio.sleep(5)  # 何らかの処理
    await interaction.followup.send("これは遅延応答です")
```

## 応答タイプ

### メッセージ送信
```python
# 通常のメッセージ
await interaction.response.send_message("通常のメッセージ")

# 一時的なメッセージ（エフェメラル）
await interaction.response.send_message(
    "このメッセージはあなたにのみ表示されます",
    ephemeral=True
)

# 埋め込みメッセージ
embed = discord.Embed(
    title="タイトル",
    description="説明",
    color=discord.Color.blue()
)
await interaction.response.send_message(embed=embed)
```

### メッセージの更新
```python
# メッセージの編集
await interaction.response.edit_message(content="更新されたメッセージ")

# 埋め込みの更新
new_embed = discord.Embed(title="新しいタイトル")
await interaction.response.edit_message(embed=new_embed)

# コンポーネントの更新
new_view = UpdatedView()
await interaction.response.edit_message(view=new_view)
```

### モーダル表示
```python
class ResponseModal(discord.ui.Modal, title="応答フォーム"):
    response = discord.ui.TextInput(
        label="応答",
        style=discord.TextStyle.paragraph
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"回答: {self.response.value}"
        )

@bot.tree.command()
async def show_modal(interaction: discord.Interaction):
    await interaction.response.send_modal(ResponseModal())
```

## 高度な処理

### 遅延応答とフォローアップ
```python
@bot.tree.command()
async def long_process(interaction: discord.Interaction):
    # 処理時間が3秒を超える場合は遅延応答が必要
    await interaction.response.defer()
    
    # 長時間の処理
    await asyncio.sleep(5)
    
    # フォローアップメッセージ
    await interaction.followup.send("処理が完了しました")
    
    # 追加のフォローアップ
    await interaction.followup.send("追加情報です", ephemeral=True)
```

### 条件付き応答
```python
@bot.tree.command()
async def conditional_response(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "この操作には管理者権限が必要です",
            ephemeral=True
        )
        return
        
    await interaction.response.send_message("管理者コマンドを実行しました")
```

### コンポーネントの動的更新
```python
class DynamicView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.value = 0
        
    @discord.ui.button(label="増加", style=discord.ButtonStyle.primary)
    async def increment(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value += 1
        await interaction.response.edit_message(
            content=f"現在の値: {self.value}",
            view=self
        )
        
    @discord.ui.button(label="減少", style=discord.ButtonStyle.danger)
    async def decrement(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value -= 1
        await interaction.response.edit_message(
            content=f"現在の値: {self.value}",
            view=self
        )
```

## エラー処理

### 基本的なエラーハンドリング
```python
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(
            f"クールダウン中です。{error.retry_after:.1f}秒後に再試行できます",
            ephemeral=True
        )
    elif isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message(
            "必要な権限がありません",
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            f"エラーが発生しました: {str(error)}",
            ephemeral=True
        )
```

### カスタムエラーハンドリング
```python
class CustomError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)

@bot.tree.command()
async def risky_command(interaction: discord.Interaction):
    try:
        # 危険な処理
        raise CustomError("カスタムエラーが発生しました")
    except CustomError as e:
        await interaction.response.send_message(
            f"エラー: {e.message}",
            ephemeral=True
        )
    except Exception as e:
        # 予期しないエラー
        await interaction.response.send_message(
            "予期しないエラーが発生しました",
            ephemeral=True
        )
        raise e  # エラーログのため再度発生させる
```

## ベストプラクティス

### 1. レスポンスタイミング
- 3秒以内に最初の応答を送信
- 長時間の処理は遅延応答を使用
- 適切なフィードバックの提供

### 2. エラー処理
- ユーザーフレンドリーなエラーメッセージ
- エフェメラルメッセージの活用
- 適切なエラーログの記録

### 3. パフォーマンス
- 効率的なデータ処理
- 適切なキャッシュの使用
- リソースの適切な解放

### 4. セキュリティ
- 権限の確認
- 入力値の検証
- レート制限の実装

## 次のステップ
- [プロジェクト構造](../04_development/01_project_structure.md)でコードの構造化について学ぶ
