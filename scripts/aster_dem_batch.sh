#! /bin/bash
## author: xin luo; xxxx
## create: 2022.03.12;

## des: Batch DEM generation (single dem generation -> dem_proc/dem_aster_stereo.ipynb).
##      1) reprojection (to wgs84) for the L1A aster vnir bands (15 m)
##      2) dem generation using aster stereo images.
## usage: the input DIR_DATA should contains a sub-directory (namely aster_raw_l1a)
## note: !!!the user should login OpenTopography firstly, because the dem download is requried.
##       the API key should be replacede in the get_dem.py script.

## workplace
cd /home/xin/Developer-luo/Glacier-in-SETP

### get data directory and utm zone number.
DIR_DATA=data/aster-stereo/SETP-2000

SETTING=scripts/stereo.default
echo 'stereo.default path:' $SETTING

## set variables
DEM_PS=30     # unit:m
TSRS_WGS84='+proj=longlat +datum=WGS84' # WGS84 projection
DIR_L1A=$DIR_DATA/aster-raw-l1a

NUMB_DATA=$(ls -d $DIR_L1A/AST_L1A*.zip | wc | awk '{print $1}')
echo "Numb of Pair-wise images to process: " $NUMB_DATA

ls -d ${DIR_L1A}/AST_L1A*.zip > $DIR_DATA/list_of_zipfile.txt  # write file_name to .txt file

N=1   # start from 1
# N=54   # start from N

