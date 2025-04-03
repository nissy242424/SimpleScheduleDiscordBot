"""
Custom exceptions for the Discord Schedule Bot.
"""

class ScheduleError(Exception):
    """スケジュール関連の基本例外クラス"""
    pass

class ValidationError(ScheduleError):
    """バリデーションエラー"""
    pass

class DatabaseError(ScheduleError):
    """データベース操作エラー"""
    pass

class ConfigError(ScheduleError):
    """設定関連のエラー"""
    pass

class CommandError(ScheduleError):
    """コマンド実行エラー"""
    pass

class ReminderError(ScheduleError):
    """リマインダー処理エラー"""
    pass
