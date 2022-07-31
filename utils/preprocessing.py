# https://github.com/denizlab/oai-xray-tkr-klg/blob/master/ExtractKnee/utils.py
    
import os
import numpy as np
import pydicom as dicom
import cv2
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
import scipy.ndimage as ndimage
import h5py
import pandas as pd
import time
import os
import numpy as np
import pydicom as dicom
import cv2
import matplotlib.pyplot as plt
import matplotlib.patches as patches


def image_preprocessing(file_path = '../data/9000296'):
    '''
    :param file_path:
    :return:
    '''
    # read data from DICOM file
    data = dicom.read_file(file_path)
    photoInterpretation = data[0x28,0x04].value # return a string of photometric interpretation
    #print('######### PHOTO INTER {} #########'.format(photoInterpretation))
    if photoInterpretation not in ['MONOCHROME2','MONOCHROME1']:
        raise ValueError('Wrong Value of Photo Interpretation: {}'.format(photoInterpretation))
    img = interpolate_resolution(data).astype(np.float64) # get fixed resolution
    img_before = img.copy()
    if photoInterpretation == 'MONOCHROME1':
        img = invert_Monochrome1(img)
    # apply normalization, move into hist_truncation.
    # img = global_contrast_normalization(img)
    # apply hist truncation
    img = hist_truncation(img)
    # get center part of image if image is large enough
    return img, data, img_before


def invert_Monochrome1(image_array):
    '''
    Image with dicome attribute [0028,0004] == MONOCHROME1 needs to
    be inverted. Otherwise, our way to detect the knee will not work.
    :param image_array:
    :return:
    '''
    image_array = image_array.max() - image_array
    return image_array


def interpolate_resolution(image_dicom, scaling_factor=0.2):
    '''
    Obtain fixed resolution from image dicom
    :param image_dicom:
    :param scaling_factor:
    :return:
    '''
    image_array = image_dicom.pixel_array
    try:
        x = image_dicom[0x28, 0x30].value[0]
        y = image_dicom[0x28, 0x30].value[1]
        image_array = ndimage.zoom(image_array, [x / scaling_factor, y / scaling_factor])
    except KeyError:
        pass
    return image_array


def get_center_image(img,img_size = (2048,2048)):
    '''
    Get the center of image
    :param img:
    :param img_size:
    :return:
    '''
    rows, cols = img.shape
    center_x = rows // 2
    center_y = cols // 2
    img_crop = img[center_x - img_size[0] // 2: center_x + img_size[0] // 2,
                   center_y - img_size[1] // 2: center_y + img_size[1] // 2]
    return img_crop


def padding(img, img_size = (2048,2048)):
    '''
    Padding image array to a specific size
    :param img:
    :param img_size:
    :return:
    '''
    rows,cols = img.shape
    x_padding = img_size[0] - rows
    y_padding = img_size[1] - cols
    if x_padding > 0:
        before_x,after_x = x_padding // 2, x_padding - x_padding // 2
    else:
        before_x,after_x = 0,0
    if y_padding > 0:
        before_y,after_y = y_padding // 2, y_padding - y_padding // 2
    else:
        before_y,after_y = 0,0
    return np.pad(img, ((before_x, after_x), (before_y, after_y), ), 'constant', constant_values=0), before_x, before_y


def global_contrast_normalization_oulu(img,lim1,multiplier = 255):
    '''
    This part is taken from oulu's lab. This how they did global contrast normalization.
    :param img:
    :param lim1:
    :param multiplier:
    :return:
    '''
    img -= lim1
    img /= img.max()
    img *= multiplier
    return img


def global_contrast_normalization(img, s=1, lambda_=10, epsilon=1e-8):
    '''
    Apply global contrast normalization based on image array.
    Deprecated since it is not working ...
    :param img:
    :param s:
    :param lambda_:
    :param epsilon:
    :return:
    '''
    # replacement for the loop
    X_average = np.mean(img)
    img_center = img - X_average

    # `su` is here the mean, instead of the sum
    contrast = np.sqrt(lambda_ + np.mean(img_center ** 2))

    img = s * img_center / max(contrast, epsilon)
    return img


def hist_truncation(img,cut_min=5,cut_max=99):
    '''
    Apply 5th and 99th truncation on the figure.
    :param img:
    :param cut_min:
    :param cut_max:
    :return:
    '''
    lim1,lim2 = np.percentile(img,[cut_min, cut_max])
    img_ = img.copy()
    img_[img < lim1] = lim1
    img_[img > lim2] = lim2
    img_ = global_contrast_normalization(img_)
    return img_