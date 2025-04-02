# エラーハンドリングとログ

## エラー処理の基本

### グローバルエラーハンドラ
```python
@bot.event
async def on_error(event, *args, **kwargs):
    """すべてのイベントのエラーを処理"""
    import traceback
    import sys
    error = sys.exc_info()
    
    # エラーのログ記録
    error_trace = "".join(traceback.format_exception(*error))
    logger.error(f'イベント {event} でエラーが発生:\n{error_trace}')

@bot.event
async def on_command_error(ctx, error):
    """コマンド実行時のエラーを処理"""
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("そのコマンドは存在しません")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("このコマンドを実行する権限がありません")
    else:
        logger.error(f'コマンドエラー: {str(error)}')
        await ctx.send(f"エラーが発生しました: {str(error)}")
```

## ログシステム

### ログの設定
```python
import logging
from logging.handlers import RotatingFileHandler
import os

# ログディレクトリの作成
if not os.path.exists('logs'):
    os.makedirs('logs')

# ログフォーマットの設定
log_format = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# ファイルハンドラの設定
file_handler = RotatingFileHandler(
    'logs/bot.log',
    maxBytes=5_000_000,  # 5MB
    backupCount=5,
    encoding='utf-8'
)
file_handler.setFormatter(log_format)

# コンソールハンドラの設定
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_format)

# ロガーの設定
logger = logging.getLogger('discord_bot')
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)
```

### ログレベルの使い分け
```python
# 情報ログ
logger.info('Botが起動しました')

# 警告ログ
logger.warning('レート制限に近づいています')

# エラーログ
logger.error('データベース接続に失敗しました', exc_info=True)

# デバッグログ
logger.debug('デバッグ情報: %s', debug_data)

# 重大なエラー
logger.critical('重大なエラーが発生しました', exc_info=True)
```

## エラーの種類と処理方法

### コマンドエラー
```python
@bot.event
async def on_command_error(ctx, error):
    """詳細なコマンドエラー処理"""
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"必要な引数が不足しています: {error.param.name}")
        
    elif isinstance(error, commands.BadArgument):
        await ctx.send("引数の型が正しくありません")
        
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(
            f"コマンドのクールダウン中です。"
            f"{error.retry_after:.1f}秒後に再試行できます"
        )
        
    elif isinstance(error, commands.DisabledCommand):
        await ctx.send("このコマンドは現在無効化されています")
        
    elif isinstance(error, commands.NoPrivateMessage):
        await ctx.send("このコマンドはDMでは使用できません")
        
    elif isinstance(error, commands.CheckFailure):
        await ctx.send("このコマンドを実行する権限がありません")
```

### カスタムエラー
```python
class CustomCommandError(commands.CommandError):
    """カスタムコマンドエラー"""
    pass

class InvalidData(CustomCommandError):
    """無効なデータエラー"""
    pass

@bot.command()
async def process_data(ctx, data: str):
    try:
        if not validate_data(data):
            raise InvalidData("無効なデータ形式です")
            
        # データ処理
        result = process(data)
        await ctx.send(f"処理結果: {result}")
        
    except InvalidData as e:
        await ctx.send(str(e))
        logger.warning(f'無効なデータ: {data}')
```

## エラー監視とデバッグ

### エラー統計
```python
class ErrorStats:
    def __init__(self):
        self.error_counts = {}
        
    def add_error(self, error_type: str):
        """エラーの発生回数をカウント"""
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
    def get_stats(self):
        """エラー統計を取得"""
        return dict(self.error_counts)

error_stats = ErrorStats()

@bot.event
async def on_command_error(ctx, error):
    # エラーの記録
    error_type = type(error).__name__
    error_stats.add_error(error_type)
    
    # エラー処理
    await handle_error(ctx, error)
```

### デバッグモード
```python
class DebugCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.debug_mode = False
        
    @commands.command()
    @commands.is_owner()
    async def toggle_debug(self, ctx):
        """デバッグモードの切り替え"""
        self.debug_mode = not self.debug_mode
        mode = "有効" if self.debug_mode else "無効"
        await ctx.send(f"デバッグモードを{mode}にしました")
        
    @commands.command()
    @commands.is_owner()
    async def show_error_stats(self, ctx):
        """エラー統計を表示"""
        stats = error_stats.get_stats()
        
        if not stats:
            await ctx.send("エラーは記録されていません")
            return
            
        message = "エラー統計:\n"
        for error_type, count in stats.items():
            message += f"- {error_type}: {count}回\n"
            
        await ctx.send(message)
```

## ベストプラクティス

### 1. エラー処理の階層化
- グローバルエラーハンドラ
- コグ固有のエラーハンドラ
- コマンド固有のエラーハンドラ

### 2. ログの管理
- 適切なログレベルの使用
- ログのローテーション
- センシティブ情報の保護

### 3. エラーの分類
- ユーザーエラー
- システムエラー
- ネットワークエラー
- 権限エラー

### 4. エラーメッセージ
- 明確で理解しやすい
- 解決方法の提示
- 適切なコンテキスト情報

## 次のステップ
- [最適化](../05_optimization/01_caching.md)でパフォーマンス向上について学ぶ
