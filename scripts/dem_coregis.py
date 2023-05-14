## author: xin luo; xxxx
## create: 2023.02.13;
## des: co-register the aster dem to srtm. 
## usage: python ./scripts/dem_coregis.py -year 2007

import os
import xdem
import pyproj
from glob import glob
import numpy as np
import argparse
from osgeo import gdal, osr

def get_args():
    """ Get command-line arguments. """
    parser = argparse.ArgumentParser(
          description='get the date(year) of the processed data')
    parser.add_argument(
          '-year', metavar='year', type=str, nargs='+',
          help='the year of the processing data',
          default=['2007'])
    return parser.parse_args()

### setting
dir_proj = '/home/xin/Developer-luo/Glacier-in-SETP'
dir_srtm = dir_proj+'/data/dem-data/srtm-c/tiles'
dir_water = dir_proj+'/data/water/water-jrc/tiles'      # jrc water map for water mask
dir_rgi60 = dir_proj+'/data/rgi60/tiles'                  # rgi glacier data for glacier mask
dir_forest = dir_proj+'/data/globeland30/2010/tiles'      # land cover data for forest mask

#########---------------- Some functions to be used -----------------###########
## Tiled data mosaic and subseting to dem extent
def tiles2extent(dir_tiled_data, extent, path_save):
    '''
    args:
      dir_data: string, directory of the tiled data
      extent: list, [left, right, bottom, up], can be obtained by readTiff() function.
      path_save, str, the file path to be saved. 
    '''
    paths_tile = glob(dir_tiled_data+'/*[!albers].tif')
    ### data mosaic
    paths_tile_sel = imgs_in_extent(paths_img=paths_tile, extent=extent)
    paths_tile_sel = " ".join(paths_tile_sel)
    command = "gdal_merge.py -co COMPRESS=LZW -o tiles_mosaic.tif " + paths_tile_sel
    print(os.popen(command).read())
    ### data subseting
    left, right, bottom, up = extent[0], extent[1], extent[2], extent[3]
    extent_str = ' '.join([str(left), str(up), str(right), str(bottom)])
    command = 'gdal_translate -projwin %s -co COMPRESS=LZW tiles_mosaic.tif %s' % (extent_str, path_save)
    print(os.popen(command).read())
    os.remove('tiles_mosaic.tif')

def coor2coor(srs_from, srs_to, x, y):
    """
    Transform coordinates from srs_from to srs_to
    input:
        srs_from and srs_to: EPSG number, (e.g., 4326, 3031)
        x and y are x-coord and y-coord corresponding to srs_from and srs_to    
    return:
        x-coord and y-coord in srs_to 
    """
    transformer = pyproj.Transformer.from_crs(int(srs_from), int(srs_to), always_xy=True)
    return transformer.transform(x,y)

def get_extent(path_img):
      RS_Data=gdal.Open(path_img)
      im_col = RS_Data.RasterXSize  # 
      im_row = RS_Data.RasterYSize  # 
      im_geotrans = RS_Data.GetGeoTransform()  # 
      im_proj = RS_Data.GetProjection()  # 
      west = im_geotrans[0]
      north = im_geotrans[3]
      east = west + im_geotrans[1] * im_col + im_geotrans[2] * im_row
      south = north + im_geotrans[5] * im_row + im_geotrans[4] * im_col
      espg_code = osr.SpatialReference(wkt=im_proj).GetAttrValue('AUTHORITY',1)
      extent = (west, east, south, north)
      return extent, espg_code

