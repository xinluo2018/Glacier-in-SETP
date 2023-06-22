# author: xin luo 
# creat: 2022.12.11; modify: 2023.6.4
# des: obtain the values as follows: lon_isat, lat_isat, h_isat, h_srtm, h_dif, land_type
#      the result is write out as tiles-based multiple-year .h5 file.
##     this scripts can be used for processing of icesat-1, icesat-2 and cryosat-2 data.
## usage: python scripts/dif_altimeter_srtm.py -dtype icesat-1


import os
import h5py
import numpy as np
import argparse
from osgeo import gdal, osr
from glob import glob

os.chdir('/home/xin/Developer-luo/Glacier-in-SETP')

def get_args():
    """ Get command-line arguments. """
    parser = argparse.ArgumentParser(
          description='get the date dyte of the processed data')
    parser.add_argument(
          '-dtype', metavar='dtype', type=str, nargs='+',
          help='the data type (icesat-1 or icesat-2 or cryosat-2) of the processing data',
          default=['cryosat-2'])
    return parser.parse_args()

#### Data to be read in
dir_srtm_tiles = 'data/dem-data/srtm-c/tiles'
dir_wat_tiles = 'data/land-cover/water/water-jrc/tiles'       ## get land type of water
dir_stable_tiles = 'data/land-cover/stable-cover/tiles-2010'  ## get stable land
dir_glacier_tiles = 'data/land-cover/rgi60/tiles'
paths_srtm_tile = glob(dir_srtm_tiles+'/tile_??_??.tif')
paths_srtm_tile.sort()
tiles_id = [path_srtm_tile[-14:-4] for path_srtm_tile in paths_srtm_tile]


##### ----------------------------copy the utility code----------------------------------- #####
### tiff image reading
def readTiff(path_in):
    '''
    return: 
        img: numpy array, exent: tuple, (x_min, x_max, y_min, y_max) 
        proj info, and dimentions: (row, col, band)
    '''
    RS_Data = gdal.Open(path_in)
    im_col = RS_Data.RasterXSize  # 
    im_row = RS_Data.RasterYSize  # 
    im_bands = RS_Data.RasterCount  # 
    im_geotrans = RS_Data.GetGeoTransform()  # 
    im_proj = RS_Data.GetProjection()  # 
    img_array = RS_Data.ReadAsArray(0, 0, im_col, im_row)  # 
    left = im_geotrans[0]
    up = im_geotrans[3]
    right = left + im_geotrans[1] * im_col + im_geotrans[2] * im_row
    bottom = up + im_geotrans[5] * im_row + im_geotrans[4] * im_col
    extent = (left, right, bottom, up)
    espg_code = osr.SpatialReference(wkt=im_proj).GetAttrValue('AUTHORITY',1)
    img_info = {'geoextent': extent, 'geotrans':im_geotrans, \
                'geosrs': espg_code, 'row': im_row, 'col': im_col,\
                    'bands': im_bands}
    if im_bands > 1:
        img_array = np.transpose(img_array, (1, 2, 0)).astype(np.float)  # 
        return img_array, img_info 
    else:
        return img_array, img_info

def geo2imagexy(x, y, gdal_trans, integer=True):
    '''
    des: from georeferenced location (i.e., lon, lat) to image location(col,row).
    input:
        x: project or georeferenced x, i.e.,lon
        y: project or georeferenced y, i.e., lat
        gdal_trans: wgs84 coordinate systems of the specific image, 
                    obtained by gdal.Open() and .GetGeoTransform(), or by geotif_io.readTiff()['geotrans']
    return: 
        image col and row corresponding to the georeferenced location.
    '''
    a = np.array([[gdal_trans[1], gdal_trans[2]], [gdal_trans[4], gdal_trans[5]]])
    b = np.array([x - gdal_trans[0], y - gdal_trans[3]])
    col_img, row_img = np.linalg.solve(a, b)
    if integer:
        col_img, row_img = np.floor(col_img).astype('int'), np.floor(row_img).astype('int')
    return row_img, col_img

