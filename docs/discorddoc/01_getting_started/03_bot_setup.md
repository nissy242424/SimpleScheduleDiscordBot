# Botのセットアップ

## Botアカウントの作成

### 1. Developer Portalでの設定
1. [Discord Developer Portal](https://discord.com/developers/applications)にアクセス
2. 「New Application」をクリック
3. アプリケーション名を入力
4. 「Bot」セクションに移動
5. 「Add Bot」をクリック
6. Botの設定を行う：
   - アイコンの設定
   - ユーザーネームの設定
   - Public Botの設定

### 2. トークンの取得
1. 「Bot」セクションでトークンを確認
2. 「Reset Token」でトークンをリセット（必要な場合）
3. トークンを安全な場所に保管

### 3. Intentの設定
1. 「Bot」セクションで必要なIntentsを有効化
   - Presence Intent
   - Server Members Intent
   - Message Content Intent

## 基本的なBotの実装

### 1. プロジェクト構造の作成
```
my_bot/
├── .env
├── .gitignore
├── requirements.txt
├── main.py
└── config.py
```

### 2. 必要なファイルの設定

#### .env
```plaintext
DISCORD_TOKEN=your_bot_token_here
```

#### .gitignore
```plaintext
# Environment variables
.env

# Python
__pycache__/
*.py[cod]
*$py.class
venv/

# IDE
.vscode/
.idea/
```

#### requirements.txt
```plaintext
discord.py>=2.0.0
python-dotenv>=0.19.0
```

#### config.py
```python
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
```

### 3. 基本的なBotコード

#### main.py
```python
import discord
from discord.ext import commands
from config import TOKEN

# Intentの設定
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Botのインスタンス化
bot = commands.Bot(command_prefix='!', intents=intents)

# 起動時のイベント
@bot.event
async def on_ready():
    print(f'{bot.user} としてログインしました')
    
# 基本的なコマンド
@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

# Botの起動
if __name__ == '__main__':
    bot.run(TOKEN)
```

## Botのサーバーへの追加

### 1. OAuth2 URLの生成
1. Developer Portalの「OAuth2」セクションに移動
2. 「URL Generator」を選択
3. スコープを選択：
   - `bot`
   - `applications.commands`
4. 必要な権限を選択
5. 生成されたURLをコピー

### 2. Botの招待
1. 生成したURLをブラウザで開く
2. 追加したいサーバーを選択
3. 権限を確認して「認証」をクリック

## Botの起動と確認

### 1. 依存関係のインストール
```bash
pip install -r requirements.txt
```

### 2. Botの起動
```bash
python main.py
```

### 3. 動作確認
1. Discord サーバーで `!ping` を実行
2. Botが「Pong!」と応答することを確認

## トラブルシューティング

### よくある問題と解決方法

1. **トークンエラー**
   - トークンが正しく設定されているか確認
   - .envファイルの存在と内容を確認

2. **Intent関連のエラー**
   - Developer Portalでの設定を確認
   - コード内でのIntents設定を確認

3. **権限エラー**
   - Botの権限設定を確認
   - サーバー内での役割の設定を確認

## 次のステップ
- [Botの初期化とIntents](../02_basic_concepts/01_initialization.md)で詳細な設定を学ぶ
- [イベントシステム](../02_basic_concepts/02_events.md)でイベント処理を学ぶ
- [コマンドシステム](../02_basic_concepts/03_commands.md)でコマンドの実装を学ぶ
