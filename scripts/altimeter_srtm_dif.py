# author: xin luo 
# creat: xin luo, 2022.12.11.   
# des: obtain the values as follows: lon_isat, lat_isat, h_isat, h_srtm, h_dif, land_type
# usage: python scripts/altimeter_srtm_dif.py -d data/icesat-1/GLAH14-2006

import os
import h5py
import numpy as np
import argparse
from osgeo import gdal, osr

os.chdir('/home/xin/Developer-luo/Glacier-in-SETP')

def get_args():
    description = "calculate the difference between the srtm and altimeter elevations."
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(         
            "-d", metavar="dir_files", type=str, nargs="+",
            help="directory of input altimeter files.",
            default=['data/icesat-1/GLAH14-2006'])  ## optional default: 'data/icesat-2/ATL06-2018'
    return parser.parse_args()

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


### Tile number determination
lefts=[91, 92, 93, 94, 95, 91, 92, 93, 94, 95, 96, 97, 91, 92, 93, 94, 95, 96, 97, 98, 94, 95, 96, 97, 98, 96, 97, 98]
bottoms=[31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 30, 30, 29, 29, 29, 29, 29, 29, 29, 29, 28, 28, 28, 28, 28, 27, 27, 27]
# bottoms = [28] 
# lefts = [95]

dir_srtm_tiles = 'data/dem-data/srtm-c/tiles'
dir_wat_tiles = 'data/water/water-jrc/tiles' ## get land type of water
dir_gl30_tiles = 'data/globeland30/2010/tiles'  ## get land type of forest
dir_glacier_tiles = 'data/rgi60/tiles'

if __name__ == '__main__':
    ### ---- read input from command line
    args = get_args()
    dir_altimeter = args.d[0]
    dir_altimeter_tiles = dir_altimeter + '/tiles'

    for i in range(len(lefts)):
        bottom, left = bottoms[i], lefts[i]
        path_srtm = dir_srtm_tiles + '/tile_'+str(bottom)+'_'+str(left)+'.tif'
        path_wat = dir_wat_tiles + '/tile_'+str(bottom)+'_'+str(left)+'.tif'
        path_gl30 = dir_gl30_tiles + '/tile_'+str(bottom)+'_'+str(left)+'.tif'
        path_glacier = dir_glacier_tiles + '/tile_'+str(bottom)+'_'+str(left)+'.tif'
        path_altimeter = dir_altimeter_tiles + '/tile_'+str(bottom)+'_'+str(left)+'.h5'
        print(path_altimeter)
        print('Tile id:', 'tile_'+str(bottom)+'_'+str(left))
        if not os.path.exists(path_altimeter):
            print('Altimeter data for this tile is not exits.')
            continue
        else:
            ### 1. load data
            ### dem data
            srtm, srtm_info = readTiff(path_srtm)
            srtm[srtm<0]=0

            ### water mask
            mask_wat = crop_to_extent(path_img=path_wat, extent=srtm_info['geoextent'], size_target=srtm.shape) # read and resize
            mask_wat = np.int8(mask_wat)

            ## Forest/shrub coverage
            gl30 = crop_to_extent(path_img=path_gl30, extent=srtm_info['geoextent'], size_target=srtm.shape) # read and resize
            mask_forest = np.where((gl30==20) | (gl30==40), 1, 0)  # extract forest/shrup from the gl30 data

            ### Glacier mask
            mask_glacier = crop_to_extent(path_img=path_glacier, extent=srtm_info['geoextent'], size_target=srtm.shape) # read and resize
            mask_glacier[mask_glacier<0]=0
            mask_glacier = np.int8(mask_glacier)

            ### altimeter data
            altimeter = {}
            with h5py.File(path_altimeter, 'r') as f_altimeter:
                altimeter['lon'] = f_altimeter['lon'][:]
                altimeter['lat'] = f_altimeter['lat'][:]
                altimeter['h'] = f_altimeter['h'][:]
                altimeter['t_dyr'] = f_altimeter['t_dyr'][:]

            ### 2. Remove altimeter data which is out of the dem image extent.
            lon_min_srtm, lon_max_srtm, lat_min_srtm, lat_max_srtm = srtm_info['geoextent']
            ids = np.where((altimeter['lon']>lon_min_srtm) & (altimeter['lon']<lon_max_srtm) & (altimeter['lat']>lat_min_srtm) & (altimeter['lat']<lat_max_srtm))[0]
            ## 2.1. update the altimeter data: remove the icesat data which is out of the srtm extent. 
            for key in altimeter:
                altimeter[key] = altimeter[key][ids]
            ## 2.2. update the altimeter data: filter the icesat footprints which have no data on the srtm image.
            row_altimeter_srtm, col_altimeter_srtm = geo2imagexy(x=altimeter['lon'], y=altimeter['lat'], gdal_trans=srtm_info['geotrans'], integer=True)  ## update the row_altimeter_srtm and col_altimeter_srtm.
            ids = np.where((srtm[row_altimeter_srtm, col_altimeter_srtm] > 0))[0]
            for key in altimeter:
                altimeter[key] = altimeter[key][ids]

            ### 3. Assign footprint type: stable (0), water (1), forest(2), glacier (3). 
            row_altimeter_srtm, col_altimeter_srtm = geo2imagexy(x=altimeter['lon'], y=altimeter['lat'], gdal_trans=srtm_info['geotrans'], integer=True)  ## update the row_isat_srtm and col_isat_srtm.
            altimeter['type_fp'] = np.zeros_like(altimeter['lon'])  ## stable type: 0
            ### water type determination, index number: 1
            ids_wat = np.where(mask_wat[row_altimeter_srtm, col_altimeter_srtm]==1)[0]
            altimeter['type_fp'][ids_wat]=1
            ### forest type determination, index number: 2
            ids_forest = np.where(mask_forest[row_altimeter_srtm, col_altimeter_srtm]==1)[0]
            altimeter['type_fp'][ids_forest]=2
            ### glacier type determination, index number: 3
            ids_glacier = np.where(mask_glacier[row_altimeter_srtm, col_altimeter_srtm]==1)[0]
            altimeter['type_fp'][ids_glacier]=3

            ### 4. Calculate the elevation difference between srtm and altimeter data.
            h_srtm = srtm[row_altimeter_srtm, col_altimeter_srtm]
            h_dif = altimeter['h'] - h_srtm
            altimeter['h_dif'] = h_dif; altimeter['h_srtm'] = h_srtm  

            ### 5. Write out the processed data
            file_out = os.path.splitext(path_altimeter)[0]+'_srtm_dif.h5'
            if os.path.exists(file_out): os.remove(file_out)
            with h5py.File(file_out, "w") as f_out:
                [f_out.create_dataset(key, data=altimeter[key]) for key in list(altimeter.keys())]
                print('Output saved to:', file_out)



