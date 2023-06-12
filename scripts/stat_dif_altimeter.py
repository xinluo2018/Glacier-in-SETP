## Author: xin luo
## create: 2023.6.8;
## des: statistic of the altimetry-based elevation difference between altimeter and srtm. 
##        output variables: mean value and standard deviation of the difference values for the 
##                        glacier and stable regions, respectively. 
##              the mean and standard deviation is calculated by tiles and by bins and by years, 
##              this script is used for icesat-2 cryosat-2 data processing.    


import os
os.chdir('/home/xin/Developer-luo/Glacier-in-SETP')
import h5py
import xarray as xr
import numpy as np
from glob import glob
from utils.geotif_io import readTiff
from utils.crop2extent import img2extent


### paths to be read in and write out.
path_stat_dif = 'data/icesat-2/stat_dif_isat2.nc'      ## path to write out

### Parameters setting.
paths_dif_tiles = glob('data/icesat-1/tiles-dif-srtm/tile_??_??.h5')
paths_dif_tiles.sort()
tiles_id = [path_dif_tiles[-13:-3] for path_dif_tiles in paths_dif_tiles ]
years = [str(year) for year in range(2018, 2023)]
elev_start, elev_end, elev_bin = 2500, 7500, 100
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
        path_dif = 'data/icesat-2/tiles-dif-srtm/' + tile_id + '.h5'
        path_glacier_tile = 'data/land-cover/rgi60/tiles/' + '/' + tile_id+'_albers.tif'
        path_srtm_tile_albers = 'data/dem-data/srtm-c/tiles/' + tile_id + '_albers.tif'  ## used for area calculation.
        srtm_tile_albers, srtm_tile_albers_info = readTiff(path_srtm_tile_albers)        
        glacier_tile_mask = img2extent(path_img=path_glacier_tile, \
                                extent=srtm_tile_albers_info['geoextent'], size_target=srtm_tile_albers.shape) # read and resize
        dem_glacier = srtm_tile_albers*glacier_tile_mask
        with h5py.File(path_dif) as dif_tile_read:
            dif_glacier_dict, dif_stable_dict = {}, {}
            ids_stable = np.where(dif_tile_read['type_fp'][:]==1)[0]
            ids_glacier = np.where(dif_tile_read['type_fp'][:]==2)[0]
            for key in dif_tile_read.keys():
                dif_stable_dict[key] = dif_tile_read[key][ids_stable]
                dif_glacier_dict[key] = dif_tile_read[key][ids_glacier]
            ids_glacier_tile = np.where(glacier_tile_mask == 1)[0]
            area_glacier_tile = ids_glacier_tile.shape[0]*0.03*0.03   ### the height and width of pixel is 0.03 km
            #### 1). Statistic of stable region.
            area_glacier_tiles[i_tile] = area_glacier_tile
            mean_stable_years, std_stable_years = stat_years(dif_stable_dict)
            mean_stable_tiles[i_tile], std_stable_tiles[i_tile] = mean_stable_years, std_stable_years
            #### 2). Statistic of glacier region.
            for i_bin, elev_bin_head in enumerate(range(elev_start, elev_end, elev_bin)):
                ids_pixels_bin = np.where((dem_glacier > elev_bin_head) & (dem_glacier < elev_bin_head+elev_bin))[0]
                area_glacier_tile_bin = ids_pixels_bin.shape[0]*0.03*0.03   ### the height and width of pixel is 0.03 km
                area_glacier_tiles_bins[i_tile, i_bin] = area_glacier_tile_bin
            mean_glacier_tile_bins_years, std_glacier_tile_bins_years  = stat_bins_years(dif_glacier_dict, \
                                                                            ele_range=(elev_start, elev_end), elev_bin=elev_bin) 
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



