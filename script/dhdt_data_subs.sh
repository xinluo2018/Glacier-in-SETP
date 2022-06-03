#! /bin/bash
## author: xin luo; xxxx
## create: 2022.05.28;
## des: basic processing including data mosaic and data subset for the released dh_dt data.

cd /Users/luo/Library/CloudStorage/OneDrive-Personal/GitHub/Glacier-in-RGI1305

path_study_area=data/study-area/study_area.shp

# ## ---- 1. the Hugonnet2021 data
## data download from: https://www.sedoo.fr/theia-publication-products/?uuid=c428c5b9-df8f-4f86-9b75-e04c778e29b9
# date_start=2000
# date_end=2020
# dir_dhdt=data/dhdt-release/Hugonnet2021/13_14_15_rgi60_${date_start}-01-01_${date_end}-01-01/dhdt
# dir_dhdt_err=data/dhdt-release/Hugonnet2021/13_14_15_rgi60_${date_start}-01-01_${date_end}-01-01/dhdt_err

# gdal_merge.py -n -9999 -a_nodata -9999 -co COMPRESS=LZW -o $dir_dhdt/dhdt_${date_start}_${date_end}.tif $dir_dhdt/*dhdt.tif
# gdal_merge.py -n -9999 -a_nodata -9999 -co COMPRESS=LZW -o $dir_dhdt_err/dhdt_err_${date_start}_${date_end}.tif $dir_dhdt_err/*dhdt_err.tif

# ## ------ subset by .shp file------ 
# gdalwarp -co COMPRESS=LZW -cutline $path_study_area -crop_to_cutline $dir_dhdt/dhdt_${date_start}_${date_end}.tif $dir_dhdt/dhdt_${date_start}_${date_end}_subs.tif
# gdalwarp -co COMPRESS=LZW -cutline $path_study_area -crop_to_cutline $dir_dhdt_err/dhdt_err_${date_start}_${date_end}.tif $dir_dhdt_err/dhdt_err_${date_start}_${date_end}_subs.tif

## ---- 2. the Shean2020 dhdt data
## data download from: https://zenodo.org/record/3872696#.YpIWYBNBwbk
# path_dhdt=data/dhdt-release/Shean2020/shean_hma_glacier_ASTER_WV_2000-2018_dhdt.tif
# path_dhdt_subs=data/dhdt-release/Shean2020/shean_hma_glacier_ASTER_WV_2000-2018_dhdt_subs.tif
# gdalwarp -co COMPRESS=LZW -cutline $path_study_area -crop_to_cutline $path_dhdt $path_dhdt_subs

# # ---- 3. the Guan2021 dhdt data
## data download from: https://zenodo.org/record/4460897#.YpIWsxNBwbk
# path_dhdt=data/dhdt-release/Guan2021/2000_2016_dh_rate.tif
# path_dhdt_subs=data/dhdt-release/Guan2021/2000_2016_dh_rate_subs.tif
# gdalwarp -co COMPRESS=LZW -cutline $path_study_area -crop_to_cutline $path_dhdt $path_dhdt_subs

# ---- 4. the Brun2017 dhdt data
### data download from: https://doi.pangaea.de/10.1594/PANGAEA.876545
# ## --4.1 convert utm projection to wgs84 coordinate system
# paths_dhdt=data/dhdt-release/Brun2017/*/dh_dt_*n??_e???.tif
# paths_dhdt_err=data/dhdt-release/Brun2017/*/dh_dt_*_err.tif
# for path_dhdt in $paths_dhdt; 
# do
#   path_dhdt_err=${path_dhdt%.*}'_err.'${path_dhdt#*.}
#   path_dhdt_wgs84=${path_dhdt%.*}'_wgs84.'${path_dhdt#*.}
#   path_dhdt_err_wgs84=${path_dhdt_err%.*}'_wgs84.'${path_dhdt_err#*.}
#   gdalwarp -overwrite -t_srs EPSG:4326  -r bilinear -co COMPRESS=LZW -co TILED=YES $path_dhdt $path_dhdt_wgs84
#   gdalwarp -overwrite -t_srs EPSG:4326  -r bilinear -co COMPRESS=LZW -co TILED=YES $path_dhdt_err $path_dhdt_err_wgs84
# done

# ## --4.2 data mosaic for the downloaded 1x1 degree tiles data
# paths_dhdt_=data/dhdt-release/Brun2017/*/dh_dt_*n??_e???_wgs84.tif
# paths_dhdt_err_=data/dhdt-release/Brun2017/*/dh_dt_*_err_wgs84.tif
# path_dhdt_mosaic=data/dhdt-release/Brun2017/dh_dt_2000-2016_ASTER_mosaic.tif
# path_dhdt_err_mosaic=data/dhdt-release/Brun2017/dh_dt_err_2000-2016_ASTER_mosaic.tif

# gdal_merge.py -n -9999 -a_nodata -9999 -co COMPRESS=LZW -o $path_dhdt_mosaic $paths_dhdt_
# gdal_merge.py -n -9999 -a_nodata -9999 -co COMPRESS=LZW -o $path_dhdt_err_mosaic $paths_dhdt_err_

# # ## --4.2 data subset and reprojection to utm.
# path_dhdt_subs=data/dhdt-release/Brun2017/dh_dt_2000-2016_ASTER_mosaic_subs.tif
# path_dhdt_err_subs=data/dhdt-release/Brun2017/dh_dt_err_2000-2016_ASTER_mosaic_subs.tif
# gdalwarp -s_srs EPSG:4326 -t_srs EPSG:32644 -r bilinear -co COMPRESS=LZW -cutline $path_study_area -crop_to_cutline $path_dhdt_mosaic $path_dhdt_subs
# gdalwarp -s_srs EPSG:4326 -t_srs EPSG:32644 -r bilinear -co COMPRESS=LZW -cutline $path_study_area -crop_to_cutline $path_dhdt_err_mosaic $path_dhdt_err_subs

