
# path_subs=data/water_jrc/water_jrc_subs.tif
# path_subs_=data/water_jrc/water_jrc_36_78.tif

# extent='78 37 79 36'
# gdal_translate -projwin $extent -co COMPRESS=LZW $path_subs $path_subs_  

# path=data/aster-stereo/2009-36-78/aster_dem/VNIR_2009.04991815/run-DEM.tif
# var=$(gdalsrsinfo -o epsg $path); 
# utm_zone=$(echo ${var:9:10})
# echo $utm_zone

PATH_DEMS_MOSAIC=data/aster-stereo/2009-36-78/dems_2009_mosaic.tif  
PATH_DEMS_MOSAIC_WGS84=data/aster-stereo/2009-36-78/dems_2009_mosaic_wgs84.tif
PATH_DEMS_SUBS=data/aster-stereo/2009-36-78/dems_2009_mosaic_subs.tif  
# TSRS_WGS84='+proj=longlat +datum=WGS84'       # WGS84 projection 
# TSRS_UTM=$(gdalsrsinfo -o proj4 $PATH_DEMS_MOSAIC);   # UTM projection of the mosaic image 
EXTENT_SUBS='78 37 79 36'  # wgs83 coordinate system
# echo $TSRS_UTM
# gdalwarp -overwrite -s_srs "$TSRS_UTM" -t_srs "$TSRS_WGS84" -r cubic -co COMPRESS=LZW $PATH_DEMS_MOSAIC $PATH_DEMS_MOSAIC_WGS84 # re-projection
gdal_translate -projwin $EXTENT_SUBS -co COMPRESS=LZW $PATH_DEMS_MOSAIC_WGS84 $PATH_DEMS_SUBS