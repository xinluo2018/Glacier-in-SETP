#! /bin/bash
## author: xin luo; xxxx
## create: 2022.03.30; modify: 2022.8.10
## des: DEMs mosaic for generated dems in west kunlun. 
##      1）the dems are mosaicked with a given prefered acquisition date.
##      2) the date of the masaic image is mapped.
## usage: ./scripts/aster_dems_mosaic.sh -l 92 -b 31

cd /home/xin/Developer-luo/Glacier-in-SETP

## Parameters configuration
YYYY=2020
# lefts=(91 92 93 94 95 91 92 93 94 95 96 97 91 92 93 94 95 96 97 98 94 95 96 97 98 96 97 98)
# bottoms=(31 31 31 31 31 30 30 30 30 30 30 30 29 29 29 29 29 29 29 29 28 28 28 28 28 27 27 27)
lefts=(97); bottoms=(29)
for (( i=0; i<${#lefts[@]}; i++)) 
  do
  left=${lefts[i]}; bottom=${bottoms[i]}
  echo 'Tile left-bottom corner:' $left $bottom;
  # left=91; bottom=21         ## default left longitude
  tile_res=1  # tile resolution, default is 1.
  right=$(expr $left + $tile_res)
  up=$(expr $bottom + $tile_res)
  date_center=0.583      # priority date, e.g., 0.5 represents the middle of a year; 0.583 represents July 1.
  DIR_DATA=data/aster-stereo/SETP-$YYYY
  DIR_Tile=$DIR_DATA/tiles-dem/tile-$bottom-$left
  mkdir -p $DIR_Tile      ### create the directory

  ## -----1) get dem paths
  Path_imgs=$DIR_DATA/aster-dem/*/run-DEM.tif
  PATH_DEMS=$(python utils/imgs_in_extent.py -imgs $Path_imgs -e $left $right $bottom $up)

  ## -----2) generate date images corresponding to dems images
  echo 'Generate dems date image:'
  for PATH_DEM in $PATH_DEMS;
  do
    PATH_DEM_DATE=$(dirname $PATH_DEM)/$(basename $PATH_DEM .tif)_date.tif
    if [ ! -f "$PATH_DEM_DATE" ]; then
      date=$(echo $(dirname $PATH_DEM | xargs basename | cut -d '_' -f 2))
      gdal_calc.py -A $PATH_DEM --outfile=$PATH_DEM_DATE --calc="($date*(A>0))"   # band math.
    fi
  done

  ## -----3) sort the path_dems by the date which near to the given date_center. 
  ## the dem nearer to date_center is placed latter.
  for PATH_DEM in $PATH_DEMS;
  do
    date=.$(dirname $PATH_DEM | xargs basename | cut -d '.' -f 2 )
    dif=$(echo $date - $date_center | bc | sed 's/-//')
    echo $dif $PATH_DEM >> $DIR_Tile/list_dems.txt
  done
  cat $DIR_Tile/list_dems.txt | sort -r > $DIR_Tile/list_dems_sort.txt
  PATH_DEMS_SORT=$(cut -d ' ' -f 2 $DIR_Tile/list_dems_sort.txt)
  echo 'Images for mosaic:'
  echo $PATH_DEMS_SORT | xargs -n 1
  rm $DIR_Tile/list_dems.txt
  # rm $DIR_Tile/list_dems_sort.txt

  ## ----- 4) dems mosaic and subset
  PATH_DEMS_MOSAIC=$DIR_Tile/dems_mosaic.tif
  echo 'dems mosaic:'
  gdal_merge.py -co COMPRESS=LZW -o $PATH_DEMS_MOSAIC $PATH_DEMS_SORT
  echo 'dems subset:'
  TSRS_proj4=$(gdalsrsinfo -o proj4 $PATH_DEMS_MOSAIC);   # UTM projection of the mosaic image 
  UTM_ZONE=$(echo ${TSRS_proj4:17:2})
  TSRS_UTM='+proj=utm +zone='$UTM_ZONE' +ellps=WGS84 +datum=WGS84 +units=m +no_defs' # UTM projection 
  TSRS_WGS84='+proj=longlat +datum=WGS84'       # WGS84 projection 
  PATH_DEMS_MOSAIC_WGS84=$DIR_Tile/dems_mosaic_wgs84.tif   
  PATH_DEMS_SUBS=$DIR_Tile/dems_mosaic_wgs84_subs.tif
  echo $TSRS_UTM 
  echo $TSRS_WGS84
  gdalwarp -overwrite -s_srs "$TSRS_UTM" -t_srs "$TSRS_WGS84" -r cubic -co COMPRESS=LZW $PATH_DEMS_MOSAIC $PATH_DEMS_MOSAIC_WGS84  # re-projected to wgs84
  extent="${left} ${up} ${right} ${bottom}" 
  gdal_translate -projwin $extent -co COMPRESS=LZW $PATH_DEMS_MOSAIC_WGS84 $PATH_DEMS_SUBS    ## subseting
  rm $PATH_DEMS_MOSAIC; 
  rm $PATH_DEMS_MOSAIC_WGS84; 

  ## ----- 5) dems date mosaic and subset
  PATH_DEMS_DATE_MOSAIC=$DIR_Tile/dems_date_mosaic.tif  ## finally to be saved.
  PATH_DEMS_DATE_SORT=''
  for PATH_DEM_SORT in $PATH_DEMS_SORT;
  do
    PATH_DEM_DATE_SORT=$(dirname $PATH_DEM_SORT)/$(basename $PATH_DEM_SORT .tif)_date.tif
    PATH_DEMS_DATE_SORT+=$PATH_DEM_DATE_SORT' '
  done
  echo 'dems date mosaic:'
  gdal_merge.py -co COMPRESS=LZW -o $PATH_DEMS_DATE_MOSAIC $PATH_DEMS_DATE_SORT
  echo 'dems date subset:'
  PATH_DEMS_DATE_MOSAIC_WGS84=$DIR_Tile/dems_date_mosaic_wgs84.tif
  PATH_DEMS_DATE_SUBS=$DIR_Tile/dems_mosaic_date_subs.tif   
  gdalwarp -overwrite -s_srs "$TSRS_UTM" -t_srs "$TSRS_WGS84" -r cubic -co COMPRESS=LZW $PATH_DEMS_DATE_MOSAIC $PATH_DEMS_DATE_MOSAIC_WGS84 # re-projection
  gdal_translate -projwin $extent -co COMPRESS=LZW $PATH_DEMS_DATE_MOSAIC_WGS84 $PATH_DEMS_DATE_SUBS
  rm $DIR_DATA/aster-dem/*/*_date.tif
  rm $PATH_DEMS_DATE_MOSAIC; 
  rm $PATH_DEMS_DATE_MOSAIC_WGS84;

done 
