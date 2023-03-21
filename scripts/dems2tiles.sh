#! /bin/bash
## author: xin luo; xxxx
## create: 2022.03.30; modify: 2022.8.10
## des: DEMs mosaic to sub-region/tile by using generated dems. 
##      1）the dems are mosaicked with a given tile/sub-region extent and the prefered acquisition date.
##      2) the date of the masaic image is mapped.
## usage: ./scripts/dems2tiles.sh -y 2007


cd /home/xin/Developer-luo/Glacier-in-SETP

## Parameters configuration
year=2007   # default

# Get the options
while getopts "y:" arg; do
   case $arg in
      y) # Enter a year
         year=$OPTARG;;
      ?) # Invalid argment
         echo "Error: Invalid argment"
         exit;;
   esac
done

lefts=(91 92 93 94 95 91 92 93 94 95 96 97 91 92 93 94 95 96 97 98 94 95 96 97 98 96 97 98)
bottoms=(31 31 31 31 31 30 30 30 30 30 30 30 29 29 29 29 29 29 29 29 28 28 28 28 28 27 27 27)
# lefts=(91); bottoms=(31)
for (( i=0; i<${#lefts[@]}; i++)) 
  do
  left=${lefts[i]}; bottom=${bottoms[i]}
  echo 'Tile left-bottom corner:' $left $bottom;
  tile_res=1  # tile resolution, default is 1.
  right=$(expr $left + $tile_res)
  up=$(expr $bottom + $tile_res)
  date_center=0.583      # priority date, e.g., 0.5 represents the middle of a year; 0.583 represents July 1.
  DIR_DATA=data/aster-stereo/SETP-$year
  DIR_Tile=$DIR_DATA/tiles-dem/tile-$bottom-$left
  mkdir -p $DIR_Tile      ### create the directory
  ## -----1) get sub-region (tile-based) dem paths
  Path_imgs=$DIR_DATA/aster-dem/*/run-DEM_wgs84_filter_coreg.tif
  PATH_DEMS=$(python utils/imgs_in_extent.py -imgs $Path_imgs -e $left $right $bottom $up)
  if [ -z "$PATH_DEMS" ]; then
    echo "There is not image in the sub-region extent"
    continue
  fi

  ## -----2) generate date images corresponding to dems images
  echo 'Generate dems date image:'
  for PATH_DEM in $PATH_DEMS;
  do
    PATH_DEM_DATE=$(dirname $PATH_DEM)/$(basename $PATH_DEM .tif)_date.tif
    if [ ! -f "$PATH_DEM_DATE" ]; then
      date=$(echo $(dirname $PATH_DEM | xargs basename | cut -d '_' -f 2))
      gdal_calc.py -A $PATH_DEM --outfile=$PATH_DEM_DATE --calc="($date*(A>0))" --NoDataValue=-999  # band math.
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
  num_dems=$(echo "$PATH_DEMS" | wc -w)
  echo "Dems for mosaic (number: $num_dems):"
  echo $PATH_DEMS_SORT | xargs -n 1
  rm $DIR_Tile/list_dems.txt

  ## ----- 4) dems mosaic and subset
  PATH_DEMS_MOSAIC=$DIR_Tile/dems_mosaic.tif
  PATH_DEMS_SUBS=$DIR_Tile/dems_mosaic_subs.tif
  echo 'dems mosaic:'
  if test -f $PATH_DEMS_MOSAIC; then rm $PATH_DEMS_MOSAIC; fi
  gdal_merge.py -n -999 -a_nodata -999 -co COMPRESS=LZW -o $PATH_DEMS_MOSAIC $PATH_DEMS_SORT
  echo 'dems subset:'
  if test -f $PATH_DEMS_SUBS; then rm $PATH_DEMS_SUBS; fi
  extent="${left} ${up} ${right} ${bottom}" 
  gdal_translate -projwin $extent -co COMPRESS=LZW $PATH_DEMS_MOSAIC $PATH_DEMS_SUBS  ## subseting
  rm $PATH_DEMS_MOSAIC; 

  ## ----- 5) dems date mosaic and subset
  PATH_DEMS_DATE_MOSAIC=$DIR_Tile/dems_date_mosaic.tif  ## finally to be saved.
  PATH_DEMS_DATE_SORT=''
  for PATH_DEM_SORT in $PATH_DEMS_SORT;
  do
    PATH_DEM_DATE_SORT=$(dirname $PATH_DEM_SORT)/$(basename $PATH_DEM_SORT .tif)_date.tif
    PATH_DEMS_DATE_SORT+=$PATH_DEM_DATE_SORT' '
  done
  echo $PATH_DEMS_DATE_SORT
  echo 'dems date mosaic:'
  if test -f $PATH_DEMS_DATE_MOSAIC; then rm $PATH_DEMS_DATE_MOSAIC; fi
  gdal_merge.py -n -999 -a_nodata -999 -co COMPRESS=LZW -o $PATH_DEMS_DATE_MOSAIC $PATH_DEMS_DATE_SORT
  echo 'dems date subset:'
  PATH_DEMS_DATE_SUBS=$DIR_Tile/dems_mosaic_date_subs.tif
  if test -f $PATH_DEMS_DATE_SUBS; then rm $PATH_DEMS_DATE_SUBS; fi
  gdal_translate -projwin $extent -co COMPRESS=LZW $PATH_DEMS_DATE_MOSAIC $PATH_DEMS_DATE_SUBS
  rm $DIR_DATA/aster-dem/*/*_date.tif;
  rm $PATH_DEMS_DATE_MOSAIC; 

done 