def crop_to_extent(path_img, extent, size_target=None, path_save=None):
    '''
    crop image to given extent/size.
    arg:
        image: the image to be croped; np.array().
        extent: extent to which image should be croped;
                list/tuple,(xmin,xmax,ymin,ymax). 
        size_target: size to which image should be croped 
              list/tuple, (row, col)
    return: 
        img_croped: the croped image, np.array()
    '''
    rs_data=gdal.Open(path_img)
    dtype_id = rs_data.GetRasterBand(1).DataType
    dtype_name = gdal.GetDataTypeName(dtype_id)
    if 'int8' in dtype_name:
        datatype = gdal.GDT_Byte
    elif 'int16' in dtype_name:
        datatype = gdal.GDT_UInt16
    else:
        datatype = gdal.GDT_Float32
    geotrans = rs_data.GetGeoTransform()
    dx, dy = geotrans[1], geotrans[5]
    nbands = rs_data.RasterCount
    proj_wkt = rs_data.GetProjection()
    NDV = rs_data.GetRasterBand(1).GetNoDataValue()
    xmin, xmax, ymin, ymax = extent

    if size_target is None:
        npix_x = int(np.round((xmax - xmin) / float(dx)))  # new col
        npix_y = int(np.round((ymin - ymax) / float(dy)))  # new row
        dx = (xmax - xmin) / float(npix_x)
        dy = (ymin - ymax) / float(npix_y)
    else:
        npix_x = size_target[1]
        npix_y = size_target[0]
        dx = (xmax - xmin) / float(size_target[1])  # new resolution
        dy = (ymin - ymax) / float(size_target[0])

    if path_save is None:
        drv = gdal.GetDriverByName('MEM')
        dest = drv.Create('', npix_x, npix_y, nbands, datatype)
    else: 
        driver = gdal.GetDriverByName("GTiff")
        dest = driver.Create(path_save, npix_x, npix_y, nbands, datatype)
        
    dest.SetProjection(proj_wkt)
    newgeotrans = (xmin, dx, 0.0, ymax, 0.0, dy)
    dest.SetGeoTransform(newgeotrans)
    if NDV is not None:
        for i in range(nbands):
            dest.GetRasterBand(i+1).SetNoDataValue(NDV)
            dest.GetRasterBand(i+1).Fill(NDV)
    else:
        for i in range(nbands):
            dest.GetRasterBand(i+1).Fill(0)

    gdal.ReprojectImage(rs_data, dest, proj_wkt, proj_wkt, gdal.GRA_Bilinear)
    out_array = dest.ReadAsArray(0, 0,  npix_x,  npix_y)

    if NDV is not None:
        out_array = np.ma.masked_where(out_array == NDV, out_array).data

    if nbands > 1:
        return np.transpose(out_array, (1, 2, 0))  # 
    else:
        return out_array
##### ---------------------------------------------------------------------------- #####

