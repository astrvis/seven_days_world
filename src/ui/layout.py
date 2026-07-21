import asyncio
import queue
import threading
import time

import flet as ft

from ui.badge import badge_view
from ui.fish import fish_view
from ui.log_box import log_box
from ui.wqzz import wqzz
from utils.consts import app_global
from utils.rapid_ocr import load_ocr_background, ocr
from utils.store import state


class Layout(ft.Column):
    def __init__(self):
        super().__init__(expand=True)
        self.bot = None
        self.event_global = app_global
        self.state = state
        self.is_running = False
        self.log_box = log_box
        self.ocr = ocr
        self._poll_task: asyncio.Task | None = None  # 保存任务引用
        self.tab_data = [
            {"title": "钓鱼", "content": fish_view},
            {"title": "徽章", "content": badge_view},
            {"title": "忘却", "content": wqzz},
        ]
        self.tabs = ft.Tabs(
            length=len(self.tab_data),
            expand=True,
            selected_index=self.state.selected_index,
            on_change=self.click_event,
            content=ft.Column(
                expand=True,
                controls=[  # type: ignore
                    ft.TabBar(
                        tabs=[ft.Tab(label=tab["title"]) for tab in self.tab_data],
                    ),
                    ft.TabBarView(
                        expand=True,
                        controls=[  # type: ignore
                            ft.Column(
                                controls=[
                                    tab["content"],
                                    ft.Text("日志记录:"),
                                    log_box.create_field(),
                                ],
                                expand=True,
                            )
                            for tab in self.tab_data
                        ],
                    ),
                ],
            ),
        )

        self.controls = [self.tabs]

    def did_mount(self) -> None:
        """✅ 视图挂载完成，self.page 已就绪"""
        # print(f"View已挂载，Page对象: {self.page is not None}")
        threading.Thread(target=load_ocr_background, daemon=True).start()
        threading.Thread(target=self._wait_ocr, daemon=True).start()
        self._poll_task = asyncio.create_task(self._poll_queue())

    def _wait_ocr(self) -> None:

        t = 120
        start_time = time.time()
        while not self.ocr.loaded:
            end_time = time.time()
            if (end_time - start_time) >= t:
                self.log_box.add_log("ocr初始化失败，请重新启动程序或查看日志文件")
                break
            time.sleep(0.05)
        self.log_box.add_log("初始化完成")

    async def _poll_queue(self) -> None:
        """统一消费全局消息队列，更新所有 tab 的 UI"""
        while True:
            try:
                msg = self.event_global.msg_queue.get_nowait()

                if isinstance(msg, dict):
                    event_type = msg.get("type", "unknown")
                    data = msg.get("data") or {}
                    self._handle_event(event_type, data)
                    self.page.update()
            except queue.Empty:
                pass
            await asyncio.sleep(0.1)

    def _handle_event(self, event_type: str, data: dict) -> None:
        """集中处理所有来自 bot 的事件"""
        log_msg = None
        need_sync = False

        if event_type in (
            "is_focus",
            "ocr_init",
            "fish_stop",
            "state",
            "wqzz_stop",
            "fish_sucess",
            "badge_stop",
        ):
            log_msg = data.get("msg", "")
            need_sync = True

        elif event_type == "error":
            log_msg = f"错误: {data.get('message', '未知错误')}"

        if log_msg:
            self.log_box.add_log(log_msg)

        if need_sync:
            for tab in self.tab_data:
                content = tab["content"]
                if hasattr(content, "sync_status_ui"):
                    content.sync_status_ui()

    def click_event(self, e: ft.Event[ft.Tabs]) -> None:
        """✅ 点击事件处理"""
        if e.control.selected_index == self.state.selected_index:
            return
        self.state.selected_index = e.control.selected_index
        self.event_global.set_stopped()

        for tab in self.tab_data:
            content = tab["content"]
            if hasattr(content, "sync_status_ui"):
                content.sync_status_ui()
