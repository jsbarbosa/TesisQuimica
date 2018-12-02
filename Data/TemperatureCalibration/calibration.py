import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import medfilt

def findZeros(ch1, ch2, ch3):
    y = np.zeros((len(ch1), 3))
    y[:, 0] = ch1[:, 1]
    y[:, 1] = ch2[:, 1]
    y[:, 2] = ch3[:, 1]
    
    y = np.mean(y, axis = 1)
    dy = abs(np.diff(y))
    abs_dy = np.zeros(len(dy) + 1)
    abs_dy[0] = dy[1]
    abs_dy[1:] = dy
    
    
    dy = medfilt(abs_dy, kernel_size = 507)
    pos = (dy > 5e-2)
    dy[pos] = 0.5
    dy[np.logical_not(pos)] = 0
    return abs_dy, dy
