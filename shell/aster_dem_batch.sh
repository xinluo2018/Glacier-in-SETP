#! /bin/bash
## author: xin luo; xxxx
## create: 2022.03.12;
## des: Batch DEM generation.
##      1) reprojection (to wgs84) for the L1A aster vnir bands (15 m)
##      2) dem generation using aster stereo images.


## parameters configuration
settings=shell/stereo.default
echo 'stereo.default path:' $settings
DEM_PS=0.0002777       ## 0.0002777(in degrees), 0.00013885 and 0.0000898 is about 31, 15 and 10 m/pixel

dir_aster=data/aster_data
dir_l1a=$dir_aster/aster_raw_L1A
dir_imgs_reproj=$dir_aster/aster_reproj    
dir_dem=$dir_aster/aster_dem

numb_data=$(ls -d $dir_l1a/AST_L1A*.zip | wc | awk '{print $1}')
echo "Numb of DEMs to process: " $numb_data

ls -d ${dir_l1a}/AST_L1A*.zip > $dir_aster/list_of_zipfile.txt  # write file_name to .txt file

N=1

# while [ $N -le $numb_data ]
while [ $N -le 2 ]

do
  echo 'processing ---> data' $N
  path_file=$(head -$N ${dir_aster}/list_of_zipfile.txt | tail -1)
  echo $path_file
  dir_file=$(dirname $path_file)
  name_file=$(basename $path_file)
  echo 'aster file path:' $path_file
  echo 'aster file name:' $name_file
  #### 1) get aster image info (acquisition time)
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

  ### 2) uzip l1a data
  name_outdem="DEM_$date_decimal"
  echo "Generating DEM from images acquired:" $name_outdem
  files_tmp=$dir_aster/out_tmp
  mkdir $files_tmp
  unzip -q $path_file -d $files_tmp/unzip  # unzip the raw l1a aster data

  ## 3) parse the l1a aster data
  aster2asp $files_tmp/unzip -o $files_tmp/parse/run

  ### 4) reproject l1a vnir image
  dir_img_reproj=$dir_imgs_reproj/VNIR_$date_decimal  # reproject aster image
  ## re-projected the l1a VNIR bands (15 m, bands of green, red, nir)  
  mapproject -t rpc --t_srs "+proj=longlat +datum=WGS84" WGS84 $files_tmp/parse/run-Band3N.tif $files_tmp/parse/run-Band3N.xml $dir_img_reproj/VNIR-Band3N_proj.tif
  mapproject -t rpc --t_srs "+proj=longlat +datum=WGS84" WGS84 $files_tmp/unzip/*VNIR_Band1*.tif $files_tmp/parse/run-Band3N.xml $dir_img_reproj/VNIR-Band1_proj.tif
  mapproject -t rpc --t_srs "+proj=longlat +datum=WGS84" WGS84 $files_tmp/unzip/*VNIR_Band2*.tif $files_tmp/parse/run-Band3N.xml $dir_img_reproj/VNIR-Band2_proj.tif

  ## 5) generate cloud point data
  ## -r aster is just OK in the source code version (not install by conda).
  ## note: try --stereo-algorithm asp_mgm; --corr-kernel 15 15; 
  ##           --subpixel-kernel 25 25 (default: 21 21 and 35 35)
  ##       try set parameters in stereo.default
  parallel_stereo -t aster -s $settings $files_tmp/parse/run-Band3N.tif \
                  $files_tmp/parse/run-Band3B.tif $files_tmp/parse/run-Band3N.xml \
                  $files_tmp/parse/run-Band3B.xml $files_tmp/stereo/run

  # 6) covert cloud point file to dem image
  point2dem -r earth --tr ${DEM_PS} $files_tmp/stereo/run-PC.tif -o $dir_dem/$date_decimal/run

  rm -rf $files_tmp      ## remove tmp file
  N=$(expr $N + 1)       ## next aster .zip file

done

rm $dir_aster/list_of_zipfile.txt

