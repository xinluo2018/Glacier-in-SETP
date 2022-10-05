## author: xin luo 
# creat: 2022.9.30
# des: select images in the given extent.


from glob import glob
from utils.get_extent import get_extent
from utils.transform_xy import coor2coor

def imgs_in_extent(paths_img, extent):
  '''
  des: selected imgs that all in the given extent.
  arg:
    paths_img: images paths;
    extent: the given extent.
  '''
  paths_img_in = []
  for path_img in paths_img:
    extent_img, espg_code = get_extent(path_img)    
    xs = (extent_img[0], extent_img[1])
    ys = (extent_img[2], extent_img[3])
    lons_img, lats_img = coor2coor(srs_from=espg_code, srs_to='4326', x=xs, y=ys)
    lon_in = extent[0]<lons_img[0]<extent[1] or extent[0]<lons_img[1]<extent[1]
    lat_in = extent[2]<lats_img[0]<extent[3] or extent[2]<lats_img[1]<extent[3]
    img_in = lon_in and lat_in
    if img_in is True:
      paths_img_in.append(path_img)
  return paths_img_in


