# UI要素

## ボタン

### 基本的なボタン
```python
class SimpleButton(discord.ui.View):
    def __init__(self):
        super().__init__()
        
    @discord.ui.button(label="クリック", style=discord.ButtonStyle.primary)
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("ボタンがクリックされました！")

@bot.command()
async def show_button(ctx):
    """ボタンを表示"""
    view = SimpleButton()
    await ctx.send("以下のボタンをクリックしてください：", view=view)
```

### 複数のボタン
```python
class MultiButtons(discord.ui.View):
    def __init__(self):
        super().__init__()
        
    @discord.ui.button(
        label="はい",
        style=discord.ButtonStyle.green,
        custom_id="yes_button"
    )
    async def yes_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("「はい」が選択されました")
        
    @discord.ui.button(
        label="いいえ",
        style=discord.ButtonStyle.red,
        custom_id="no_button"
    )
    async def no_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("「いいえ」が選択されました")
```

### カスタムボタン
```python
class ColorButton(discord.ui.Button):
    def __init__(self, color: str):
        super().__init__(
            label=color,
            style=discord.ButtonStyle.primary,
            custom_id=f"color_{color.lower()}"
        )
        self.color = color
        
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"{self.color}が選択されました")

class ColorView(discord.ui.View):
    def __init__(self):
        super().__init__()
        colors = ["赤", "青", "緑", "黄"]
        for color in colors:
            self.add_item(ColorButton(color))
```

## セレクトメニュー

### 単一選択メニュー
```python
class RoleSelect(discord.ui.View):
    @discord.ui.select(
        placeholder="ロールを選択",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                label="メンバー",
                description="一般メンバーロール",
                emoji="👥"
            ),
            discord.SelectOption(
                label="モデレーター",
                description="モデレーターロール",
                emoji="🛡️"
            )
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        await interaction.response.send_message(f"{select.values[0]}が選択されました")
```

### 複数選択メニュー
```python
class MultiSelect(discord.ui.View):
    @discord.ui.select(
        placeholder="興味のある分野を選択",
        min_values=1,
        max_values=3,
        options=[
            discord.SelectOption(label="プログラミング", emoji="💻"),
            discord.SelectOption(label="ゲーム", emoji="🎮"),
            discord.SelectOption(label="音楽", emoji="🎵"),
            discord.SelectOption(label="アート", emoji="🎨")
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        selections = ", ".join(select.values)
        await interaction.response.send_message(f"選択された項目: {selections}")
```

## モーダル（フォーム）

### 基本的なフォーム
```python
class FeedbackModal(discord.ui.Modal, title="フィードバック"):
    name = discord.ui.TextInput(
        label="名前",
        placeholder="あなたの名前を入力",
        required=True,
        max_length=50
    )
    
    feedback = discord.ui.TextInput(
        label="フィードバック",
        style=discord.TextStyle.paragraph,
        placeholder="フィードバックを入力してください",
        required=True,
        max_length=1000
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"フィードバックを受け付けました！\n"
            f"名前: {self.name.value}\n"
            f"内容: {self.feedback.value}"
        )

@bot.command()
async def feedback(ctx):
    """フィードバックフォームを表示"""
    modal = FeedbackModal()
    await ctx.send("以下のボタンをクリックしてフィードバックを送信：",
                  view=discord.ui.Button(label="フィードバック", style=discord.ButtonStyle.primary))
```

### 複雑なフォーム
```python
class SurveyModal(discord.ui.Modal, title="アンケート"):
    name = discord.ui.TextInput(
        label="名前",
        required=True
    )
    
    age = discord.ui.TextInput(
        label="年齢",
        required=True,
        max_length=3
    )
    
    favorite_color = discord.ui.TextInput(
        label="好きな色",
        required=True
    )
    
    reason = discord.ui.TextInput(
        label="理由",
        style=discord.TextStyle.paragraph,
        required=False,
        max_length=500
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        # 入力値の検証
        try:
            age = int(self.age.value)
            if age < 0 or age > 150:
                raise ValueError("Invalid age")
        except ValueError:
            await interaction.response.send_message(
                "有効な年齢を入力してください",
                ephemeral=True
            )
            return
            
        # データの保存や処理
        await interaction.response.send_message(
            f"アンケートの回答ありがとうございます！\n"
            f"名前: {self.name.value}\n"
            f"年齢: {age}\n"
            f"好きな色: {self.favorite_color.value}\n"
            f"理由: {self.reason.value or '未入力'}"
        )
```

## 高度な使用例

### インタラクティブメニュー
```python
class MenuView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)  # 3分でタイムアウト
        
    @discord.ui.button(label="メインメニュー", style=discord.ButtonStyle.primary)
    async def main_menu(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="メインメニュー",
            description="以下のオプションから選択してください",
            color=discord.Color.blue()
        )
        await interaction.response.edit_message(embed=embed, view=self)
        
    @discord.ui.select(
        placeholder="メニューを選択",
        options=[
            discord.SelectOption(label="プロフィール", value="profile"),
            discord.SelectOption(label="設定", value="settings"),
            discord.SelectOption(label="ヘルプ", value="help")
        ]
    )
    async def menu_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        if select.values[0] == "profile":
            await self.show_profile(interaction)
        elif select.values[0] == "settings":
            await self.show_settings(interaction)
        elif select.values[0] == "help":
            await self.show_help(interaction)
            
    async def show_profile(self, interaction: discord.Interaction):
        embed = discord.Embed(title="プロフィール")
        await interaction.response.edit_message(embed=embed)
        
    async def show_settings(self, interaction: discord.Interaction):
        embed = discord.Embed(title="設定")
        await interaction.response.edit_message(embed=embed)
        
    async def show_help(self, interaction: discord.Interaction):
        embed = discord.Embed(title="ヘルプ")
        await interaction.response.edit_message(embed=embed)
```

## ベストプラクティス

### 1. UI設計
- 直感的な操作方法
- 適切なラベルと説明
- 視認性の高いレイアウト

### 2. エラー処理
- 入力値の検証
- タイムアウト処理
- エラーメッセージの表示

### 3. パフォーマンス
- コンポーネントの再利用
- メモリ使用量の最適化
- 適切なタイムアウト設定

### 4. ユーザビリティ
- フィードバックの提供
- 適切な応答時間
- アクセシビリティへの配慮

## 次のステップ
- [インタラクション処理](03_interactions.md)でユーザーとのインタラクションの詳細を学ぶ
