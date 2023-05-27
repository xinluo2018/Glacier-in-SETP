## author: xin luo 
# creat: 2023.5.12; # modify: 
# des: statistic of the elevation differences on the glacier region tile by tile, and bin by bin. 
##     the statistical indicators include mean and standard deviation.
## usage: python ./scripts/stat_dems_glacier.py


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
paths_stat_dems = dir_proj+'/data/aster-stereo/stat_glacier_elev_dif.h5'


def stat_glacier_bins(dem_base, glacier_mask, elev_dif_maps, elev_range=[2500, 7500], bin_range=100, coef_sigma=3):
    """
    des: calculate glacier area for each bin, and mean and standard deviation for per tile and per bin.
    input: 
        dem_base: base dem image;
        glacier_mask: glacier mask image.
        elev_dif_maps: dems differences maps.
        elev_range: elevation range for the bins deteremination.
        bin_range: elevation range for each bin.
        coef_sigma: multiplier coefficient of the sigma for the outlier values filtering.
    return:     
        glacier_area_bins: glacier area of each bin.
        mean_dif_bins: mean value of the dem diferences of each bin. 
        std_dif_bins: standard value of the dem differences of each bin.       
    """

    glacier_area_bins, mean_dif_bins, std_dif_bins = {}, {}, {}
    dem_glacier = dem_base*glacier_mask
    elev_start, elev_end = elev_range
    num_bin = int((elev_end - elev_start)/bin_range)
    for i_bin in range(num_bin):
        elev_start_bin, elev_end_bin = elev_start + i_bin*bin_range, elev_start + (i_bin+1)*bin_range
        print('bin range: %s-%s.'%(elev_start_bin, elev_end_bin))
        ### 1) glacier area of bin
        ids_pixels_bin = np.where((dem_glacier > elev_start_bin) & (dem_glacier < elev_end_bin))
        glacier_area_bin = ids_pixels_bin[0].shape[0]*0.03*0.03   ### the height and width of pixel is 0.03 km
        glacier_area_bins[str(elev_start_bin)+'_'+str(elev_end_bin)] = glacier_area_bin
        ### 2) statistic (mean and std values) of bins
        mean_dif_bins[str(elev_start_bin)+'_'+str(elev_end_bin)] = []
        std_dif_bins[str(elev_start_bin)+'_'+str(elev_end_bin)] = []
        ## for each (year) elevation map.
        for i_dem in range(elev_dif_maps.shape[-1]):
            print('i_dem:', i_dem)
            #### 1. Elevation differences filtering by mean +- 3*sigma
            ids_dem_bin = np.where((dem_glacier > elev_start_bin) & (dem_glacier < elev_end_bin) & \
                                                        (elev_dif_maps[:,:,i_dem] > -150) & (elev_dif_maps[:,:,i_dem] < 150))            
            points_dem_bin = elev_dif_maps[:,:,i_dem][ids_dem_bin]
            print('Number of valid elevation differences:', ids_dem_bin[0].shape[0])
            if ids_dem_bin[0].shape[0] < 100:
                mean_dif_bins[str(elev_start_bin)+'_'+str(elev_end_bin)].append(np.nan)
                std_dif_bins[str(elev_start_bin)+'_'+str(elev_end_bin)].append(np.nan)
                continue
            elif ids_dem_bin[0].shape[0] >= 100:
                mean_dif_bin = np.mean(points_dem_bin)
                dif_sigma_bin = np.std(points_dem_bin)
                thre_max, thre_min = mean_dif_bin + coef_sigma*dif_sigma_bin, mean_dif_bin - coef_sigma*dif_sigma_bin
                ids_filter = np.where((points_dem_bin > thre_min) & (points_dem_bin < thre_max))
                points_dem_bin_filter = points_dem_bin[ids_filter]
                #### 2. Calculate the mean and standard deviation of the filtered elevation differences.
                num_filtered = points_dem_bin_filter.shape[0]
                print('Number of filtered elevation differences:', num_filtered)
                if num_filtered < 100:
                    mean_dif_bins[str(elev_start_bin)+'_'+str(elev_end_bin)].append(np.nan)
                    std_dif_bins[str(elev_start_bin)+'_'+str(elev_end_bin)].append(np.nan)
                    continue
                elif num_filtered >= 100:
                    ### mean and standard deviation of elevation difference of bin
                    mean_dif_bins[str(elev_start_bin)+'_'+str(elev_end_bin)].append(np.mean(points_dem_bin_filter))
                    std_dif_bins[str(elev_start_bin)+'_'+str(elev_end_bin)].append(np.std(points_dem_bin_filter))

    return glacier_area_bins, mean_dif_bins, std_dif_bins 


if __name__ == '__main__':
    if os.path.exists(paths_stat_dems): os.remove(paths_stat_dems)
    with h5py.File(paths_stat_dems, "w") as f:   
        for path_dif_tile in paths_dif_tiles:
            print('Processing tile: ', path_dif_tile)
            ### configuration
            full_name = os.path.basename(path_dif_tile)
            tile_id = os.path.splitext(full_name)[0][:10]
            path_glacier = 'data/land-cover/rgi60/tiles/'+tile_id+'_albers.tif'
            path_srtm_albers = 'data/dem-data/srtm-c/tiles/' + tile_id + '_albers.tif'  ## used for area calculation.
            srtm_albers, srtm_albers_info = readTiff(path_srtm_albers)
            glacier_mask = img2extent(path_img=path_glacier, \
                                extent=srtm_albers_info['geoextent'], size_target=srtm_albers.shape) # read and resize
            elev_dif_maps = img2extent(path_img=path_dif_tile, \
                                extent=srtm_albers_info['geoextent'], size_target=srtm_albers.shape) # read and resize    
            elev_dif_maps_ = np.nan_to_num(elev_dif_maps, nan=-999)    ### convert nan to -999.
            ### 1) statistic for each bin of tile.
            glacier_area_bins, mean_dif_bins, std_dif_bins = stat_glacier_bins(dem_base=srtm_albers, \
                    glacier_mask=glacier_mask, elev_dif_maps=elev_dif_maps_, elev_range=[2500, 7500], bin_range=100)
            ### 2) write out to the .h5 file.
            for id_bin in list(glacier_area_bins.keys()):
                f.create_dataset(tile_id+"/glacier_area_bins/"+id_bin, data=np.array([glacier_area_bins[id_bin]]))
                f.create_dataset(tile_id+"/mean_dif_bins/"+id_bin, data=mean_dif_bins[id_bin])
                f.create_dataset(tile_id+"/std_dif_bins/"+id_bin, data=std_dif_bins[id_bin])


