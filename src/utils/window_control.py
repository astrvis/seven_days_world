import time

import pygetwindow as gw
import win32api
import win32com.client
import win32con
import win32gui


def focus_game_window(keyword: str) -> int | None:
    """聚焦游戏窗口"""

    target_win = None

    for win in gw.getAllWindows():
        if keyword in win.title:
            target_win = win
            break

    if target_win is None:
        print("未找到窗口")
        return

    hwnd = target_win._hWnd

    try:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

        # 强制置顶
        win32gui.SetWindowPos(
            hwnd,
            win32con.HWND_TOPMOST,
            0,
            0,
            0,
            0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE,
        )

        time.sleep(0.1)

        win32gui.SetWindowPos(
            hwnd,
            win32con.HWND_NOTOPMOST,
            0,
            0,
            0,
            0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE,
        )
        shell = win32com.client.Dispatch("WScript.Shell")
        shell.SendKeys("%")

        time.sleep(0.1)

        win32gui.SetForegroundWindow(hwnd)

        print("✅ 已聚焦窗口:", target_win.title)
        return hwnd

    except Exception as e:
        print("❌ 聚焦窗口失败:", e)


def can_run(hwnd):
    """判断是否聚焦于游戏窗口且鼠标在窗口内"""
    if win32gui.GetForegroundWindow() != hwnd:
        return False

    # 鼠标必须在窗口内
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    x, y = win32api.GetCursorPos()

    return left <= x <= right and top <= y <= bottom
