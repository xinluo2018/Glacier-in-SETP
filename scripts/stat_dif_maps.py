## author: xin luo 
# creat: 2023.5.12; # modify: 2023.6.4
# des: statistic of the dems-based elevation differences on 1) the glacier region by tiles and bins,
#      and 2）the stable region by tiles.
##     The statistical indicators include mean and standard deviation.
## usage: python ./scripts/stat_dems_glacier.py


dir_proj = '/home/xin/Developer-luo/Glacier-in-SETP'

import os, sys
sys.path.append(dir_proj)
import numpy as np
from glob import glob
import xarray as xr
from utils.geotif_io import readTiff
from utils.crop2extent import img2extent

### Paths/Files to be read in.
dir_proj = '/home/xin/Developer-luo/Glacier-in-SETP'
paths_dif_tiles = glob('data/aster-stereo/tiles-dif-map/*_albers.tif')
dir_glacier_tile = 'data/land-cover/rgi60/tiles'
dir_stable_tile = 'data/land-cover/stable-cover/tiles-2010'            
path_srtm_tile_albers = 'data/dem-data/srtm-c/tiles' 

### Path to be write out.
paths_stat_dif_dems = dir_proj+'/data/aster-stereo/stat_dif_tiles_bins.nc'

### Parameters setting
elev_bin_start, elev_bin_end, elev_bin = 2500, 7500, 100
bins_id = [str(i_ele) + '-' +str(i_ele+100) for i_ele in range(elev_bin_start, elev_bin_end, elev_bin)]
years = [str(year) for year in range(2000, 2022)]


def stat_dif_maps(stable_mask, elev_dif_maps, coef_sigma=3):
    """
    des: calculate mean and standard deviation for stable region for each difference map.
    input: 
        stable_mask: stable mask image.
        elev_dif_maps: dems differences maps.
        coef_sigma: multiplier coefficient of the sigma for the outlier values filtering.
    return:     
        mean_dif_maps: list, mean value of the diference maps. 
        std_dif_maps: list, standard value of the difference maps.       
    """
    mean_dif_maps, std_dif_maps = [], []
    ## for each (year) elevation map.
    for i_map in range(elev_dif_maps.shape[-1]):
        print('i_map:', i_map)
        #### 1. Elevation differences filtering by mean +- 3*sigma
        ids_map = np.where((stable_mask == 1) & (elev_dif_maps[:,:,i_map] > -150) & (elev_dif_maps[:,:,i_map] < 150))
        points_map = elev_dif_maps[:,:,i_map][ids_map]
        # print('Number of valid elevation differences:', ids_map[0].shape[0])
        if ids_map[0].shape[0] < 100:
            mean_dif_maps.append(np.nan)
            std_dif_maps.append(np.nan)
            continue
        elif ids_map[0].shape[0] >= 100:
            mean_dif = np.mean(points_map)
            sigma_dif = np.std(points_map)
            thre_max, thre_min = mean_dif + coef_sigma*sigma_dif, mean_dif - coef_sigma*sigma_dif
            ids_filter = np.where((points_map > thre_min) & (points_map < thre_max))
            points_map_filter = points_map[ids_filter]
            #### 2. Calculate the mean and standard deviation of the filtered elevation differences.
            num_filtered = points_map_filter.shape[0]
            # print('Number of filtered elevation differences:', num_filtered)
            if num_filtered < 100:
                mean_dif_maps.append(np.nan)
                std_dif_maps.append(np.nan)
                continue
            elif num_filtered >= 100:
                ### mean and standard deviation of elevation difference of bin
                mean_dif_maps.append(np.mean(points_map_filter))
                std_dif_maps.append(np.std(points_map_filter))
    return mean_dif_maps, std_dif_maps 

