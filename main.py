# code to select rois' from dorsal cortex of mouse

import numpy as np
import scipy.io as sio
import matplotlib.pyplot as plt

from utils import mark_class

fname = '/home/cat/Downloads/allenDorsalMap.mat'

mark = mark_class()

mark.load_mat(fname)

mark.mark_ROI()