while [ $N -le $NUMB_DATA ]
# while [ $N -le 11 ]

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
  echo 'date......'
  echo $YYYY $MM $DD
  HOURDEC=$(echo "($HH+($MN/60.)+($SS/3600.))/24." | bc -l)
  DOY=$(date -d "$YYYY-$MM-$DD" +%j)   ## for linux os
  # DOY=$(date -j -f "%Y-%m-%d" $YYYY-$MM-$DD +%j)    ## for mac os
  DATE_DECIMAL=$(echo "$YYYY+($DOY+$HOURDEC)/365.25" | bc -l | awk '{printf "%.8f\n",$0}')
  #  create new directory (store 1) projected aster image, 
  #  2) generated dem data, 3) medium temporal data)
  FILES_TMP=$DIR_DATA/tmp_$DATE_DECIMAL
  DIR_IMG_REPROJ=$DIR_DATA/aster-reproj/VNIR_$DATE_DECIMAL  # reproject aster image
  DIR_DEM=$DIR_DATA/aster-dem/VNIR_$DATE_DECIMAL
  mkdir $FILES_TMP $DIR_IMG_REPROJ $DIR_DEM

  ### Temporary script, optional delete it later.
  if test -f "$DIR_DEM/run-DEM.tif"; then
    echo "$DIR_DEM/run-DEM.tif exist"
    rm -rf $FILES_TMP      ## remove tmp file
    N=$(expr $N + 1)       ## next aster .zip file
    continue
  fi

  ### 2) uzip l1a data
  NAME_OUTDEM="DEM_$DATE_DECIMAL"
  echo "Generating DEM from images acquired:" $NAME_OUTDEM
  unzip -q $PATH_FILE -d $FILES_TMP/unzip  # unzip the raw l1a aster data

  ## 3) parse the l1a aster stereo image and re-projection.
  aster2asp $FILES_TMP/unzip -o $FILES_TMP/parse/VNIR
  # re-projected the l1a VNIR bands (15 m, bands of green, red, nir)  
  # to wgs84
  mapproject -t rpc --t_srs "$TSRS_WGS84" WGS84 $FILES_TMP/parse/VNIR-Band3N.tif $FILES_TMP/parse/VNIR-Band3N.xml $DIR_IMG_REPROJ/VNIR-Band3N_wgs84.tif

  ## 4) srtm dem acquisition 
  ## 4.1) calculate l1a aster image extent.
  EXTENT=$(python utils/get_img_extent.py $DIR_IMG_REPROJ/VNIR-Band3N_wgs84.tif)  
  echo $EXTENT
  rm $DIR_IMG_REPROJ/VNIR-Band3N_wgs84.tif   
  read -a EXTENT <<< $EXTENT
  WEST=${EXTENT[0]}; EAST=${EXTENT[1]}
  SOUTH=${EXTENT[2]}; NORTH=${EXTENT[3]}
  WEST_INT=$((${WEST%.*}+1)); EAST_INT=$((${EAST%.*}+1))
  if [ $WEST_INT -gt 180 ]; then WEST=$(echo $WEST - 360 | bc); fi ## longitude offset from [0,360] to [-180,180].
  if [ $EAST_INT -gt 180 ]; then EAST=$(echo $EAST - 360 | bc); fi
  ## 4.2) srtm dem acquisition.
  # ## a) get srtm dem online, optional
  # python utils/get_dem.py SRTMGL1_E --bounds $WEST $EAST $SOUTH $NORTH --out $FILES_TMP/srtm_wgs84.tif
  ## b) get srtm dem from the tiled srtm files, optional.
  ## search tile-based dem paths, the dems should full cover the obtained aster image 
  Path_imgs=data/dem-data/srtm-c/tiles/tile_??_??.tif
  PATH_DEMS=$(python utils/imgs_in_extent.py -imgs $Path_imgs -e $WEST $EAST $SOUTH $NORTH)
  gdal_merge.py -co COMPRESS=LZW -o dem_mosaic.tif $PATH_DEMS   # tiled dems mosaic
  gdal_translate -projwin $WEST $NORTH $EAST $SOUTH -co COMPRESS=LZW dem_mosaic.tif $FILES_TMP/srtm_wgs84.tif   # dems subset
  rm dem_mosaic.tif

  # ## 4.3) to utm (srtm dem data)
  ## calculate utm zone
  LON=$(echo "scale=3; $WEST / 2 + $EAST / 2" | bc)
  UTM_ZONE=$(echo "scale=4; $LON / 6 + 31" | bc)
  UTM_ZONE=$(echo $UTM_ZONE | awk '{print int($1)}')
  TSRS_UTM='+proj=utm +zone='$UTM_ZONE' +ellps=WGS84 +datum=WGS84 +units=m +no_defs'  # UTM projection   
  gdalwarp -overwrite -s_srs "$TSRS_WGS84" -t_srs "$TSRS_UTM" -tr 30 30 -r cubic -co COMPRESS=LZW -co TILED=YES $FILES_TMP/srtm_wgs84.tif $FILES_TMP/srtm_utm.tif

  ## 4.4) mapproject onto the give srtm DEM (for the l1a aster stereo image)
  mapproject -t rpc --t_srs "$TSRS_UTM" $FILES_TMP/srtm_utm.tif $FILES_TMP/parse/VNIR-Band3N.tif $FILES_TMP/parse/VNIR-Band3N.xml $DIR_IMG_REPROJ/VNIR-Band3N_utm.tif
  mapproject -t rpc --t_srs "$TSRS_UTM" $FILES_TMP/srtm_utm.tif $FILES_TMP/parse/VNIR-Band3B.tif $FILES_TMP/parse/VNIR-Band3B.xml $DIR_IMG_REPROJ/VNIR-Band3B_utm.tif
  mapproject -t rpc --t_srs "$TSRS_UTM" $FILES_TMP/srtm_utm.tif $FILES_TMP/unzip/*VNIR_Band1*.tif $FILES_TMP/parse/VNIR-Band3N.xml $DIR_IMG_REPROJ/VNIR-Band1_utm.tif 
  mapproject -t rpc --t_srs "$TSRS_UTM" $FILES_TMP/srtm_utm.tif $FILES_TMP/unzip/*VNIR_Band2*.tif $FILES_TMP/parse/VNIR-Band3N.xml $DIR_IMG_REPROJ/VNIR-Band2_utm.tif 
  python utils/lay_stack.py $DIR_IMG_REPROJ/VNIR-Band1_utm.tif $DIR_IMG_REPROJ/VNIR-Band2_utm.tif \
                                  $DIR_IMG_REPROJ/VNIR-Band3N_utm.tif $DIR_IMG_REPROJ/VNIR-LaySta_utm.tif 

  ## 5) generate cloud point data with the utm-projected aster images
  ## note: 1) try --stereo-algorithm asp_mgm; --corr-kernel 15 15;
  ##           --subpixel-kernel 25 25 (default: 21 21 and 35 35)
  ##       2) try set parameters in stereo.default file; 
  ##       3) --ip-filter-using-dem not performs good. and we use gdal_calc.py to achieve the same objective.
  parallel_stereo -t astermaprpc -s $SETTING --skip-rough-homography \
                      $DIR_IMG_REPROJ/VNIR-Band3N_utm.tif $DIR_IMG_REPROJ/VNIR-Band3B_utm.tif \
                      $FILES_TMP/parse/VNIR-Band3N.xml $FILES_TMP/parse/VNIR-Band3B.xml \
                      $FILES_TMP/pc_utm_out/run $FILES_TMP/srtm_utm.tif

  # 6) covert cloud point file to dem image
  point2dem --tr ${DEM_PS} --t_srs "$TSRS_UTM" --errorimage $FILES_TMP/pc_utm_out/run-PC.tif -o $DIR_DEM/run --nodata-value -999

  rm -rf $FILES_TMP      ## remove tmp file
  N=$(expr $N + 1)       ## next aster .zip file
done

rm $DIR_DATA/list_of_zipfile.txt

