import argparse
import cv2
import numpy
import sys
from typing import Any

import mosaic


# default image path
SRC_IMG_PATH: str = "images/lena.jpg"
MASK_IMG_PATH: str = "images/mask.png"
OUTPUT_IMG_PATH: str = "images/output.jpg"


class Img:
    def __init__(self, img_path: str):
        image = cv2.imread(img_path)
        if image is None:
            print("Couldn't read the image: " + img_path)
            sys.exit()
        else:
            self.img: numpy.ndarrays = image
            self.height, self.width = image.shape[:2]


SRC: Img  # source image
MASK: Img  # image to use as mask
TMP_IMG: numpy.ndarray  # editing image
RESULT_IMG: numpy.ndarray  # image to save

# cursor position in the image
CURSOR_X: int = 0
CURSOR_Y: int = 0

# diameter of mosic
DIA_HEIGHT: int = 50
DIA_WIDTH: int = 50

# courner angle of mosic
CORNER: list = [[1, 1], [1, 1]]  # [0][0]:左上, [0][1]:右上, [1][0]:左下, [1][1]:右下

# size of each mosaic cell
HORIZON: float = 0.1
VERTICAL: float = 0.1

MODE: str = 'M'  # current drawing mode
OPACITY: int = 1  # opacity of mosaic

IS_SHARP_COLOR: bool = False  # apply sharp color
FEATHER: int = 10  # degree of blur the boundary of mosaic

WINDOW: str = "main"

def main() -> None:
    global MODE, TMP_IMG, RESULT_IMG, SRC, MASK, OUTPUT_IMG_PATH
    parse()
    read_img()
    init_gui()

    while(1):
        key = cv2.waitKey(1)

        # reflect keyboard inputs
        if key == ord("m"):  # "m" key then change mosaic input mode
            MODE = 'M'
        if key == ord("b"):  # "b" key then change blur input mode
            MODE = 'B'
        if key == ord("i"):  # "i" key then change image input mode
            MODE = 'I'
        if key == ord("a"):  # "a" key then apply currently editing mosaic
            RESULT_IMG = TMP_IMG
            cv2.imshow(WINDOW, RESULT_IMG)
        if key == ord("r"):  # "o" key then revert
            TMP_IMG = RESULT_IMG
            cv2.imshow(WINDOW, RESULT_IMG)

        if key == 27:  # Esc key then exit
            break
        if key == ord("s"):  # "s" key then save and exit
            cv2.imwrite(OUTPUT_IMG_PATH, TMP_IMG)
            break

""" refelect command line args """
def parse() -> None:
    global SRC_IMG_PATH, MASK_IMG_PATH, OUTPUT_IMG_PATH

    # create command line options
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--src', default=SRC_IMG_PATH)
    parser.add_argument('-m', '--mask', default=MASK_IMG_PATH)
    parser.add_argument('-o', '--output', default=OUTPUT_IMG_PATH)

    # get args
    args = parser.parse_args()

    # change from default path if specified option value
    if args.src != "":
        SRC_IMG_PATH = args.src
    if args.mask != "":
        MASK_IMG_PATH = args.mask
    if args.output != "":
        OUTPUT_IMG_PATH = args.output

""" read specified path and set glocal variables """
def read_img() -> None:
    global SRC, TMP_IMG, RESULT_IMG, MASK
    SRC = Img(SRC_IMG_PATH)
    TMP_IMG = SRC.img
    RESULT_IMG = SRC.img
    MASK = Img(MASK_IMG_PATH)


""" call mosaic function """
def edit():
    global TMP_IMG

    TMP_IMG = mosaic.add_mosaic(
        RESULT_IMG, DIA_HEIGHT, DIA_WIDTH, CURSOR_Y, CURSOR_X,
        CORNER, HORIZON, VERTICAL, OPACITY, FEATHER, IS_SHARP_COLOR, MODE, image_mask=MASK.img)
    
    cv2.imshow(WINDOW, TMP_IMG)


""" reflect the mouse operation """
def callback(event, x: int, y: int, flags: int, param: Any) -> None:
    global CURSOR_X, CURSOR_Y

    # left click
    if event == cv2.EVENT_LBUTTONDOWN:
        CURSOR_X, CURSOR_Y = x, y

    edit()


""" get trackbar's change """
def get_pram(pos: int) -> None:
    global DIA_HEIGHT, DIA_WIDTH, HORIZON, VERTICAL, CORNER, OPACITY, BRIGHTNESS, IS_SHARP_COLOR, FEATHER
    DIA_HEIGHT = cv2.getTrackbarPos("height", WINDOW)
    DIA_WIDTH = cv2.getTrackbarPos("width", WINDOW)
    CORNER[0][0] = cv2.getTrackbarPos("corner_ur", WINDOW)
    CORNER[0][1] = cv2.getTrackbarPos("corner_ul", WINDOW)
    CORNER[1][0] = cv2.getTrackbarPos("corner_ll", WINDOW)
    CORNER[1][1] = cv2.getTrackbarPos("corner_lr", WINDOW)

    HORIZON = cv2.getTrackbarPos("horizon", WINDOW) * 0.01
    if HORIZON == 0:
        HORIZON = 0.01

    VERTICAL = cv2.getTrackbarPos("vertical", WINDOW) * 0.01
    if VERTICAL == 0:
        VERTICAL = 0.01

    OPACITY = cv2.getTrackbarPos("opacity", WINDOW) * 0.01

    sharp_color_flag = cv2.getTrackbarPos("sharp_color", WINDOW)
    IS_SHARP_COLOR = False if sharp_color_flag == 0 else True
    
    FEATHER = cv2.getTrackbarPos("feather", WINDOW)

    edit()

""" GUI initial settings """
def init_gui() -> None:
    # set name of the GUI window
    cv2.namedWindow(WINDOW, cv2.WINDOW_AUTOSIZE)

    # set callback function to reflect mouse operations
    cv2.setMouseCallback(WINDOW, callback)

    # trackbar related to mosaic area
    cv2.createTrackbar("height", WINDOW, 100, SRC.height, get_pram)  # height
    cv2.createTrackbar("width", WINDOW, 100, SRC.width, get_pram)  # width
    cv2.createTrackbar("corner_ul", WINDOW, 0, 100, get_pram)  # corner(upper left)
    cv2.createTrackbar("corner_ur", WINDOW, 0, 100, get_pram)  # corner(upper right)
    cv2.createTrackbar("corner_ll", WINDOW, 0, 100, get_pram)  # corner(lower left)
    cv2.createTrackbar("corner_lr", WINDOW, 0, 100, get_pram)  # corner(lower right)

    # trackbar related to mosaic detail options
    cv2.createTrackbar("horizon", WINDOW, 10, 100, get_pram)   # width of each mosaic cell
    cv2.createTrackbar("vertical", WINDOW, 10, 100, get_pram)  # height of each mosaic cell
    cv2.createTrackbar("opacity", WINDOW, 100, 100, get_pram)  # opacity of mosaic
    cv2.createTrackbar("sharp_color", WINDOW, 0, 1, get_pram)  # sharp coler
    cv2.createTrackbar("feather", WINDOW, 10, 100, get_pram)  # degree of blur the boundary of mosaic

    cv2.imshow(WINDOW, SRC.img)

main()