def imgs_in_extent(paths_img, extent):
  '''
  des: selected imgs that in the given extent.
  arg:
    paths_img: list, images paths;
    extent: the given extent(wgs84). list -> [left, right, bottom, up]
  '''
  paths_imgs_extent = []
  for path_img in paths_img:
    extent_img, espg_code = get_extent(path_img)    
    xs = (extent_img[0], extent_img[1])
    ys = (extent_img[2], extent_img[3])
    if espg_code != '4326':
      lons_img, lats_img = coor2coor(srs_from=espg_code, srs_to='4326', x=xs, y=ys)
    else: 
      lons_img, lats_img = xs, ys
    lon_in_left = lons_img[1]<extent[0]       ### the case that image is on the left of the extent
    lon_in_right = lons_img[0]>extent[1]
    lat_in_up = lats_img[0]>extent[3]
    lat_in_down = lats_img[1]<extent[2]
    img_in = lon_in_left or lon_in_right or lat_in_up or lat_in_down    ## for each case, there is no overlap between the image and extent. 
    if img_in is False:
      paths_imgs_extent.append(path_img)
  return paths_imgs_extent

#########------------------------------ Main processing -----------------------###########
if __name__ == '__main__':
    # extract arguments 
    args = get_args()
    year = args.year[0]
    print('------------- The data in %s is processing -------------' % (year))
    ### dems for co-registration.
    paths_dem = glob(dir_proj+'/data/aster-stereo/SETP-%s/aster-dem/*/run-DEM_wgs84_filter.tif' % (year))    # slave dem
    paths_dem_aligned = [os.path.splitext(path)[0]+'_coreg.tif' for path in paths_dem]
    print('Number of dems to be processed: ', len(paths_dem))
    for id, path_dem in enumerate(paths_dem): 
        print('------------- Processing the %dth dem -------------' % (id+1))
        print(path_dem)
        path_dem, path_dem_aligned = paths_dem[id], paths_dem_aligned[id]
        extent_dem, espg_dem = get_extent(path_dem)
        ### get the auxilary data.
        path_srtm_extent = dir_proj+'/srtm_extent.tif'
        path_wat_extent = dir_proj+'/wat_extent.tif'
        path_glacier_extent = dir_proj+'/glacier_extent.tif'
        path_forest_extent = dir_proj+'/forest_extent.tif'
        tiles2extent(dir_tiled_data = dir_srtm, extent = extent_dem, path_save = path_srtm_extent)
        tiles2extent(dir_tiled_data = dir_water, extent = extent_dem, path_save = path_wat_extent)
        tiles2extent(dir_tiled_data = dir_rgi60, extent = extent_dem, path_save = path_glacier_extent)
        tiles2extent(dir_tiled_data = dir_forest, extent = extent_dem, path_save = path_forest_extent)
        ### dems co-registration by using xdem software:
        ## --1.data reading
        srtm = xdem.DEM(dir_proj+'/srtm_extent.tif')
        dem = xdem.DEM(path_dem).reproject(srtm)   # slave dem
        srtm = srtm.reproject(dem)    # ensure the geo-info are completely the same. some bug for the xdem
        ## --2. water/glacier/forest mask (water:1, glacier:2, forest:3, other:0)
        water_jrc = xdem.DEM(dir_proj+'/wat_extent.tif').reproject(srtm)
        rgi60_mask = xdem.DEM(dir_proj+'/glacier_extent.tif').reproject(srtm)
        forest_mask = xdem.DEM(dir_proj+'/forest_extent.tif').reproject(srtm)
        forest_mask.data[0] = np.where(forest_mask.data[0]==20, 1, 0) ### extract forest
        mask_wat_gla_forest = water_jrc.data[0]+rgi60_mask.data[0]*2 + forest_mask.data[0]*3
        mask_stable = np.ma.masked_equal(mask_wat_gla_forest ,0).mask     ### get stable region
        ## --3.dems co-registration by using method proposed by Nuth and Kaab.
        try:
          nuth_kaab = xdem.coreg.NuthKaab(max_iterations=20, offset_threshold=0.05)  # offset_threshold is the distance threshold
          nuth_kaab.fit(reference_dem=srtm, dem_to_be_aligned=dem, inlier_mask=mask_stable, verbose=True)
          dem_aligned = nuth_kaab.apply(dem)
          dem_aligned.save(path_dem_aligned)  # save the co-registered dem.
        except:
          print('!!!The aster dem coregistration is failed')
          pass
    os.remove(path_srtm_extent); os.remove(path_wat_extent); 
    os.remove(path_glacier_extent); os.remove(path_forest_extent)



