#! /bin/bash 

cd /Users/luo/Library/CloudStorage/OneDrive-Personal/GitHub/Glacier-in-RGI1305
path_1=data/water/water-jrc/occurrence_90E_30Nv1_3_2020.tif
path_2=data/water/water-jrc/occurrence_90E_40Nv1_3_2020.tif
path_out=data/water/water-jrc/occurrence_mosaic.tif
path_out_subs=data/water/water-jrc/occurrence_mosaic_subs.tif
path_subs_300m=data/water/water-jrc/occurrence_mosaic_subs_300m.tif
# gdal_merge.py -init 0 -n -999 -co COMPRESS=LZW -o $path_out $path_1 $path_2

# # extent: str(ulx) str(uly) str(lrx) str(lry), e.g., extent='72 38 84 34'
# gdal_translate -projwin 91 32 99 27 -co COMPRESS=LZW $path_out $path_out_subs

### ------ downsampling/resize ------ 
gdal_translate -outsize 10% 10% -r average -co COMPRESS=LZW $path_out_subs $path_subs_300m



