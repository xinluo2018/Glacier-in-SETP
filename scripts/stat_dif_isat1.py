## Author: xin luo
## create: 2023.3.18; modify: 2023.6.5
## des: statistic of the altimetry-based elevation difference between altimeter and srtm. 
##      output variables: mean value and standard deviation of the difference values for the 
##                        glacier and stable regions, respectively. 
##      the mean and standard deviation is calculated by bins and by years, and this script is only used for icesat-1 data processing.    


import os
os.chdir('/home/xin/Developer-luo/Glacier-in-SETP')
import h5py
import xarray as xr
import numpy as np
from glob import glob
from utils.geotif_io import readTiff
from utils.crop2extent import img2extent


### Note: the tiles should be merged firstly.
command_merge = 'python utils/merge_files.py data/icesat-1/tiles-dif-srtm/tile_??_??.h5 -o data/icesat-1/tiles-dif-srtm/tiles_merge.h5'
print(os.popen(command_merge).read())

### paths to be read in and write out.
path_dif_merge = 'data/icesat-1/tiles-dif-srtm/tiles_merge.h5'   ## path of data to read in
path_stat_dif = 'data/icesat-1/stat_dif_isat1.nc'      ## path to write out

### Parameters setting.
paths_dif_tiles = glob('data/icesat-1/tiles-dif-srtm/tile_??_??.h5')
paths_dif_tiles.sort()
tiles_id = [path_dif_tiles[-13:-3] for path_dif_tiles in paths_dif_tiles ]
years = [str(year) for year in range(2003, 2010)]
elev_start, elev_end, elev_bin = 2500, 7500, 500
bins_id = [str(elev_bin_start) + '-' + str(elev_bin_start+elev_bin) for \
                                    elev_bin_start in range(elev_start, elev_end, elev_bin)]
num_bins, num_tiles, num_years = len(bins_id), len(tiles_id), len(years)

### Define function 
def stat_years(altimeter_dict):
    mean_years = np.empty(shape=(num_years))
    std_years = np.empty(shape=(num_years))
    ### Looping for years
    for i_year, year in enumerate(years):
        year = float(year)
        ids_year = np.where((altimeter_dict['t_dyr']>year) & (altimeter_dict['t_dyr']<year+1))[0] 
        if ids_year.shape[0]>5:
            mean_dif = np.mean(altimeter_dict['h_dif'][ids_year])
            std_dif = np.std(altimeter_dict['h_dif'][ids_year])
        else:
            mean_dif, std_dif = np.nan, np.nan
        mean_years[i_year] = mean_dif
        std_years[i_year] = std_dif
    return mean_years, std_years

def stat_bins_years(altimeter_dict, ele_range=(2500, 7500), elev_bin = 100):
    mean_years_bins = np.empty(shape=(num_bins, num_years))
    std_years_bins = np.empty(shape=(num_bins, num_years))
    ### 1. Looping for years
    for i_year, year in enumerate(years):
        year = float(year)
        dif_year = {}
        ids_year = np.where((altimeter_dict['t_dyr']>year) & (altimeter_dict['t_dyr']<year+1))[0] 
        for key in altimeter_dict.keys(): 
            dif_year[key] = altimeter_dict[key][ids_year]     ## selected the data of one year.
        ### 2. Looping for bins
        for i_bin, elev_bin_start in enumerate(range(ele_range[0], ele_range[1], elev_bin)):
            elev_bin_end = elev_bin_start + elev_bin
            ids_year_bin = np.where((dif_year['h_srtm'] < elev_bin_end) & (dif_year['h_srtm']>elev_bin_start))[0]
            if ids_year_bin.shape[0]>=5:
                mean_year_bin = np.mean(dif_year['h_dif'][ids_year_bin])
                std_year_bin = np.std(dif_year['h_dif'][ids_year_bin])
            else:
                mean_year_bin, std_year_bin = np.nan, np.nan
            mean_years_bins[i_bin, i_year] = mean_year_bin
            std_years_bins[i_bin, i_year] = std_year_bin

    return mean_years_bins, std_years_bins


if __name__ == '__main__':

    ### 1) Glacier area of bins
    glacier_area_tiles_bins = np.empty(shape=(num_tiles, num_bins))
    print('------- Calculate glacier area of bins -------')
    for i_tile, tile_id in enumerate(tiles_id):
        path_glacier_tile = 'data/land-cover/rgi60/tiles/' + '/' + tile_id+'_albers.tif'
        path_srtm_tile_albers = 'data/dem-data/srtm-c/tiles/' + tile_id + '_albers.tif'  ## used for area calculation.
        print('srtm_tile_id:', path_srtm_tile_albers)
        srtm_tile_albers, srtm_tile_albers_info = readTiff(path_srtm_tile_albers)
        glacier_tile_mask = img2extent(path_img=path_glacier_tile, \
                                extent=srtm_tile_albers_info['geoextent'], size_target=srtm_tile_albers.shape) # read and resize
        dem_glacier = srtm_tile_albers*glacier_tile_mask
        for i_bin, elev_bin_head in enumerate(range(elev_start, elev_end, elev_bin)):
            ids_pixels_bin = np.where((dem_glacier > elev_bin_head) & (dem_glacier < elev_bin_head+elev_bin))[0]
            glacier_area_bin = ids_pixels_bin.shape[0]*0.03*0.03   ### the height and width of pixel is 0.03 km
            glacier_area_tiles_bins[i_tile, i_bin] = glacier_area_bin
    glacier_area_bins = np.sum(glacier_area_tiles_bins, axis=0)

    ### 2) statistic of the mean and standard deviation of difference value.
    print('------- statistic of the mean and standard deviation -------')
    f_read = h5py.File(path_dif_merge)
    dif_glacier_dict, dif_stable_dict = {}, {}
    ids_glacier = np.where(f_read['type_fp'][:]==2)[0]
    ids_stable = np.where(f_read['type_fp'][:]==1)[0]
    for key in f_read.keys():
        dif_glacier_dict[key] = f_read[key][ids_glacier]
        dif_stable_dict[key] = f_read[key][ids_stable]
    f_read.close()

    mean_stable_years, std_stable_years = stat_years(altimeter_dict=dif_stable_dict)
    mean_glacier_years_bins, std_glacier_years_bins = stat_bins_years(altimeter_dict=dif_glacier_dict, \
                                                                    ele_range=(elev_start, elev_end), elev_bin = elev_bin)

    ### 3) write out statistic of stable region to the xarray .nc file.
    if os.path.exists(path_stat_dif): os.remove(path_stat_dif)
    ### Conver to xarray data.
    stat_dif_xr =xr.Dataset(
            {"area_glacier_bins": (["bins_id"], glacier_area_bins),          
            "mean_glacier_bins": (["bins_id", "years"], mean_glacier_years_bins),         
            "std_glacier_bins": (["bins_id", "years"], std_glacier_years_bins),         
            "mean_stable_bins": (["years"], mean_stable_years),         
            "std_stable_bins": (["years"], std_stable_years),         
            },
            coords={'bins_id': bins_id,
                    'years': years})
    stat_dif_xr.to_netcdf(path_stat_dif)





