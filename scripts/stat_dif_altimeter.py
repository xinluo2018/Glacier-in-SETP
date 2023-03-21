## author: xin luo
## create: 2023.3.18; modify:   
## des: statistic of the elevation difference between altimeter and srtm. 
##      output variables include: 1) number of altimeter points on the glacier and stable regions, respectively.
##                                2) average value and standard deviation of the difference value for the glacier and stable regions, respectively.
## usage: python stat_dif_altimeter.py -d data/icesat-1/GLAH14-2008/tiles

import os
import h5py
import numpy as np
import argparse

lefts=[91, 92, 93, 94, 95, 91, 92, 93, 94, 95, 96, 97, 91, 92, 93, 94, 95, 96, 97, 98, 94, 95, 96, 97, 98, 96, 97, 98]
bottoms=[31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 30, 30, 29, 29, 29, 29, 29, 29, 29, 29, 28, 28, 28, 28, 28, 27, 27, 27]

def get_args():
    description = "statistic of the elevation difference between altimeter and srtm."
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(         
            "-d", metavar=('dir_in'), type=str, nargs="+",
            help="directory of tiles of elevation difference between altimeter and srtm.",
            default=['data/icesat-1/GLAH14-2008/tiles'])   ##  'data/icesat-2/ATL06-2019/tiles'; optional
    parser.add_argument(           
            '-o', metavar=('outdir'), dest='outdir', type=str, nargs=1,
            help='path to output folder', 
            default=[""])
    return parser.parse_args()

if __name__ == '__main__':
    ### ---- read input from command line
    args = get_args()
    dir_in = args.d[0]
    dir_out = args.outdir[0] if args.outdir[0] != '' else dir_in
    dif_record = {'tile':[], 'num_glacier':[], 'mean_glacier':[], 'std_glacier':[], \
                                            'num_stable':[], 'mean_stable':[], 'std_stable':[]}
    for i, left in enumerate(lefts):
        ### ele_dif data
        tile_name = 'tile_'+str(bottoms[i])+'_'+str(left)
        path_tile = dir_in + '/' + tile_name + '_srtm_dif.h5'
        if os.path.isfile(path_tile): 
            elev_dif = h5py.File(path_tile, 'r')
            h_dif = elev_dif['h_dif'][:]
            idx_glacier = np.argwhere(elev_dif['type_fp'][:]==3).flatten()
            idx_stable = np.argwhere(elev_dif['type_fp'][:]==0).flatten()
            ###  Statistic for the glacier region
            dif_glacier = h_dif[idx_glacier]
            dif_glacier[np.abs(dif_glacier)>150]=np.nan     ### Remove the outlier altimeter_srtm difference data.
            dif_glacier_filter = dif_glacier[~np.isnan(dif_glacier)]
            num_glacier = len(dif_glacier_filter)
            dif_glacier_mean = np.median(dif_glacier_filter) if len(dif_glacier_filter) != 0 else np.nan
            dif_glacier_std = np.std(dif_glacier_filter) if len(dif_glacier_filter) != 0 else np.nan
            ###  Statistic for the stable region
            dif_stable = h_dif[idx_stable]
            dif_stable[np.abs(dif_stable)>150]=np.nan     ### Remove the outlier altimeter_srtm difference data.
            dif_stable_filter = dif_stable[~np.isnan(dif_stable)]
            num_stable = len(dif_stable_filter)
            dif_stable_mean = np.nanmedian(dif_stable) if len(dif_stable) != 0 else np.nan
            dif_stable_std = np.nanstd(dif_stable) if len(dif_stable) != 0 else np.nan
        else:
            num_glacier, dif_glacier_mean, dif_glacier_std = 0, np.nan, np.nan
            num_stable, dif_stable_mean, dif_stable_std = 0, np.nan, np.nan
        ### Record the information
        dif_record['tile'].append(tile_name)
        dif_record['num_glacier'].append(num_glacier); dif_record['mean_glacier'].append(dif_glacier_mean)
        dif_record['std_glacier'].append(dif_glacier_std); dif_record['num_stable'].append(num_stable)
        dif_record['mean_stable'].append(dif_stable_mean); dif_record['std_stable'].append(dif_stable_std)

    #### ----- write out .h5 file
    ofile = dir_out +'/static_dif.h5'
    with h5py.File(ofile, "w") as f_out:
        [f_out.create_dataset(key, data=dif_record[key]) for key in dif_record.keys()]
    print('written file:', ofile)