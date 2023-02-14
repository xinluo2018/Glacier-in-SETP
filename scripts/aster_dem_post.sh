#! /bin/bash
## author: xin luo; xxxx
## create: 2023.02.13;
## des: post-processing for the generated aster dems. include: 
##    2) reproject the generated dem to wgs84.
##    1) aster dem outlier filtering by difference value between aster dem and srtm dem.
## usage: ./scripts/aster_dem_post.sh -y 2007

## workplace
cd /home/xin/Developer-luo/Glacier-in-SETP

## Parameters configuration
year=2007     # default

# Get the options
while getopts "y:" option; do
   case $option in
      y) # Enter a year
         year=$OPTARG;;
      ?) # Invalid option
         echo "Error: Invalid option"
         exit;;
   esac
done

### get data directory and utm zone number.
DIR_DATA=data/aster-stereo/SETP-$year
DIRs_DEM=$DIR_DATA/aster-dem/*
for DIR_DEM in $DIRs_DEM
do
  echo Processing: $DIR_DEM

  # 1) reproject the generated dem to wgs84.
  TSRS_proj4=$(gdalsrsinfo -o proj4 $DIR_DEM/run-DEM.tif);   # UTM projection of the mosaic image 
  UTM_ZONE=$(echo ${TSRS_proj4:17:2})
  TSRS_UTM='+proj=utm +zone='$UTM_ZONE' +ellps=WGS84 +datum=WGS84 +units=m +no_defs' # UTM projection 
  TSRS_WGS84='+proj=longlat +datum=WGS84'       # WGS84 projection 
  gdalwarp -overwrite -s_srs "$TSRS_UTM" -t_srs "$TSRS_WGS84" -srcnodata -3.4028235e+38 -dstnodata -999 -r cubic -co COMPRESS=LZW $DIR_DEM/run-DEM.tif $DIR_DEM/run-DEM_wgs84.tif   # re-projected to wgs84

  # 2) aster dem outlier filtering by difference value between aster dem and srtm dem.
  ## 2.1) get srtm dem from the previous downloaded file.
  ## calculate aster dem extent.
  EXTENT=$(python utils/get_img_extent.py $DIR_DEM/run-DEM_wgs84.tif)  
  echo Extent: $EXTENT
  read -a EXTENT <<< $EXTENT
  WEST=${EXTENT[0]}; EAST=${EXTENT[1]}
  SOUTH=${EXTENT[2]}; NORTH=${EXTENT[3]}
  WEST_INT=$((${WEST%.*}+1)); EAST_INT=$((${EAST%.*}+1))
  if [ $WEST_INT -gt 180 ]; then WEST=$(echo $WEST - 360 | bc); fi ## longitude offset from [0,360] to [-180,180].
  if [ $EAST_INT -gt 180 ]; then EAST=$(echo $EAST - 360 | bc); fi
  paths_srtm=data/dem-data/srtm-c/tiles/tile_??_??.tif
  paths_srtm_sel=$(python utils/imgs_in_extent.py -imgs $paths_srtm -e $WEST $EAST $SOUTH $NORTH)
  echo $paths_srtm_sel
  if test -f srtm_mosaic_tmp.tif; then rm srtm_mosaic_tmp.tif; fi
  gdal_merge.py -co COMPRESS=LZW -o srtm_mosaic_tmp.tif $paths_srtm_sel   # tiled dems mosaic
  if test -f srtm_subs_tmp.tif; then rm srtm_subs_tmp.tif; fi
  gdal_translate -projwin $WEST $NORTH $EAST $SOUTH -co COMPRESS=LZW srtm_mosaic_tmp.tif srtm_subs_tmp.tif   # dems subset
  rm srtm_mosaic_tmp.tif
  ## 2.2 dem outlier filtering with difference value between aster dem and srtm dem.
  python utils/lay_stack.py $DIR_DEM/run-DEM_wgs84.tif srtm_subs_tmp.tif dem_srtm_laysta.tif --extent_mode img_1
  gdal_calc.py --overwrite -A dem_srtm_laysta.tif --A_band=1 -B dem_srtm_laysta.tif --B_band=2 \
                                          --outfile=$DIR_DEM/run-DEM_wgs84_filter_tmp.tif --calc="A*(abs(A-B)<150)" --NoDataValue=-999

  gdalwarp -overwrite -srcnodata "0" -dstnodata "-999" $DIR_DEM/run-DEM_wgs84_filter_tmp.tif $DIR_DEM/run-DEM_wgs84_filter.tif
  rm srtm_subs_tmp.tif 
  rm $DIR_DEM/run-DEM_wgs84_filter_tmp.tif
done






