## author: xin luo 
# creat: 2023.6.7; 
# des: Area weighting by tiles and bins in the statistics.

import numpy as np
# import matplotlib.pyplot as plt
# import h5py
# from utils.ransac_fitting import ransac_fitting
# import pandas as pd
# import xarray as xr



def stat_tiles_weighting(mean_tiles, std_tiles, glacier_area_tiles):
    """
    des: tiles-based glacier area weighted elevation change calculation.
    args:
        mean_tiles: xarray.DataArray, (tiles_id, years), mean elevation change for each tile.
        std_tiles: xarray.DataArray, (tiles_id, years), standard deviation of elevation change for each tile.
        glacier_area_tiles: xarray.DataArray, (tiles_id), glacier area for each tile.
    return: 
        mean_setp_tilesWeighted: xr.dataarray, glacier-area weighted mean elevation change for overall setp. 
        std_setp_tilesWeighted:  xr.dataarray, glacier-area weighted standard deviation of elevation change for overall setp.
    """
    ### glacier area (tile-based) weighted mean elevation change for setp.
    years = mean_tiles.years.values
    tiles_id = mean_tiles.tiles_id.values
    glacier_area_tiles_2d = glacier_area_tiles.expand_dims(dim={'times': years}, axis=1)  ## (tiles_id, years)
    glacier_area_tiles_2d = ~np.isnan(mean_tiles)*glacier_area_tiles_2d.values  ## (tiles_id, years), mask the nan values before area weighting
    glacier_area_1d = glacier_area_tiles_2d.sum(dim=('tiles_id'))   ### (years,)    
    glacier_area_2d = glacier_area_1d.expand_dims(dim={'tiles_id': tiles_id}, axis=0)   ### (tiles_id, years)    
    glacier_area_tilesWeight_2d = glacier_area_tiles_2d/glacier_area_2d   ### (tiles_id, years)
    mean_setp_tilesWeighted = mean_tiles*glacier_area_tilesWeight_2d    ## (tiles_id, years)
    mean_setp_tilesWeighted = mean_setp_tilesWeighted.sum(dim=('tiles_id'))     ## (years,)   
    std_setp_tilesWeighted = std_tiles*glacier_area_tilesWeight_2d    ## (tiles_id, years)
    std_setp_tilesWeighted = std_setp_tilesWeighted.sum(dim=('tiles_id'))     ## (years,)   
    return mean_setp_tilesWeighted, std_setp_tilesWeighted


def stat_bins_weighting(mean_bins, std_bins, glacier_area_bins):
    """
    des: bins-based glacier area weighted calculation.
    args:
        mean_bins: xarray.DataArray, (bins_id, years), mean elevation change for each bin.
        std_bins: xarray.DataArray, (bins_id, years), standard deviation of elevation change for each bin.
        glacier_area_bins: xarray.DataArray, (bins_id), glacier area for each bin.
        years_data: list, contain the years of the data, e.g., [2001, 2002, 2003, ...]
        return: 
        mean_tilesWeighted: xr.dataarray, glacier-area weighted mean elevation change for overall setp. 
        std_tilesWeighted:  xr.dataarray, glacier-area weighted standard deviation of elevation change for overall setp.
    """
    years = mean_bins.years.values
    bins_id = mean_bins.bins_id.values
    glacier_area_bins_2d = glacier_area_bins.expand_dims(dim={'years': years}, axis=1)  ## (bins_id, years)
    glacier_area_bins_2d = ~np.isnan(mean_bins)*glacier_area_bins_2d.values  ## (bins_id, years), mask the nan values before area weighting
    glacier_area_1d = glacier_area_bins_2d.sum(dim=('bins_id'))   ### (years,)    
    glacier_area_2d = glacier_area_1d.expand_dims(dim={'bins_id': bins_id}, axis=0)   ### (bins_id, years)    
    glacier_area_binsWeight_2d = glacier_area_bins_2d/glacier_area_2d   ### (bins_id, years)
    mean_binsWeighted = mean_bins*glacier_area_binsWeight_2d    ## (bins_id, years)
    mean_binsWeighted = mean_binsWeighted.sum(dim=('bins_id'))     ## (years,)   
    std_binsWeighted = std_bins*glacier_area_binsWeight_2d    ## (bins_id, years)
    std_binsWeighted = std_binsWeighted.sum(dim=('bins_id'))     ## (years,)   
    return mean_binsWeighted, std_binsWeighted

