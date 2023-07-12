## Author: xin luo
## create: 2023.6.28;
## des: split h5 tile into sub tile.. 
## usage: python h5tile_to_subtile.py


import os
os.chdir('/home/xin/Developer-luo/Glacier-in-SETP')
from glob import glob
import h5py
from utils.subset_file import subset
from utils.merge_files import merge
from utils.geotif_io import readTiff

data_type = 'cryosat-2'
path_merged = 'data/' + data_type + '/tiles-dif-srtm/tiles_merge.h5'

if __name__ == '__main__':
    print('data type is:', data_type)
    ### 1. Files merge
    paths_tile = glob('data/' + data_type + '/tiles-dif-srtm/tile_??_??.h5')
    ### Exclude the nota tiles.
    paths_valid = []
    for path_tile in paths_tile:
        file = h5py.File(path_tile)
        try:
            file['h_dif']
            paths_valid.append(path_tile)
        except:
            pass
    merge(ifiles=paths_valid, ofile=path_merged)
    print('.... the tiles have been merged!')
    ### 2. Split the merged file into subtile.
    dir_srtm_tile = 'data/dem-data/srtm-c/tiles-sub' 
    paths_srtm_tile = glob(dir_srtm_tile+'/tile_???_???.tif')
    path_altimeter = 'data/' + data_type + '/tiles-dif-srtm/tiles_merge.h5'
    dif_tiles_sub_dif = 'data/' + data_type + '/tiles-sub-dif-srtm'
    if not os.path.exists(dif_tiles_sub_dif): os.makedirs(dif_tiles_sub_dif)
    for path_srtm_tile in paths_srtm_tile:
        tile_id = os.path.basename(path_srtm_tile).split('.')[0]
        path_save = dif_tiles_sub_dif + '/' + tile_id +'.h5'
        srtm_tile, srtm_tile_info = readTiff(path_srtm_tile)
        extent_subs = srtm_tile_info['geoextent']
        subset(ifile=path_altimeter, ofile=path_save, extent=extent_subs, coord_name=['lon', 'lat'])
    print('.... the merged file have been split into sub tiles!')



