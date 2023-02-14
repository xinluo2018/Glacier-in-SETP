## author: xin luo 
## creat: 2022.3.16; modify: 2023.2.12
## des: layer stacking for remote sensing images

from osgeo import gdal
from osgeo import osr
import numpy as np
import argparse

def lay_stack(path_imgs, path_out, extent_mode='union', res=None):
    '''
    input:
    path_imgs: list, contains the paths of bands/imgs to be stacked
    path_out: str, the output path of the layer stacked image
    extent_mode: string, 'union', 'intersection' and 'img_1';
                 if union, true, the output extent is the extents union of input images. 
                 esif intersection, the output extent is the extents intersection of input images.
                 esif img_1, the output extent is the extents of input image 1.
    res: resolution of the layer stacked image. if not set, \
         the resolution of the first image of path_imgs is the default.
    note: the first image in the path_imgs is the reference image.
    '''

    ## base image
    left_min, right_min, bottom_min, up_min = float("inf"), float("inf"), float("inf"), float("inf")
    left_max, right_max, bottom_max, up_max = -float("inf"), -float("inf"), -float("inf"), -float("inf")
    for i, path_img in enumerate(path_imgs):
        img = gdal.Open(path_img, gdal.GA_ReadOnly)
        im_geotrans = img.GetGeoTransform()
        if i == 0:
            base_proj = img.GetProjection()
            dx, dy = im_geotrans[1], im_geotrans[5] # 
        im_x = img.RasterXSize  # 
        im_y = img.RasterYSize  # 
        left = im_geotrans[0]
        up = im_geotrans[3]
        right = left + im_geotrans[1] * im_x + im_geotrans[2] * im_y
        bottom = up + im_geotrans[5] * im_y + im_geotrans[4] * im_x
        if i == 0: extent_0 = [left, right, up, bottom]
        if left_min > left: left_min = left; 
        if right_min > right: right_min = right
        if up_min > up: up_min = up
        if bottom_min > bottom: bottom_min = bottom
        if left_max < left: left_max = left
        if right_max < right: right_max = right
        if up_max < up: up_max = up
        if bottom_max < bottom: bottom_max = bottom
    if extent_mode == 'img_1':
        extent = extent_0
    elif extent_mode == 'union':
        extent = [left_min, right_max, up_max, bottom_min]
    elif extent_mode == 'intersection':
        extent = [left_max, right_min, up_min, bottom_max]

    if res is not None:   # update the dx and dy
        dx, dy = res, -res

    base_x = int(np.round((extent[1] - extent[0]) / float(dx)))  # new col, integer
    base_y = int(np.round((extent[3] - extent[2]) / float(dy)))  # new row, integer
    base_dx = (extent[1] - extent[0]) / float(base_x)  # update dx and dy, may be a little bias with the original dx and dy.  
    base_dy = (extent[3] - extent[2]) / float(base_y)
    base_geotrans = (extent[0], base_dx, 0.0, extent[2], 0.0, base_dy)

    ## layer stacking 
    base_n = 0
    for i_img, path_stack in enumerate(path_imgs):
        ## image to be layer stacked
        stack_img = gdal.Open(path_stack)
        stack_Proj = stack_img.GetProjection()
        stack_n = stack_img.RasterCount

        ## align image to the base image
        driver= gdal.GetDriverByName('GTiff')
        stack_align = driver.Create(path_out, base_x, base_y, stack_n, gdal.GDT_Float32)
        stack_align.SetGeoTransform(base_geotrans)
        stack_align.SetProjection(base_proj)
        gdal.ReprojectImage(stack_img, stack_align, stack_Proj, base_proj, gdal.GRA_Bilinear)

        ## layer stacking
        n_bands = base_n+stack_n
        img_stack = driver.Create(path_out, base_x, base_y, n_bands, gdal.GDT_Float32)

        if(img_stack!= None):
            img_stack.SetGeoTransform(base_geotrans)       # 
            img_stack.SetProjection(base_proj)      # 
        for i_band in range(base_n):
            img_stack.GetRasterBand(i_band+1).WriteArray(base_img.GetRasterBand(i_band+1).ReadAsArray())
        for i_band in range(stack_n):
            img_stack.GetRasterBand(base_n+i_band+1).WriteArray(stack_align.GetRasterBand(i_band+1).ReadAsArray())
        ## update base image
        base_n = n_bands
        base_img = img_stack
    print('Images layer stacking done.')
    del img_stack, base_img, stack_img 


def get_args():

    """ Get command-line arguments. """
    parser = argparse.ArgumentParser(
            description='layer stacking for remote sensing images')
    parser.add_argument(
            'path_imgs', metavar='path_imgs', type=str, nargs='*',
            help='contains the paths of bands/imgs to be stacked')
    parser.add_argument(
            'path_out', metavar='path_out', type=str, nargs='+',
            help='the output path of the layer stacked image')
    parser.add_argument(
            '--extent_mode',
            choices=('union','intersection', 'img_1'),
            default='union')
    parser.add_argument(
            '--resolution', type=int, nargs=1,
            help='resolution of the output image',
            default=[None])
    return parser.parse_args()


if __name__ == '__main__':

    # extract arguments 
    args = get_args()
    path_imgs = args.path_imgs
    path_out = args.path_out[0]
    extent_mode = args.extent_mode
    res = args.resolution[0]
    lay_stack(path_imgs, path_out, extent_mode, res)