def stat_bins_tiles_weighting(mean_tiles_bins, std_tiles_bins, glacier_area_tiles_bins):
    """
    des: glacier area-weighting by bins and tiles.
    !!! bins-based glacier area weighting -> tiles-based glacier area weighting.
    args:
        mean_tiles_bin: xarray.DataArray, (tiles_id, bins_id, years), mean elevation change for each bin of each tile.
        std_tiles_bin: xarray.DataArray, (tiles_id, bins_id, years), standard deviation of elevation change for each bin of each tile.
        glacier_area_bins: xarray.DataArray, (tiles_id, bins_id), glacier area for each bin of each tile.
    return: 
        mean_tiles_weighted: xr.dataarray, glacier-area weighted mean elevation change for each tile. 
        mean_setp_weighted: xr.dataarray, glacier-area weighted mean elevation change for overall setp. 
    """
    ### a) glacier area (bin-based) weighting by bins.
    years = mean_tiles_bins.years.values
    bins_id = mean_tiles_bins.bins_id.values
    tiles_id = mean_tiles_bins.tiles_id.values
    glacier_area_tiles_bins_3d = glacier_area_tiles_bins.expand_dims(dim={"years": years}, axis=2)
    glacier_area_tiles_bins_3d = ~np.isnan(mean_tiles_bins)*glacier_area_tiles_bins_3d  ## mask the nan values before area weighting
    glacier_area_tiles_2d = glacier_area_tiles_bins_3d.sum(dim=('bins_id'))
    glacier_area_tiles_3d = glacier_area_tiles_2d.expand_dims(dim={'bins_id': bins_id}, axis=1)
    glacier_area_binsWeight_3d = glacier_area_tiles_bins_3d/glacier_area_tiles_3d   ## (tiles_id, bins_id, years), weights for each bin of each year.
    mean_tiles_binsWeighted = mean_tiles_bins * glacier_area_binsWeight_3d.values  
    mean_tiles_binsWeighted = mean_tiles_binsWeighted.sum(dim=('bins_id'))       ## (tiles_id, years)
    mean_tiles_binsWeighted = mean_tiles_binsWeighted.where(mean_tiles_binsWeighted!=0, np.nan)  # if values == 0, value -> np.nan. 
    std_tiles_binsWeighted = std_tiles_bins * glacier_area_binsWeight_3d
    std_tiles_binsWeighted = std_tiles_binsWeighted.sum(dim=('bins_id'))       ## (tiles_id, years)
    ### b) glacier area (tile-based) weighting by tiles.
    glacier_area_tiles = glacier_area_tiles_bins.sum(dim='bins_id')   ###（tiles_id,）
    glacier_area_tiles_2d = glacier_area_tiles.expand_dims(dim={'years': years}, axis=1)  ## (tiles_id, years)
    glacier_area_tiles_2d = ~np.isnan(mean_tiles_binsWeighted)*glacier_area_tiles_2d.values  ## (tiles_id, years), mask the nan values before area weighting
    glacier_area_1d = glacier_area_tiles_2d.sum(dim=('tiles_id'))   ### (years,)    
    glacier_area_2d = glacier_area_1d.expand_dims(dim={'tiles_id': tiles_id}, axis=0)   ### (tiles_id, years)    
    glacier_area_tilesWeight_2d = glacier_area_tiles_2d/glacier_area_2d   ### (tiles_id, years)
    mean_setp_tilesWeighted = mean_tiles_binsWeighted*glacier_area_tilesWeight_2d    ## (tiles_id, years)
    mean_setp_tilesWeighted = mean_setp_tilesWeighted.sum(dim=('tiles_id'))     ## (years,)      
    std_setp_tilesWeighted = std_tiles_binsWeighted*glacier_area_tilesWeight_2d    ## (tiles_id, years)
    std_setp_tilesWeighted = std_setp_tilesWeighted.sum(dim=('tiles_id'))     ## (years,)   

    return mean_tiles_binsWeighted, std_tiles_binsWeighted, mean_setp_tilesWeighted, std_setp_tilesWeighted



