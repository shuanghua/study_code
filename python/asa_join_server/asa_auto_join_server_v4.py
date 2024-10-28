import os
import time
import sys
from mss import mss
from win11toast import notify
from datetime import datetime
from ctypes import byref, sizeof
from win_lib import *
from image_lib import *

#-----------------------------------------------------------------------------------------
# 挤服开始了，监听挤服失败和挤服成功
def check_multiple_images(hwnd, images):
    print("开始检测是否出现错误图片")
    for image in images:
        location = find_image_on_screen(hwnd,image) # 调用 opencv 图片识别， 过程相对耗时
        if location:
            return image, location
    # time.sleep(5)    # 用于调试
    return None

#-----------------------------------------------------------------------------------------

def find_and_click_image(hwnd, image):
    while True:
        position = find_image_on_screen_position(hwnd, image)
        if position:
            # click_at_position_postmessage(hwnd, position[0], position[1])
            click_at_position_sendmessage(hwnd, position[0], position[1])
            continue
        else:
            break

# ======================== action ================================

def action_click_cancel(hwnd):
    find_and_click_image(hwnd, png_cancell)
    two_back_to_start_menu(hwnd)


def action_click_ok(hwnd):
    find_and_click_image(hwnd, png_ok)
    two_back_to_start_menu(hwnd)


def action_click_accept_server_full_noback(hwnd):
    find_and_click_image(hwnd, png_accept_server_full)


def action_click_accept_timeout_noback(hwnd):
    find_and_click_image(hwnd, accept_timeout)


def action_click_accept_join_failed_oneback(hwnd):
    find_and_click_image(hwnd, png_accept_join_failed_oneback)
    one_back_to_start_menu(hwnd)


#当检测到指定图片时发送通知并退出程序
def action_joined_with_notification(hwnd):
    notify(
        title="方舟生存飞升挤服",
        body="您已成功加入服务器， 挤服结束！",
        duration="long"  # 通知持续时间
    )
    winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
    print("检测到成功加入服务器，程序终止运行")
    sys.exit(0)  # 正常退出程序

#-----------------------------------------------------------------------------------------

# 返回到主界面
def one_back_to_start_menu(hwnd):
    find_and_click_image(hwnd, png_back_to_start_menu)


def one_back_to_meun_list(hwnd):
    find_and_click_image(hwnd, png_back_to_menu_list)


def two_back_to_start_menu(hwnd):
    find_and_click_image(hwnd, png_back_to_menu_list)
    one_back_to_start_menu(hwnd)


# 遍历本地图片库，找到对应图片，执行对应操作, 返回值：是否需要返回主菜单重新加入
def waiting_join_result(hwnd, images):
    start_time = time.time()
    need_rejoin = False
    print("等待服务器响应")
    while True:
        # 找到错误图片， 执行完对应操作后， 界面会返回到主菜单， 所以应该再次点击 join last session
        result = check_multiple_images(hwnd, list(images.keys()))
        if result:
            detected_image, _ = result
            action = images[detected_image]
            action(hwnd)
            print(f"执行 {action.__name__} 操作成功， 界面已经回到主菜单")
            need_rejoin = True
            break
        
        # 等待错误时长为 120秒， 超过就返回主菜单点击 join last session
        if time.time() - start_time > 120:
            exist = find_image_on_screen(hwnd, png_back_to_menu_list)
            if exist:
                two_back_to_start_menu(hwnd)
                need_rejoin = True
                break   # 需要重新回到主菜单， 并点击 join last session
            else: # 超时了， 但一直卡在黑洞界面， 此时只能继续等待, 并检测可能出现错误的图片
                continue

    return need_rejoin 


def start_join_last_session(hwnd):
    find_and_click_image(hwnd, png_join_last_session)


script_dir = os.path.dirname(os.path.abspath(__file__))
images_dir = os.path.join(script_dir, "images\\")
png_join_last_session = images_dir + "click_join_last.png"

png_server_full_accept = images_dir + "server_full_accept.png"
png_server_full_cancel = images_dir + "server_full_cancel.png"
png_timeout_accept_noback = images_dir + "timeout_accept_noback.png"
png_timedout_cancel = images_dir + "timedout_cancel.png"
png_timeout_ok = images_dir + "timeout_ok.png"

png_join_success = images_dir + "join_success.png"
png_join_success2 = images_dir + "join_success2.png"
# png_join_success3 = images_dir + "join_success3.png"
png_join_success4 = images_dir + "join_success4.png"

png_join_failed_accept = images_dir + "join_failed_accept.png"

png_back_to_menu_list = images_dir + "back_to_menu_list.png"
png_back_to_start_menu = images_dir + "back_to_start_menu.png"

png_cancell = images_dir + "click_cancell.png"
png_ok = images_dir + "click_ok.png"
png_accept_server_full = images_dir + "accept_server_full.png"
png_accept_join_failed_oneback = images_dir + "accept_join_failed_oneback.png"
accept_timeout = images_dir + "accept_timeout.png"

png_start_game = images_dir + "start.png"
png_join_game = images_dir + "join_game.png"
png_server_list = images_dir + "server_list.png"

process_name = "ArkAscended.exe"

# 图片 - 对应操作
images = {
    png_server_full_accept: action_click_accept_server_full_noback,
    png_server_full_cancel: action_click_cancel,
    png_timeout_accept_noback: action_click_accept_timeout_noback,
    png_timedout_cancel: action_click_cancel,
    png_timeout_ok: action_click_ok,
    png_join_failed_accept: action_click_accept_join_failed_oneback,
    png_join_success: action_joined_with_notification,
    png_join_success2: action_joined_with_notification,
    # png_join_success3: action_joined_with_notification,
    png_join_success4: action_joined_with_notification,
}

def start_game(hwnd):
    running = True
    while True:
        if running:
            start_join_last_session(hwnd) # 点击 加入上次挤服的服务器
            need_rejoin = waiting_join_result(hwnd, images) # 等待结果， 并执行对应操作
            if need_rejoin:
                running = True
                continue
            else:
                running = False
                send_notify(body="挤服停止")
                break

def test(hwnd):
    while True:
        find_and_click_image(hwnd, png_start_game)
        find_and_click_image(hwnd, png_join_game)
        two_back_to_start_menu(hwnd)

# v4 版本实现了自动识别挤服的基本功能， 但还有优化的地方
# 点击响应比较慢，待查明优化
# 多张图的遍历采用的是串行识别， 识别效率较低， 待优化
def main():
    hwnd = find_process_by_name(process_name)
    
    show_window(hwnd) # 取消最小化
    resize_window_complete(hwnd, 1280, 720, False)
    # set_window_topmost(hwnd, topmost = True) # 置顶窗口

    # # background_screenshot(hwnd) # debug: 截图 + 分辨率调整

    send_notify(body="开始挤服")

    if find_image_on_screen(hwnd, png_server_list):
        two_back_to_start_menu(hwnd)
    elif find_image_on_screen(hwnd, png_join_game):
        one_back_to_start_menu
        
    start_game(hwnd)

if __name__ == "__main__":
    main()
