## author: xin luo 
# creat: 2023.2.19; # modify: 
# des: generate dem difference maps by using aster dems.
## usage: python scripts/dif_dems_srtm.py


dir_proj = '/home/xin/Developer-luo/Glacier-in-SETP'

import os, sys
sys.path.append(dir_proj)
import numpy as np
from glob import glob
from utils.geotif_io import readTiff, writeTiff
from utils.lay_stack import lay_stack

### Setting
# years = ['2000','2001','2002']
years = [ str(year) for year in range(2000,2023)]


dir_srtm_tiles = 'data/dem-data/srtm-c/tiles'
paths_srtm_tile = glob(dir_srtm_tiles+'/tile_??_??.tif')
paths_srtm_tile.sort()
tiles_id = [path_srtm_tile[-14:-4] for path_srtm_tile in paths_srtm_tile]


if __name__ == '__main__':
  for tile_id in tiles_id:
  # for tile_id in tile_ids[2:3]:    ### check 1 tile.
    ### 1. layer stacking of the dems and auxilary data.
    print('-------------------- Processing tile: %s ---------------------' % (tile_id))
    path_dems = [dir_proj + '/data/aster-stereo/SETP-%s/tiles-dem/'+ tile_id.replace('_', '-') + '/dems_mosaic_subs.tif' for tile_id in tiles_id]
    path_nodata = dir_proj + '/data/aster-stereo/tiles-nodata/' + tile_id + '.tif' 
    path_dems = [ path_dem if os.path.exists(path_dem) else path_nodata for path_dem in path_dems ]
    path_tile_save = dir_proj + '/data/aster-stereo/tiles-dif-map/' + tile_id + '.tif'
    ### Auxilary data
    path_srtm = dir_proj + '/data/dem-data/srtm-c/tiles/' + tile_id + '.tif'
    ### merge into one paths list
    paths_img = [path_srtm] + path_dems
    lay_stack(path_imgs=paths_img, path_out='dems_laysta.tif', extent_mode='union', res=None)  # Multitemporal dems layer stacking.
    ### 2. Multitemporal elevation changes calculating. 
    dems_laysta, dems_laysta_info = readTiff('dems_laysta.tif')
    num_dems = dems_laysta.shape[-1]-1
    print('Number of the dems: ', num_dems)
    dems_dif_map = np.zeros_like(dems_laysta[:,:,0:num_dems])
    for i in range(num_dems):
      dems_dif_map[:,:,i] = dems_laysta[:,:,i+1]-dems_laysta[:,:,0]  # calculate dems diffference.     
    ### 3. Mask the nodata region and the outlier data (elevation difference>150).    
    dems_dif_map = np.ma.masked_where(np.logical_or(dems_laysta[:,:,1:] == 0, abs(dems_dif_map)>150), dems_dif_map)
    ### 4. Write out the dems_change_map as geotiff format.
    writeTiff(im_data=dems_dif_map.filled(np.nan), im_geotrans=dems_laysta_info['geotrans'], 
                                              im_geosrs=dems_laysta_info['geosrs'], path_out=path_tile_save)
    os.remove('dems_laysta.tif')



