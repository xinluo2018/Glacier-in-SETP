#! /bin/bash
## author: xin luo; xxxx
## create: 2022.03.30;
## des: DEMs mosaic for generated dems in west kunlun. 
##      1）the outlier data in aster dem are filtered with auxiliary srtm-c dem data.
##      2）the dems are mosaicked with a given prefered acquisition date.
##      3) the date of the masaic image is mapped.
## usage: the input DIR_DATA should contains a sub-directory (namely aster_dem)


### get data directory
DIR_DATA=data/aster-stereo/wkunlun-2000

## parameters configuration
cd /Users/luo/Library/CloudStorage/OneDrive-Personal/GitHub/Glacier-in-RGI1305
PATH_SHP=data/study-area/study_area_buf_rect.shp
date_center=0.5      # priority date, e.g., 0.5 represent the middle of a year.

## -----1) get data file information
NAME_FILE=$(basename $DIR_DATA)
YYYY=$(echo ${NAME_FILE:8:12}) ## year of the dem data
# ## get dems path
PATH_DEMS=$(ls $DIR_DATA/aster_dem/VNIR*/run-DEM.tif)

## -----2) generate date image corresponding to dems data
echo 'Generate dems date image:'
for PATH_DEM in $PATH_DEMS;
do
  PATH_DEM_DATE=$(dirname $PATH_DEM)/$(basename $PATH_DEM .tif)_date.tif
  date=$(echo $(dirname $PATH_DEM | xargs basename | cut -d '_' -f 2))
  gdal_calc.py -A $PATH_DEM --outfile=$PATH_DEM_DATE --calc="($date*(A>0))"  # band math.
done

## -----3) sort the path_dems by the date which near to the given date_center. 
## the dem nearer to date_center is placed latter.
for PATH_DEM in $PATH_DEMS;
do
  date=.$(dirname $PATH_DEM | xargs basename | cut -d '.' -f 2 )
  dif=$(echo $date - $date_center | bc | sed 's/-//')
  echo $dif $PATH_DEM >> $DIR_DATA/aster_dem/list_dems.txt
done
cat $DIR_DATA/aster_dem/list_dems.txt | sort -r > $DIR_DATA/aster_dem/list_dems_sort.txt
PATH_DEMS_SORT=$(cut -d ' ' -f 2 $DIR_DATA/aster_dem/list_dems_sort.txt)
echo 'Images for mosaic:'
echo $PATH_DEMS_SORT | xargs -n 1
rm $DIR_DATA/aster_dem/list_dems.txt
rm $DIR_DATA/aster_dem/list_dems_sort.txt

## ----- 4) dems mosaic
PATH_DEMS_MOSAIC=data/aster-stereo/wkunlun-dems/dems_${YYYY}_mosaic.tif  ## finally to be saved.
echo 'dems mosaic:'
gdal_merge.py -co COMPRESS=LZW -o $PATH_DEMS_MOSAIC $PATH_DEMS_SORT
echo 'dems subset:'
PATH_DEMS_SUBS=data/aster-stereo/wkunlun-dems/dems_${YYYY}_mosaic_subs.tif   
gdalwarp -overwrite -co COMPRESS=LZW -cutline $PATH_SHP -crop_to_cutline $PATH_DEMS_MOSAIC $PATH_DEMS_SUBS
rm $PATH_DEMS_MOSAIC; 

## ----- 5) dems date mosaic and subset
PATH_DEMS_DATE_MOSAIC=data/aster-stereo/wkunlun-dems/dems_date_${YYYY}_mosaic.tif  ## finally to be saved.
PATH_DEMS_DATE_SORT=''
for PATH_DEM_SORT in $PATH_DEMS_SORT;
do
  PATH_DEM_DATE_SORT=$(dirname $PATH_DEM_SORT)/$(basename $PATH_DEM_SORT .tif)_date.tif
  PATH_DEMS_DATE_SORT+=$PATH_DEM_DATE_SORT' '
done
echo 'dems date mosaic:'
gdal_merge.py -co COMPRESS=LZW -o $PATH_DEMS_DATE_MOSAIC $PATH_DEMS_DATE_SORT
echo 'dems date subset:'
PATH_DEMS_DATE_SUBS=data/aster-stereo/wkunlun-dems/dems_date_${YYYY}_mosaic_subs.tif   
gdalwarp -overwrite -co COMPRESS=LZW -cutline $PATH_SHP -crop_to_cutline $PATH_DEMS_DATE_MOSAIC $PATH_DEMS_DATE_SUBS
rm $DIR_DATA/aster_dem/*/*_date.tif
rm $PATH_DEMS_DATE_MOSAIC; 


