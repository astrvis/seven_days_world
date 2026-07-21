import os
import sys

import cv2
import numpy as np


def get_res_path():
    if getattr(sys, "frozen", False):
        return os.path.join(os.path.dirname(sys.executable), "res")
    return os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "res"
    )


def mss_to_cv(mss_img):
    # mss截图转OpenCV BGR图
    arr = np.array(mss_img)
    return cv2.cvtColor(arr, cv2.COLOR_BGRA2BGR)


def get_text_mask(img):
    # """提取白色文字掩码：只保留亮白色文字，所有背景全部置黑"""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # 筛选高亮度白色文字（阈值200，只保留接近纯白的文字）
    _, mask = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)

    return mask


def get_text_mask2(img):
    # 转换为 HSV 空间（更适合颜色分割）
    # hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # 定义绿色范围（H: 40~80 对应黄绿→纯绿；S>50, V>100 避免灰绿/暗绿）
    # 注意：OpenCV 的 H 范围是 [0, 179]（不是 0~360）
    lower = np.array([150, 100, 150])  # H, S, V 下限
    upper = np.array([179, 255, 255])  # H 上限设为 179（最大值）

    mask = cv2.inRange(img, lower, upper)

    # 可选：轻微开运算去噪（避免细碎白点）
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    return mask


def check_exist(mss_img, template_path=None, threshold=0.68, type: int = 1):
    if template_path is None:
        template_path = os.path.join(get_res_path(), "stamina_text.png")
    # 1、处理当前游戏截图，提取纯文字掩码（过滤动态背景）

    frame = mss_to_cv(mss_img)
    # print(f"原图尺寸：{frame.shape}")
    if type == 1:
        frame_mask = get_text_mask(frame)
    elif type == 2:
        frame_mask = get_text_mask2(frame)
    cv2.imwrite(
        os.path.join(os.path.dirname(sys.executable), "frame_mask.png"), frame_mask
    )
    # 2、读取模板，同样提取文字掩码
    template_bgr = cv2.imread(template_path)
    if template_bgr is None:
        raise FileNotFoundError("「剩余耐力」模板图片缺失")
    # print(f"模板图尺寸：{template_bgr.shape}")
    template_mask = get_text_mask(template_bgr)
    # cv2.imwrite("template_mask.png", template_mask)
    # 3、掩码模板匹配：只对比白色文字，背景自动忽略
    match_result = cv2.matchTemplate(frame_mask, template_mask, cv2.TM_CCOEFF_NORMED)
    max_similar = np.max(match_result)
    # # print(f"文字轮廓匹配相似度：{max_similar:.2f}")

    return max_similar >= threshold, max_similar


def check_fishing_rod_exit(mss_img, threshold=0.68) -> np.bool_:
    template_path = os.path.join(get_res_path(), "11.png")
    a, b = check_exist(mss_img, template_path, threshold)
    # print("鱼竿匹配度", a, b)
    return a


def check_fishing_exit(mss_img, threshold=0.5):
    template_path = os.path.join(get_res_path(), "fish_text.png")
    a, b = check_exist(mss_img, template_path, threshold)
    # print("垂钓匹配度", b)
    return a


def check_fish_success(mss_img, threshold=0.5):
    template_path = os.path.join(get_res_path(), "f_text.png")
    a, b = check_exist(mss_img, template_path, threshold)
    # print("成功匹配度", b)
    return a


def check_a(mss_img, threshold=0.5):
    template_path = os.path.join(get_res_path(), "a.png")
    a, b = check_exist(mss_img, template_path, threshold)
    # print("a匹配度", b)
    return a


def check_d(mss_img, threshold=0.5):
    template_path = os.path.join(get_res_path(), "d.png")
    a, b = check_exist(mss_img, template_path, threshold)
    # print("d匹配度", b)
    return a


def check_away(mss_img, threshold=0.68):
    template_path = os.path.join(get_res_path(), "away.png")
    a, b = check_exist(mss_img, template_path, threshold)
    # print("d匹配度", b)
    return a


def check_dian_man(mss_img, threshold=0.68):
    template_path = os.path.join(get_res_path(), "result.png")
    a, b = check_exist(mss_img, template_path, threshold, 2)
    # print("d匹配度", b)
    return a


def check_fish_rod(mss_img, threshold=0.68):
    template_path = os.path.join(get_res_path(), "fish_rod.png")
    a, b = check_exist(mss_img, template_path, threshold)
    # print("鱼竿匹配度", b)
    return a
