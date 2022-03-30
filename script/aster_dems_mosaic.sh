#! /bin/bash
## author: xin luo; xxxx
## create: 2022.03.30;
## des: DEMs mosaic for generated dems in west kunlun.
## usage: the input DIR_DATA should contains a sub-directory (namely aster_dem)

### get data directory and utm zone number.
DIR_DATA=data/aster_data/wkunlun-2021
NAME_FILE=$(basename $DIR_DATA)
YYYY=$(echo ${NAME_FILE:8:12}) ## year of the dem data

## parameters configuration
cd /Users/luo/Library/CloudStorage/OneDrive-Personal/GitHub/Glacier-in-RGI1305

## get dems path
PATH_DEMS=$(ls $DIR_DATA/aster_dem/VNIR*/run-DEM*.tif)

## mosaic
PATH_OUT=$DIR_DATA/aster_dem/dems_mosaic_$YYYY.tif
gdal_merge.py -init 0 -co COMPRESS=LZW -o $PATH_OUT $PATH_DEMS

## move the dem data
mv $PATH_OUT data/aster_data/wkunlun-dems/

