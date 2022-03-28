#! /bin/bash
## author: xin luo; xxxx
## create: 2022.03.12;
## des: Batch DEM generation (single dem generation -> dem_proc/dem_aster_stereo.ipynb).
##      1) reprojection (to wgs84) for the L1A aster vnir bands (15 m)
##      2) dem generation using aster stereo images.
## usage: the input dir_data should contains a sub-directory (namely aster_raw_l1a)
## todo: automatically determine the utm_zone through obtained longitude and latitude.


### get data directory and utm zone number.
# dir_data=data/aster_data/demo_tmp
# utm_zone='10'
while getopts d:z: flag
do
  case "${flag}" in
      d) dir_data=${OPTARG};;
  esac
done

## parameters configuration
cd /Users/luo/Library/CloudStorage/OneDrive-Personal/GitHub/Glacier-in-RGI1305

# settings=script/stereo.default
# echo 'stereo.default path:' $settings

### augments.
DEM_PS=30     # unit:m

## set variables
tsrs_wgs84='+proj=longlat +datum=WGS84' # UTM projection 
dir_l1a=$dir_data/aster_raw_L1A

numb_data=$(ls -d $dir_l1a/AST_L1A*.zip | wc | awk '{print $1}')
echo "Numb of DEMs to process: " $numb_data

ls -d ${dir_l1a}/AST_L1A*.zip > $dir_data/list_of_zipfile.txt  # write file_name to .txt file

N=1

while [ $N -le $numb_data ]
# while [ $N -le 2 ]

