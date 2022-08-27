#! /bin/bash
## author: xin luo; xxxx
## create: 2022.03.30; modify: 2022.8.10
## des: DEMs mosaic for generated dems in west kunlun. 
##      1）the outlier data in aster dem are filtered with auxiliary srtm-c dem data.
##      2）the dems are mosaicked with a given prefered acquisition date.
##      3) the date of the masaic image is mapped.
## usage: the input DIR_DATA should contains a sub-directory (namely aster_dem)

### get data directory
DIR_DATA=data/aster-stereo/2009-36-78

## parameters configuration
cd /Users/luo/Library/CloudStorage/OneDrive-Personal/GitHub/Glacier-in-RGI1305
date_center=0.54      # priority date, e.g., 0.5 represent the middle of a year.
EXTENT_SUBS='78 37 79 36'  # wgs84 coordinate system

## -----1) get data file information
NAME_FILE=$(basename $DIR_DATA)
YYYY=$(echo ${NAME_FILE:0:4}) ## year of the dem data
# ## get dems path
PATH_DEMS=$(ls $DIR_DATA/aster_dem/VNIR*/run-DEM.tif)

## -----2) generate date images corresponding to dems images
echo 'Generate dems date image:'
for PATH_DEM in $PATH_DEMS;
do
  PATH_DEM_DATE=$(dirname $PATH_DEM)/$(basename $PATH_DEM .tif)_date.tif
  date=$(echo $(dirname $PATH_DEM | xargs basename | cut -d '_' -f 2))
  gdal_calc.py -A $PATH_DEM --outfile=$PATH_DEM_DATE --calc="($date*(A>0))"   # band math.
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
PATH_DEMS_MOSAIC=$DIR_DATA/dems_${YYYY}_mosaic.tif  
echo 'dems mosaic:'
gdal_merge.py -co COMPRESS=LZW -o $PATH_DEMS_MOSAIC $PATH_DEMS_SORT
echo 'dems subset:'
TSRS_WGS84='+proj=longlat +datum=WGS84'       # WGS84 projection 
TSRS_UTM=$(gdalsrsinfo -o proj4 $PATH_DEMS_MOSAIC);   # UTM projection of the mosaic image 
PATH_DEMS_MOSAIC_WGS84=$DIR_DATA/dems_${YYYY}_mosaic_wgs84.tif   
PATH_DEMS_SUBS=$DIR_DATA/dems_${YYYY}_mosaic_subs.tif   
gdalwarp -overwrite -s_srs "$TSRS_UTM" -t_srs "$TSRS_WGS84" -r cubic -co COMPRESS=LZW $PATH_DEMS_MOSAIC $PATH_DEMS_MOSAIC_WGS84 # re-projection
gdal_translate -projwin $EXTENT_SUBS -co COMPRESS=LZW $PATH_DEMS_MOSAIC_WGS84 $PATH_DEMS_SUBS
rm $PATH_DEMS_MOSAIC; 
rm $PATH_DEMS_MOSAIC_WGS84; 

## ----- 5) dems date mosaic and subset
PATH_DEMS_DATE_MOSAIC=$DIR_DATA/dems_date_${YYYY}_mosaic.tif  ## finally to be saved.
PATH_DEMS_DATE_SORT=''
for PATH_DEM_SORT in $PATH_DEMS_SORT;
do
  PATH_DEM_DATE_SORT=$(dirname $PATH_DEM_SORT)/$(basename $PATH_DEM_SORT .tif)_date.tif
  PATH_DEMS_DATE_SORT+=$PATH_DEM_DATE_SORT' '
done
echo 'dems date mosaic:'
gdal_merge.py -co COMPRESS=LZW -o $PATH_DEMS_DATE_MOSAIC $PATH_DEMS_DATE_SORT
echo 'dems date subset:'
PATH_DEMS_DATE_MOSAIC_WGS84=$DIR_DATA/dems_date_${YYYY}_mosaic_wgs84.tif
PATH_DEMS_DATE_SUBS=$DIR_DATA/dems_date_${YYYY}_mosaic_subs.tif   
gdalwarp -overwrite -s_srs "$TSRS_UTM" -t_srs "$TSRS_WGS84" -r cubic -co COMPRESS=LZW $PATH_DEMS_DATE_MOSAIC $PATH_DEMS_DATE_MOSAIC_WGS84 # re-projection
gdal_translate -projwin $EXTENT_SUBS -co COMPRESS=LZW $PATH_DEMS_DATE_MOSAIC_WGS84 $PATH_DEMS_DATE_SUBS
rm $DIR_DATA/aster_dem/*/*_date.tif
rm $PATH_DEMS_DATE_MOSAIC; 
rm $PATH_DEMS_DATE_MOSAIC_WGS84; 
