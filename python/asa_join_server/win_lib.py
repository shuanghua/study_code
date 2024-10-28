import cv2
import numpy as np
import win32gui
import win32ui
import win32process
import win32api
import win32con
import winsound  # Windows系统的声音模块
import time
import psutil
import win32com.client
from win11toast import notify
from ctypes import windll, byref, sizeof,Structure, c_long, c_ulong, c_ulonglong

def send_notify(body, title="方舟生存飞升挤服"):
    notify(title = title, body = body, duration = "short")
    winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)


def find_process_by_name(process_name):
    target_pid = None
    for proc in psutil.process_iter(['name', 'pid']):
        if proc.info['name'].lower() == process_name.lower():
            target_pid = proc.info['pid']
            break
    
    if not target_pid:
        print(f"未找到进程: {process_name}")
        return False

    # 找到进程的主窗口
    def callback(hwnd, hwnds):
        if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
            _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
            if found_pid == target_pid:
                hwnds.append(hwnd)
        return True
    hwnds = []
    win32gui.EnumWindows(callback, hwnds)
    if not hwnds:
        print(f"未找到窗口: {process_name}")
        return False
    hwnd = hwnds[0]
    print(f"进程名: {process_name}  窗口句柄: {hwnd}")
    return hwnd


# ==================================点击======================================
# 定义输入事件的结构体
class MOUSEINPUT(Structure):
    _fields_ = [
        ("dx", c_long),
        ("dy", c_long),
        ("mouseData", c_ulong),
        ("dwFlags", c_ulong),
        ("time", c_ulong),
        ("dwExtraInfo", c_ulonglong)
    ]


class INPUT(Structure):
    _fields_ = [
        ("type", c_ulong),
        ("mi", MOUSEINPUT)
    ]


# 将窗口坐标换算成屏幕坐标
def click_at_position3(hwnd, x, y):
    # 获取窗口的位置和状态
    rect = win32gui.GetWindowRect(hwnd)
    client_rect = win32gui.GetClientRect(hwnd)
    border_width = ((rect[2] - rect[0]) - client_rect[2]) // 2
    title_height = (rect[3] - rect[1]) - client_rect[3] - border_width

    # 计算相对于屏幕的绝对坐标
    screen_x = x - border_width
    screen_y = y - title_height

    # 创建鼠标移动输入
    move_input = INPUT()
    move_input.type = 0  # INPUT_MOUSE
    move_input.mi.dx = int(screen_x * (65535.0 / win32api.GetSystemMetrics(0)))
    move_input.mi.dy = int(screen_y * (65535.0 / win32api.GetSystemMetrics(1)))
    move_input.mi.mouseData = 0
    move_input.mi.dwFlags = 0x0001 | 0x8000  # MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE
    move_input.mi.time = 0
    move_input.mi.dwExtraInfo = 0

    # 创建鼠标按下输入
    down_input = INPUT()
    down_input.type = 0  # INPUT_MOUSE
    down_input.mi.dx = int(screen_x * (65535.0 / win32api.GetSystemMetrics(0)))
    down_input.mi.dy = int(screen_y * (65535.0 / win32api.GetSystemMetrics(1)))
    down_input.mi.mouseData = 0
    down_input.mi.dwFlags = 0x0002 | 0x8000  # MOUSEEVENTF_LEFTDOWN | MOUSEEVENTF_ABSOLUTE
    down_input.mi.time = 0
    down_input.mi.dwExtraInfo = 0

    # 创建鼠标松开输入
    up_input = INPUT()
    up_input.type = 0  # INPUT_MOUSE
    up_input.mi.dx = int(screen_x * (65535.0 / win32api.GetSystemMetrics(0)))
    up_input.mi.dy = int(screen_y * (65535.0 / win32api.GetSystemMetrics(1)))
    up_input.mi.mouseData = 0
    up_input.mi.dwFlags = 0x0004 | 0x8000  # MOUSEEVENTF_LEFTUP | MOUSEEVENTF_ABSOLUTE
    up_input.mi.time = 0
    up_input.mi.dwExtraInfo = 0

    # 发送输入序列
    inputs = (INPUT * 3)(move_input, down_input, up_input)
    result = windll.user32.SendInput(3, byref(inputs), sizeof(INPUT))
    
    if result != 3:
        print(f"SendInput failed: {win32api.GetLastError()}")
        return False
        
    return True
 

