## author: xin luo 
# creat: 2023.5.12; # modify: 
# des: statistic of the elevation differences on the stable region tile by tile. 
##     the statistical indicators include mean and standard deviation.
## usage: python ./scripts/stat_dems_stable.py

dir_proj = '/home/xin/Developer-luo/Glacier-in-SETP'

import os, sys
sys.path.append(dir_proj)
import h5py
import numpy as np
from glob import glob
from utils.geotif_io import readTiff
from utils.crop2extent import img2extent

dir_proj = '/home/xin/Developer-luo/Glacier-in-SETP'
paths_dif_tiles = glob('data/aster-stereo/tiles-dif-map/*_albers.tif')
paths_stat_dems = dir_proj+'/data/aster-stereo/stat_stable_elev_dif.h5'

def stat_stable(stable_mask, elev_dif_maps, coef_sigma=3):
    """
    des: calculate mean and standard deviation for stable region for each tile.
    input: 
        dem_base: base dem image;
        stable_mask: stable mask image.
        elev_dif_maps: dems differences maps.
        coef_sigma: multiplier coefficient of the sigma for the outlier values filtering.
    return:     
        mean_dif_tiles: mean value of the dem diferences of each tile. 
        std_dif_tiles: standard value of the dem differences of each tile.       
    """

    mean_dif_dems, std_dif_dems = [], []
    ## for each (year) elevation map.
    for i_dem in range(elev_dif_maps.shape[-1]):
        print('i_dem:', i_dem)
        #### 1. Elevation differences filtering by mean +- 3*sigma
        ids_dem = np.where((stable_mask == 1) & (elev_dif_maps[:,:,i_dem] > -150) & (elev_dif_maps[:,:,i_dem] < 150))
        points_dem = elev_dif_maps[:,:,i_dem][ids_dem]
        print('Number of valid elevation differences:', ids_dem[0].shape[0])
        if ids_dem[0].shape[0] < 100:
            mean_dif_dems.append(np.nan)
            std_dif_dems.append(np.nan)
            continue
        elif ids_dem[0].shape[0] >= 100:
            mean_dif = np.mean(points_dem)
            sigma_dif = np.std(points_dem)
            thre_max, thre_min = mean_dif + coef_sigma*sigma_dif, mean_dif - coef_sigma*sigma_dif
            ids_filter = np.where((points_dem > thre_min) & (points_dem < thre_max))
            points_dem_filter = points_dem[ids_filter]
            #### 2. Calculate the mean and standard deviation of the filtered elevation differences.
            num_filtered = points_dem_filter.shape[0]
            print('Number of filtered elevation differences:', num_filtered)
            if num_filtered < 100:
                mean_dif_dems.append(np.nan)
                std_dif_dems.append(np.nan)
                continue
            elif num_filtered >= 100:
                ### mean and standard deviation of elevation difference of bin
                mean_dif_dems.append(np.mean(points_dem_filter))
                std_dif_dems.append(np.std(points_dem_filter))
    return mean_dif_dems, std_dif_dems 

if __name__ == '__main__':
    if os.path.exists(paths_stat_dems): os.remove(paths_stat_dems)
    with h5py.File(paths_stat_dems, "w") as f:   
        for path_dif_tile in paths_dif_tiles:
            print('Processing tile: ', path_dif_tile)
            ### configuration
            full_name = os.path.basename(path_dif_tile)
            tile_id = os.path.splitext(full_name)[0][:10]
            path_stable = 'data/land-cover/stable-cover/tiles-2010/'+tile_id+'_albers.tif'            
            path_glacier = 'data/land-cover/rgi60/tiles/'+tile_id+'_albers.tif'
            elev_dif_maps, elev_dif_maps_info = readTiff(path_dif_tile)
            glacier_mask = img2extent(path_img=path_glacier, \
                                extent=elev_dif_maps_info['geoextent'], size_target=elev_dif_maps.shape[0:2]) # read and resize
            stable_mask = img2extent(path_img=path_stable, \
                            extent=elev_dif_maps_info['geoextent'], size_target=elev_dif_maps.shape[0:2]) # read and resize
            elev_dif_maps_ = np.nan_to_num(elev_dif_maps, nan=-999)    ### convert nan to -999.
            ids_glacier_tile = np.where(glacier_mask == 1)
            glacier_area_tile = ids_glacier_tile[0].shape[0]*0.03*0.03   ### the height and width of pixel is 0.03 km

            ### 1) statistic for each tile.
            mean_dif, std_dif = stat_stable(stable_mask=stable_mask, elev_dif_maps=elev_dif_maps_, coef_sigma=3)
            ### 2) write out to the .h5 file.
            f.create_dataset(tile_id+"/glacier_area", data=np.array([glacier_area_tile]))
            f.create_dataset(tile_id+"/mean_dif", data=mean_dif)
            f.create_dataset(tile_id+"/std_dif", data=std_dif)


