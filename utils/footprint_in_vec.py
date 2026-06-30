import geopandas as gpd
import h5py
import numpy as np
from shapely import vectorized
from shapely.geometry import Point

# from concurrent.futures import ThreadPoolExecutor
def footprint_in_vec(paths_file, path_vec):
  '''
  des: calculate the number of footprint in the vector file
  arg:
    paths_file: list of file paths
    path_vec: vector file path
  '''
  fps = []
  for fn in paths_file:
    with h5py.File(fn) as f:
      lon, lat = f['lon'][:], f['lat'][:]
      fps += list(zip(lon,lat))
  fps_arr = np.array(fps)
  vec_gpd = gpd.read_file(path_vec)
  vec_geo = vec_gpd.unary_union
  contains_results = vectorized.contains(vec_geo, fps_arr[:, 0], fps_arr[:, 1])
  num_vec = sum(contains_results) 
  fps_sel = np.array(fps)[contains_results]
  fps_sel = [Point(x, y) for x, y in fps_sel]
  return num_vec, fps_sel
