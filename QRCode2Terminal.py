from PIL import Image
import argparse
import numpy as np
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument("--qrcode", help="Show the QRCode in Terminal")

args = parser.parse_args()

args = parser.parse_args()

txt = ""
QR_WIDTH = 0
QR_HEIGHT = 0
X = 0
Y = 0


def transfer_img_2_txt(image):
    txt = ""
    img = np.array(image)
    rows, cols = img.shape
    for i in range(rows):
        for j in range(cols):
            if (img[i, j] < 128):
                txt += "\033[40m  \033[0m"  # BLACK
            else:
                txt += "\033[47m  \033[0m"  # WHITE
        txt += '\033[0m\n'

    print(txt)


def search_by_anchor(img_array):
    global QR_WIDTH, QR_HEIGHT, X, Y
    rows, cols = img_array.shape

    for j in range(cols):
        for i in range(rows):
            if (img_array[i, j] < 128):
                X = i
                Y = j
                break
        if X > 0: break

    # calculate right top anchor point
    first_row = img_array[Y]
    # print(first_row.shape)
    for i in range(len(first_row) - 1, -1, -1):
        if first_row[i] < 128:
            QR_WIDTH = i - X + 1
            break
        if QR_WIDTH > 0: break

    first_col = img_array[:, X]
    for i in range(len(first_col) - 1, -1, -1):
        if first_col[i] < 128:
            QR_HEIGHT = i - Y + 1
            break
        if QR_HEIGHT > 0: break


def search_min_w(img_array):
    rows, cols = img_array.shape
    count = 0
    min_w = 100

    i = X
    while i < rows:
        for j in range(cols):
            if img_array[i, j] < 128:
                count += 1
            else:
                min_w = count if 0 < count < min_w else min_w
                count = 0
        i += 5
    return min_w


def regenerate_qrcode(img_array, width):
    rows, cols = img_array.shape

    index_y = Y
    txt = ""

    while index_y < (cols - Y):
        index_x = X
        while index_x < (rows - X):
            if img_array[index_x, index_y] < 128:  # black
                txt += "\033[40m  \033[0m"
            else:  # white
                txt += "\033[47m  \033[0m"
            index_x += width
        txt += '\033[0m\n'
        index_y += width
    print(txt)


def transfer(source_image):
    img_ori = Image.open(source_image).convert('L')
    img_arr = np.array(img_ori)
    search_by_anchor(img_arr)
    wid = search_min_w(img_arr)
    regenerate_qrcode(img_arr, wid)
