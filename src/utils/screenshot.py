import sys
import threading
import time
import tkinter as tk
from tkinter import messagebox

import cv2
import mss
import mss.tools
import numpy as np

from config import SCREEN_RETRY_COUNT, SCREEN_RETRY_DELAY

_MSS = None
_MSS_LOCK = threading.Lock()
_MSS_BROKEN = True


def get_mss_instance():
    """线程安全获取mss，损坏自动重建"""
    global _MSS, _MSS_BROKEN
    with _MSS_LOCK:
        if _MSS_BROKEN or _MSS is None:
            old_mss = _MSS
            _MSS = None
            try:
                _MSS = mss.mss()
                _MSS_BROKEN = False
            except Exception as err:
                print(f"创建mss实例失败：{str(err)}")
                _MSS_BROKEN = True
                _MSS = old_mss
                time.sleep(0.1)
            if old_mss is not None and old_mss is not _MSS:
                try:
                    old_mss.close()
                except Exception:
                    pass
        return _MSS


def screen_screenshot(area=None) -> mss.ScreenShot | None:
    global _MSS_BROKEN
    for i in range(SCREEN_RETRY_COUNT):
        try:
            sct = get_mss_instance()
            if sct is None:
                continue
            capture_area = area if area else sct.monitors[1]
            img: mss.ScreenShot = sct.grab(capture_area)
            # 校验截图有效，空画面标记损坏
            if img.pixels is None or img.size[0] <= 1 or img.size[1] <= 1:
                raise Exception("捕获画面为空")
            assert img is not None
            return img
        except Exception as err:
            print(f"第{i + 1}次截图失败：{str(err)}")
            # 标记捕获器损坏，下一次强制重建
            _MSS_BROKEN = True
            time.sleep(SCREEN_RETRY_DELAY)

    # 重试全部失败弹窗退出
    def show_error_and_exit():
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "截图多次失败",
            f"已重试{SCREEN_RETRY_COUNT}次，截图始终失败！\n原因：无法抓取画面",
        )
        root.destroy()
        sys.exit(1)

    show_error_and_exit()


def show_screenshot(img):
    frame = np.array(img)  # 格式 BGRA
    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

    cv2.imshow("截图预览", frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def save_mss_image(img: mss.ScreenShot, save_path: str) -> None:
    # 注意：是 mss.tools，不是 img.tools
    mss.tools.to_png(img.rgb, img.size, output=save_path)


def cut_image(img, i=1):
    img = cv2.imread(img)
    if img is None:
        raise FileNotFoundError("无法读取图片，请检查路径是否正确")
    # 定义裁剪区域 (注意顺序是 Y轴在前，X轴在后)

    if i == 1:
        # 890 1030 375 423
        x, y, w, h = 890, 375, 140, 48
        cropped_img = img[y : y + h, x : x + w]
        cv2.imwrite("away.jpg", cropped_img)
    elif i == 2:
        # 1011 1066 441 473 55 32
        x, y, w, h = 1011, 441, 55, 32
        # 使用 NumPy 切片截取 ⚠️ 关键：格式为 [y:y+h, x:x+w]
        cropped_img = img[y : y + h, x : x + w]
        cv2.imwrite("result.jpg", cropped_img)


# heading=0 正北，90正东，180正南，270正西
# 示例：你截图箭头≈285°（西北偏西）
