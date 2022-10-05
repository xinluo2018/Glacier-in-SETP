#! /bin/bash 
## author: xin luo;
## create: 2022.05.13;
## des: download and preprocessing (reproject, resample) the SRTM V3.0 dem data. the data is void-filled data
## note: !!!the user should login OpenTopography firstly.

WEST=91; EAST=99; SOUTH=27; NORTH=32     ## extent of the target region.
path_dem=data/dem-data/srtm-c/SRTMGL3.tif
path_dem_utm=data/dem-data/srtm-c/SRTMGL1_E_wkunlun_utm_tmp.tif
cd /Users/luo/Library/CloudStorage/OneDrive-Personal/GitHub/Glacier-in-RGI1305

# ## ---- 1. download the dem data
# python utils/get_dem.py SRTMGL3 $WEST $EAST $SOUTH $NORTH --out $path_dem

## ---- 2. downsample the dem data
path_dem_down=data/dem-data/srtm-c/SRTMGL3_900m.tif
gdal_translate -outsize 10% 10% -r average -co COMPRESS=LZW $path_dem $path_dem_down

# ## ---- 2. utm projection
# TSRS_WGS84='+proj=longlat +datum=WGS84' # WGS84 projection 
# ## calculate utm zone, for the utm projection.
# LON=$(echo "scale=3; $WEST / 2 + $EAST / 2" | bc)
# UTM_ZONE=$(echo "scale=4; $LON / 6 + 31" | bc)
# UTM_ZONE=$(echo $UTM_ZONE | awk '{print int($1)}')
# echo 'UTM_ZONE:' $UTM_ZONE
# TSRS_UTM='+proj=utm +zone='$UTM_ZONE' +ellps=WGS84 +datum=WGS84 +units=m +no_defs' # UTM projection 
# gdalwarp -overwrite -s_srs "$TSRS_WGS84" -t_srs "$TSRS_UTM" -tr 30 30 -r cubic -co COMPRESS=LZW -co TILED=YES $path_dem $path_dem_utm

