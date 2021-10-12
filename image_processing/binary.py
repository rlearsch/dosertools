import numpy as np
import skimage
import data_processing as dp

def bottom_border_white(image : skimage.io.ImageCollection) -> int:
    (height,width) = np.shape(image)
    sum_rows = np.sum(image, axis = 1)
    full_white_max = 255*width
    max_rows = list(sum_rows == full_white_max)
    if True in max_rows:
        bottom_c = np.argmax(sum_rows)
        return bottom_c

    white_runs = dp.array.continuous_nonzero(sum_rows)
    if len(white_runs) == 1:
        bottom_c = white_runs[0][1] - 10
    elif len(white_runs) > 1:
        bottom_c = white_runs[-1][0]
    elif len(white_runs) == 0:
        bottom_c = len(sum_rows)
    return bottom_c

    # need to understand each portion
    # is bottom_c guaranteed to return
    # need test images that hit each condition
    
