# 必要条件

## 開発環境の準備

### Python環境
- Python 3.8以上のインストール
  ```bash
  # Pythonのバージョン確認
  python --version
  ```

- pip（パッケージマネージャー）の確認
  ```bash
  # pipのバージョン確認
  pip --version
  ```

### 必要なパッケージ
1. **discord.py**
   ```bash
   # discord.pyのインストール
   python -m pip install -U discord.py
   ```

2. **仮想環境（推奨）**
   ```bash
   # 仮想環境の作成
   python -m venv venv

   # 仮想環境の有効化
   # Windows
   .\venv\Scripts\activate
   # Unix/macOS
   source venv/bin/activate
   ```

### 開発ツール
- VSCode（推奨）
  - Python拡張機能
  - GitLens（推奨）
  - Discord Markdown Preview（推奨）

## Discord開発者アカウント

### アカウント作成
1. [Discord](https://discord.com/)でアカウントを作成
2. メールアドレスの確認
3. 2要素認証の設定（推奨）

### Developer Portal
1. [Discord Developer Portal](https://discord.com/developers/applications)にアクセス
2. 「New Application」をクリック
3. アプリケーション名を設定

## 必要な権限

### Bot用の権限
基本的な権限：
- Send Messages
- Read Messages/View Channels
- Send Messages in Threads
- Embed Links
- Attach Files
- Read Message History
- Add Reactions
- Use Slash Commands

追加の権限（機能に応じて）：
- Manage Messages
- Manage Channels
- Manage Roles
- Connect（音声機能用）
- Speak（音声機能用）

### Intents設定
必要なIntents：
- Presence Intent
- Server Members Intent
- Message Content Intent

```python
# Intentsの設定例
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True
```

## ネットワーク要件

### 接続要件
- 安定したインターネット接続
- Discord APIへのアクセス（ポート443）
- WebSocketの接続維持

### レート制限
- Global Rate Limits
- Route-Specific Rate Limits
- Per-Guild Rate Limits

## セキュリティ要件

### トークン管理
- Botトークンの安全な保管
- 環境変数の使用
- .gitignoreの適切な設定

### 環境変数
```python
# .env ファイルの例
DISCORD_TOKEN=your_bot_token_here
GUILD_ID=your_guild_id_here
```

```python
# 環境変数の読み込み
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
```

## 次のステップ
- [Botのセットアップ](03_bot_setup.md)に進む
- 基本的なBotを作成し、サーバーに追加する方法を学ぶ
