## Author: xin luo
## create: 2023.3.18; modify: 2023.6.5
## des: statistic of the altimetry-based elevation difference between altimeter and srtm. 
##      output variables: mean value and standard deviation of the difference values for the 
##                        glacier and stable regions, respectively. 
##      the mean and standard deviation is calculated by bins and by years, and this script is only used for icesat-1 data processing.    
## usage: python scripts/stat_dif_isat1.py


import os
os.chdir('/home/xin/Developer-luo/Glacier-in-SETP')
import h5py
import xarray as xr
import numpy as np
from glob import glob
from utils.geotif_io import readTiff
from utils.crop2extent import img2extent


### paths to be read in and write out.
# path_dif_merge = 'data/icesat-1/tiles-dif-srtm/tiles_merge.h5'   ## path of data to read in
path_stat_dif = 'data/icesat-1/stat_dif_isat1.nc'      ## path to write out

### Parameters setting.
paths_dif_tiles = glob('data/icesat-1/tiles-dif-srtm/tile_??_??.h5')
paths_dif_tiles.sort()
tiles_id = [path_dif_tiles[-13:-3] for path_dif_tiles in paths_dif_tiles ]
years = [str(year) for year in range(2003, 2010)]
num_tiles, num_years = len(tiles_id), len(years)


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

def stat_years_stable(altimeter_dict, coef_sigma):
    mean_years = np.empty(shape=(num_years))
    std_years = np.empty(shape=(num_years))
    ### Looping for years
    for i_year, year in enumerate(years):
        year = float(year)
        ids_year_valid = np.where((altimeter_dict['t_dyr']>year) & (altimeter_dict['t_dyr']<year+1) & \
                                                        (altimeter_dict['h_dif'] < 50) & (altimeter_dict['h_dif'] > -50)) 
        points_sel = altimeter_dict['h_dif'][ids_year_valid]
        points_sel_filter = outlier_remove_sigma(data=points_sel, coef_sigma=coef_sigma)
        if points_sel_filter.shape[0]>=5:
            mean_dif = np.mean(points_sel_filter)
            std_dif = np.std(points_sel_filter)
        else:
            mean_dif, std_dif = np.nan, np.nan
        mean_years[i_year] = mean_dif
        std_years[i_year] = std_dif
    return mean_years, std_years


### Define function 
def stat_years_glacier(altimeter_dict, coef_sigma):
    mean_years = np.empty(shape=(num_years))
    std_years = np.empty(shape=(num_years))
    ### Looping for years
    for i_year, year in enumerate(years):
        year = float(year)
        ids_year_valid = np.where((altimeter_dict['t_dyr']>year) & (altimeter_dict['t_dyr']<year+1) & \
                                                    (altimeter_dict['h_dif']<100) & (altimeter_dict['h_dif']>-100)) 
        points_sel = altimeter_dict['h_dif'][ids_year_valid]
        points_sel_filter = outlier_remove_sigma(data=points_sel, coef_sigma=coef_sigma)
        if points_sel_filter.shape[0]<5:
            mean_dif, std_dif = np.nan, np.nan    
        else:
            mean_dif = np.mean(points_sel_filter)
            std_dif = np.std(points_sel_filter)        
        mean_years[i_year] = mean_dif
        std_years[i_year] = std_dif
    return mean_years, std_years


if __name__ == '__main__':

    ### 1) Glacier area of bins
    area_glacier_tiles = np.empty(shape=(num_tiles))
    mean_stable_tiles_years = np.empty(shape=(num_tiles, num_years))
    std_stable_tiles_years = np.empty(shape=(num_tiles, num_years))
    mean_glacier_tiles_years = np.empty(shape=(num_tiles, num_years))
    std_glacier_tiles_years = np.empty(shape=(num_tiles, num_years))

    print('------- Calculate glacier area by tiles -------')
    for i_tile, tile_id in enumerate(tiles_id):
        path_glacier_tile = 'data/land-cover/rgi60/tiles/' + '/' + tile_id+'_albers.tif'
        path_srtm_tile_albers = 'data/dem-data/srtm-c/tiles/' + tile_id + '_albers.tif'  ## used for area calculation.
        path_dif_tile = 'data/icesat-1/tiles-dif-srtm/'+tile_id+'.h5'
        print('tile_id:', tile_id)
        srtm_tile_albers, srtm_tile_albers_info = readTiff(path_srtm_tile_albers)
        glacier_tile_mask = img2extent(path_img=path_glacier_tile, \
                                extent=srtm_tile_albers_info['geoextent'], size_target=srtm_tile_albers.shape) # read and resize
        dem_glacier = srtm_tile_albers*glacier_tile_mask

        ### 1) glacier area by tiles
        ids_glacier_tile = np.where(glacier_tile_mask == 1)[0]
        area_glacier_tiles[i_tile] = ids_glacier_tile.shape[0]*0.03*0.03   ### the height and width of pixel is 0.03 km

        ### 2) Statistic of the mean and standard deviation of difference value by tiles.
        f_read = h5py.File(path_dif_tile)
        dif_glacier_tile_dict, dif_stable_tile_dict = {}, {}
        ids_stable_tile = np.where(f_read['type_fp'][:]==1)
        ids_glacier_tile = np.where(f_read['type_fp'][:]==2)
        for key in f_read.keys():
            dif_glacier_tile_dict[key] = f_read[key][ids_glacier_tile]
            dif_stable_tile_dict[key] = f_read[key][ids_stable_tile]
        f_read.close()

        mean_stable_tile_years, std_tile_stable_years = stat_years_stable(altimeter_dict=dif_stable_tile_dict, coef_sigma=2)
        mean_glacier_tile_years, std_glacier_tile_years = stat_years_glacier(altimeter_dict=dif_glacier_tile_dict, coef_sigma=2)
        mean_stable_tiles_years[i_tile, :], std_stable_tiles_years[i_tile, :] = mean_stable_tile_years, std_tile_stable_years
        mean_glacier_tiles_years[i_tile, :], std_glacier_tiles_years[i_tile, :] = mean_glacier_tile_years, std_glacier_tile_years

    ### 3) write out statistic of stable region to the xarray .nc file.
    if os.path.exists(path_stat_dif): os.remove(path_stat_dif)
    ### Conver to xarray data.
    stat_dif_xr =xr.Dataset(
            {
            "area_glacier_tiles": (["tiles_id"], area_glacier_tiles),
            "mean_glacier_tiles_years": (["tiles_id", "years"], mean_glacier_tiles_years),         
            "std_glacier_tiles_years": (["tiles_id", "years"], std_glacier_tiles_years),         
            "mean_stable_tiles_years": (["tiles_id", "years"], mean_stable_tiles_years),         
            "std_stable_tiles_years": (["tiles_id", "years"], std_stable_tiles_years),         
            },
            coords={
                'tiles_id': tiles_id,
                'years': years,
                })
    stat_dif_xr.to_netcdf(path_stat_dif)



