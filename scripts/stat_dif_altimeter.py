## Author: xin luo
## create: 2023.6.8;
## des: statistic of the altimetry-based elevation difference between altimeter and srtm. 
##        output variables: mean value and standard deviation of the difference values for the 
##                        glacier and stable regions, respectively. 
##              the mean and standard deviation is calculated by tiles and by bins and by years, 
##              this script is used for icesat-2 and cryosat-2 data processing.    
## usage: python scripts/stat_dif_altimeter.py -dtype icesat-2

import os
os.chdir('/home/xin/Developer-luo/Glacier-in-SETP')
import h5py
import xarray as xr
import numpy as np
from glob import glob
from utils.geotif_io import readTiff
from utils.crop2extent import img2extent
import argparse

# spatial_unit = 'tile'   ## 'tile
spatial_unit = 'tile_sub'   ## 'tile

def get_args():
    """ Get command-line arguments. """
    parser = argparse.ArgumentParser(
          description='get the date dyte of the processed data')
    parser.add_argument(
          '-dtype', metavar='dtype', type=str, nargs='+',
          help='the data type (icesat-2 or cryosat-2) of the processing data',
          default=['cryosat-2'])
    return parser.parse_args()

def outlier_remove_sigma(data, coef_sigma):
    data = data[~np.isnan(data)]
    if data.shape[0] != 0:
        mean_dif_year = np.mean(data)
        sigma_dif_year = np.std(data)
        thre_max, thre_min = mean_dif_year+coef_sigma*sigma_dif_year, mean_dif_year-coef_sigma*sigma_dif_year
        ids_filter = np.where((data > thre_min) & (data < thre_max))
        data_filter = data[ids_filter]
    else: data_filter = np.array([])
    return data_filter

### Function: statistics for stable region by years.
def stat_stable_years(altimeter_dict, num_years, coef_sigma=3):
    mean_years = np.empty(shape=(num_years))
    std_years = np.empty(shape=(num_years))
    ### Looping for years
    for i_year, year in enumerate(years):
        year = float(year)
        ids_year_stable = np.where((altimeter_dict['t_dyr']>year) & (altimeter_dict['t_dyr']<year+1) & \
                                                    (altimeter_dict['h_dif']<50) & (altimeter_dict['h_dif']>-50))
        points_sel = altimeter_dict['h_dif'][ids_year_stable]
        points_sel_filter = outlier_remove_sigma(data=points_sel, coef_sigma=coef_sigma)
        if points_sel_filter.shape[0]>=5:
            mean_dif_year, std_dif_year = np.mean(points_sel_filter), np.std(points_sel_filter)
        else:
            mean_dif_year, std_dif_year = np.nan, np.nan
        mean_years[i_year] = mean_dif_year
        std_years[i_year] = std_dif_year
    return mean_years, std_years


### Function: statistics for glacier region by bins and years.
def stat_glacier_bins_years(altimeter_dict, num_years, ele_range=(2500, 7500), elev_bin = 100, coef_sigma=3):
    mean_years_bins = np.empty(shape=(num_bins, num_years))
    std_years_bins = np.empty(shape=(num_bins, num_years))
    ### 1. Looping for years
    for i_year, year in enumerate(years):
        year = float(year)
        dif_year = {}
        ids_year = np.where((altimeter_dict['t_dyr']>year) & (altimeter_dict['t_dyr']<year+1) & \
                                                (altimeter_dict['h_dif']<100) & (altimeter_dict['h_dif']>-100))
        for key in altimeter_dict.keys():
            dif_year[key] = altimeter_dict[key][ids_year]     ## selected the data of one year.
        ### 2. Looping for bins
        for i_bin, elev_bin_start in enumerate(range(ele_range[0], ele_range[1], elev_bin)):
            elev_bin_end = elev_bin_start + elev_bin
            ids_year_bin = np.where((dif_year['h_srtm'] < elev_bin_end) & (dif_year['h_srtm']>elev_bin_start))
            points_sel = dif_year['h_dif'][ids_year_bin]
            points_sel_filter = outlier_remove_sigma(data=points_sel, coef_sigma=coef_sigma)
            if points_sel_filter.shape[0]>=5:
                mean_year_bin, std_year_bin = np.mean(points_sel_filter), np.std(points_sel_filter)
            else:
                mean_year_bin, std_year_bin = np.nan, np.nan
            mean_years_bins[i_bin, i_year] = mean_year_bin
            std_years_bins[i_bin, i_year] = std_year_bin
    return mean_years_bins, std_years_bins

