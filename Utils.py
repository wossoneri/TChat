# coding: utf-8
from datetime import datetime


def get_greetings():
    h = datetime.now().hour
    if 0 < h <= 6:
        return "凌晨好！"
    elif 6 < h <= 9:
        return "早上好！"
    elif 9 < h <= 12:
        return "上午好！"
    elif 12 < h <= 18:
        return "下午好！"
    elif 18 < h <= 23:
        return "晚上好！"

        # if __name__ == '__main__':
        #     get_greetings()
