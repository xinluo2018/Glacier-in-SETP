## Author: xin luo
## create: 2023.6.23;
## des: reprojection from the wgs84 projection to albers projection. 
## usage: python reproj2albers.py


from glob import glob
from utils.imgs_in_extent import imgs_in_extent
import matplotlib.pyplot as plt
import os


def reproj_imgs(path_imgs):
  '''
  args:
    path_imgs: paths of the images for reprojection.
  '''
  for path_img in path_imgs:
    path_out = path_img.split('.')[0] + '_albers.tif'
    command_reproj = 'gdalwarp -overwrite -dstnodata nan -s_srs EPSG:4326 -t_srs ' + proj_albers_china \
                                    + ' -tr 30 30 -r bilinear -co COMPRESS=LZW -co TILED=YES '+ path_img + ' ' + path_out
    print(os.popen(command_reproj).read())


### Define the area-equal projection
proj_albers_china = "'+proj=aea +ellps=krass +lon_0=105 +lat_1=25 +lat_2=47'"   ## Equal area projection for China

if __name__ == '__main__':
  # ### 1.dems difference map
  # dir_img_in = 'data/aster-stereo/tiles-sub-dif-map'
  # path_imgs = glob(dir_img_in + '/tile_???_???.tif')
  # reproj_imgs(path_imgs=path_imgs)


  # ### 2.srtm data
  # dir_img_in = 'data/dem-data/srtm-c/tiles-sub'
  # path_imgs = glob(dir_img_in + '/tile_???_???.tif')
  # reproj_imgs(path_imgs=path_imgs)


  # ### 3.RGI6.0 glacier data
  # dir_img_in = 'data/land-cover/rgi60/tiles-sub'
  # path_imgs = glob(dir_img_in + '/tile_???_???.tif')
  # reproj_imgs(path_imgs=path_imgs)


  ### 4.stable cover data
  dir_img_in = 'data/land-cover/stable-cover/tiles-sub-2010'
  path_imgs = glob(dir_img_in + '/tile_???_???.tif')
  reproj_imgs(path_imgs=path_imgs)


  # ### 5.JRC water 
  # dir_img_in = 'data/land-cover/water/water-jrc/tiles-sub'
  # path_imgs = glob(dir_img_in + '/tile_???_???.tif')
  # reproj_imgs(path_imgs=path_imgs)




