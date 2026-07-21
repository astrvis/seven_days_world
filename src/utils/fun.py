import time

from utils.consts import app_global
from utils.store import state
from utils.window_control import can_run


def focus_monitor():
    """独立焦点监控循环"""
    last_state = True  # 上次焦点状态，避免重复触发
    debounce_count = 0  # 防抖计数
    DEBOUNCE_THRESHOLD = 2  # 连续 2 次检测结果一致才生效（约 1 秒）
    event_global = app_global
    while True:
        # print("focus", self._monitor_event.is_set())
        if event_global.is_running() or event_global.is_paused():
            current = can_run(state.hwnd)
            if current != last_state:
                # 状态发生变化，开始防抖计时
                debounce_count += 1
                if debounce_count >= DEBOUNCE_THRESHOLD:
                    # print(f"窗口{current}")
                    if current:
                        # self.on_resume()  # ⭐ can_run 成立 → 恢复
                        event_global.set_running()
                        event_global.msg_queue.put(
                            {"type": "is_focus", "data": {"msg": "回到游戏窗口"}}
                        )
                    else:
                        # self.on_pause()  # ⭐ can_run 不成立 → 暂停
                        event_global.set_paused()
                        event_global.msg_queue.put(
                            {"type": "is_focus", "data": {"msg": "不在游戏窗口"}}
                        )
                    last_state = current
                    debounce_count = 0
            else:
                # 状态未变化，重置防抖计数
                debounce_count = 0
            time.sleep(0.02)
