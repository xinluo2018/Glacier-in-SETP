#! /bin/bash 

path_root=/Users/luo/Library/CloudStorage/OneDrive-Personal/GitHub/Glacier-in-RGI1305
dir_data=${path_root}/data/dem-data/srtm-c
# paths_dem=$(ls ${dir_data}/*V??_C/DEM/*.tif)
# echo $paths_dem

# path_out=$dir_data/dem_mosaic.tif
# echo 'Run the images mosaic...'
# gdal_merge.py -init 0 -co COMPRESS=LZW -o $path_out $paths_dem

## downsample
path_in=$dir_data/SRTMGL3_wgs84.tif
path_out=$dir_data/SRTMGL3_wgs84_900m.tif
gdal_translate -outsize 10% 10% -r average -co COMPRESS=LZW $path_in $path_out 


