#! /bin/bash
## author: xin luo; xxxx
## create: 2022.03.30;
## des: DEMs mosaic for generated dems in west kunlun. 
##      1）the outlier data in aster dem are filtered with auxiliary srtm-c dem data.
##      2）the dem data that nearest to July 1st is the top priority.        
## usage: the input DIR_DATA should contains a sub-directory (namely aster_dem)


### get data directory
DIR_DATA=data/aster_data/wkunlun-2000

## parameters configuration
cd /Users/luo/Library/CloudStorage/OneDrive-Personal/GitHub/Glacier-in-RGI1305
PATH_SHP=data/study_area/study_area_buffer.shp

## -----1) get data file information
NAME_FILE=$(basename $DIR_DATA)
YYYY=$(echo ${NAME_FILE:8:12}) ## year of the dem data

## get dems path
PATH_DEMS=$(ls $DIR_DATA/aster_dem/VNIR*/run-DEM.tif)

## ----- 2) aster dem thresholding by using srtm-c dem
##          the difference>100 between srtm dem and aster dem are masked. 

for PATH_DEM in $PATH_DEMS;
do
  DIR_DEM=$(dirname $PATH_DEM)
  PATH_DEM_THRE=$DIR_DEM/run-DEM_thre.tif
  PATH_DEMS_STACK=$DIR_DEM/run-DEM_laysta.tif
  PATH_SRTM_C=data/dem_data/srtm-c/SRTMGL1_E_wkunlun_utm.tif
  python utils/lay_stack.py $PATH_DEM $PATH_SRTM_C $PATH_DEMS_STACK --union False
  gdal_calc.py -A $PATH_DEMS_STACK --A_band=1 -B $PATH_DEMS_STACK --B_band=2 \
                --outfile=$PATH_DEM_THRE --calc="(A*(abs(B-A)<100)-999*(abs(B-A)>100))"
  rm $PATH_DEMS_STACK
done


## -----3) sort the path_dems. 
## the dem nearer to July 1st is placed latter.
PATH_DEMS_THRE=$(ls $DIR_DATA/aster_dem/VNIR*/run-DEM_thre.tif)   ##
for PATH_DEM in $PATH_DEMS_THRE;
do
  date=.$(dirname $PATH_DEM | xargs basename | cut -d '.' -f 2 )
  dif=$(echo $date - 0.5 | bc | sed 's/-//')
  echo $dif $PATH_DEM >> $DIR_DATA/aster_dem/list_dems.txt
done

cat $DIR_DATA/aster_dem/list_dems.txt | sort -r > $DIR_DATA/aster_dem/list_dems_sort.txt
PATH_DEMS_SORT=$(cut -d ' ' -f 2 $DIR_DATA/aster_dem/list_dems_sort.txt)
echo 'Images for mosaic:'
echo $PATH_DEMS_SORT | xargs -n 1
rm $DIR_DATA/aster_dem/list_dems.txt
rm $DIR_DATA/aster_dem/list_dems_sort.txt

## ----- 4) mosaic
PATH_MOSAIC=data/aster_data/wkunlun-dems/dems_mosaic_${YYYY}.tif  ## finally to be saved.
gdal_merge.py -init 0 -n -999 -co COMPRESS=LZW -o $PATH_MOSAIC $PATH_DEMS_SORT

## ----- 5) subset with study area vector file
PATH_SUBS=data/aster_data/wkunlun-dems/dems_mosaic_${YYYY}_subs.tif   
gdalwarp -co COMPRESS=LZW -cutline $PATH_SHP $PATH_MOSAIC $PATH_SUBS
mv $PATH_SUBS $PATH_MOSAIC