# PostMessage 基于整个窗口坐标
def click_at_position_postmessage(hwnd, x, y):
    print("开始点击坐标")

    win32gui.SendMessage(hwnd, win32con.WM_MOUSEACTIVATE, hwnd, win32con.HTCLIENT)
    win32gui.SendMessage(hwnd, win32con.WM_SETFOCUS, 0, 0)
    # win32gui.SetForegroundWindow(hwnd)

    # 转换为客户区坐标
    client_point = win32gui.ScreenToClient(hwnd, (x, y))
    lParam = win32api.MAKELONG(client_point[0], client_point[1])
    win32gui.PostMessage(hwnd, win32con.WM_MOUSEMOVE, 0, lParam) # 发送鼠标移动消息
    time.sleep(0.1)  # 给一点延迟确保消息被处理
    win32gui.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam) # 发送鼠标按下消息
    time.sleep(0.1)  # 给一点延迟确保消息被处理
    win32gui.PostMessage(hwnd, win32con.WM_LBUTTONUP, 0, lParam) # 发送鼠标松开消息
    print("坐标点击成功")
    time.sleep(0.8)  # 给一点延迟确保消息被处理


# SendMessage （基于整个窗口坐标）
def click_at_position_sendmessage(hwnd, x, y):
    print("开始点击坐标")
    win32gui.SendMessage(hwnd, win32con.WM_MOUSEACTIVATE, hwnd, win32con.HTCLIENT)
    win32gui.SendMessage(hwnd, win32con.WM_SETFOCUS, 0, 0)

    client_point = win32gui.ScreenToClient(hwnd, (x, y))
    lParam = win32api.MAKELONG(client_point[0], client_point[1])
    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONUP, 0, lParam)
    print("坐标点击成功")
    time.sleep(1)  # 给一点延迟确保画面刷新


# mouse_event 模拟物理鼠标事件的点击（基于整个屏幕坐标）
def click_at_position_mouse_event(x, y):
    win32api.SetCursorPos((x, y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)       


# =============================窗口==============================


def get_window_rect(hwnd):
    rect = win32gui.GetWindowRect(hwnd)
    return {
        "left": rect[0],
        "top": rect[1],
        "width": rect[2] - rect[0],
        "height": rect[3] - rect[1]
    }


# 如果最小化了， 则恢复窗口显示
def show_window(hwnd):
    placement = win32gui.GetWindowPlacement(hwnd) # 获取窗口状态
    if placement[1] == win32con.SW_SHOWMINIMIZED:  # 窗口被最小化
        print("窗口已最小化，正在恢复...")
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        time.sleep(0.5)  # 给窗口一些恢复的时间
    # 将窗口设为前台
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.2)  # 稍微等待一下确保窗口已切换到前台

# 窗口置顶
def set_window_topmost(hwnd, topmost):
    if topmost:
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, 
                                win32con.SWP_NOMOVE + win32con.SWP_NOSIZE)
    else:
        win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, 
                                win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

def set_window_size(hwnd, pos_x, pos_y, window_width, window_height):
    print(f"计算窗口大小: {window_width}x{window_height}")
    style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
    win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, (style & ~win32con.WS_POPUP) | win32con.WS_OVERLAPPEDWINDOW)
    win32gui.SetWindowPos(
        hwnd, win32con.HWND_NOTOPMOST,  # HWND_TOPMOST 置顶  HWND_NOTOPMOST 不置顶
        pos_x, pos_y,  # 窗口左上角坐标
        window_width, window_height, 
        win32con.SWP_FRAMECHANGED | win32con.SWP_NOZORDER | win32con.SWP_SHOWWINDOW
    )  


# 获取屏幕尺寸
def get_screen_size():
    return win32api.GetSystemMetrics(win32con.SM_CXSCREEN), win32api.GetSystemMetrics(win32con.SM_CYSCREEN)


def check_resolution(hwnd, target_width, target_height):
    client_rect = win32gui.GetClientRect(hwnd) # 获取窗口客户区 rect
    current_width = client_rect[2] - client_rect[0]
    current_height = client_rect[3] - client_rect[1]
    print(f"目标窗口分辨率: {target_width}x{target_height}")
    print(f"当前窗口分辨率: {current_width}x{current_height}")
    return current_width == target_width and current_height == target_height


# 不适用于方舟飞升游戏客户端
# 计算要所设置分辨率对应的窗口大小  大小 = 分辨率+边框+标题栏
def calculate_window_rect(hwnd, target_width, target_height):
    border_width = win32api.GetSystemMetrics(win32con.SM_CXSIZEFRAME)
    border_height = win32api.GetSystemMetrics(win32con.SM_CYSIZEFRAME)
    caption_height = win32api.GetSystemMetrics(win32con.SM_CYCAPTION)
    # print(f"边框宽度: {border_width}, 边框高度: {border_height}, 标题栏高度: {caption_height}")
    window_width = target_width + (border_width * 2)
    window_height = target_height + (border_height * 2) + caption_height
    return window_width, window_height


# 适用于方舟飞升游戏客户端
# 计算包含边框和标题栏的完整窗口尺寸  大小 = 分辨率+边框+标题栏
def calculate_window_rect1(hwnd, client_width, client_height):
    # 创建一个RECT结构，包含所需的客户区大小
    rect = win32gui.GetClientRect(hwnd)
    win_rect = win32gui.GetWindowRect(hwnd)
    # 计算边框和标题栏的大小
    border_width = ((win_rect[2] - win_rect[0]) - rect[2]) // 2
    title_height = (win_rect[3] - win_rect[1]) - rect[3] - border_width
    window_width = client_width + (border_width * 2)
    window_height = client_height + title_height + border_width
    # print(f"边框宽度: {border_width}, 标题栏高度: {title_height}")
    return window_width, window_height


