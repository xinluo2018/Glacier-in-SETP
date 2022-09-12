#! /bin/bash 
## author: xin luo;
## create: 2022.05.14;
## des: mosaic, subset and projection for the download tandem files.
##      the tandem data is 1x1 degree tiled data

cd /Users/luo/Library/CloudStorage/OneDrive-Personal/GitHub/Glacier-in-RGI1305

DIR_DATA=data/dem-data/tandem-x
NUMB_DATA=$(ls -d $DIR_DATA/TDM1_DEM*.zip | wc | awk '{print $1}')
echo "Numb of DEMs to process: " $NUMB_DATA

### ----- 1) Unzip the dem file.
ls -d ${DIR_DATA}/TDM1_DEM*.zip > $DIR_DATA/list_of_zipfile.txt  # write file_name to .txt file
N=1
PATHS_UNZIP=''
while [ $N -le $NUMB_DATA ]
do
  PATH_ZIP=$(head -$N ${DIR_DATA}/list_of_zipfile.txt | tail -1)
  unzip $PATH_ZIP -d $DIR_DATA
  N=$(expr $N + 1)       ## next aster .zip file
done
rm $DIR_DATA/list_of_zipfile.txt

### ----- 2) mosaic
PATH_DEMs=$(ls $DIR_DATA/TDM1_DEM*/DEM/*_DEM.tif)
PATH_MOSAIC=$DIR_DATA/dems_mosaic.tif  ## 
gdal_merge.py -init 0 -n -999 -co COMPRESS=LZW -o $PATH_MOSAIC $PATH_DEMs

# ## ---- 3) subset with study area vector file
WEST=80.118; EAST=81.941; SOUTH=34.907; NORTH=35.852
EXTENT="$WEST $NORTH $EAST $SOUTH"
PATH_SUBS=$DIR_DATA/dems_mosaic_wkunlun.tif  ## 
gdal_translate -co COMPRESS=LZW -projwin $EXTENT $PATH_MOSAIC $PATH_SUBS  ## by extent 
## gdalwarp -co COMPRESS=LZW -cutline $PATH_SHP $PATH_MOSAIC $PATH_SUBS  ## by .shp file

## ------ 4) reprojection
## the download tandem is wgs84 coordinates 
TSRS_WGS84='+proj=longlat +datum=WGS84' # WGS84 projection 
LON=$(echo "scale=3; $WEST / 2 + $EAST / 2" | bc)
UTM_ZONE=$(echo "scale=4; $LON / 6 + 31" | bc)
UTM_ZONE=$(echo $UTM_ZONE | awk '{print int($1)}')
echo $UTM_ZONE
TSRS_UTM='+proj=utm +zone='$UTM_ZONE' +ellps=WGS84 +datum=WGS84 +units=m +no_defs' # UTM projection 
gdalwarp -s_srs "$TSRS_WGS84" -t_srs "$TSRS_UTM" -r bilinear -co COMPRESS=LZW -co TILED=YES $PATH_SUBS $DIR_DATA/dems_mosaic_wkunlun_utm.tif


