import threading
import time

import cv2
import numpy as np
import pythoncom
from mss.screenshot import ScreenShot

from config import FISH_DATA
from ui.log_box import log_box
from utils.consts import app_global
from utils.fun import focus_monitor
from utils.mouse_operate import (
    abs_click_enter,
    hold_key,
    mouse_down,
    mouse_up,
    press_key,
)
from utils.rapid_ocr import ocr
from utils.screenshot import screen_screenshot
from utils.setting import cfg
from utils.store import state
from utils.template_match import (
    check_a,
    check_away,
    check_d,
    check_fish_rod,
    check_fish_success,
    check_fishing_exit,
    check_fishing_rod_exit,
)
from utils.window_control import focus_game_window


class FishingBot:
    def __init__(self) -> None:
        super().__init__()
        self.state = state
        """全局状态"""
        self.is_fish = False
        """是否有鱼"""

        self.is_pressing_reel = False
        """是否按下收线左键"""
        self.msg_queue = app_global.msg_queue
        """消息队列"""
        self._thread = threading.Thread(target=self.run_fishing_loop, daemon=True)
        """鱼竿循环线程"""
        self.ocr = ocr
        """OCR识别"""
        self.event_global = app_global
        """全局事件"""
        self.log_box = log_box
        """日志框"""
        self._thread_focus_monitor = threading.Thread(target=focus_monitor, daemon=True)
        """窗口监控线程"""
        self.success_fish = {}
        """成功钓到的鱼"""

    def quick_check_fishing(self) -> np.bool_:
        """轻量检测是否处于鱼竿模式"""
        img = screen_screenshot(FISH_DATA["FISH_ROD"])
        resutl = check_fishing_rod_exit(img)
        return resutl

    def format_tag(self, tag: str) -> int | None:
        """格式化道具键位"""
        if tag in ("4", "5", "6", "7", "8", "9"):
            return int(tag) - 3
        elif tag == "0":
            return 7
        elif tag == "-":
            return 8
        else:
            return None

    def try_enter_fishing_mode(self) -> bool | None:
        """循环切换指定道具键位，尝试进入鱼竿模式"""
        keyword_fish = self.state.tags
        keyword_fish_len = len(keyword_fish)
        if keyword_fish_len == 0:
            print("请先设置鱼竿键位")
            return False
        t1 = 0
        t2 = 0
        for i, tag in enumerate(keyword_fish):
            if self.event_global.is_stopped():
                return
            if self.event_global.is_paused():
                self.event_global.wait_if_paused()
                continue

            t = self.format_tag(tag)
            if t is None:
                continue
            rl = FISH_DATA["ROD_LIST"]
            ml1, ml2 = FISH_DATA["ML1"], FISH_DATA["ML2"]
            w = rl["width"]
            if t % 2 == 0:
                t2 += ml2
            else:
                t1 += ml1

            left = rl["left"] + (t - 1) * w + t1 + t2

            rod_img_xy = {
                "left": left,
                "top": rl["top"],
                "width": w,
                "height": rl["height"],
            }

            rod_img = screen_screenshot(rod_img_xy)
            if rod_img is None:
                continue

            fish_rod = check_fish_rod(rod_img)
            if fish_rod:
                press_key(str(tag))
                t2 = self.event_global.sleep(1)
                if t2 == "paused":
                    self.event_global.wait_if_paused()
                    continue
                elif t2 == "stop":
                    return
                abs_click_enter()
                t2 = self.event_global.sleep(3)
                if t2 == "paused":
                    self.event_global.wait_if_paused()
                    continue
                elif t2 == "stop":
                    return
                return
            if i + 1 == keyword_fish_len:
                tip = (
                    f"已遍历 {str(keyword_fish)} 所有道具，无可用鱼竿！耐久耗尽或未携带"
                )
                self.msg_queue.put({"type": "fish_stop", "data": {"msg": tip}})
                # 所有鱼竿失效，弹窗退出程序
                self.request_stop()
                pythoncom.CoInitialize()
                focus_game_window("阿星的小助手")

                # self.show_msg_box(tip)
                # return

    def single_fish_task(self):
        """单次完整钓鱼业务逻辑（适配你的原有功能）"""
        # 检测是否在垂钓位置
        fish_exit_roi = FISH_DATA["EXIT_AREA"]
        # 成功钓上位置
        fish_success_roi = FISH_DATA["SUCCESS_AREA"]
        # 左右拉扯位置
        ad_roi = FISH_DATA["AD_AREA"]
        # 有没有上钩

        img_fish = screen_screenshot(fish_success_roi)
        img_fish_success = check_fish_success(img_fish, 0.5)
        # print("succss", img_fish_success)
        if img_fish_success:
            check_result_img = screen_screenshot(FISH_DATA["SCUSSS_FISH_AREA"])
            if check_result_img is None:
                return
            # self.ocr(check_result_img)
            for f_n in FISH_DATA["FISH_NAMES"]:
                is_exit, result = self.ocr.recognize_image(
                    check_result_img,
                    f_n,
                    self.ocr.XY_TYPE(**FISH_DATA["SCUSSS_FISH_AREA"]),
                )
                f_data = self.success_fish.get(f_n[0], 0)
                if is_exit:
                    self.success_fish[f_n[0]] = f_data + 1
            parts = [f"{k}:{v}条" for k, v in self.success_fish.items()]
            msg = "，".join(parts)
            self.msg_queue.put({"type": "fish_sucess", "data": {"msg": msg}})
            while img_fish_success:
                img_fish_2 = screen_screenshot(fish_success_roi)
                img_fish_success_2 = check_fish_success(img_fish_2, 0.5)
                if not img_fish_success_2:
                    break
                time.sleep(0.3)
                press_key("f")
            self.is_fish = False
            return

        fish_exit = screen_screenshot(fish_exit_roi)
        fishing_exit = check_fishing_exit(fish_exit)
        # show_screenshot(fish_exit)
        if not fishing_exit and not self.is_fish:
            # print("❌ 未在垂钓模式，鱼脱钩，重新抛竿")
            self.reel_mouse_up()
            self.is_fish = False
            abs_click_enter(1)
            t2 = self.event_global.sleep(3)
            if t2 == "paused":
                self.event_global.wait_if_paused()
                return
            elif t2 == "stop":
                return
            return
        else:
            has_fish, arc_rate = self.check_fish_has_cyan_arc()
            # print(
            #     f"光圈状态:{has_fish} 圆弧完整度:{arc_rate:.2f} 鱼上钩标记:{self.is_fish}"
            # )
            if has_fish:
                # 标记鱼咬勾
                self.is_fish = True
                self.reel_mouse_down()
                # print("🐟 鱼咬钩，开启张力控制")

            while self.is_fish:
                time.sleep(0.05)
                fish_type_img = screen_screenshot(FISH_DATA["FISH_TYPE_AREA"])
                if fish_type_img is None:
                    return
                is_exit, result = self.ocr.recognize_image(
                    fish_type_img,
                    FISH_DATA["FISH_TYPE_DATA_AREA"],
                    self.ocr.XY_TYPE(**FISH_DATA["FISH_TYPE_DATA_AREA"]),
                )
                if is_exit:
                    press_key("esc")
                    self.is_fish = False
                    break

                fish_exit_after = screen_screenshot(fish_exit_roi)
                fishing_exit_after = check_fishing_exit(fish_exit_after)
                if not fishing_exit_after:
                    #     # 检测不在垂钓了
                    self.is_fish = False
                    break
                has_fish_ed, arc_rate_ed = self.check_fish_has_cyan_arc()
                if arc_rate_ed > self.state.max_threshold:
                    self.reel_mouse_up()
                # 张力不足，长按填充光圈
                elif arc_rate_ed < self.state.min_threshold:
                    self.reel_mouse_down()
                # t = time.time()
                ad_img = screen_screenshot(ad_roi)
                press_a = check_a(ad_img, 0.9)
                press_d = check_d(ad_img, 0.9)
                if press_a or press_d:
                    # 拉扯瞬间强制松开收线左键，杜绝张力叠加冲满
                    self.reel_mouse_up()
                    if press_a:
                        # print("← 向左拉扯，按住A")
                        # hold_key("a", 2)  # 缩短阻塞时长，原2s→0.2s，减少光圈暂停时间
                        hold_key(
                            "a", 2, stop_check=lambda: self.event_global.is_running()
                        )
                    if press_d:
                        # print("→ 向右拉扯，按住D")
                        # hold_key("d", 2)
                        hold_key(
                            "d", 2, stop_check=lambda: self.event_global.is_running()
                        )

    def run_fishing_loop(self):
        """主循环：耐久耗尽自动换鱼竿，无限挂机"""

        # 先重置鼠标状态，防止卡死按住
        while True:
            if self.event_global.is_stopped():
                return
            if self.event_global.is_paused():
                self.event_global.wait_if_paused()
                continue

            if self.quick_check_fishing():
                # print("--- 鱼竿模式 ---")
                self.single_fish_task()
            else:
                # print("⚠️ 已退出垂钓，重新切换鱼竿进入")
                self.try_enter_fishing_mode()

            self.away()

    def check_fish_has_cyan_arc(self, min_area: int = 120) -> tuple[bool, float]:
        """
        识别任意残缺青色发光弧，适配圆环逐步消失动画
        :param min_area: 青色发光最小像素面积，低于该值判定无鱼
        :return: (是否检测到上钩弧, 圆弧周长占完整圆比例，无弧则返回0.0)
        """
        fish_xy = FISH_DATA["RING_AREA"]
        img: ScreenShot = screen_screenshot(fish_xy)  # type: ignore

        # 修复mss图像转OpenCV格式
        width, height = img.size
        bgra_data = np.frombuffer(img.bgra, dtype=np.uint8).reshape((height, width, 4))
        bgr = bgra_data[:, :, :3]

        hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
        lower_cyan = np.array([82, 130, 140])
        upper_cyan = np.array([108, 255, 255])
        mask = cv2.inRange(hsv, lower_cyan, upper_cyan)

        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            # 无青色轮廓，返回 False + 占比0
            return False, 0.0

        max_round_ratio = 0.0
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < min_area:
                continue

            (x, y), radius = cv2.minEnclosingCircle(cnt)
            perimeter = cv2.arcLength(cnt, False)
            if perimeter < 10:
                continue

            circle_peri = 2 * np.pi * radius
            round_ratio = perimeter / circle_peri
            # 记录当前最大圆弧占比
            if round_ratio > max_round_ratio:
                max_round_ratio = round_ratio

            # if 0.3 <= round_ratio <= 1.3:
            if round_ratio > 0:
                # print(f"检测到青色发光弧，面积:{area},圆弧占比:{round_ratio:.2f}")
                return True, round_ratio

        # 存在青色噪点，但无有效圆弧
        return False, max_round_ratio

    def reel_mouse_down(self) -> None:
        """松开收线左键"""
        if not self.is_pressing_reel:
            mouse_down()
            self.is_pressing_reel = True
            # print("【按下左键收线】")

    def reel_mouse_up(self) -> None:
        if self.is_pressing_reel:
            mouse_up()
            self.is_pressing_reel = False
            # print("【松开左键防断线】")

    def request_stop(self) -> None:
        """彻底停止（不可逆）"""
        self.event_global.set_stopped()
        self.msg_queue.put({"type": "fish_stop", "data": {"msg": "已停止钓鱼"}})
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

    def request_start(self) -> None:
        """启动"""
        self.init_status()
        if not self.ocr.loaded:
            self.log_box.add_log("等待初始化。。。")
            return
        key_fish = self.state.tags
        if len(key_fish) < 1:
            self.log_box.add_log("请先设置鱼竿键位")
            return

        self.event_global.set_running()

        hwnd = focus_game_window(cfg["GAME_WINDOW_KEY"])
        if hwnd is not None:
            self.state.hwnd = hwnd

            if (
                not hasattr(self, "_thread")
                or self._thread is None
                or not self._thread.is_alive()
            ):
                self._thread = threading.Thread(
                    target=self.run_fishing_loop, daemon=True
                )
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

            self.log_box.add_log("开始钓鱼")

        else:
            self.log_box.add_log("未找到游戏窗口，请检查窗口关键字配置")
            self.request_stop()

    def away(self):
        """检测掉线"""
        away_xy = FISH_DATA["AWAY_AREA"]
        away_img = screen_screenshot(away_xy)
        is_away = check_away(away_img)
        if is_away:
            press_key("f")

    def init_status(self) -> None:
        """初始化状态"""
        self.success_fish = {}
        self.is_fish = False
        self.is_pressing_reel = False
