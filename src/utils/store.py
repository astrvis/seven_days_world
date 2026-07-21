from __future__ import annotations

import ast
import threading
from typing import Callable, List

from utils.setting import cfg, set_setting


class AppState:
    _instance: AppState | None = None
    _lock = threading.Lock()
    _tags: str
    _max_threshold: float
    _mix_threshold: float
    _subscribers: list[Callable]
    _fish_interval: float
    _running: bool
    _game_window_key: str
    _hwnd: int
    _level_type: str
    _badge_count: int
    _selected_index: int
    _wwzz_count: int
    _food_tags: str
    _food_interval: int
    _is_food: bool
    _wx_key: str
    _wx_number: int
    _is_wx: bool
    _wqzz_type: int

    def __new__(cls) -> "AppState":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)

                    # 2. 在运行时只做纯赋值，去掉冒号和类型标注
                    cls._instance._subscribers = []
                    cls._instance._tags = cfg["KEYWORD_FISH"]
                    cls._instance._max_threshold = cfg["MAX_THRESHOLD"]
                    cls._instance._min_threshold = cfg["MIN_THRESHOLD"]
                    cls._instance._game_window_key = cfg["GAME_WINDOW_KEY"]
                    cls._instance._running = False
                    cls._instance._hwnd = 0
                    cls._instance._level_type = cfg["LEVEL_TYPE"]
                    cls._instance._badge_count = cfg["BADGE_COUNT"]
                    cls._instance._selected_index = cfg["SELECTED_INDEX"]
                    cls._instance._wwzz_count = cfg["WWZZ_COUNT"]
                    cls._instance._food_tags = cfg["FOOD_TAGS"]
                    cls._instance._food_interval = cfg["FOOD_INTERVAL"]
                    cls._instance._is_food = cfg["IS_FOOD"]
                    cls._instance._wx_key = cfg["WX_KEY"]
                    cls._instance._wx_number = cfg["WX_NUMBER"]
                    cls._instance._is_wx = cfg["IS_WX"]
                    cls._instance._wqzz_type = int(cfg["WQZZ_TYPE"])

        return cls._instance

    # ✅ 所有写操作走 property，自动通知订阅者
    @property
    def tags(self) -> List[str]:
        v: str = self._tags
        try:
            data = ast.literal_eval(v)
            # 强制校验必须是字符串列表
            if isinstance(data, list) and all(isinstance(item, str) for item in data):
                return data
            return []
        except (ValueError, SyntaxError, TypeError):
            # 格式错误、空字符串、非法语法全部返回空列表
            return []

    @tags.setter
    def tags(self, value: List[str]):
        self._tags = str(value)
        set_setting("KEYWORD_FISH", str(value))
        self._notify()

    @property
    def max_threshold(self) -> float:
        return self._max_threshold

    @max_threshold.setter
    def max_threshold(self, value: float):
        if value < 0:
            raise ValueError("max_threshold must >= 0")  # ✅ 统一校验
        self._max_threshold = value
        set_setting("MAX_THRESHOLD", value)
        self._notify()

    @property
    def min_threshold(self) -> float:
        return self._min_threshold

    @min_threshold.setter
    def min_threshold(self, value: float):
        if value >= 10:
            raise ValueError("min_threshold must < 10")  # ✅ 统一校验
        self._min_threshold = value
        set_setting("MIN_THRESHOLD", value)
        self._notify()

    def subscribe(self, callback: Callable):
        self._subscribers.append(callback)

    def unsubscribe(self, callback: Callable):
        self._subscribers.remove(callback)

    def _notify(self):
        for cb in self._subscribers:
            cb()

    @property
    def game_window_key(self) -> str:
        return self.game_window_key

    @game_window_key.setter
    def game_window_key(self, value: str):
        self.game_window_key = value
        set_setting("GAME_WINDOW_KEY", value)

    @property
    def is_running(self) -> bool:
        return self._running

    @is_running.setter
    def running(self, value: bool):
        self._running = value

    @property
    def hwnd(self) -> int:
        return self._hwnd

    @hwnd.setter
    def hwnd(self, value: int):
        self._hwnd = value

    @property
    def level_type(self):
        return self._level_type

    @level_type.setter
    def level_type(self, value: str):
        self._level_type = value
        set_setting("LEVEL_TYPE", value)

    @property
    def badge_count(self):
        return self._badge_count

    @badge_count.setter
    def badge_count(self, val: int):
        self._badge_count = val
        set_setting("BADGE_COUNT", val)

    @property
    def selected_index(self):
        return self._selected_index

    @selected_index.setter
    def selected_index(self, val: int):
        self._selected_index = val
        set_setting("SELECTED_INDEX", val)

    @property
    def wwzz_count(self):
        return self._wwzz_count

    @wwzz_count.setter
    def wwzz_count(self, val: int):
        self._wwzz_count = val
        set_setting("WWZZ_COUNT", val)

    @property
    def food_tags(self) -> List[str]:
        v: str = self._food_tags
        try:
            data = ast.literal_eval(v)
            # 强制校验必须是字符串列表
            if isinstance(data, list) and all(isinstance(item, str) for item in data):
                return data
            return []
        except (ValueError, SyntaxError, TypeError) as e:
            print(e)
            return []
            # 格式错误、空字符串、非法语法全部返回空列表

    @food_tags.setter
    def food_tags(self, value: List[str]) -> None:
        self._food_tags = str(value)
        set_setting("FOOD_TAGS", str(value))
        self._notify()

    @property
    def food_interval(self) -> int:
        return self._food_interval

    @food_interval.setter
    def food_interval(self, val: int) -> None:
        self._food_interval = val
        set_setting("FOOD_INTERVAL", val)

    @property
    def is_food(self) -> bool:
        return self._is_food

    @is_food.setter
    def is_food(self, val: bool) -> None:
        self._is_food = val
        set_setting("IS_FOOD", val)

    @property
    def wx_key(self) -> str:
        return self._wx_key

    @wx_key.setter
    def wx_key(self, val: str) -> None:
        self._wx_key = val
        set_setting("WX_KEY", val)

    @property
    def wx_number(self) -> int:
        return self._wx_number

    @wx_number.setter
    def wx_number(self, val: int) -> None:
        self._wx_number = val
        set_setting("WX_NUMBER", val)

    @property
    def is_wx(self) -> bool:
        return self._is_wx

    @is_wx.setter
    def is_wx(self, val: bool) -> None:
        self._is_wx = val
        set_setting("IS_WX", val)

    @property
    def wqzz_type(self) -> int:
        return self._wqzz_type

    @wqzz_type.setter
    def wqzz_type(self, val: int) -> None:
        self._wqzz_type = val
        set_setting("WQZZ_TYPE", val)


state = AppState()
