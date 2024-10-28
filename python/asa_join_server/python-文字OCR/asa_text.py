from win_lib import *
from image_lib import *
from text_lib import *
from typing import Union, List, Dict, Optional, Tuple

ark_language: str = "en"

# 设置语言， 预留给将来的 kotlin kmp compose ui 调用
def set_language(language):
    ark_language = language


def back_to_main_menu(hwnd):
    x, y = find_text_on_screen(hwnd, "BACK")
    click_at_position_sendmessage(hwnd, x, y)


def back_to_menu_list(hwnd):
    x, y = find_text_on_screen(hwnd, "BACK")
    click_at_position_sendmessage(hwnd, x, y)


def two_back_to_main_menu(hwnd):
    back_to_menu_list(hwnd)
    back_to_main_menu(hwnd)


def main():



    process_name = "ArkAscended.exe"

    hwnd = find_process_by_name(process_name)

    # 取消最小化 设置前台 激活窗口
    show_window(hwnd)

    match ark_language:
        case "en":
            print("当前语言为英文")
        case "zh":
            print("当前语言为中文")
        case _:
            print("暂不支持该语言")
            return
            

    running = True

    exists = find_text_on_screen(hwnd, "JOIN LAST SESSION")
    if exists:
        print(f"找到")
        #position = find_text_on_screen_position(hwnd, "JOIN LAST SESSION")
        #x1, y1, _, _ = position
        #click_at_position_sendmessage(hwnd, x1, y1)
    else:
        print(f"未找到")


    # while True:
    #     if keyboard.is_pressed('f5'):
    #         send_notify(body="开始挤服")
    #         running = True

    #     if running:
    #         running = True
            
    #         x1, y1 = find_text_on_screen_position(hwnd, "JOIN LAST SESSION")
    #         click_at_position_sendmessage(hwnd, x1, y1)

    #         find_text_on_screen(hwnd, "This Server is full. Please try again later.")

    #         need_rejoin = waiting_join_result(hwnd, images) # 等待结果， 并执行对应操作
    #         if need_rejoin:
    #             running = True
    #             continue
    #         else:
    #             print(f"手动停止")
    #             running = False
    #             send_notify(body="停止挤服")
    #             continue

if __name__ == "__main__":
    main()