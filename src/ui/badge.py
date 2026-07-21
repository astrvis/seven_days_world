from typing import cast

import flet as ft

from tasks.badge_task import BadgeBot
from ui.log_box import log_box
from utils.consts import app_global
from utils.rapid_ocr import ocr
from utils.store import state


class Badge_View(ft.Column):
    def __init__(self):
        super().__init__()
        self._event_global = app_global
        self.badge_bot = BadgeBot()
        self.ocr = ocr
        self.count = 0
        self.state = state
        self.status_text = ft.Text()
        self.Level_type_input = ft.Column(
            controls=[
                ft.Text("关卡类型:"),
                ft.Dropdown(
                    width=200,
                    value=self.state.level_type,
                    on_select=self._on_select_event,  # type: ignore
                    options=[
                        ft.DropdownOption(key="ordinary", text="挑战馆长"),
                        ft.DropdownOption(key="chaos", text="混沌试炼"),
                    ],
                ),
            ]
        )

        self.count_input = ft.Column(
            controls=[
                ft.Text("次数"),
                ft.TextField(
                    width=200,
                    hint_text="刷取次数:",
                    keyboard_type=ft.KeyboardType.NUMBER,  # 移动端弹出数字键盘
                    input_filter=ft.NumbersOnlyInputFilter(),  # 阻止非数字字符输入
                    value=str(self.state.badge_count),
                    on_blur=self.on_blur_event,
                ),
            ]
        )
        self.btn_status = ft.Row()
        self.log_box = log_box
        self.controls = [
            self.status_text,
            self.Level_type_input,
            self.count_input,
            self.btn_status,
        ]

    def sync_status_ui(self) -> None:
        """✅ 统一的状态刷新方法（必须在主线程调用）"""
        # is_running = getattr(self.fishing_bot, "is_running", False)
        status = False if self._event_global.is_stopped() else True
        self.status_text.value = "🟢 运行中" if status else "🔴 未启动"

        self.btn_status.controls = [
            ft.ElevatedButton(
                "启动", width=100, on_click=self.on_start, disabled=status
            ),
            ft.ElevatedButton(
                "停止",
                width=100,
                color="red",
                on_click=self.on_stop,
                disabled=not status,
            ),
        ]
        self.update()

    def did_mount(self) -> None:
        self.sync_status_ui()

    # 次数框变化
    def on_blur_event(self, e) -> None:
        value = e.control.value.strip()
        if not value:
            return
        # 去除前导零，但保留纯 "0"
        stripped = value.lstrip("0") or "0"
        if stripped != self.state.badge_count:
            e.control.value = stripped
            self.state.badge_count = int(stripped)
            e.control.update()

    def on_start(self) -> None:
        self.badge_bot.on_start()

        self.sync_status_ui()

    def on_stop(self) -> None:
        self.badge_bot.on_stop()
        self.log_box.add_log("停止刷徽章")
        self.sync_status_ui()

    def _on_select_event(self, e: ft.ControlEvent) -> None:
        if self.state.level_type == e.data:
            return
        self.state.level_type = e.data if e.data is not None else ""
        dd = cast(ft.Dropdown, e.control)
        label = next((opt.text for opt in dd.options if opt.key == e.data), "")
        self.log_box.add_log(f"关卡类型已切换为: {label}")
        e.control.update()


badge_view = Badge_View()
