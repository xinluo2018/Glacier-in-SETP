#! /bin/bash 

path_root=/Users/luo/Library/CloudStorage/OneDrive-Personal/GitHub/Glacier-in-RGI1305

path_shp=${path_root}/data/boundary/wkl_kara_merge_shp/wkl_kara_merge.shp
path_input=${path_root}/data/dem-data/srtm-c/SRTMGL3_wgs84_900m.tif
path_out=${path_root}/data/dem-data/srtm-c/SRTMGL3_wgs84_900m_subs.tif

### ------ subset by .shp file------
gdalwarp -co COMPRESS=LZW -cutline $path_shp -crop_to_cutline $path_input $path_out

