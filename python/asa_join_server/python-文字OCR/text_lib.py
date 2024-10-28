import pytesseract
import easyocr
import torch
import cv2
from typing import Union, List, Dict, Optional, Tuple

import torch.version
from win_lib import *

def preprocess_image(image):
    """预处理图像以提高 OCR 识别效果"""
    # 转为灰度图
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 二值化图像（自适应阈值）
    binary = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )

    # 去除噪声（开操作）
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
    clean_image = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

    return clean_image


def find_text_on_screen(hwnd, text: Union[str, List[str]]) -> Union[bool, Dict[str, bool]]:
    screenshot = background_screenshot(hwnd)
    if screenshot is None:
        return False if isinstance(text, str) else {t: False for t in text}

    reader = easyocr.Reader(['en'])  # 使用简体中文和英文
    # reader = easyocr.Reader(['ch_sim', 'en'])  # 使用简体中文和英文

    # 使用 EasyOCR 识别图像中的文字
    results = reader.readtext(screenshot)
    
    # 提取所有识别出的文本
    image_text = ' '.join([result[1] for result in results])
    print(f"{image_text}")
    if isinstance(text, str):
        # 如果输入是单个字符串，直接返回是否找到
        return text.lower() in image_text.lower()
    elif isinstance(text, list):
        # 如果输入是字符串列表，返回字典
        return {item: item.lower() in image_text.lower() for item in text}
    else:
        raise ValueError("Input 'text' must be a string or a list of strings")


def find_text_on_screen_position(hwnd):
    print("返回文本在屏幕上的坐标")