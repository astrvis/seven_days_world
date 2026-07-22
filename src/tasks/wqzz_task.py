import threading
import time

from config import WQZZ_DATA
from ui.log_box import log_box
from utils.consts import app_global
from utils.fun import focus_monitor
from utils.mouse_operate import (
    abs_click,
    aim_to_light,
    mouse_down,
    mouse_up,
    press_key,
    rel_mouse,
)
from utils.rapid_ocr import ocr
from utils.screenshot import screen_screenshot
from utils.setting import cfg
from utils.store import state
from utils.window_control import focus_game_window


class WQZZ_Bot:
    def __init__(self):
        self.ocr = ocr
        """ocr识别库"""
        self.state = state
        """全局状态"""
        self.log_box = log_box
        """日志框"""
        self.event_global = app_global
        """全局事件"""
        self.is_init_scene = True
        """是否初始化场景"""
        self.is_boos_scene = False
        """是否boss场景"""
        self.is_kill_boos = False
        """是否杀死boss"""
        self.is_reward = False
        """是否领取奖励"""
        self.is_pressing_reel = False
        """是否按下左键"""
        self.is_fire = False
        """是否开枪"""
        self.init_offsetX = 260
        """初始视角X偏移量"""
        self.count = 0
        """当前局数"""
        self.msg_queue = app_global.msg_queue
        """消息队列"""
        self._thread_focus_monitor = threading.Thread(target=focus_monitor, daemon=True)
        """关注窗口线程监控"""
        self.start_interval: float = time.time()
        """开始时间间隔"""
        self.wx_count = 0
        """万能手次数"""
        self.loop_time = 20

    def init_status(self) -> None:
        """初始化状态"""
        self.is_init_scene = True
        self.is_boos_scene = False
        self.is_kill_boos = False
        self.is_reward = False
        self.is_pressing_reel = False
        self.is_fire = False

    def run_wqzz_loop(self):
        """运行主循环"""

        while True:
            if self.event_global.is_stopped():
                # print("停止")
                return
            if self.event_global.is_paused():
                # print("暂停")
                self.event_global.wait_if_paused()
                continue
            #
            self.single_wqzz_task()
            time.sleep(0.2)

    def single_wqzz_task(self):
        """运行单任务循环"""
        self.start_task()
        self.init_scene_task()
        self.boss_scene_task()
        self.kill_boss_task()
        self.reward_task()
        self.success_task()

    def start_task(self) -> None:
        """开始任务"""
        start_img = screen_screenshot(WQZZ_DATA["NOT_START"])
        if start_img is None:
            return
        start_exist, xy = self.ocr.recognize_image(
            start_img, WQZZ_DATA["NOT_START_NAME"], WQZZ_DATA["NOT_START"]
        )
        if start_exist:
            self.init_status()
            press_key("f")
            time.sleep(0.5)
            [press_key("d") for _ in range(self.state.wqzz_type)]
            time.sleep(0.5)
            press_key("f")
            return

    def buff_task(self) -> None:
        """使用万能手任务"""
        if self.state.is_wx:
            if self.wx_count >= self.state.wx_number and self.wx_count > 0:
                self.log_box.add_log("使用万能手")
                time.sleep(0.5)
                press_key(str(self.state.wx_key))
                time.sleep(0.5)
                self.wx_count = 0
        """食用食物"""
        if self.state.is_food:
            t = time.time()
            if t - self.start_interval >= self.state.food_interval:
                print("食用食物")
                self.start_interval = t
                for tag in self.state.food_tags:
                    if self.event_global.is_stopped():
                        # print("停止")
                        return
                    if self.event_global.is_paused():
                        # print("暂停")
                        self.event_global.wait_if_paused()
                        continue
                    t2 = self.event_global.sleep(1)
                    if t2 == "paused":
                        self.event_global.wait_if_paused()
                        return
                    elif t2 == "stop":
                        return
                    press_key(str(tag))
                    t2 = self.event_global.sleep(3)
                    if t2 == "paused":
                        self.event_global.wait_if_paused()
                        return
                    elif t2 == "stop":
                        return

    def init_scene_task(self) -> None:
        """初始化场景任务"""
        if self.is_init_scene:
            # 检查是否进入场景
            # print("初始化场景")
            scene_img = screen_screenshot(WQZZ_DATA["BOOS"])
            if scene_img is None:
                return
            scene_exist, xy = self.ocr.recognize_image(
                scene_img, WQZZ_DATA["SCENE_NAME"], WQZZ_DATA["BOOS"]
            )
            if scene_exist:
                # self.is_start = True
                self.buff_task()
                time.sleep(1)
                rel_mouse(250, 0)
                time.sleep(0.2)
                press_key("w", 3)
                s = time.time()
                while self.is_init_scene:
                    if self.event_global.is_stopped():
                        return
                    if self.event_global.is_paused():
                        self.event_global.wait_if_paused()
                        continue
                    t = time.time()
                    if t - s >= self.loop_time:
                        self.esc_exit()
                        # self.is_start = False
                        return

                    skip_img = screen_screenshot(WQZZ_DATA["SKIP"])
                    if skip_img is None:
                        continue
                    exist_skip, xy = self.ocr.recognize_image(
                        skip_img, WQZZ_DATA["SKIP_NAME"], WQZZ_DATA["SKIP"]
                    )
                    if exist_skip:
                        press_key("space", 2)
                        break
                    press_key("space")
                self.init_status()
                self.is_init_scene = False
                self.is_boos_scene = True

    def boss_scene_task(self) -> None:
        """boss场景任务"""
        if self.is_boos_scene:
            print("boss场景")

            # 检查是否进入boss场景
            boos_scene_img = screen_screenshot(WQZZ_DATA["BOOS"])
            if boos_scene_img is None:
                return
            scene_exist, xy = self.ocr.recognize_image(
                boos_scene_img, WQZZ_DATA["SCENE_NAME"], WQZZ_DATA["BOOS"]
            )
            if scene_exist:
                print("已进入boss场景")
                self.reel_mouse_down()
                time.sleep(0.3)
                self.reel_mouse_up()

                press_key("x")
                time.sleep(1)
                press_key("x")
                time.sleep(0.3)

                self.reel_mouse_down()
                thread1 = threading.Thread(target=self.recoil, daemon=True)
                thread1.start()
                press_key("e")
                self.is_fire = True
                self.is_boos_scene = False

    def kill_boss_task(self) -> None:
        """击杀boss"""
        if self.is_fire:
            # print("击杀boss")
            boos_img = screen_screenshot(WQZZ_DATA["BOOS"])
            if boos_img is None:
                return
            kill_boos, xy = self.ocr.recognize_image(
                boos_img, WQZZ_DATA["BOOS_NAME"], WQZZ_DATA["BOOS"]
            )
            # boss 死亡
            if kill_boos:
                self.reel_mouse_up()

                self.is_fire = False
                self.is_reward = True
                press_key("r")

    def reward_task(self) -> None:
        """领取奖励"""
        if self.is_reward:
            press_key("s", 0.3)
            aim_to_light()
            s = time.time()
            while self.is_reward:
                if self.event_global.is_stopped():
                    # print("停止")
                    return
                if self.event_global.is_paused():
                    # print("暂停")
                    self.event_global.wait_if_paused()
                    continue
                t = time.time()
                if t - s >= self.loop_time:
                    self.esc_exit()
                    return
                time.sleep(0.1)
                press_key("w", 0.5)
                xz_img = screen_screenshot(WQZZ_DATA["XIANGZI"])
                if xz_img is None:
                    continue
                xz_exits, r = self.ocr.recognize_image(
                    xz_img, WQZZ_DATA["XIANGZI_NAME"], WQZZ_DATA["XIANGZI"]
                )
                if xz_exits:
                    press_key("f")
                    time.sleep(0.2)
                    press_key("f")
                    time.sleep(0.2)

                    self.is_reward = False
                    self.esc_exit()

    def success_task(self) -> None:
        """再次挑战"""
        success_img = screen_screenshot(WQZZ_DATA["SUCCESS"])
        if success_img is None:
            return
        success_exits, r = self.ocr.recognize_image(
            success_img, WQZZ_DATA["SUCCESS_NAME"], WQZZ_DATA["SUCCESS"]
        )
        if success_exits:
            time.sleep(0.2)

            self.init_status()
            count = self.state.wwzz_count
            self.count += 1
            self.wx_count += 1
            self.log_box.add_log(f"已刷取{self.count}次")
            if count > 0 and self.count >= count:
                self.on_stop()
                self.msg_queue.put(
                    {
                        "type": "wqzz_stop",
                        "data": {"msg": f"已完成{count}次刷取任务"},
                    }
                )
                return
            press_key("y")

    def recoil(self) -> None:
        """压枪"""
        POWER = 50
        INTERVAL = 1
        while self.is_pressing_reel:
            if self.event_global.is_stopped():
                return
            if self.event_global.is_paused():
                self.event_global.wait_if_paused()
                continue
            rel_mouse(0, POWER)
            time.sleep(INTERVAL)

    def on_start(self) -> None:
        self.init_status()
        self.start_init_status()
        self.event_global.set_running()
        hwnd = focus_game_window(cfg["GAME_WINDOW_KEY"])
        if hwnd:
            self.state.hwnd = hwnd

            threading.Thread(target=self.run_wqzz_loop, daemon=True).start()
            if (
                not hasattr(self, "_thread_focus_monitor")
                or self._thread_focus_monitor is None
                or not self._thread_focus_monitor.is_alive()
            ):
                self._thread_focus_monitor = threading.Thread(
                    target=focus_monitor, daemon=True
                )
                self._thread_focus_monitor.start()
            # self.is_fire = True
        else:
            self.log_box.add_log("未找到游戏窗口，请检查窗口关键字配置")
            self.on_stop()

    def on_stop(self) -> None:
        self.event_global.set_stopped()
        self.init_status()
        self.start_init_status()
        # self.is_start = False
        # self.is_fire = False

    def start_init_status(self) -> None:
        self.count = 0
        self.wx_count = 0
        self.start_interval = time.time()

    def reel_mouse_down(self) -> None:
        if not self.is_pressing_reel:
            mouse_down()
            self.is_pressing_reel = True
            # print("【按下左键收线】")

    def reel_mouse_up(self) -> None:
        if self.is_pressing_reel:
            mouse_up()
            self.is_pressing_reel = False
            # print("【松开左键防断线】")

    def esc_exit(self) -> None:
        total = 20
        for i in range(total):
            if self.event_global.is_stopped():
                return
            if self.event_global.is_paused():
                self.event_global.wait_if_paused()
                continue

            press_key("esc")
            time.sleep(0.3)
            esc_img = screen_screenshot(WQZZ_DATA["ESC"])
            if esc_img is None:
                continue
            esc_exits, r = self.ocr.recognize_image(
                esc_img, WQZZ_DATA["ESC_NAME"], WQZZ_DATA["ESC"]
            )
            if esc_exits:
                # x, y = WQZZ_DATA["EXIT_XY"]
                # abs_click(x, y)
                self.init_status()
                abs_click(r.x, r.y)
                time.sleep(0.3)
                press_key("f")
                break

            if i == total - 1:
                self.on_stop()
                self.event_global.msg_queue.put(
                    {
                        "type": "wqzz_stop",
                        "data": {"msg": "页面出错,退出关卡失败"},
                    }
                )


wqzz_bot = WQZZ_Bot()
