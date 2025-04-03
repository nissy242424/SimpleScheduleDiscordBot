# Discord スケジュール調整 Bot

## 概要
Discordサーバーでイベントの日程調整を簡単に行えるBotです。
投票機能（⭕🔺❌）とリマインダー機能を備えています。

## 主な機能
- スケジュール作成（最大10件の候補日時）
- 参加可否の投票（⭕🔺❌）
- リマインダー通知（候補日の1日前）
- スケジュール一覧表示

## 技術スタック
- Python 3.11
- discord.py
- aiosqlite
- python-dotenv

## セットアップ
1. 依存関係のインストール
```bash
python -m venv .venv
source .venv/Scripts/activate  # Windows
pip install -r requirements.txt
```

2. Discord Developer Portal設定
- [Discord Developer Portal](https://discord.com/developers/applications)でアプリケーションを作成
- Bot設定で必要なIntentsを有効化:
  - Message Content Intent
  - Server Members Intent
- Botトークンの取得と保管

3. 環境変数の設定
```bash
cp .env.example .env
# .envファイルを編集し、Discord Botトークンを設定
```

4. Botの招待設定
- OAuth2 URL Generatorで以下の権限を設定:
  - View Channels (チャンネルの閲覧)
  - Send Messages (メッセージの送信)
  - Embed Links (埋め込みリンク)
  - Add Reactions (リアクションの追加)
  - Read Message History (メッセージ履歴の読み取り)
  - Mention Everyone (全員メンション)
  - Manage Messages (メッセージの管理)
  - Use Slash Commands (スラッシュコマンドの使用)
  - Create Commands (コマンドの作成)
- 生成されたURLでBotをサーバーに招待

5. Botの起動
```bash
python -m src.simple_schedule_bot.main
```

## 使用方法
### スケジュール作成
```
/schedule create
```
- タイトルと説明（任意）を入力
- 最大10件まで候補日時を追加可能
- 作成後、参加者が投票可能

### 投票方法
- ⭕: 参加可能
- 🔺: 検討中/調整可能
- ❌: 参加不可

### スケジュール一覧
```
/schedule list
```
- 現在進行中のスケジュール一覧を表示
- 各スケジュールの投票状況を確認可能

### ヘルプ表示
```
/schedule help
```
- 各コマンドの詳細な使用方法を表示

## リマインダー機能
- 最も近い候補日の1日前に自動通知
- 未回答者にメンションで通知
- 投票が完了すると通知は送信されません

## データベース
- SQLiteを使用
- データは自動的にバックアップ
- 簡単な運用保守が可能

## 注意事項
- 一度作成したスケジュールの候補日時は編集できません
- 投票はいつでも変更可能です
- スケジュールの削除は作成者のみ可能です

## トラブルシューティング
### Bot が応答しない場合
1. Botのステータスが「オンライン」になっているか確認
2. コマンドを入力したチャンネルにBotが参加しているか確認
3. Botに適切な権限が付与されているか確認

### データベースエラーが発生する場合
1. ディスク容量に十分な空きがあるか確認
2. データベースファイルのパーミッションを確認
3. 必要に応じてデータベースファイルを再作成

## ライセンス
MIT License

## 貢献
1. Fork the Project
2. Create your Feature Branch
3. Commit your Changes
4. Push to the Branch
5. Open a Pull Request
