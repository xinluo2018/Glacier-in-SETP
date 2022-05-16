#! /bin/bash 
## author: xin luo;
## create: 2022.05.13;
## des: download srtm dem data.
## note: !!!the user should login OpenTopography firstly.


WEST=80.118; EAST=81.941; SOUTH=34.907; NORTH=35.852    ## extent of the target region.
path_dem_wgs84=data/dem-data/srtm-c/SRTMGL1_E_wkunlun_wgs84_tmp.tif
path_dem_utm=data/dem-data/srtm-c/SRTMGL1_E_wkunlun_utm_tmp.tif
cd /Users/luo/Library/CloudStorage/OneDrive-Personal/GitHub/Glacier-in-RGI1305

## ---- 1. download the dem data
python utils/get_dem.py SRTMGL1_E $WEST $EAST $SOUTH $NORTH --out $path_dem_wgs84

## ---- 2. utm projection
TSRS_WGS84='+proj=longlat +datum=WGS84' # WGS84 projection 
## calculate utm zone, for the utm projection.
LON=$(echo "scale=3; $WEST / 2 + $EAST / 2" | bc)
UTM_ZONE=$(echo "scale=4; $LON / 6 + 31" | bc)
UTM_ZONE=$(echo $UTM_ZONE | awk '{print int($1)}')
echo 'UTM_ZONE:' $UTM_ZONE
TSRS_UTM='+proj=utm +zone='$UTM_ZONE' +ellps=WGS84 +datum=WGS84 +units=m +no_defs' # UTM projection 
gdalwarp -overwrite -s_srs "$TSRS_WGS84" -t_srs "$TSRS_UTM" -tr 30 30 -r cubic -co COMPRESS=LZW -co TILED=YES $path_dem_wgs84 $path_dem_utm

