import copy
import json
import os
import shutil
import sys
import tempfile

from config import (
    BADGE_COUNT,
    FISH_DATA,
    GAME_WINDOW_KEY,
    LEVEL_TYPE,
    MAX_THRESHOLD,
    MIN_THRESHOLD,
    SCREEN_RETRY_COUNT,
    SCREEN_RETRY_DELAY,
    SELECTED_INDEX,
    WQZZ_DATA,
    WWZZ_COUNT,
)

# ==========================================
# 1. 动态聚合顶部变量为默认配置字典
# ==========================================


DEFAULT_CONFIG = {
    # 游戏窗口关键词
    "GAME_WINDOW_KEY": GAME_WINDOW_KEY,
    "SCREEN_RETRY_COUNT": SCREEN_RETRY_COUNT,
    "SCREEN_RETRY_DELAY": SCREEN_RETRY_DELAY,
    # 鱼竿键位
    "KEYWORD_FISH": FISH_DATA["KEYWORD_FISH"],
    "MAX_THRESHOLD": MAX_THRESHOLD,  # 弧度超过这个数立刻松鼠标
    "MIN_THRESHOLD": MIN_THRESHOLD,  # 弧度低于这个数长按鼠标
    "LEVEL_TYPE": LEVEL_TYPE,
    "BADGE_COUNT": BADGE_COUNT,
    "SELECTED_INDEX": SELECTED_INDEX,
    "WWZZ_COUNT": WWZZ_COUNT,
    "FOOD_TAGS": WQZZ_DATA["FOOD_TAGS"],
    "FOOD_INTERVAL": WQZZ_DATA["FOOD_INTERVAL"],
    "IS_FOOD": WQZZ_DATA["IS_FOOD"],
    "WX_KEY": WQZZ_DATA["WX_KEY"],
    "WX_NUMBER": WQZZ_DATA["WX_NUMBER"],
    "IS_WX": WQZZ_DATA["IS_WX"],
    "WQZZ_TYPE": WQZZ_DATA["WQZZ_TYPE"],
}


def get_base_path():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


CONFIG_PATH = os.path.join(get_base_path(), "settings.json")


# ==========================================
# 2. 读写函数
# ==========================================
def load():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        merged = {**DEFAULT_CONFIG, **data}
        # 可选：检测并警告本地文件中已废弃的旧key
        stale_keys = set(data.keys()) - set(DEFAULT_CONFIG.keys())
        if stale_keys:
            print(f"[Config Warning] 本地配置包含已废弃字段: {stale_keys}")
        return merged
    except FileNotFoundError:
        return DEFAULT_CONFIG.copy()
    except json.JSONDecodeError as e:
        print(f"[Config Error] settings.json 格式损坏，使用默认配置: {e}")
        return DEFAULT_CONFIG.copy()


def save(data: dict):
    """安全保存到本地（原子写入防损坏）"""
    dir_name = os.path.dirname(CONFIG_PATH)
    fd, tmp_path = tempfile.mkstemp(dir=dir_name, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        shutil.move(tmp_path, CONFIG_PATH)
    except Exception:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise


def set_setting(key: str, value):
    """对外暴露的唯一修改入口"""
    if key not in DEFAULT_CONFIG:
        raise KeyError(f"未知配置项: {key}")
    # 对可变对象做深拷贝，避免引用相同导致 == 判断失效，同时隔离外部污染
    new_value = (
        copy.deepcopy(value) if isinstance(value, (list, dict)) else value
    )  # 值未变化时跳过写入，减少无意义IO
    if cfg.get(key) == new_value:
        return

    cfg[key] = new_value  # 1. 更新内存中的字典
    save(cfg)  # 2. 调用安全保存


def generate_default_config():
    """
    生成默认配置文件。
    仅在 settings.json 不存在时创建；若已存在则跳过，避免覆盖用户自定义配置。
    """
    if not os.path.exists(CONFIG_PATH):
        save(DEFAULT_CONFIG)
        print(f"[Config] 已生成默认配置文件: {CONFIG_PATH}")


# ==========================================
# 3. 反向同步（可选但强烈推荐）
# ==========================================
# 将加载后的配置重新赋值给顶部变量
# 这样业务代码依然可以直接用 config.USERNAME，无需改成字典访问
cfg = load()
generate_default_config()
for key in DEFAULT_CONFIG:
    globals()[key] = cfg[key]
