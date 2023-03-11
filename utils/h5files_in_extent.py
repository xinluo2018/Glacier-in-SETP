## author: xin luo 
## creat: 2023.3.11
## des: select .h5 files that fall in the given extent.
## usage: python utils/h5files_in_extent.py -h $paths_h5 -e $left $right $bottom $up

from glob import glob
import argparse
import h5py
import numpy as np

def get_args():
    description = "find the .h5 files (readout icesat-1, -2 and cryosat-2 data) fall in the given extent."
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        '-h5files', metavar='h5files', type=str, nargs='+',
        help=('.h5 files path for searching for.'))
    parser.add_argument(
        '-e', metavar=('left','right','bottom', 'up'), dest='extent', type=float, nargs=4,
        help=('extent for image finding.'),
        default=[91, 92, 27, 28])
    return parser.parse_args()

def h5files_in_extent(paths_h5, extent):
    '''
    des: selected h5 files (read-out icesat-1,-2, cryosat-2 data) that in the given extent.
    arg:
      paths_h5: list, .h5 files paths;
      extent: the given extent(wgs84). list -> [left, right, bottom, up]
    '''
    paths_h5_sel = []
    left, right, bottom, up = extent[0], extent[1], extent[2], extent[3]
    for path_h5 in paths_h5:
      f_h5 = h5py.File(path_h5, 'r')
      lon, lat = f_h5['lon'][:], f_h5['lat'][:]
      ids = np.argwhere( (lon<right) & (lon>left) & (lat<up) & (lat>bottom)).flatten()
      if len(ids) >0:
        paths_h5_sel.append(path_h5)
    return paths_h5_sel

if __name__ == '__main__':  
  args = get_args()
  paths_h5 = args.h5files[:]
  extent = args.extent[:]
  paths_h5_extent = h5files_in_extent(paths_h5, extent)
  for path in paths_h5_extent:
    print(path)


