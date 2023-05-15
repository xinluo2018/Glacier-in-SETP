## author: xin luo 
# creat: 2023.5.12; # modify: 
# des: statistic of the elevation difference maps tile by tile. 
##     the statistical indicators include mean and standar deviation.
## usage: python scripts/stat_dif_dems.py

import os
import h5py
import numpy as np
from glob import glob
from utils.geotif_io import readTiff
from utils.crop2extent import img2extent

dir_proj = '/home/xin/Developer-luo/Glacier-in-SETP'
paths_dif_tiles = glob('data/aster-stereo/tiles-dif-map/*_albers.tif')
paths_stat_dems = dir_proj+'/data/aster-stereo/stat_elev_dif.h5'


def stat_tile(glacier_mask, elev_dif_maps):
  mean_dif_tile, std_dif_tile = [], []
  for i in range(elev_dif_maps.shape[-1]):
    ids_pixels_tile = np.where((glacier_mask == 1) & (elev_dif_maps[:,:,i] >-150)& (elev_dif_maps[:,:,i] < 150))
    if ids_pixels_tile[0].shape[0] < 100:  ## the number of valid pixel should lager than 100.
      mean_dif_tile.append(np.nan)
      std_dif_tile.append(np.nan)
      continue
    else:
      mean_dif_tile_year = np.mean(elev_dif_maps[:,:,i][ids_pixels_tile])
      std_dif_tile_year = np.std(elev_dif_maps[:,:,i][ids_pixels_tile])
      mean_dif_tile.append(mean_dif_tile_year)
      std_dif_tile.append(std_dif_tile_year)
  return mean_dif_tile, std_dif_tile

def stat_glacier_bins(dem, glacier_mask, elev_dif_maps, elev_range=[2500, 7500], bin_range=100):
    glacier_area_bins, mean_dif_bins, std_dif_bins = {}, {}, {}
    dem_glacier = dem*glacier_mask
    elev_start, elev_end = elev_range
    num_bin = int((elev_end - elev_start)/bin_range)
    for i in range(num_bin):
        elev_start_bin, elev_end_bin = elev_start + i*bin_range, elev_start + (i+1)*bin_range
        ### 1) glacier area of bin
        # glacier_area_bins[str(elev_start_bin)+'_'+str(elev_end_bin)] = []
        ids_pixels_bin = np.where((dem_glacier > elev_start_bin) & (dem_glacier < elev_end_bin))
        glacier_area_bin = ids_pixels_bin[0].shape[0]*0.03*0.03   ### the height and width of pixel is 0.03 km
        glacier_area_bins[str(elev_start_bin)+'_'+str(elev_end_bin)] = glacier_area_bin
        ### 2) statistic (mean and std values) of bins
        mean_dif_bins[str(elev_start_bin)+'_'+str(elev_end_bin)] = []
        std_dif_bins[str(elev_start_bin)+'_'+str(elev_end_bin)] = []
        ## for each (year) elevation map.
        for i in range(elev_dif_maps.shape[-1]):
            ids_pixels_bin = np.where((dem_glacier > elev_start_bin) & (dem_glacier < elev_end_bin) & \
                                                        (elev_dif_maps[:,:,i] >-150)& (elev_dif_maps[:,:,i] < 150))
            if ids_pixels_bin[0].shape[0] > 100:
                ### mean and standard deviation of elevation difference of bin
                mean_dif_bins[str(elev_start_bin)+'_'+str(elev_end_bin)].append(np.mean(elev_dif_maps[:,:,i][ids_pixels_bin]))
                std_dif_bins[str(elev_start_bin)+'_'+str(elev_end_bin)].append(np.std(elev_dif_maps[:,:,i][ids_pixels_bin]))
            else:
                mean_dif_bins[str(elev_start_bin)+'_'+str(elev_end_bin)].append(np.nan)
                std_dif_bins[str(elev_start_bin)+'_'+str(elev_end_bin)].append(np.nan)

    return glacier_area_bins, mean_dif_bins, std_dif_bins 

if __name__ == '__main__':
    with h5py.File(paths_stat_dems, "w") as f:   
        for path_dif_tile in paths_dif_tiles:
            print('Processing tile: ', path_dif_tile)
            ### configuration
            full_name = os.path.basename(path_dif_tile)
            tile_id = os.path.splitext(full_name)[0][:10]
            path_glacier = 'data/rgi60/tiles/'+tile_id+'_albers.tif'
            path_srtm_albers = 'data/dem-data/srtm-c/tiles/' + tile_id + '_albers.tif'  ## used for area calculation.
            srtm_albers, srtm_albers_info = readTiff(path_srtm_albers)
            glacier_mask = img2extent(path_img=path_glacier, \
                                extent=srtm_albers_info['geoextent'], size_target=srtm_albers.shape) # read and resize
            elev_dif_maps = img2extent(path_img=path_dif_tile, \
                                extent=srtm_albers_info['geoextent'], size_target=srtm_albers.shape) # read and resize    

            ### 1) statistic for overall tile.
            mean_dif_tile, std_dif_tile = stat_tile(glacier_mask=glacier_mask, elev_dif_maps=elev_dif_maps)
            ### 2) statistic for each bin of tile.
            glacier_area_bins, mean_dif_bins, std_dif_bins = stat_glacier_bins(dem=srtm_albers, \
                            glacier_mask=glacier_mask, elev_dif_maps=elev_dif_maps, elev_range=[2500, 7500], bin_range=100)
            ### 3) write out to the .h5 file.
            f.create_dataset(tile_id+"/mean_dif_tile", data=mean_dif_tile)
            f.create_dataset(tile_id+"/std_dif_tile", data=std_dif_tile)
            for id_bin in list(glacier_area_bins.keys()):
                f.create_dataset(tile_id+"/glacier_area_bins/"+id_bin, data=np.array([glacier_area_bins[id_bin]]))
                f.create_dataset(tile_id+"/mean_dif_bins/"+id_bin, data=mean_dif_bins[id_bin])
                f.create_dataset(tile_id+"/std_dif_bins/"+id_bin, data=std_dif_bins[id_bin])


