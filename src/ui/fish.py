import asyncio

import flet as ft

from tasks.fish_task import FishingBot
from ui.log_box import log_box
from utils.consts import app_global
from utils.store import state


class Fish_View(ft.Column):
    def __init__(self):
        super().__init__()
        self.state = state

        self.fishing_bot = FishingBot()
        self._poll_task: asyncio.Task | None = None  # 保存任务引用
        self.log_box = log_box
        self.tags = self.state.tags
        self._event_global = app_global
        # ==================启停状态===================#
        self.status_text = ft.Text()

        # ==================键位行===================#
        self.keyword_row = ft.Row(wrap=True)

        # 键位行的输入框
        self.keyword_input = ft.TextField(
            hint_text="键位",
            width=100,
            on_submit=self.on_add,
            margin=ft.Margin(left=10, top=0, right=10, bottom=0),
        )

        # ================弧度阈值===================#

        self.threshold_row = ft.Row(
            wrap=True, margin=ft.Margin(left=10, top=0, right=10, bottom=0)
        )
        self.threshold_row.controls = [
            ft.Text(value="最大值："),
            ft.TextField(
                width=100,
                value=str(state.max_threshold),
                on_blur=self.on_threshold_blur,
                data="max_threshold",
            ),
            ft.Text(value="最小值："),
            ft.TextField(
                width=100,
                value=str(state.min_threshold),
                on_blur=self.on_threshold_blur,
                data="min_threshold",
            ),
        ]

        # ==============启停按钮========================#
        self.btn_status = ft.Row(wrap=True)

        # 主控件
        self.controls = [
            self.status_text,
            ft.Text("渔具键位:"),
            ft.Column(controls=[self.keyword_row]),
            ft.Text("弧度阈值:"),
            self.threshold_row,
            self.btn_status,
        ]

    # ================= 状态与 UI 同步 =================
    def sync_status_ui(self):
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

    # ================= 生命周期 =================
    def did_mount(self):
        self.refresh_tags()
        self.sync_status_ui()  # ✅ 挂载时立即同步一次状态
        # self._poll_task = asyncio.create_task(self._poll_queue())

    # ================= 标签管理 =================
    def refresh_tags(self):
        chips = [
            ft.Chip(label=ft.Text(t), on_delete=lambda e, v=t: self.remove_tag(v))
            for t in self.tags
        ]
        self.keyword_row.controls = [
            self.keyword_input,
            ft.Button("添加", on_click=self.on_add),
            *chips,
        ]
        self.update()

    # 添加标签
    def on_add(self, e):
        value = self.keyword_input.value.strip()
        if value and value not in self.state.tags:
            self.tags.append(value)
            self.state.tags = self.tags
            self.keyword_input.value = ""
            self.refresh_tags()

    # 删除标签
    def remove_tag(self, value):
        if value in self.state.tags:
            self.tags.remove(value)
            self.state.tags = self.tags
            self.refresh_tags()

    # =============阈值输入管理=============
    def on_threshold_blur(self, e):
        ctrl = e.control
        field_key = ctrl.data  # 拿到标记的字段名：min_threshold / max_threshold
        raw_val = ctrl.value.strip()

        try:
            num = float(raw_val)
            num = round(num, 2)
            # 可选：数值区间限制，根据key区分规则
            if num < 0:
                raise ValueError("不能为负数")
            elif num >= 10:
                raise ValueError("不能大于9")
            # 动态赋值到state对应字段
            setattr(self.state, field_key, num)
            ctrl.value = str(num)
        except (ValueError, TypeError):
            # 非法输入，恢复原有正确数值
            original_val = getattr(self.state, field_key)
            ctrl.value = str(original_val)

        self.update()

    # ==============启停=====================
    def on_start(self, e):
        self.fishing_bot.request_start()
        self.sync_status_ui()

    def on_stop(self):
        self.fishing_bot.request_stop()  # ✅ 通知后台线程安全退出
        self.log_box.add_log("停止钓鱼")
        self.sync_status_ui()
        self.state.hwnd = 0

    # async def _poll_queue(self):
    #     while True:
    #         try:
    #             msg = self.msg_queue.get_nowait()
    #             if isinstance(msg, dict):
    #                 event_type = msg.get("type", "unknown")
    #                 data = msg.get("data") or {}  # ⭐ 确保 data 至少是空字典
    #                 self._handle_event(event_type, data)
    #                 self.page.update()
    #                 # self._handle_event(msg["type"], msg.get("data"))
    #             # 处理消息并更新UI
    #             self.page.update()
    #         except queue.Empty:
    #             pass
    #         await asyncio.sleep(0.1)

    # def _handle_event(self, event_type: str, data: dict):
    #     """集中处理所有来自Bot的状态变更"""
    #     if event_type == "fish_caught":
    #         count = data.get("count", 0)
    #         self.log_box.add_log(f"捕获 {count} 条鱼")
    #         pass  # 更新UI
    #     elif event_type == "is_focus":
    #         msg = data.get("msg", "")
    #         self.log_box.add_log(msg)
    #     elif event_type == "ocr_init":
    #         msg = data.get("msg", "")
    #         self.log_box.add_log(msg)
    #     elif event_type == "stop":
    #         msg = data.get("msg", "")
    #         self.log_box.add_log(msg)
    #         self.sync_status_ui()
    #     elif event_type == "fish_sucess":
    #         count = data.get("count", 0)
    #         self.log_box.add_log(f"电鳗{count}条")
    #         self.sync_status_ui()
    #     elif event_type == "state":
    #         msg = data.get("msg", "")
    #         self.log_box.add_log(msg)
    #         self.sync_status_ui()
    #     elif event_type == "error":
    #         # error 事件不需要 count
    #         self.log_box.add_log(f"错误: {data.get('message', '未知错误')}")
    #     else:
    #         print(f"[WARN] 未处理的事件类型: {event_type}, data={data}")

    def will_unmount(self):
        if self._poll_task and not self._poll_task.done():
            self._poll_task.cancel()


fish_view = Fish_View()
