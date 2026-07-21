import ctypes
import time

import cv2
import numpy as np
import pydirectinput

from utils.consts import app_global
from utils.screenshot import screen_screenshot

# 修复Windows高DPI坐标偏移，必须放在最顶部
ctypes.windll.shcore.SetProcessDpiAwareness(2)

# 全局间隔
pydirectinput.PAUSE = 0.06
pydirectinput.FAILSAFE = False


# ==================== 鼠标 ====================
def abs_click_enter(duration=0.05):
    pydirectinput.mouseDown()
    time.sleep(duration)
    pydirectinput.mouseUp()


def abs_click(screen_x: int, screen_y: int, duration=0.08):
    """绝对坐标左键点击（交互、拾取、打开界面）"""
    pydirectinput.moveTo(screen_x, screen_y, duration=duration)
    pydirectinput.click()
    # print(f"点击 {screen_x},{screen_y}")


def rel_mouse(dx: int, dy: int, duration=0.05):
    """【第三人称视角旋转专用】相对移动，左右/上下转镜头
    dx>0=右转；dx<0=左转；dy>0=低头；dy<0=抬头
    """
    pydirectinput.moveRel(dx, dy, relative=True, duration=duration)
    # print(f"视角偏移 dx:{dx} dy:{dy}")


def mouse_down() -> None:
    """鼠标按下"""
    pydirectinput.mouseDown()


def mouse_up() -> None:
    """鼠标松开"""
    pydirectinput.mouseUp()


# ==================== 键盘 ====================
def press_key(key: str, hold=0.05):
    """单次按键：w/a/s/d/space/e/1/2/esc"""
    pydirectinput.keyDown(key)
    time.sleep(hold)
    pydirectinput.keyUp(key)


def many_key(keys: list[str], interval: float = 0.05):
    """长按按键（跑步、瞄准）"""
    pydirectinput.press(keys, presses=1, interval=interval)


def hold_key(key, seconds, stop_check=None):

    pydirectinput.keyDown(key)

    start = time.time()

    try:
        while time.time() - start < seconds:
            if stop_check and not stop_check():
                return

            time.sleep(0.05)

    finally:
        pydirectinput.keyUp(key)


def aim_to_light():
    """瞄准光束以获得奖励坐标"""
    SCREEN_CENTER_X = 1920 // 2
    LOWER_BLUE = np.array([90, 150, 180])
    UPPER_BLUE = np.array([130, 255, 255])
    # 精准吸附参数
    SMOOTH_STEPS = 6
    SENS = 1.2
    LOCK_THRESHOLD = 30
    MIN_LIGHT_AREA = 300  # 过滤噪点：只有蓝色区域大于300像素才判定为光束

    # 全局搜索参数
    SEARCH_STEP = 8
    SEARCH_DELAY = 0.03
    search_dir = -1

    while True:
        if app_global.is_stopped():
            # print("停止")
            return
        if app_global.is_paused():
            # print("暂停")
            app_global.wait_if_paused()
            continue
        img = screen_screenshot()
        frame = np.array(img)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        mask = cv2.inRange(hsv, LOWER_BLUE, UPPER_BLUE)
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 筛选真正的光束轮廓，过滤小噪点
        valid_contours = [
            cnt for cnt in contours if cv2.contourArea(cnt) > MIN_LIGHT_AREA
        ]
        # print(f"有效光束数量：{len(valid_contours)}")
        # 情况1：画面里没有有效光束 → 执行搜索旋转
        if len(valid_contours) == 0:
            pydirectinput.moveRel(SEARCH_STEP * 420 * search_dir, 0, relative=True)
            time.sleep(SEARCH_DELAY)
            continue

        # 情况2：已经看到光束，停止搜索旋转，进入精准对齐
        max_contour = max(valid_contours, key=cv2.contourArea)
        M = cv2.moments(max_contour)
        if M["m00"] != 0:
            target_x = int(M["m10"] / M["m00"])
            dx = target_x - SCREEN_CENTER_X

            # 横向误差达标，直接结束全部循环
            if abs(dx) < LOCK_THRESHOLD:
                return

            step_x = (dx * SENS) / SMOOTH_STEPS
            aim_finish = False
            for _ in range(SMOOTH_STEPS):
                if app_global.is_stopped():
                    # print("停止")
                    return
                if app_global.is_paused():
                    # print("暂停")
                    app_global.wait_if_paused()
                    continue
                pydirectinput.moveRel(int(step_x), 0, relative=True)
                time.sleep(0.001)
                new_dx = target_x - SCREEN_CENTER_X
                if abs(new_dx) < LOCK_THRESHOLD:
                    aim_finish = True
                    break
            if aim_finish:
                return
