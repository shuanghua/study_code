import cv2
import time
import datetime
from win_lib import *


# OpenCV 图片识别, 截图+识别
# image: 用户提供的图片
# 检查图片是否在屏幕截图中
def find_image_on_screen(hwnd, image):
    screenshot = background_screenshot(hwnd)
    time.sleep(0.5)
    template = cv2.imread(image, cv2.IMREAD_COLOR)
    # 确保模板和截图具有相同的通道数
    if template.shape[2] != screenshot.shape[2]:
        # print(f"截图分辨率: {screenshot.shape}")
        if template.shape[2] == 3 and screenshot.shape[2] == 4:
            screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)
        elif template.shape[2] == 4 and screenshot.shape[2] == 3:
            template = cv2.cvtColor(template, cv2.COLOR_BGRA2BGR)
    try:
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        print(f"检测： {image}, 相似率: {max_val}")

        if max_val > 0.8:        # 阈值保持在0.8
            local_time = datetime.datetime.fromtimestamp(time.time())
            formatted_time = local_time.strftime("%H:%M:%S")

            print(f"找到图片: {image},  匹配率： {max_val}  时间：{formatted_time}  图片的坐标： {max_loc}")
            
            return max_loc
        
    except cv2.error as e:
        print(f"OpenCV error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    return None     # 识别失败


# 需要计算窗口边框和标题栏的偏移
def find_image_on_screen_position(hwnd, image):
    location = find_image_on_screen(hwnd, image)
    if location:
        borders = win32gui.GetWindowRect(hwnd)
        client_rect = win32gui.GetClientRect(hwnd)
        border_width = ((borders[2] - borders[0]) - client_rect[2]) // 2
        title_height = (borders[3] - borders[1]) - client_rect[3] - border_width
        window_rect = get_window_rect(hwnd)
        global_x = window_rect["left"] + location[0] + border_width
        global_y = window_rect["top"] + location[1] + title_height
        print(f"转换坐标: ({global_x}, {global_y})")
        return (global_x, global_y)
    return None