# 方舟飞升游戏客户端必须是窗口化模式， 全屏和窗口化全屏调整后会导致鼠标点击位置不对（该问题来自方舟飞升客户端特有的）
def resize_window_complete(hwnd, target_width, target_height, left_top=False):
    # 包含边框和标题栏的窗口大小
    window_width, window_height = calculate_window_rect1(hwnd,target_width, target_height)

    (screen_width, _) = get_screen_size()
    # 计算窗口位置（居中）
    # x = (screen_width - window_width) // 2 if center else 0
    x = int(0 if left_top else screen_width * 0.8) # 0.58 刚好能显示出来错误提示框
    y = 0
    
    # 将窗口 移动到指定的位置 并 设置成指定的分辨率
    set_window_size(hwnd, x, y, window_width, window_height)
    
    # 验证新的分辨率
    time.sleep(0.5)  # 给窗口一些时间来响应
    if check_resolution(hwnd, target_width, target_height):
        print(f"窗口大小调整成功: {target_width}x{target_height}")
        return True
    else:
        print("窗口大小调整失败， 实际分辨率与目标不符")
        return False
    

# ==================================截图======================================


def background_screenshot(hwnd):
    try:
        # 获取窗口客户区的大小
        rect = win32gui.GetClientRect(hwnd)
        width = rect[2] - rect[0]
        height = rect[3] - rect[1]

        # 创建设备上下文
        hwnd_dc = win32gui.GetWindowDC(hwnd)
        mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
        save_dc = mfc_dc.CreateCompatibleDC()

        # 创建位图对象
        save_bitmap = win32ui.CreateBitmap()
        save_bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
        save_dc.SelectObject(save_bitmap)

        # 复制窗口内容到位图
        result = windll.user32.PrintWindow(hwnd, save_dc.GetSafeHdc(), 3)

        if result == 1:
            # 将位图转换为numpy数组
            bmpinfo = save_bitmap.GetInfo()
            bmpstr = save_bitmap.GetBitmapBits(True)
            img = np.frombuffer(bmpstr, dtype='uint8')
            img.shape = (height, width, 4)

            # 转换为BGR格式
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        else:
            print("PrintWindow failed")
            img = None

        # 清理资源
        win32gui.DeleteObject(save_bitmap.GetHandle())
        save_dc.DeleteDC()
        mfc_dc.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwnd_dc)
        # cv2.imwrite("D:\\img\\debug_screenshot.png", img)# 保存截图用于调试 
        return img

    except Exception as e:
        print(f"后台截图出现异常: {e}")
        return None
    

def background_screenshot1(hwnd):
    try:
        # 获取窗口客户区的大小
        rect = win32gui.GetClientRect(hwnd)
        width = rect[2] - rect[0]
        height = rect[3] - rect[1]

        # 创建设备上下文
        hwnd_dc = win32gui.GetWindowDC(hwnd)
        mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
        save_dc = mfc_dc.CreateCompatibleDC()

        # 创建位图对象
        save_bitmap = win32ui.CreateBitmap()
        save_bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
        save_dc.SelectObject(save_bitmap)

        # 复制窗口内容到位图
        result = windll.user32.PrintWindow(hwnd, save_dc.GetSafeHdc(), 3)

        if result == 1:
            # 将位图转换为numpy数组
            bmpinfo = save_bitmap.GetInfo()
            bmpstr = save_bitmap.GetBitmapBits(True)
            img = np.frombuffer(bmpstr, dtype='uint8')
            img.shape = (height, width, 4)

            # 转换为BGR格式
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

            # 图像预处理
            # 1. 转换为灰度图
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # 2. 应用高斯模糊以减少噪声
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)

            # 3. 自适应阈值处理，以处理不同光照条件
            binary = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

            # 4. 腐蚀和膨胀操作以去除小噪点和连接断开的文本
            kernel = np.ones((1, 1), np.uint8)
            eroded = cv2.erode(binary, kernel, iterations=1)
            processed = cv2.dilate(eroded, kernel, iterations=1)

        else:
            print("PrintWindow failed")
            processed = None

        # 保存处理后的图像用于调试
        # 保存原始图像和处理后的图像用于调试
        cv2.imwrite("D:\\img\\debug_screenshot_original.png", img)
        cv2.imwrite("D:\\img\\debug_screenshot_processed.png", processed)
        
        # 清理资源
        win32gui.DeleteObject(save_bitmap.GetHandle())
        save_dc.DeleteDC()
        mfc_dc.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwnd_dc)
        return processed

    except Exception as e:
        print(f"Error in background_screenshot: {e}")
        return None