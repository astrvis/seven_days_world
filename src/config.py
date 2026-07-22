GAME_WINDOW_KEY = "七日世界"
# """游戏窗口名称"""
SCREEN_RETRY_COUNT = 3
# """截图重试次数"""
SCREEN_RETRY_DELAY = 0.5
# """截图延迟"""


FISH_DATA = {
    # """鱼竿键位"""
    "KEYWORD_FISH": '["7", "8", "9", "0", "-"]',
    # """鱼竿列表识别框"""
    "ROD_LIST": {"left": 1344, "top": 961, "width": 66, "height": 63},
    # """边距"""
    "ML1": 1,
    "ML2": 2,
    # """鱼类型识别框数据"""
    "FISH_NAMES": [["电鳗", "电", "鳗"], ["极寒水母", "极寒", "水母"]],
    # """青色光圈识别框"""
    "RING_AREA": {"left": 913, "top": 786, "width": 107, "height": 96},
    # """垂钓检测框"""
    "EXIT_AREA": {"left": 959, "top": 880, "width": 50, "height": 50},
    # """钓上鱼弹窗框"""
    "SUCCESS_AREA": {"left": 1217, "top": 545, "width": 38, "height": 28},
    # """AD拉扯校正框"""
    "AD_AREA": {"left": 796, "top": 767, "width": 385, "height": 120},
    # """鱼竿识别框"""
    "FISH_ROD": {"left": 882, "top": 1002, "width": 64, "height": 22},
    # """鱼类型识别框"""
    "FISH_TYPE_AREA": {"left": 459, "top": 221, "width": 895, "height": 733},
    # """鱼类型识别框数据"""
    "FISH_TYPE_DATA_AREA": ["鱼", "鯧", "鲨"],
    # """检测掉线识别框"""
    "AWAY_AREA": {"left": 890, "top": 375, "width": 140, "height": 48},
    # """成功钓上鱼识别框"""
    "SCUSSS_FISH_AREA": {"left": 1011, "top": 441, "width": 55, "height": 32},
}


# """徽章识别框数据"""
BADGE_DATA_AREA = {
    "START": {"left": 420, "top": 300, "width": 1240, "height": 600},
    "RESULT_NAME": ["混沌", "混", "沌", "交谈", "交", "谈"],
    "ORDINARY_NAME": ["挑战馆长", "挑战", "馆长"],
    "CHAOS_NAME": ["混沌试炼", "混沌", "试炼"],
    "SUCCESS": {"left": 1470, "top": 720, "width": 400, "height": 300},
    "SUCCESS_NAME": ["确认"],
    # 异维大猫", "异维", "异维大猫"
    "PAGE": 4,
    "LIST": {"left": 1160, "top": 470, "width": 700, "height": 350},
    "SUCCESS_TIPS": {"left": 880, "top": 360, "width": 150, "height": 70},
    "SUCCESS_TIPS_NAME": ["系统提示", "提示"],
    "SUCCESS_ITEM": {"left": 810, "top": 90, "width": 290, "height": 80},
    "SUCCESS_ITEM_NAME": ["获得物品", "物品"],
}
# """屏幕尺寸"""
SCREEN_SIZE = {"WIDTH": 1920, "HEIGHT": 1080}
# """当前徽章类型"""
LEVEL_TYPE = "ordinary"
# """当前徽章局数"""
BADGE_COUNT = 0
# """最大压力阈值"""
MAX_THRESHOLD = 1.4  # 弧度超过这个数立刻松鼠标
# """最小压力阈值"""
MIN_THRESHOLD = 1.0  # 弧度低于这个数长按鼠标
# """当前选中的tab索引"""
SELECTED_INDEX = 0

# """忘却识别框数据"""
WQZZ_DATA = {
    # """奖励识别框"""
    "COORDS": {"left": 450, "top": 910, "width": 180, "height": 150},
    # """左上角识别框"""
    "BOOS": {"left": 15, "top": 10, "width": 300, "height": 200},
    # """boss杀死识别数据"""
    "BOOS_NAME": ["奖励", "奖", "励"],
    # """boss未击杀识别数据"""
    "SCENE_NAME": ["异界生命", "异界"],
    # """成功宝箱识别框"""
    "XIANGZI": {"left": 415, "top": 230, "width": 1225, "height": 610},
    # """成功宝箱识别数据"""
    "XIANGZI_NAME": ["宝箱", "宝", "箱"],
    # """离开副本识别框"""
    "EXIT_LEVEL": {"left": 300, "top": 230, "width": 1445, "height": 610},
    # """离开副本识别数据"""
    "EXIT_LEVEL_NAME": ["离开副本", "离开", "副本"],
    # """跳过动画识别框"""
    "SKIP": {"left": 1610, "top": 880, "width": 280, "height": 188},
    # """跳过动画识别数据"""
    "SKIP_NAME": ["跳过动画", "跳过", "动画"],
    # """再次挑战识别框"""
    "SUCCESS": {"left": 1415, "top": 930, "width": 400, "height": 125},
    # """再次挑战识别数据"""
    "SUCCESS_NAME": ["再次挑战", "再次", "挑战"],
    # """脱离卡死识别框"""
    "ESC": {"left": 90, "top": 960, "width": 460, "height": 110},
    # """脱离卡死识别数据"""
    "ESC_NAME": ["离开副本", "离开", "副本"],
    # """地图识别框"""
    "MAP": {"left": 1654, "top": 42, "width": 220, "height": 220},
    "NOT_START": {"left": 250, "top": 300, "width": 1300, "height": 500},
    "NOT_START_NAME": ["位面入口", "位面", "入口"],
    "EXIT_XY": (180, 1035),
    "FOOD_TAGS": '["8", "9", "0", "-"]',
    "FOOD_INTERVAL": 2700,  # 秒
    "IS_FOOD": False,
    "WX_KEY": "7",
    "WX_NUMBER": 30,
    "IS_WX": False,
    "WQZZ_TYPE": 1,
}

# """当前忘却局数"""
WWZZ_COUNT = 0
