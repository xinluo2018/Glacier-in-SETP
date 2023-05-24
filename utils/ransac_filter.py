## author: xin luo 
# creat: 2023.5.14; # modify: 2023.5.21
# des: filter out the outlier values with ransac algorithm.


import numpy as np
from sklearn import linear_model

def ransac_filter(x, y, thre):
    '''
    input:
        x,y: 1-dimension, np.array()
        thre: float, filter threshold corresponding to the difference between y and y_ransac 
    return: 
        y_filter: the filtered y
        y_ransac_fit: ransac fitting y
        ransac_coef: ransac fitting coefficient.
    '''
    x_new = x[~np.isnan(y)]
    y_new = y[~np.isnan(y)]
    ransac = linear_model.RANSACRegressor(random_state=42)
    x = np.array(x)[:, np.newaxis]
    x_new = np.array(x_new)[:, np.newaxis]
    ransac.fit(x_new, y_new)
    y_ransac_fit = ransac.predict(x)
    dif_y = np.array(abs(np.nan_to_num(y) - y_ransac_fit))
    y_filter = np.where(dif_y>thre, np.nan, y)
    ransac_coef = ransac.estimator_.coef_
    return y_filter, y_ransac_fit, ransac_coef