do
  echo 'processing ---> data' $N
  path_file=$(head -$N ${dir_data}/list_of_zipfile.txt | tail -1)
  echo $path_file
  dir_file=$(dirname $path_file)
  name_file=$(basename $path_file)
  echo 'aster file path:' $path_file
  echo 'aster file name:' $name_file
  #### 1) get image acquisition time.
  MM=$(echo ${name_file:11:2})
  DD=$(echo ${name_file:13:2})
  YYYY=$(echo ${name_file:15:4})
  HH=$(echo ${name_file:19:2})
  MN=$(echo ${name_file:21:2})
  SS=$(echo ${name_file:23:2})
  hourdec=$(echo "($HH+($MN/60.)+($SS/3600.))/24." | bc -l)
  # doy=$(date -d "$YYYY-$MM-$DD" +%j)   ## for linux os
  doy=$(date -j -f "%Y-%m-%d" $YYYY-$MM-$DD +%j)    ## for mac os
  date_decimal=$(echo "$YYYY+($doy+$hourdec)/365.25" | bc -l | awk '{printf "%.8f\n",$0}')
  #  create new directory (store 1) projected aster image, 
  #  2) generated dem data, 3) medium temporal data)
  files_tmp=$dir_data/tmp_$date_decimal
  dir_img_reproj=$dir_data/aster_reproj/VNIR_$date_decimal  # reproject aster image
  dir_dem=$dir_data/aster_dem/VNIR_$date_decimal
  mkdir $files_tmp $dir_img_reproj $dir_dem

  ### 2) uzip l1a data
  name_outdem="DEM_$date_decimal"
  echo "Generating DEM from images acquired:" $name_outdem
  unzip -q $path_file -d $files_tmp/unzip  # unzip the raw l1a aster data

  ## 3) parse the l1a aster data
  aster2asp $files_tmp/unzip -o $files_tmp/parse/run
  ## 4) reproject l1a vnir image
  ## re-projected the l1a VNIR bands (15 m, bands of green, red, nir)  
  ## 4.1) to wgs84
  mapproject -t rpc --t_srs "$tsrs_wgs84" WGS84 $files_tmp/parse/run-Band3N.tif $files_tmp/parse/run-Band3N.xml $dir_img_reproj/VNIR-Band3N_wgs84.tif
  mapproject -t rpc --t_srs "$tsrs_wgs84" WGS84 $files_tmp/unzip/*VNIR_Band1*.tif $files_tmp/parse/run-Band3N.xml $dir_img_reproj/VNIR-Band1_wgs84.tif
  mapproject -t rpc --t_srs "$tsrs_wgs84" WGS84 $files_tmp/unzip/*VNIR_Band2*.tif $files_tmp/parse/run-Band3N.xml $dir_img_reproj/VNIR-Band2_wgs84.tif
  python utils/lay_stack.py  $dir_img_reproj/VNIR-Band1_wgs84.tif $dir_img_reproj/VNIR-Band2_wgs84.tif \
                             $dir_img_reproj/VNIR-Band3N_wgs84.tif $dir_img_reproj/VNIR-LaySta_wgs84.tif 

  ## 4.2) get image extent and downloda srtm dem data 
  extent=$(python utils/get_extent.py $dir_img_reproj/VNIR-Band3N_wgs84.tif) 
  read -a extent <<< $extent
  west=${extent[1]}; east=${extent[2]}
  south=${extent[3]}; north=${extent[4]}
  west_int=$((${west%.*}+1)); east_int=$((${east%.*}+1))
  if [ $west_int -gt 180 ]; then west=$(echo $west - 360 | bc); fi
  if [ $east_int -gt 180 ]; then east=$(echo $east - 360 | bc); fi
  ## obtain utm zone
  lon=$(echo "scale=3; $west / 2 + $east / 2" | bc)
  utm_zone=$(echo $lon / 6 + 31 | bc)
  tsrs_utm='+proj=utm +zone='$utm_zone' +ellps=WGS84 +datum=WGS84 +units=m +no_defs' # UTM projection 
  
  python utils/get_dem.py SRTMGL1_E $west $east $south $north --out $files_tmp/srtm_wgs84.tif
   # # ## 4.3) to utm (both for dem data and aster image)
  gdalwarp -overwrite -s_srs "$tsrs_wgs84" -t_srs "$tsrs_utm" -tr 30 30 -r cubic -co COMPRESS=LZW -co TILED=YES $files_tmp/srtm_wgs84.tif $files_tmp/srtm_utm.tif

  mapproject -t rpc --t_srs "$tsrs_utm" $files_tmp/srtm_utm.tif $files_tmp/parse/run-Band3N.tif $files_tmp/parse/run-Band3N.xml $dir_img_reproj/VNIR-Band3N_utm.tif
  mapproject -t rpc --t_srs "$tsrs_utm" $files_tmp/srtm_utm.tif $files_tmp/parse/run-Band3B.tif $files_tmp/parse/run-Band3B.xml $dir_img_reproj/VNIR-Band3B_utm.tif
  mapproject -t rpc --t_srs "$tsrs_utm" $files_tmp/srtm_utm.tif $files_tmp/unzip/*VNIR_Band1*.tif $files_tmp/parse/run-Band3N.xml $dir_img_reproj/VNIR-Band1_utm.tif 
  mapproject -t rpc --t_srs "$tsrs_utm" $files_tmp/srtm_utm.tif $files_tmp/unzip/*VNIR_Band2*.tif $files_tmp/parse/run-Band3N.xml $dir_img_reproj/VNIR-Band2_utm.tif 
  python utils/lay_stack.py  $dir_img_reproj/VNIR-Band1_utm.tif $dir_img_reproj/VNIR-Band2_utm.tif \
                             $dir_img_reproj/VNIR-Band3N_utm.tif $dir_img_reproj/VNIR-LaySta_utm.tif 

  ## 5) generate cloud point data with the utm-projected aster images
  ## note: try --stereo-algorithm asp_mgm; --corr-kernel 15 15; 
  ##           --subpixel-kernel 25 25 (default: 21 21 and 35 35)
  ##       try set parameters in stereo.default file
  parallel_stereo -t astermaprpc --skip-rough-homography --subpixel-mode 3 \
                      $dir_img_reproj/VNIR-Band3N_utm.tif $dir_img_reproj/VNIR-Band3B_utm.tif \
                      $files_tmp/parse/run-Band3N.xml $files_tmp/parse/run-Band3B.xml \
                      $files_tmp/pc_utm_out/run $files_tmp/srtm_utm.tif

  # 6) covert cloud point file to dem image
  point2dem --tr ${DEM_PS} --t_srs "$tsrs_utm" --errorimage $files_tmp/pc_utm_out/run-PC.tif -o $dir_dem/run

  rm -rf $files_tmp      ## remove tmp file
  N=$(expr $N + 1)       ## next aster .zip file

done

rm $dir_data/list_of_zipfile.txt

