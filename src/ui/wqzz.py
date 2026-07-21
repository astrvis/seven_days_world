import flet as ft

from tasks.wqzz_task import wqzz_bot
from ui.log_box import log_box
from utils.consts import app_global
from utils.store import state


class WQZZ(ft.Column):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._event_global = app_global

        self.wqzz_bot = wqzz_bot
        self.state = state
        self.food_tags: list[str] = self.state.food_tags
        self.status_text = ft.Text("🔴 未启动")
        self.type_input = ft.Column(
            controls=[
                ft.Text("关卡类型:"),
                ft.Dropdown(
                    width=200,
                    value=str(self.state.wqzz_type),
                    on_select=self._on_select_event,  # type: ignore
                    options=[
                        ft.DropdownOption(key="1", text="困难"),
                        ft.DropdownOption(key="2", text="大师"),
                    ],
                ),
            ]
        )
        self.items = [
            ft.Text("次数:"),
            ft.TextField(
                width=130,
                hint_text="刷取次数:",
                keyboard_type=ft.KeyboardType.NUMBER,  # 移动端弹出数字键盘
                input_filter=ft.NumbersOnlyInputFilter(),  # 阻止非数字字符输入
                value=str(self.state.wwzz_count),
                on_blur=lambda e: self.on_blur_handel(e, "wwzz_count"),
            ),
        ]
        self.count_input = ft.Column(controls=list(self.items))

        self.wx_input_row = ft.Row(
            controls=[
                ft.TextField(
                    width=130,
                    label="万能手键位",
                    value=self.state.wx_key,
                    on_blur=lambda e: self.on_blur_handel(e, "wx_key"),
                ),
                ft.TextField(
                    width=130,
                    label="间隔局数",
                    value=str(self.state.wx_number),
                    keyboard_type=ft.KeyboardType.NUMBER,  # 移动端弹出数字键盘
                    input_filter=ft.NumbersOnlyInputFilter(),  # 阻止非数字字符输入
                    on_blur=lambda e: self.on_blur_handel(e, "wx_number"),
                ),
                ft.Switch(
                    value=self.state.is_wx,
                    on_change=lambda e: self.on_change_handel(e, "is_wx"),
                ),
            ]
        )
        self.wx_input = ft.Column(
            controls=[ft.Text("自动使用万能手:"), self.wx_input_row]
        )

        # ====自动食用食物====#

        self.keyword_row = ft.Row(wrap=True)
        self.foods_input_row = ft.Row(
            controls=[
                ft.TextField(
                    width=130,
                    label="间隔时间",
                    value=str(self.state.food_interval),
                    keyboard_type=ft.KeyboardType.NUMBER,  # 移动端弹出数字键盘
                    input_filter=ft.NumbersOnlyInputFilter(),  # 阻止非数字字符输入
                    on_blur=lambda e: self.on_blur_handel(e, "food_interval"),
                ),
                self.keyword_row,
                ft.Switch(
                    value=self.state.is_food,
                    on_change=lambda e: self.on_change_handel(e, "is_food"),
                ),
            ]
        )

        # 键位行的输入框
        self.keyword_input = ft.TextField(
            hint_text="食物键位",
            width=130,
            # on_submit=self.on_add,
            margin=ft.Margin(left=10, top=0, right=10, bottom=0),
        )
        self.foods_input = ft.Column(
            controls=[
                ft.Text("自动使用食物:"),
                self.foods_input_row,
            ]
        )
        self.btn_status = ft.Row()
        self.log_box = log_box
        self.controls = [
            self.status_text,
            self.type_input,
            self.count_input,
            self.wx_input,
            self.foods_input,
            self.btn_status,
            # self.text,
        ]
        # ================= 状态与 UI 同步 =================

    def sync_status_ui(self) -> None:
        """✅ 统一的状态刷新方法（必须在主线程调用）"""
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
    def did_mount(self) -> None:
        self.sync_status_ui()  # ✅ 挂载时立即同步一次状态
        self.refresh_tags()

    # ==============启停=====================

    def on_start(self) -> None:
        if not self.wqzz_bot.ocr.loaded:
            self.log_box.add_log("OCR模型未加载完成，请稍后")
            return
        self.wqzz_bot.on_start()
        self.sync_status_ui()

    def on_stop(self) -> None:
        self.wqzz_bot.on_stop()
        self.sync_status_ui()

    def on_blur_event(self, e: ft.Event[ft.TextField]) -> None:
        tf: ft.TextField = e.control
        if not tf.value:
            return
        self.state.wwzz_count = int(tf.value)
        self.sync_status_ui()

    # ================= 标签管理 =================
    def refresh_tags(self):
        chips = [
            ft.Chip(label=ft.Text(t), on_delete=lambda e, v=t: self.remove_tag(v))
            for t in self.food_tags
        ]

        self.keyword_row.controls = [
            self.keyword_input,
            ft.Button("添加", on_click=self.on_add),
            *chips,
        ]
        self.update()

    # 删除标签
    def remove_tag(self, value):
        if value in self.food_tags:
            self.food_tags.remove(value)
            self.state.food_tags = self.food_tags
            self.refresh_tags()

    def on_add(self, e) -> None:
        value = self.keyword_input.value.strip()
        if value and value not in self.food_tags:
            self.food_tags.append(value)
            self.state.food_tags = self.food_tags
            self.keyword_input.value = ""
            self.refresh_tags()

    def on_blur_handel(self, e: ft.Event[ft.TextField], data: str) -> None:
        tf: ft.TextField = e.control
        if not tf.value and not data:
            return

        item = hasattr(self.state, data)
        if item:
            if data in ("wwzz_count", "wx_number", "food_interval"):
                v = tf.value.lstrip("0") or "0"
                v = int(v)
            else:
                v = tf.value
        tf.value = str(v)
        setattr(self.state, data, v)
        tf.update()

    def on_change_handel(self, e: ft.Event[ft.Switch], data: str) -> None:
        tf: ft.Switch = e.control
        if not tf.value and not data:
            return
        setattr(self.state, data, tf.value)
        tf.update()

    def _on_select_event(self, e: ft.Event[ft.Dropdown]) -> None:
        dd: ft.Dropdown = e.control
        if not dd.value:
            return
        v = int(dd.value)
        self.state.wqzz_type = v
        dd.update()


wqzz = WQZZ()
