#! /bin/bash 

cd /home/xin/Developer-luo/Glacier-in-SETP

# path_in=data/globeland30/2010/N47_30_2010LC030/n47_30_2010lc030.tif
# path_out=data/globeland30/2010/N47_30_2010LC030/n47_30_2010lc030_wgs84.tif
# gdalwarp -overwrite -s_srs EPSG:32647 -t_srs EPSG:4326 -r cubic -co COMPRESS=LZW -co TILED=YES $path_in $path_out

# path_in=data/globeland30/2020/N47_30_2020LC030/n47_30_2020lc030.tif
# path_out=data/globeland30/2020/N47_30_2020LC030/n47_30_2020lc030_wgs84.tif
# gdalwarp -overwrite -s_srs EPSG:32647 -t_srs EPSG:4326 -r cubic -co COMPRESS=LZW -co TILED=YES $path_in $path_out

# path_out=data/globeland30/2010/globeland30_2010_mosaic.tif
# path_in=data/globeland30/2010/*/*_wgs84.tif
# gdal_merge.py -init 0 -n 0 -co COMPRESS=LZW -o $path_out $path_in

path_out=data/globeland30/2020/globeland30_mosaic.tif
path_in=data/globeland30/2020/*/*_wgs84.tif
gdal_merge.py -init 0 -n 0 -co COMPRESS=LZW -o $path_out $path_in

# extent='91 32 99 27'
# path_in=data/globeland30/2010/globeland30_2010_mosaic.tif
# path_out=data/globeland30/2010/globeland30_2010_mosaic_subs.tif
# gdal_translate -projwin $extent -co COMPRESS=LZW $path_in $path_out

extent='91 32 99 27'
path_in=data/globeland30/2020/globeland30_mosaic.tif
path_out=data/globeland30/2020/globeland30_mosaic_subs.tif
gdal_translate -projwin $extent -co COMPRESS=LZW $path_in $path_out