def stat_dif_maps_bins(glacier_mask, elev_dif_maps, dem_base, elev_range=[2500, 7500], bin_range=100, coef_sigma=3):
    """
    des: calculate glacier area, mean and standard deviation for each bin and \
         each difference map.
    input: 
        dem_base: base dem image;
        glacier_mask: glacier mask image.
        elev_dif_maps: dems differences maps.
        elev_range: elevation range for the bins deteremination.
        bin_range: elevation range for each bin.
        coef_sigma: multiplier coefficient of the sigma for the outlier values filtering.
    return:     
        glacier_area_bins: np.array(), glacier area of each bin.
        mean_dif_bins: np.array(), mean value of the dem diferences of each bin.
        std_dif_bins: np.array(), standard value of the dem differences of each bin.
    """

    # glacier_area_bins, mean_dif_bins, std_dif_bins = {}, {}, {}
    glacier_area_bins = np.empty(shape=(num_bins))
    mean_dif_bins = np.empty(shape=(num_bins, num_years))
    std_dif_bins = np.empty(shape=(num_bins, num_years))
    dem_glacier = dem_base*glacier_mask
    elev_start, elev_end = elev_range
    num_bin = int((elev_end - elev_start)/bin_range)
    for i_bin in range(num_bin):
        elev_start_bin, elev_end_bin = elev_start + i_bin*bin_range, elev_start + (i_bin+1)*bin_range
        print('bin range: %s-%s.'%(elev_start_bin, elev_end_bin))
        ### 1) glacier area of bin
        ids_pixels_bin = np.where((dem_glacier > elev_start_bin) & (dem_glacier < elev_end_bin))
        glacier_area_bin = ids_pixels_bin[0].shape[0]*0.03*0.03   ### the height and width of pixel is 0.03 km
        glacier_area_bins[i_bin] = glacier_area_bin
        ### 2) statistic (mean and std values) of bins
        for i_map in range(elev_dif_maps.shape[-1]):
            # print('i_dem:', i_dem)
            #### 1. Elevation differences filtering by mean +- 3*sigma
            ids_map_bin = np.where((dem_glacier > elev_start_bin) & (dem_glacier < elev_end_bin) & \
                                                (elev_dif_maps[:,:,i_map] > -150) & (elev_dif_maps[:,:,i_map] < 150))            
            points_map_bin = elev_dif_maps[:,:,i_map][ids_map_bin]
            # print('Number of valid elevation differences:', ids_dem_bin[0].shape[0])
            if ids_map_bin[0].shape[0] < 100:
                mean_dif_bins[i_bin, i_map] = np.nan
                std_dif_bins[i_bin, i_map] = np.nan
                continue
            elif ids_map_bin[0].shape[0] >= 100:
                mean_dif_bin = np.mean(points_map_bin)
                dif_sigma_bin = np.std(points_map_bin)
                thre_max, thre_min = mean_dif_bin + coef_sigma*dif_sigma_bin, mean_dif_bin - coef_sigma*dif_sigma_bin
                ids_filter = np.where((points_map_bin > thre_min) & (points_map_bin < thre_max))
                points_dem_bin_filter = points_map_bin[ids_filter]
                #### 2. Calculate the mean and standard deviation of the filtered elevation differences.
                num_filtered = points_dem_bin_filter.shape[0]
                # print('Number of filtered elevation differences:', num_filtered)
                if num_filtered < 100:
                    mean_dif_bins[i_bin, i_map] = np.nan
                    std_dif_bins[i_bin, i_map] = np.nan
                    continue
                elif num_filtered >= 100:
                    ### mean and standard deviation of elevation difference of bin
                    mean_dif_bins[i_bin, i_map] = np.mean(points_dem_bin_filter)
                    std_dif_bins[i_bin, i_map] = np.std(points_dem_bin_filter)
    return glacier_area_bins, mean_dif_bins, std_dif_bins 