def stat_tiles_bins_weighting(mean_tiles_bins, std_tiles_bins, glacier_area_tiles_bins):
    """
    des: glacier area-weighted elevation change calculation.  
         !!! tiles-based glacier area weighting -> bins-based glacier area weighting.
    args:
        mean_tiles_bin: xarray.DataArray, (tiles_id, bins_id, years), mean elevation change for each bin of each tile.
        std_tiles_bin: xarray.DataArray, (tiles_id, bins_id, years), standard deviation of elevation change for each bin of each tile.
        glacier_area_tiles_bins: xarray.DataArray, (tiles_id, bins_id), glacier area for each bin of each tile.
    return: 
        mean_bins_tilesweighted: xr.dataarray, glacier-area weighted mean elevation change for each tile. 
        std_bins_tilesweighted: xr.dataarray, glacier-area weighted mean elevation change for each tile. 
        mean_setp_weighted: xr.dataarray, glacier-area weighted mean elevation change for overall setp. 
        std_setp_weighted: xr.dataarray, glacier-area weighted mean elevation change for overall setp. 
    """
    years = mean_tiles_bins.years.values
    bins_id = mean_tiles_bins.bins_id.values
    tiles_id = mean_tiles_bins.tiles_id.values
    glacier_area_tiles_bins_3d = glacier_area_tiles_bins.expand_dims(dim={"years": years}, axis=2)
    glacier_area_tiles_bins_3d = ~np.isnan(mean_tiles_bins)*glacier_area_tiles_bins_3d.values   ## mask the nan values before area weighting
    glacier_area_bins_2d = glacier_area_tiles_bins_3d.sum(dim=('tiles_id'))   ### (bins_id, years), sumation of area for each bin of setp.
    glacier_area_bins_3d = glacier_area_bins_2d.expand_dims(dim={'tiles_id': tiles_id}, axis=0)  ## (tiles_id, bins_id, years)
    glacier_area_tilesWeight_3d = glacier_area_tiles_bins_3d/glacier_area_bins_3d.values   ### weights for each bin of setp  
    mean_bins_tilesWeighted_3d = mean_tiles_bins*glacier_area_tilesWeight_3d.values
    mean_bins_tilesWeighted = mean_bins_tilesWeighted_3d.sum(dim='tiles_id')   ### (bins_id, years)
    std_bins_tilesWeighted_3d = std_tiles_bins*glacier_area_tilesWeight_3d.values
    std_bins_tilesWeighted = std_bins_tilesWeighted_3d.sum(dim='tiles_id')     ### (bins_id, years)
    ### b) glacier area (tile-based) weighted mean elevation change for setp.
    glacier_area_bins = glacier_area_tiles_bins.sum(dim='tiles_id')   ###（bins_id）
    glacier_area_bins_2d = glacier_area_bins.expand_dims(dim={'years': years}, axis=1)  ## (bins_id, years)
    glacier_area_bins_2d = ~np.isnan(mean_bins_tilesWeighted)*glacier_area_bins_2d.values  ## (bins_id, years), mask the nan values before area weighting
    glacier_area_1d = glacier_area_bins_2d.sum(dim=('bins_id'))   ### (years,)    
    glacier_area_2d = glacier_area_1d.expand_dims(dim={'bins_id': bins_id}, axis=0)   ### (bins_id, years)    
    glacier_area_binsWeight_2d = glacier_area_bins_2d/glacier_area_2d              ## (bins_id, years)
    mean_setp_binsWeighted = mean_bins_tilesWeighted*glacier_area_binsWeight_2d    ## (bins_id, years)
    mean_setp_binsWeighted = mean_setp_binsWeighted.sum(dim=('bins_id'))           ## (years,)   
    std_setp_binsWeighted = std_bins_tilesWeighted*glacier_area_binsWeight_2d      ## (bins_id, years)
    std_setp_binsWeighted = std_setp_binsWeighted.sum(dim=('bins_id'))             ## (years,)   
    return mean_bins_tilesWeighted, std_bins_tilesWeighted, mean_setp_binsWeighted, std_setp_binsWeighted


