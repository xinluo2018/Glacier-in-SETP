#! /bin/bash
## author: xin luo; xxxx
## create: 2022.03.12;
## des: Batch DEM generation (single dem generation -> dem_proc/dem_aster_stereo.ipynb).
##      1) reprojection (to wgs84) for the L1A aster vnir bands (15 m)
##      2) dem generation using aster stereo images.
## usage: the input DIR_DATA should contains a sub-directory (namely aster_raw_l1a)


### get data directory and utm zone number.
DIR_DATA=data/aster_data/wkunlun-2001
# while getopts d:z: flag
# do
#   case "${flag}" in
#       d) DIR_DATA=${OPTARG};;
#   esac
# done

## parameters configuration
cd /Users/luo/Library/CloudStorage/OneDrive-Personal/GitHub/Glacier-in-RGI1305

SETTING=script/stereo.default
echo 'stereo.default path:' $SETTING

## set variables
DEM_PS=30     # unit:m
TSRS_WGS84='+proj=longlat +datum=WGS84' # UTM projection 
DIR_L1A=$DIR_DATA/aster_raw_L1A

NUMB_DATA=$(ls -d $DIR_L1A/AST_L1A*.zip | wc | awk '{print $1}')
echo "Numb of DEMs to process: " $NUMB_DATA

ls -d ${DIR_L1A}/AST_L1A*.zip > $DIR_DATA/list_of_zipfile.txt  # write file_name to .txt file

N=1

# while [ $N -le $NUMB_DATA ]
while [ $N -le 3 ]