if __name__ == '__main__':

    ### Data setting.
    args = get_args()
    dtype = args.dtype[0]
    print('------------- The processing data is %s -------------' % (dtype))
    ### paths to be read in and write out.
    if dtype == 'icesat-1':
        dif_outlier_thre = 100
        dir_altimeter = 'data/icesat-1'
        data_type = 'GLAH14' 
        years = [str(year) for year in range(2003, 2010)]
    if dtype == 'icesat-2':
        dif_outlier_thre = 100
        dir_altimeter = 'data/icesat-2'
        data_type = 'ATL06'
        years = [str(year) for year in range(2018, 2023)]
    elif dtype == 'cryosat-2':
        dif_outlier_thre = 100
        dir_altimeter = 'data/cryosat-2'
        data_type = 'eolis-point'
        years = [str(year) for year in range(2010, 2023)]

    #### Data to be writen out
    dir_dif_altimeter = dir_altimeter + '/tiles-dif-srtm'

    if not os.path.exists(dir_dif_altimeter): os.makedirs(dir_dif_altimeter)
    for tile_id in tiles_id:
        print('Tile id:', tile_id)
        path_dif_altimeter = dir_dif_altimeter + '/'+tile_id+'.h5'
        if os.path.exists(path_dif_altimeter): os.remove(path_dif_altimeter)
        path_srtm_tile = dir_srtm_tiles + '/'+ tile_id + '.tif'
        path_wat_tile = dir_wat_tiles + '/'+tile_id+'.tif'
        path_stable_tile = dir_stable_tiles + '/'+tile_id+'.tif'
        path_glacier_tile = dir_glacier_tiles + '/'+ tile_id +'.tif'
        f_write = h5py.File(path_dif_altimeter, "w")
        altimeter_tile_years = {}
        for year in years:
            path_altimeter_tile_year = dir_altimeter + '/' + data_type+'-'+year + '/tiles/' + tile_id + '.h5'
            print(path_altimeter_tile_year)
            if not os.path.exists(path_altimeter_tile_year):
                print('Altimeter data for this tile is not exits.')
                continue
            else:
                ### 1. load data
                ### DEM data
                srtm_tile, srtm_tile_info = readTiff(path_srtm_tile)
                ### Stable mask
                mask_stable_tile = crop_to_extent(path_img=path_stable_tile, extent=srtm_tile_info['geoextent'], size_target=srtm_tile.shape) # read and resize
                ### Glacier mask
                mask_glacier_tile = crop_to_extent(path_img=path_glacier_tile, extent=srtm_tile_info['geoextent'], size_target=srtm_tile.shape) # read and resize

                ### Load altimeter data
                with h5py.File(path_altimeter_tile_year, 'r') as f_altimeter:
                    if len(altimeter_tile_years) == 0:
                        altimeter_tile_years['lon'] = f_altimeter['lon'][:]
                        altimeter_tile_years['lat'] = f_altimeter['lat'][:]
                        altimeter_tile_years['h'] = f_altimeter['h'][:]
                        altimeter_tile_years['t_dyr'] = f_altimeter['t_dyr'][:]
                        if data_type == 'eolis-point': altimeter_tile_years['is_swath'] = f_altimeter['is_swath'][:]
                    else:
                        altimeter_tile_years['lon'] = np.concatenate([altimeter_tile_years['lon'], f_altimeter['lon'][:]], axis=0) 
                        altimeter_tile_years['lat'] = np.concatenate([altimeter_tile_years['lat'], f_altimeter['lat'][:]], axis=0) 
                        altimeter_tile_years['h'] = np.concatenate([altimeter_tile_years['h'], f_altimeter['h'][:]], axis=0) 
                        altimeter_tile_years['t_dyr'] = np.concatenate([altimeter_tile_years['t_dyr'], f_altimeter['t_dyr'][:]], axis=0)
                        if data_type == 'eolis-point': 
                            altimeter_tile_years['is_swath'] = np.concatenate([altimeter_tile_years['is_swath'], f_altimeter['is_swath'][:]], axis=0) 

        if len(altimeter_tile_years) == 0: continue
        ### 2. Remove altimeter data which is out of the dem image extent.
        lon_min_srtm_tile, lon_max_srtm_tile, lat_min_srtm_tile, lat_max_srtm_tile = srtm_tile_info['geoextent']
        ids = np.where((altimeter_tile_years['lon']>lon_min_srtm_tile) & (altimeter_tile_years['lon']<lon_max_srtm_tile) & \
                                    (altimeter_tile_years['lat']>lat_min_srtm_tile) & (altimeter_tile_years['lat']<lat_max_srtm_tile))[0]
        ## 2.1. Update the altimeter data: remove the icesat data which is out of the srtm extent. 
        for key in altimeter_tile_years:
            altimeter_tile_years[key] = altimeter_tile_years[key][ids]
        ## 2.2. Update the altimeter data: filter the icesat footprints which have no data on the srtm image.
        row_altimeter_srtm, col_altimeter_srtm = geo2imagexy(x=altimeter_tile_years['lon'], \
                            y=altimeter_tile_years['lat'], gdal_trans=srtm_tile_info['geotrans'], integer=True)  ## update the row_altimeter_srtm and col_altimeter_srtm.
        ids = np.where((srtm_tile[row_altimeter_srtm, col_altimeter_srtm] > 0))[0]
        for key in altimeter_tile_years:
            altimeter_tile_years[key] = altimeter_tile_years[key][ids]

        ### 3. Assign footprint type:  stable (1), glacier (2). 
        altimeter_tile_years['type_fp'] = np.zeros_like(altimeter_tile_years['lon'])  ## stable type: 0
        ### Stable land cover type determination, index number: 1
        ids_stable = np.where(mask_stable_tile[row_altimeter_srtm, col_altimeter_srtm]==1)[0]
        altimeter_tile_years['type_fp'][ids_stable]=1
        ### Glacier land cover type determination, index number: 2
        ids_glacier = np.where(mask_glacier_tile[row_altimeter_srtm, col_altimeter_srtm]==1)[0]
        altimeter_tile_years['type_fp'][ids_glacier]=2
        ### Mask out the non-stable and non-glacier data
        # altimeter_tile_years_ = {}
        ids_valid = np.where(altimeter_tile_years['type_fp']>=1)[0]
        for key in altimeter_tile_years:
            altimeter_tile_years[key] = altimeter_tile_years[key][ids_valid] 

        ### 4. Calculate the elevation difference between srtm and altimeter data.
        row_altimeter_srtm, col_altimeter_srtm = geo2imagexy(x=altimeter_tile_years['lon'], \
                            y=altimeter_tile_years['lat'], gdal_trans=srtm_tile_info['geotrans'], integer=True)  ## update the row_altimeter_srtm and col_altimeter_srtm.
        h_srtm = srtm_tile[row_altimeter_srtm, col_altimeter_srtm]
        h_dif = altimeter_tile_years['h'] - h_srtm
        altimeter_tile_years['h_dif'] = h_dif
        altimeter_tile_years['h_srtm'] = h_srtm 
        ids_valid = np.where(abs(altimeter_tile_years['h_dif'])<dif_outlier_thre)[0]    ### outlier filtering.
        for keys in altimeter_tile_years:
            altimeter_tile_years[keys] = altimeter_tile_years[keys][ids_valid]
        ### 5. Write out the processed data
        for key in list(altimeter_tile_years.keys()):
            f_write.create_dataset(key, data=altimeter_tile_years[key])
        f_write.close()
        print('Write out to:', path_dif_altimeter)







