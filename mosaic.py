# coding: UTF-8

import cv2 as cv
import numpy

def _mosaic(src: numpy.ndarray, horizon: float,
            vertical: float, is_sharp: bool) -> numpy.ndarray:
    result = src.copy()
    src_height, src_width, _ = src.shape

    # length of each mosaic cell
    cell_height = int(src_height * horizon)
    cell_width = int(src_width * vertical)

    if is_sharp is False:
        # create mosaic by scaling
        small = cv.resize(src, None, fx=1 / cell_width, fy=1 / cell_height,
                          interpolation=cv.INTER_AREA)
        return cv.resize(small, src.shape[:2][::-1],
                         interpolation=cv.INTER_NEAREST)
    else:  # apply sharp color (specify the central pixel of original range as mosaic color)
        for y in range(0, src_height, cell_height):
            for x in range(0, src_width, cell_width):
                # calculate the length that protrude from the mosaic applied area
                x_over, y_over = 0, 0
                if src_width - cell_width < x:
                    x_over = cell_width - (src_width - x)
                if src_height - cell_height < y:
                    y_over = cell_height - (src_height - y)

                # get central pixel color of each mosaic tile
                center_y = y - y_over + (cell_height // 2)
                center_x = x - x_over + (cell_width // 2)
                b, g, r = src[center_y, center_x]

                # change color of each mosaic tile into one color
                blank = numpy.zeros((cell_height - y_over,
                                     cell_width - x_over, 3))
                blank += [r, g, b][::-1]
                result[y:y + cell_height - y_over,
                       x:x + cell_width - x_over] = blank
        return result


"""create mask image"""
def _mask_with_img(mask: numpy.ndarray,
                   height: int, width: int) -> numpy.ndarray:
    m_height, m_width, _ = mask.shape
    # calculate the expansion rate of mask image
    if float(height) / m_height > float(width) / m_width:
        resize_ratio = float(height) / m_height
    else:
        resize_ratio = float(width) / m_width

    resize_height = int(m_height * resize_ratio)
    resize_width = int(m_width * resize_ratio)
    return cv.resize(mask, (resize_height, resize_width))

""" transform the mosaic or blur part into ellipse shape """
def _make_ellipse(clip: numpy.ndarray, dst: numpy.ndarray, size: tuple, corner: list) -> numpy.ndarray:
    # draw ellipse
    cv.ellipse(clip, size, size, 0, 0, 360, (0, 0, 0), -1)

    # specify each corner angle of ellipse
    cv.ellipse(clip, size, size, 0, 0, 90, (0, 0, 0), corner[1][1])
    cv.ellipse(clip, size, size, 0, 90, 180, (0, 0, 0), corner[1][0])
    cv.ellipse(clip, size, size, 0, 180, 270, (0, 0, 0), corner[0][1])
    cv.ellipse(clip, size, size, 0, 270, 360, (0, 0, 0), corner[0][0])

    # create a mask to transform the mosaic or blur part
    black = numpy.array([0, 0, 0])
    mask = cv.inRange(clip.copy(), black, black)

    dst = cv.bitwise_and(dst, dst, mask=mask)
    return dst + clip

""" blur the boundary of mask edge """
def _blur_mask_edge(original_img: numpy.ndarray,
                    edited_img: numpy.ndarray, contours: list,
                    feather: int, opacity: float = 0) -> numpy.ndarray:
    frame_height, frame_width, _ = edited_img.shape
    black_img = numpy.zeros((frame_height, frame_width), dtype=numpy.uint8)


    feather_mask = cv.drawContours(black_img, contours, -1, (255, 255, 255), thickness=feather)

    if 1 < feather:
        feather_mask = cv.drawContours(black_img, contours, -1,
                                       (0, 0, 0), thickness=feather-1)
    feather_mask_inv = cv.bitwise_not(feather_mask)

    masked_original_img = cv.bitwise_and(original_img, original_img, mask=feather_mask)
    masked_edited_img = cv.bitwise_and(edited_img, edited_img, mask=feather_mask_inv)

    union_img = masked_edited_img + masked_original_img
    union_img = cv.addWeighted(edited_img, 1 - opacity, union_img, opacity, 0)

    if opacity == 0:
        for f in range(1, feather):
            opacity += 1 / feather
            union_img = _blur_mask_edge(original_img, union_img, contours, feather - f, opacity=opacity)

    return union_img


def add_mosaic(
        frame: numpy.ndarray, # source image
        dia_height: int, # diameter of mosaic
        dia_width: int, # diameter of mosaic
        y: int, # center of mosaic scope
        x: int, # center of mosaic scope
        corner: list = [[0, 0], [0, 0]], # 0 - 100 , [[upper left, upper right], [lower left, lower right]]
        horizon: float = 0.06, # 0.00 - 1.00
        vertical: float = 0.06, # 0.00 - 1.00
        opacity: float = 0.9, # 0.00 - 1.00
        feather: int = 30,
        is_sharp_color: bool = False, # apply sharp color or not
        mode: str = 'M', # drawing mode
        image_mask: numpy.ndarray = None) -> numpy.ndarray: 

    dia_height = int(dia_height)
    dia_width = int(dia_width)
    y = int(y)
    x = int(x)

    result_img: numpy.ndarray = frame.copy() 

    # calculate radius
    height = dia_height // 2
    width = dia_width // 2

    # define the scope of application image processing
    sx = x - width if width < x else 0
    sy = y - height if height < y else 0
    ex = x + width
    ey = y + height

    # original image in the scope
    clip = frame[sy:ey, sx:ex].copy()

    dst: numpy.ndarray

    if mode == 'M':
        dst = _mosaic(clip, horizon, vertical, is_sharp_color)
    if mode == 'B':
        dst = cv.blur(clip, (5, 5), 0)
    if mode == 'I': 
        dst = _mask_with_img(image_mask, height*2, width*2)
        ey = sy+dst.shape[0]
        ex = sx+dst.shape[1]
        result_img[sy:ey, sx:ex] = cv.addWeighted(
            result_img[sy:ey, sx:ex], 1-opacity, dst, opacity, 0)
        return result_img


    dst = _make_ellipse(clip, dst, (width, height), corner)

    result_img[sy:ey, sx:ex] = cv.addWeighted(result_img[sy:ey, sx:ex], 1.0-opacity, dst, opacity, 0)

    # get mask edge
    black = numpy.array([0, 0, 0])
    frame_height, frame_width, _ = frame.shape
    contours_mask = numpy.zeros((frame_height, frame_width), dtype=numpy.uint8)
    contours_mask[sy:ey, sx:ex] = cv.inRange(clip.copy(), black, black)
    contours, _ = cv.findContours(contours_mask,
                                  cv.RETR_TREE,
                                  cv.CHAIN_APPROX_SIMPLE)

    # blur mask edge
    result_img = _blur_mask_edge(frame, result_img, contours, feather)

    return result_img