do
  echo 'processing ---> data' $N
  PATH_FILE=$(head -$N ${DIR_DATA}/list_of_zipfile.txt | tail -1)
  NAME_FILE=$(basename $PATH_FILE)
  echo 'aster file path:' $PATH_FILE
  #### 1) get image acquisition time.
  MM=$(echo ${NAME_FILE:11:2})
  DD=$(echo ${NAME_FILE:13:2})
  YYYY=$(echo ${NAME_FILE:15:4})
  HH=$(echo ${NAME_FILE:19:2})
  MN=$(echo ${NAME_FILE:21:2})
  SS=$(echo ${NAME_FILE:23:2})
  HOURDEC=$(echo "($HH+($MN/60.)+($SS/3600.))/24." | bc -l)
  # DOY=$(date -d "$YYYY-$MM-$DD" +%j)   ## for linux os
  DOY=$(date -j -f "%Y-%m-%d" $YYYY-$MM-$DD +%j)    ## for mac os
  DATE_DECIMAL=$(echo "$YYYY+($DOY+$HOURDEC)/365.25" | bc -l | awk '{printf "%.8f\n",$0}')
  #  create new directory (store 1) projected aster image, 
  #  2) generated dem data, 3) medium temporal data)
  FILES_TMP=$DIR_DATA/tmp_$DATE_DECIMAL
  DIR_IMG_REPROJ=$DIR_DATA/aster_reproj/VNIR_$DATE_DECIMAL  # reproject aster image
  DIR_DEM=$DIR_DATA/aster_dem/VNIR_$DATE_DECIMAL
  mkdir $FILES_TMP $DIR_IMG_REPROJ $DIR_DEM

  ### 2) uzip l1a data
  NAME_OUTDEM="DEM_$DATE_DECIMAL"
  echo "Generating DEM from images acquired:" $NAME_OUTDEM
  unzip -q $PATH_FILE -d $FILES_TMP/unzip  # unzip the raw l1a aster data

  ## 3) parse the l1a aster data
  aster2asp $FILES_TMP/unzip -o $FILES_TMP/parse/run
  ## 4) reproject l1a vnir image
  ## re-projected the l1a VNIR bands (15 m, bands of green, red, nir)  
  ## 4.1) to wgs84
  mapproject -t rpc --t_srs "$TSRS_WGS84" WGS84 $FILES_TMP/parse/run-Band3N.tif $FILES_TMP/parse/run-Band3N.xml $DIR_IMG_REPROJ/VNIR-Band3N_wgs84.tif

  ## 4.2) get image extent and download srtm dem data 
  EXTENT=$(python utils/get_extent.py $DIR_IMG_REPROJ/VNIR-Band3N_wgs84.tif)  
  rm $DIR_IMG_REPROJ/VNIR-Band3N_wgs84.tif
  read -a EXTENT <<< $EXTENT
  WEST=${EXTENT[1]}; EAST=${EXTENT[2]}
  SOUTH=${EXTENT[3]}; NORTH=${EXTENT[4]}
  WEST_INT=$((${WEST%.*}+1)); EAST_INT=$((${EAST%.*}+1))
  if [ $WEST_INT -gt 180 ]; then WEST=$(echo $WEST - 360 | bc); fi ## longitude offset from [0,360] to [-180,180].
  if [ $EAST_INT -gt 180 ]; then EAST=$(echo $EAST - 360 | bc); fi
  ## calculate utm zone
  LON=$(echo "scale=3; $WEST / 2 + $EAST / 2" | bc)
  UTM_ZONE=$(echo "scale=4; $LON / 6 + 31" | bc)
  UTM_ZONE=$(echo $UTM_ZONE | awk '{print int($1)}')
  echo $UTM_ZONE

  TSRS_UTM='+proj=utm +zone='$UTM_ZONE' +ellps=WGS84 +datum=WGS84 +units=m +no_defs' # UTM projection 
  
  python utils/get_dem.py SRTMGL1_E $WEST $EAST $SOUTH $NORTH --out $FILES_TMP/srtm_wgs84.tif
   # # ## 4.3) to utm (both for dem data and aster image)
  gdalwarp -overwrite -s_srs "$TSRS_WGS84" -t_srs "$TSRS_UTM" -tr 30 30 -r cubic -co COMPRESS=LZW -co TILED=YES $FILES_TMP/srtm_wgs84.tif $FILES_TMP/srtm_utm.tif

  mapproject -t rpc --t_srs "$TSRS_UTM" $FILES_TMP/srtm_utm.tif $FILES_TMP/parse/run-Band3N.tif $FILES_TMP/parse/run-Band3N.xml $DIR_IMG_REPROJ/VNIR-Band3N_utm.tif
  mapproject -t rpc --t_srs "$TSRS_UTM" $FILES_TMP/srtm_utm.tif $FILES_TMP/parse/run-Band3B.tif $FILES_TMP/parse/run-Band3B.xml $DIR_IMG_REPROJ/VNIR-Band3B_utm.tif
  mapproject -t rpc --t_srs "$TSRS_UTM" $FILES_TMP/srtm_utm.tif $FILES_TMP/unzip/*VNIR_Band1*.tif $FILES_TMP/parse/run-Band3N.xml $DIR_IMG_REPROJ/VNIR-Band1_utm.tif 
  mapproject -t rpc --t_srs "$TSRS_UTM" $FILES_TMP/srtm_utm.tif $FILES_TMP/unzip/*VNIR_Band2*.tif $FILES_TMP/parse/run-Band3N.xml $DIR_IMG_REPROJ/VNIR-Band2_utm.tif 
  python utils/lay_stack.py  $DIR_IMG_REPROJ/VNIR-Band1_utm.tif $DIR_IMG_REPROJ/VNIR-Band2_utm.tif \
                             $DIR_IMG_REPROJ/VNIR-Band3N_utm.tif $DIR_IMG_REPROJ/VNIR-LaySta_utm.tif 

  ## 5) generate cloud point data with the utm-projected aster images
  ## note: try --stereo-algorithm asp_mgm; --corr-kernel 15 15;
  ##           --subpixel-kernel 25 25 (default: 21 21 and 35 35)
  ##       try set parameters in stereo.default file
  parallel_stereo -t astermaprpc -s $SETTING --skip-rough-homography \
                      $DIR_IMG_REPROJ/VNIR-Band3N_utm.tif $DIR_IMG_REPROJ/VNIR-Band3B_utm.tif \
                      $FILES_TMP/parse/run-Band3N.xml $FILES_TMP/parse/run-Band3B.xml \
                      $FILES_TMP/pc_utm_out/run $FILES_TMP/srtm_utm.tif

  # 6) covert cloud point file to dem image
  point2dem --tr ${DEM_PS} --t_srs "$TSRS_UTM" --errorimage $FILES_TMP/pc_utm_out/run-PC.tif -o $DIR_DEM/run

  rm -rf $FILES_TMP      ## remove tmp file
  N=$(expr $N + 1)       ## next aster .zip file

done

rm $DIR_DATA/list_of_zipfile.txt