if __name__ == '__main__':
    num_tiles, num_bins, num_years = len(paths_dif_tiles), (elev_bin_end-elev_bin_start)//elev_bin, len(years)
    ### statistic for the glacier region
    mean_glacier_tiles_bins = np.empty(shape=(num_tiles, num_bins, num_years))
    std_glacier_tiles_bins = np.empty(shape=(num_tiles, num_bins, num_years))
    area_glacier_tiles_bins = np.empty(shape=(num_tiles, num_bins))
    ### statistic for the stable region
    mean_stable_tiles = np.empty(shape=(num_tiles, num_years))
    std_stable_tiles = np.empty(shape=(num_tiles, num_years))
    area_glacier_tiles = np.empty(shape=(num_tiles))

    tiles_id = []
    for i, path_dif_tile in enumerate(paths_dif_tiles):
        print('Processing tile: ', path_dif_tile)
        ### configuration
        full_name = os.path.basename(path_dif_tile)
        tile_id = os.path.splitext(full_name)[0][:10]
        tiles_id.append(tile_id)
        path_stable_tile = dir_stable_tile + '/' + tile_id + '_albers.tif'            
        path_glacier_tile = dir_glacier_tile + '/' + tile_id+'_albers.tif'
        path_srtm_tile_albers = 'data/dem-data/srtm-c/tiles/' + tile_id + '_albers.tif'  ## used for area calculation.
        srtm_tile_albers, srtm_tile_albers_info = readTiff(path_srtm_tile_albers)

        stable_tile_mask = img2extent(path_img=path_stable_tile, \
                            extent=srtm_tile_albers_info['geoextent'], size_target=srtm_tile_albers.shape) # read and resize
        glacier_tile_mask = img2extent(path_img=path_glacier_tile, \
                            extent=srtm_tile_albers_info['geoextent'], size_target=srtm_tile_albers.shape) # read and resize
        elev_dif_tile_maps = img2extent(path_img=path_dif_tile, \
                            extent=srtm_tile_albers_info['geoextent'], size_target=srtm_tile_albers.shape) # read and resize    
        elev_dif_tile_maps_ = np.nan_to_num(elev_dif_tile_maps, nan=-999)    ### convert nan to -999.

        ### 1) statistic for stable region by tiles.
        mean_dif_tile, std_dif_tile = stat_dif_maps(stable_mask=stable_tile_mask, elev_dif_maps=elev_dif_tile_maps_, coef_sigma=3)
        ids_glacier_tile = np.where(glacier_tile_mask == 1)
        glacier_area_tile = ids_glacier_tile[0].shape[0]*0.03*0.03   ### the height and width of pixel is 0.03 km
        mean_stable_tiles[i,:] = mean_dif_tile
        std_stable_tiles[i,:] = std_dif_tile
        area_glacier_tiles[i] = glacier_area_tile

        ### 2) statistic for glacier region by maps and bins.
        glacier_area_tile_bins, mean_dif_tile_bins, std_dif_tile_bins = stat_dif_maps_bins(dem_base=srtm_tile_albers, \
                    glacier_mask=glacier_tile_mask, elev_dif_maps=elev_dif_tile_maps_, elev_range=[elev_bin_start, elev_bin_end], bin_range=elev_bin)
        mean_glacier_tiles_bins[i,:,:] = mean_dif_tile_bins
        std_glacier_tiles_bins[i,:,:] = std_dif_tile_bins
        area_glacier_tiles_bins[i,:] = glacier_area_tile_bins

    ### 3) write out statistic both on stable region and glacier regoin to the xarray .nc file.
    if os.path.exists(paths_stat_dif_dems): os.remove(paths_stat_dif_dems)
    ### Conver to xarray data.
    stat_dif_dems_xr =xr.Dataset(
            {"area_glacier_tiles": (["tiles_id"], area_glacier_tiles),     
             "area_glacier_tiles_bins": (["tiles_id", "bins_id"], area_glacier_tiles_bins),      
            "mean_stable_tiles": (["tiles_id", "years"], mean_stable_tiles),         
            "std_stable_tiles": (["tiles_id", "years"], std_stable_tiles),
            "mean_glacier_tiles_bins": (["tiles_id", "bins_id", "years"], mean_glacier_tiles_bins),         
            "std_glacier_tiles_bins": (["tiles_id", "bins_id", "years"], std_glacier_tiles_bins),          
            },
            coords={'tiles_id': tiles_id,
                    'bins_id': bins_id,
                    'years': years})
    stat_dif_dems_xr.to_netcdf(paths_stat_dif_dems)

