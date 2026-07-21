import queue
import threading
from enum import Enum, auto
from typing import Literal


class WorkerState(Enum):
    RUNNING = auto()
    PAUSED = auto()
    STOPPED = auto()


# 全局状态管理器：唯一实例，封装修改状态的方法
class AppGlobal:
    def __init__(self):
        # 私有变量，外部禁止直接读写
        self._worker_state: WorkerState = WorkerState.STOPPED
        # 线程锁，防止多线程（你的钓鱼bot+UI）并发修改冲突
        self._lock = threading.Lock()
        self._event = threading.Event()
        self._event.set()
        self.msg_queue = queue.Queue()

    # 只读对外接口：获取当前状态
    @property
    def worker_state(self) -> WorkerState:
        with self._lock:
            return self._worker_state

    # 封装状态变更方法，所有改状态逻辑统一写这里
    def set_running(self):
        """切换为运行中"""
        with self._lock:
            if self._worker_state != WorkerState.RUNNING:
                self._event.clear()
                self._worker_state = WorkerState.RUNNING
                self._event.set()

    def set_paused(self):
        """切换为暂停"""
        with self._lock:
            if self._worker_state != WorkerState.PAUSED:
                self._event.clear()
                self._worker_state = WorkerState.PAUSED
                self._event.set()

    def set_stopped(self):
        """切换为停止"""
        with self._lock:
            if self._worker_state != WorkerState.STOPPED:
                self._event.clear()
                self._worker_state = WorkerState.STOPPED
                self._event.set()

    # 辅助判断方法，外部不用写枚举对比
    def is_running(self) -> bool:
        return self.worker_state == WorkerState.RUNNING

    def is_paused(self) -> bool:
        return self.worker_state == WorkerState.PAUSED

    def is_stopped(self) -> bool:
        return self.worker_state == WorkerState.STOPPED

    def sleep(self, seconds: float) -> Literal["stop", "paused", "running"]:
        """
        可中断睡眠，返回打断原因或自然结束状态
        - 自然等完 → RUNNING
        - 被暂停打断 → PAUSED
        - 被停止打断 → STOPPED
        """
        interrupted = self._event.wait(timeout=seconds)
        if interrupted:
            self._event.clear()
            if self._worker_state == WorkerState.STOPPED:
                return "stop"
            elif self._worker_state == WorkerState.PAUSED:
                return "paused"
            # return self._worker_state
        # return WorkerState.RUNNING
        return "running"

    def wait_if_paused(self):
        """工作线程在循环中调用此方法代替 sleep 轮询"""
        self._event.wait()


# 全局唯一单例，整个项目只实例化一次
app_global = AppGlobal()