if __name__ == '__main__':
    # extract arguments 
    args = get_args()
    dtype = args.dtype[0]
    print('------------- The processing data is %s -------------' % (dtype))

    ### paths to be read in and write out.
    if dtype == 'icesat-2':
        years = [str(year) for year in range(2018, 2023)]
        data_dir = 'data/icesat-2'
        if spatial_unit == 'tile_sub':
            path_stat_dif = data_dir + '/stat_dif_isat2_tiles_sub_bins.nc'  ## path to write out
        elif spatial_unit == 'tile':
            path_stat_dif = data_dir + '/stat_dif_isat2_tiles_bins.nc'      ## path to write out    
    elif dtype == 'cryosat-2':
        years = [str(year) for year in range(2010, 2023)]
        data_dir = 'data/cryosat-2'
        if spatial_unit == 'tile_sub':
            path_stat_dif = data_dir + '/stat_dif_cryo2_tiles_sub_bins.nc'      ## path to write out                
        elif spatial_unit == 'tile':
            path_stat_dif = data_dir + '/stat_dif_cryo2_tiles_bins.nc'      ## path to write out

    ### Parameters setting.
    if spatial_unit == 'tile_sub': dir_dif_srtm = 'tiles-sub-dif-srtm'; dir_tiles = 'tiles-sub'
    elif spatial_unit == 'tile': dir_dif_srtm = 'tiles-dif-srtm'; dir_tiles = 'tiles'
    paths_dif_tiles = glob(data_dir + '/' + dir_dif_srtm + '/tile_*.h5')

    paths_dif_tiles.sort()
    tiles_id = [path_dif_tiles.split('/')[-1].split('.')[0] for path_dif_tiles in paths_dif_tiles ]
    elev_start, elev_end, elev_bin = 2500, 7500, 100
    bins_id = [str(elev_bin_start) + '-' + str(elev_bin_start+elev_bin) for \
                                            elev_bin_start in range(elev_start, elev_end, elev_bin)]
    num_bins, num_tiles, num_years = len(bins_id), len(tiles_id), len(years)
    ### statistic for the glacier region
    mean_glacier_tiles_bins = np.empty(shape=(num_tiles, num_bins, num_years))
    std_glacier_tiles_bins = np.empty(shape=(num_tiles, num_bins, num_years))
    area_glacier_tiles_bins = np.empty(shape=(num_tiles, num_bins))
    ### statistic for the stable region
    mean_stable_tiles = np.empty(shape=(num_tiles, num_years))
    std_stable_tiles = np.empty(shape=(num_tiles, num_years))
    area_glacier_tiles = np.empty(shape=(num_tiles))

    for i_tile, tile_id in enumerate(tiles_id):
        print('...Tile id in processing:', tile_id)
        path_dif = data_dir + '/' + dir_dif_srtm + '/' + tile_id + '.h5'
        path_glacier_tile = 'data/land-cover/rgi60/'+dir_tiles+'/' + '/' + tile_id+'_albers.tif'
        path_srtm_tile_albers = 'data/dem-data/srtm-c/'+dir_tiles+'/' + tile_id + '_albers.tif'  ## used for area calculation.
        srtm_tile_albers, srtm_tile_albers_info = readTiff(path_srtm_tile_albers)        
        glacier_tile_mask = img2extent(path_img=path_glacier_tile, \
                                extent=srtm_tile_albers_info['geoextent'], size_target=srtm_tile_albers.shape) # read and resize
        dem_glacier = srtm_tile_albers*glacier_tile_mask
        
        ### glacier area by tiles
        ids_glacier_tile = np.where(glacier_tile_mask == 1)
        area_glacier_tiles[i_tile] = ids_glacier_tile[0].shape[0]*0.03*0.03   ### the height and width of pixel is 0.03 km

        ### glacier area by bins
        for i_bin, elev_bin_head in enumerate(range(elev_start, elev_end, elev_bin)):
            ids_pixels_bin = np.where((dem_glacier > elev_bin_head) & (dem_glacier < elev_bin_head+elev_bin))
            area_glacier_tile_bin = ids_pixels_bin[0].shape[0]*0.03*0.03   ### the height and width of pixel is 0.03 km
            area_glacier_tiles_bins[i_tile, i_bin] = area_glacier_tile_bin

        if not h5py.File(path_dif).keys():          ### if the tiled data is empty.
            print('--- this tiled data is empty!!!')
            mean_glacier_tiles_bins[i_tile,:,:], std_glacier_tiles_bins[i_tile,:,:] = np.nan, np.nan            
            mean_stable_tiles[i_tile], std_stable_tiles[i_tile] = np.nan, np.nan
            continue

        with h5py.File(path_dif) as dif_tile_read:
            dif_glacier_dict, dif_stable_dict = {}, {}
            ids_stable = np.where(dif_tile_read['type_fp'][:]==1)
            ids_glacier = np.where(dif_tile_read['type_fp'][:]==2)
            for key in dif_tile_read.keys():
                dif_stable_dict[key] = dif_tile_read[key][ids_stable]
                dif_glacier_dict[key] = dif_tile_read[key][ids_glacier]
            #### 1). Statistic of stable region.
            mean_stable_years, std_stable_years = stat_stable_years(dif_stable_dict, num_years, coef_sigma=2)
            mean_stable_tiles[i_tile], std_stable_tiles[i_tile] = mean_stable_years, std_stable_years
            #### 2). Statistic of glacier region.
            mean_glacier_tile_bins_years, std_glacier_tile_bins_years = stat_glacier_bins_years(dif_glacier_dict, \
                                                            num_years, ele_range=(elev_start, elev_end), elev_bin=elev_bin, coef_sigma=2) 
            mean_glacier_tiles_bins[i_tile,:,:], std_glacier_tiles_bins[i_tile,:,:] = mean_glacier_tile_bins_years, std_glacier_tile_bins_years


    ### 3) write out statistic of stable region to the xarray .nc file.
    if os.path.exists(path_stat_dif): os.remove(path_stat_dif)
    ### Conver to xarray data.
    stat_dif_xr =xr.Dataset(
            {"area_glacier_tiles": (["tiles_id"], area_glacier_tiles),          
            "area_glacier_tiles_bins": (["tiles_id", "bins_id"], area_glacier_tiles_bins),      
            "mean_glacier_tiles_bins": (["tiles_id", "bins_id", "years"], mean_glacier_tiles_bins),         
            "std_glacier_tiles_bins": (["tiles_id", "bins_id", "years"], std_glacier_tiles_bins),         
            "mean_stable_tiles": (["tiles_id", "years"], mean_stable_tiles),         
            "std_stable_tiles": (["tiles_id", "years"], std_stable_tiles),         
            },
            coords={'tiles_id': tiles_id,
                    'bins_id': bins_id,
                    'years': years})    
    stat_dif_xr.to_netcdf(path_stat_dif)

