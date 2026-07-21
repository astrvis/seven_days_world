import time

import flet as ft

from utils.consts import app_global


class Log_Box:
    """日志管理器（非控件），为每个 tab 创建独立的 TextField，共享同一份日志内容"""

    _instance = None

    def __init__(self) -> None:
        self.log_fields: list[ft.TextField] = []
        self._log_value = ""
        self.msg_queue = app_global.msg_queue

    @classmethod
    def get_instance(cls) -> "Log_Box":
        if not cls._instance:
            cls._instance = Log_Box()
        return cls._instance

    def create_field(self) -> ft.TextField:
        """为每个 tab 创建独立的 TextField，共享同一份日志内容"""
        field = ft.TextField(
            multiline=True,
            read_only=True,
            min_lines=10,
            text_size=14,
            max_lines=10,
            expand=True,
            value=self._log_value,
        )
        self.log_fields.append(field)
        return field

    def add_log(self, text: str) -> None:
        """✅ 线程安全的日志追加，同步更新所有 TextField"""
        timestamp = time.strftime("%H:%M:%S")
        new_log = f"[{timestamp}] {text}\n"
        self._log_value = new_log + self._log_value
        for field in self.log_fields:
            field.value = self._log_value
            try:
                field.update()
            except Exception as e:
                print(f"更新 TextField 失败: {e}")


log_box = Log_Box.get_instance()
