## author: xin luo 
# creat: 2023.2.19; # modify: 
# des: generate dem difference maps by using aster dems.
## usage: 


dir_proj = '/home/xin/Developer-luo/Glacier-in-SETP'

import os, sys
sys.path.append(dir_proj)
import numpy as np
from utils.geotif_io import readTiff, writeTiff
from utils.lay_stack import lay_stack

### Setting
years = ['2006','2007','2008', '2009', '2018','2019','2020','2021']
tile_ids = [(91,31),(92,31),(93,31),(94,31),(95,31),(91,30),(92,30),(93,30),(94,30),(95,30),(96,30),(97,30),
           (91,29),(92,29),(93,29),(94,29),(95,29),(96,29),(97,29),(98,29),(94,28),(95,28),(96,28),(97,28),(98,28),
           (96,27),(97,27),(98,27)]

if __name__ == '__main__':
  for tile_id in tile_ids:
  # for tile_id in tile_ids[2:3]:    ### check 1 tile.
    ### 1. layer stacking of the dems and auxilary data.
    tile_lat, tile_lon = str(tile_id[1]), str(tile_id[0])
    print('-------------------- Processing tile: tile_%s_%s ---------------------' % (tile_lat, tile_lon) )
    path_dems = [dir_proj + '/data/aster-stereo/SETP-%s/tiles-dem/tile-%s-%s/dems_mosaic_subs.tif' % (year, tile_lat, tile_lon) for year in years]
    path_nodata = dir_proj + '/data/aster-stereo/tiles-nodata/tile_%s_%s.tif' % (tile_lat, tile_lon) 
    path_dems = [ path_dem if os.path.exists(path_dem) else path_nodata for path_dem in path_dems ]
    path_tile_save = dir_proj + '/data/aster-stereo/tiles-dif-map/tile_%s_%s.tif' % (tile_lat, tile_lon)
    ### Auxilary data
    path_srtm = dir_proj + '/data/dem-data/srtm-c/tiles/tile_%s_%s.tif' % (tile_lat, tile_lon)
    path_glacier = dir_proj + '/data/rgi60/tiles/tile_%s_%s.tif' % (tile_lat, tile_lon)
    ### merge into one paths list
    paths_img = [path_srtm] + path_dems + [path_glacier]
    lay_stack(path_imgs=paths_img, path_out='dems_laysta.tif', extent_mode='union', res=None)  # Multitemporal dems layer stacking.
    dems, dems_info = readTiff('dems_laysta.tif')
    num_dems = dems.shape[-1]-2
    print('Number of the dems: ', num_dems)
    ### 2. Mask the nodata dem region and the non-glacier region for the dems.
    glacier_mask_3d = np.broadcast_to(dems[:,:,-1:], (dems.shape[0], dems.shape[1], dems.shape[2]))
    dems = np.ma.masked_where(np.logical_or(glacier_mask_3d == 0, dems == 0), dems) 
    ### Multitemporal elevation changes calculating. 
    dems_dif_map = np.zeros_like(dems.data[:,:,0:num_dems])
    for i in range(num_dems):
      dems_dif_map[:,:,i] = dems[:,:,0]-dems[:,:,i+1]  # calculate dems diffference.
      dems_dif_map[:,:,i] = np.where(dems.mask[:,:,i+1] == True, -999, dems_dif_map[:,:,i])  ## mask the non-dem and non-glacier region.
    dems_dif_map = np.ma.masked_where(np.logical_or(dems_dif_map==-999, abs(dems_dif_map)>150), dems_dif_map)
    ## 3. Filter out outliers of the dems (lower than mean - 3*sigma, or larger than mean - 3*sigma).
    dems_dif_filter = dems_dif_map.copy()
    for i_dem in range(dems_dif_map.shape[-1]):
    # for i_dem in range(1,2):
      print('Processing dem changes map %d' % (i_dem+1))
      num_valid = (~dems_dif_filter[:,:,i_dem].mask).sum()   ### number of the valid points
      # print('Number of valid dem change pixels: ', num_valid)
      if num_valid < 200 and num_valid > 0:
        dems_dif_filter[:,:,i_dem] = np.ma.masked_all(dems_dif_filter[:,:,i_dem].shape)
      else:
        dif_mean, dif_sigma = np.mean(dems_dif_filter), np.std(dems_dif_filter)
        thre_max, thre_min = dif_mean + 3*dif_sigma, dif_mean - 3*dif_sigma
        dems_dif_filter[:,:,i_dem] = np.ma.masked_where(np.logical_or(dems_dif_filter[:,:,i_dem]>thre_max, dems_dif_filter[:,:,i_dem]<thre_min), dems_dif_filter[:,:,i_dem])  
      num_filter = (~dems_dif_filter[:,:,i_dem].mask).sum()   ### number of the filtered points
      print('Number of filtered dem change pixels: ', num_filter)
      if num_filter < 200 and num_valid > 0:
        dems_dif_filter[:,:,i_dem] = np.ma.masked_all(dems_dif_filter[:,:,i_dem].shape)
    ### 4. write out the dems_change_map as geotiff format.
    writeTiff(im_data=dems_dif_filter.filled(-999), im_geotrans=dems_info['geotrans'], im_geosrs=dems_info['geosrs'], path_out=path_tile_save)
    os.remove('dems_laysta.tif')
