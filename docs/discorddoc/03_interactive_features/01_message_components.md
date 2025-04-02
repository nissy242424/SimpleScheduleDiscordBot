# メッセージコンポーネント

## 埋め込みメッセージ（Embed）

### 基本的な埋め込み
```python
@bot.command()
async def info(ctx):
    """サーバー情報を表示"""
    embed = discord.Embed(
        title="サーバー情報",
        description="このサーバーの基本情報です",
        color=discord.Color.blue()
    )
    
    embed.add_field(name="サーバー名", value=ctx.guild.name, inline=True)
    embed.add_field(name="メンバー数", value=ctx.guild.member_count, inline=True)
    embed.set_footer(text=f"ID: {ctx.guild.id}")
    
    await ctx.send(embed=embed)
```

### 高度な埋め込み
```python
@bot.command()
async def profile(ctx, member: discord.Member = None):
    """ユーザープロフィールを表示"""
    member = member or ctx.author
    
    embed = discord.Embed(
        title=f"{member.name}のプロフィール",
        description=member.mention,
        color=member.color
    )
    
    embed.set_thumbnail(url=member.avatar.url)
    embed.add_field(name="参加日", value=member.joined_at.strftime("%Y/%m/%d"), inline=True)
    embed.add_field(name="アカウント作成日", value=member.created_at.strftime("%Y/%m/%d"), inline=True)
    embed.add_field(name="ロール", value=" ".join([role.mention for role in member.roles[1:]]), inline=False)
    
    await ctx.send(embed=embed)
```

## メッセージの編集と更新

### プログレスバー
```python
@bot.command()
async def progress(ctx):
    """進捗バーを表示"""
    message = await ctx.send("処理を開始します...")
    
    progress = ["⬜"] * 10
    for i in range(10):
        progress[i] = "🟦"
        await message.edit(content="".join(progress) + f" {(i+1)*10}%")
        await asyncio.sleep(1)
    
    await message.edit(content="処理が完了しました！")
```

### リアクション付きメッセージ
```python
@bot.command()
async def poll(ctx, question, *options):
    """投票を作成"""
    if len(options) > 10:
        await ctx.send("選択肢は10個までです")
        return
        
    # 数字の絵文字
    reactions = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    
    description = []
    for i, option in enumerate(options):
        description.append(f"{reactions[i]} {option}")
    
    embed = discord.Embed(
        title=question,
        description="\n".join(description),
        color=discord.Color.blue()
    )
    
    poll_msg = await ctx.send(embed=embed)
    
    for i in range(len(options)):
        await poll_msg.add_reaction(reactions[i])
```

## ファイル添付

### 画像の送信
```python
@bot.command()
async def send_image(ctx):
    """画像を送信"""
    file = discord.File("path/to/image.png", filename="image.png")
    embed = discord.Embed(title="画像タイトル")
    embed.set_image(url="attachment://image.png")
    await ctx.send(file=file, embed=embed)
```

### ファイルのアップロード
```python
@bot.command()
async def upload(ctx):
    """ファイルをアップロード"""
    files = [
        discord.File("file1.txt", filename="uploaded_file1.txt"),
        discord.File("file2.pdf", filename="uploaded_file2.pdf")
    ]
    await ctx.send("ファイルをアップロードしました:", files=files)
```

## メッセージテンプレート

### ヘルプメッセージ
```python
def create_help_embed(command_list):
    embed = discord.Embed(
        title="コマンド一覧",
        description="使用可能なコマンドの説明です",
        color=discord.Color.green()
    )
    
    for cmd in command_list:
        embed.add_field(
            name=f"`{cmd.name}`",
            value=cmd.help or "説明なし",
            inline=False
        )
    
    return embed
```

### エラーメッセージ
```python
def create_error_embed(error_type, description):
    embed = discord.Embed(
        title="エラー",
        description=description,
        color=discord.Color.red()
    )
    embed.set_footer(text=f"エラータイプ: {error_type}")
    return embed
```

## 高度な使用例

### ページネーション
```python
class Paginator:
    def __init__(self, ctx, items, per_page=10):
        self.ctx = ctx
        self.items = items
        self.per_page = per_page
        self.pages = [items[i:i+per_page] for i in range(0, len(items), per_page)]
        self.current_page = 0
        
    def get_page_embed(self):
        embed = discord.Embed(
            title=f"ページ {self.current_page + 1}/{len(self.pages)}",
            description="\n".join(self.pages[self.current_page]),
            color=discord.Color.blue()
        )
        return embed
    
    async def start(self):
        if not self.pages:
            return await self.ctx.send("表示するアイテムがありません")
            
        message = await self.ctx.send(embed=self.get_page_embed())
        
        # ページ送りのリアクションを追加
        await message.add_reaction("◀️")
        await message.add_reaction("▶️")
        
        def check(reaction, user):
            return user == self.ctx.author and str(reaction.emoji) in ["◀️", "▶️"]
            
        while True:
            try:
                reaction, user = await self.ctx.bot.wait_for(
                    "reaction_add",
                    timeout=60.0,
                    check=check
                )
                
                if str(reaction.emoji) == "▶️" and self.current_page < len(self.pages) - 1:
                    self.current_page += 1
                    await message.edit(embed=self.get_page_embed())
                    
                elif str(reaction.emoji) == "◀️" and self.current_page > 0:
                    self.current_page -= 1
                    await message.edit(embed=self.get_page_embed())
                    
                await message.remove_reaction(reaction, user)
                
            except asyncio.TimeoutError:
                await message.clear_reactions()
                break
```

## ベストプラクティス

### 1. メッセージの設計
- 明確で読みやすい構造
- 適切な色使い
- 必要な情報のみ表示

### 2. パフォーマンス
- 大きなメッセージの分割
- 適切な更新頻度
- リアクションの制限

### 3. エラー処理
- タイムアウトの処理
- 権限エラーの処理
- 入力検証

### 4. ユーザビリティ
- 直感的な操作方法
- 適切なフィードバック
- ヘルプの提供

## 次のステップ
- [UI要素](02_ui_elements.md)でボタンやセレクトメニューの実装を学ぶ
