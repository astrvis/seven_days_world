import threading
import time

from config import BADGE_DATA_AREA
from ui.log_box import log_box
from utils.consts import app_global
from utils.fun import focus_monitor
from utils.mouse_operate import abs_click, press_key
from utils.rapid_ocr import ocr
from utils.screenshot import screen_screenshot
from utils.setting import cfg
from utils.store import state
from utils.window_control import focus_game_window


class BadgeBot:
    def __init__(self) -> None:
        super().__init__()
        self.ocr = ocr
        self.event_global = app_global
        self.log_box = log_box
        self.state = state
        self.count = 0
        self.start_before = False
        self.start_after = False
        self._thread = threading.Thread(target=self.run_badge_loop, daemon=True)
        self._thread_focus_monitor = threading.Thread(target=focus_monitor, daemon=True)

    def run_badge_loop(self):
        while True:
            if self.event_global.is_stopped():
                # print("停止")
                return
            if self.event_global.is_paused():
                # print("暂停")
                self.event_global.wait_if_paused()
                continue
            self.single_badge_task()
            time.sleep(0.2)

    def single_badge_task(self):
        # ===开始检测====#
        if not self.start_before:
            start_image = screen_screenshot(BADGE_DATA_AREA["START"])
            if start_image is None:
                return

            start_exist, s_xy = self.ocr.recognize_image(
                start_image, BADGE_DATA_AREA["RESULT_NAME"], BADGE_DATA_AREA["START"]
            )

            if start_exist:
                time.sleep(0.5)
                press_key("f")
                time.sleep(0.5)

        # === 选项检测====#
        if not self.start_after:
            for i in range(BADGE_DATA_AREA["PAGE"]):
                if self.event_global.is_stopped():
                    # print("停止")
                    return
                if self.event_global.is_paused():
                    # print("暂停")
                    self.event_global.wait_if_paused()
                    continue
                image = screen_screenshot(BADGE_DATA_AREA["LIST"])
                if image is None:
                    return
                list_isexis, list_xy = self.ocr.recognize_image(
                    image, BADGE_DATA_AREA["ORDINARY_NAME"], BADGE_DATA_AREA["LIST"]
                )
                if list_isexis:
                    assert list_xy is not None
                    self.start_after = True
                    self.start_before = True
                    time.sleep(0.2)
                    abs_click(list_xy.x, list_xy.y)
                    break
                else:
                    time.sleep(0.2)
                    press_key("down")
                    time.sleep(0.2)
                    press_key("down")

        # ===完成检测===#
        # ===获得物品====#
        success_item_img = screen_screenshot(BADGE_DATA_AREA["SUCCESS_ITEM"])
        if success_item_img is None:
            return
        success_item_exist, success_item_xy = self.ocr.recognize_image(
            success_item_img,
            BADGE_DATA_AREA["SUCCESS_ITEM_NAME"],
            BADGE_DATA_AREA["SUCCESS_ITEM"],
        )

        if success_item_exist:
            press_key("esc")
            time.sleep(0.5)

        # ===提示物品重复===#

        success_tips_img = screen_screenshot(BADGE_DATA_AREA["SUCCESS_TIPS"])
        if success_tips_img is None:
            return
        success_tips_exist, success_tips_xy = self.ocr.recognize_image(
            success_tips_img,
            BADGE_DATA_AREA["SUCCESS_TIPS_NAME"],
            BADGE_DATA_AREA["SUCCESS_TIPS"],
        )

        if success_tips_exist:
            press_key("f")
            time.sleep(0.5)

        # ===完成确认===#
        success_img = screen_screenshot(BADGE_DATA_AREA["SUCCESS"])
        if success_img is None:
            return
        success_exist, success_xy = self.ocr.recognize_image(
            success_img, BADGE_DATA_AREA["SUCCESS_NAME"], BADGE_DATA_AREA["SUCCESS"]
        )

        if success_exist:
            press_key("f")
            self.start_before = False
            self.start_after = False
            self.count += 1
            self.log_box.add_log(f"已刷取{self.count}次")
            badge_count = self.state.badge_count
            if badge_count > 0 and self.count >= badge_count:
                self.on_stop()
                msg = f"已完成{badge_count}次刷取任务"
                app_global.msg_queue.put({"type": "badge_stop", "data": {"msg": msg}})

            time.sleep(0.5)

    def on_start(self):
        if not self.ocr.loaded:
            self.log_box.add_log("OCR模型未加载完成，请稍后")
            return

        hwnd = focus_game_window(cfg["GAME_WINDOW_KEY"])
        if hwnd:
            self.state.hwnd = hwnd
            self.init_status()
            # threading.Thread(target=self.run_badge_loop, daemon=True).start()
            self.event_global.set_running()

            if (
                not hasattr(self, "_thread")
                or self._thread is None
                or not self._thread.is_alive()
            ):
                self._thread = threading.Thread(target=self.run_badge_loop, daemon=True)
                self._thread.start()

            if (
                not hasattr(self, "_thread_focus_monitor")
                or self._thread_focus_monitor is None
                or not self._thread_focus_monitor.is_alive()
            ):
                self._thread_focus_monitor = threading.Thread(
                    target=focus_monitor, daemon=True
                )
                self._thread_focus_monitor.start()

        else:
            self.log_box.add_log("未找到游戏窗口，请检查窗口关键字配置")
            self.on_stop()

    def on_stop(self):
        self.event_global.set_stopped()
        self.init_status()
        thread = getattr(self, "_thread", None)
        thread2 = getattr(self, "_thread_focus_monitor", None)
        if thread2 is not None and thread2.is_alive():
            try:
                thread2.join(timeout=2)
            except RuntimeError as e:
                # 兜底捕获极端并发情况下的 "cannot join thread before it is started"
                print(f"[Warning] Join skipped due to race condition: {e}")

        if thread is not None and thread.is_alive():
            try:
                thread.join(timeout=2)
            except RuntimeError as e:
                # 兜底捕获极端并发情况下的 "cannot join thread before it is started"
                print(f"[Warning] Join skipped due to race condition: {e}")

    def init_status(self):
        self.count = 0
        self.start_before = False
        self.start_after = False
