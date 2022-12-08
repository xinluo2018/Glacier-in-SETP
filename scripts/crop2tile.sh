#! /bin/bash 
## author: xin luo;
## create: 2022.12.7;
## des: Crop one large image to multiple-tile image. 
##      This script can be used for cropping of water_jcr image, globeland30 image et al.

cd /home/xin/Desktop/developer-luo/Glacier-in-SETP

lefts=(91 92 93 94 95 91 92 93 94 95 96 97 91 92 93 94 95 96 97 98 94 95 96 97 98 96 97 98)
bottoms=(31 31 31 31 31 30 30 30 30 30 30 30 29 29 29 29 29 29 29 29 28 28 28 28 28 27 27 27)
proj_albers_china="+proj=aea +ellps=krass +lon_0=105 +lat_1=25 +lat_2=47"   ## Equal area projection for China
# lefts=(97); bottoms=(30)
for (( i=0; i<${#lefts[@]}; i++)) 
  do
  left=${lefts[i]}; bottom=${bottoms[i]}
  ### -- 1. crop the water_jcr image to tiles
  # path_in=data/water/water-jrc/mask_mosaic_subs.tif  ## the provide water mask image should full cover the tiles extent
  # path_out=data/water/water-jrc/wat-tiles/tile-$bottom-$left.tif
  # path_out_reproj=data/water/water-jrc/wat-tiles/tile-$bottom-${left}_albers.tif
  ### -- 2. crop the globeland30 image to tiles
  # path_in=data/globeland30/2020/globeland30_mosaic_subs.tif  ## the provide water mask image should full cover the tiles extent
  # path_out=data/globeland30/2020/tiles/tile-$bottom-$left.tif
  # path_out_reproj=data/globeland30/2020/tiles/tile-$bottom-${left}_albers.tif
  # ### -- 3. crop the srtm dem to tiles
  # path_in=data/dem-data/srtm-c/SRTMGL1_E.tif    ## the provide water mask image should full cover the tiles extent
  # path_out=data/dem-data/srtm-c/tiles/tile-$bottom-$left.tif
  # path_out_reproj=data/dem-data/srtm-c/tiles/tile-$bottom-${left}_albers.tif
  ## -- 4. crop the rgi60 glacier to tiles
  path_in=data/rgi60/rgi60_setp_mask.tif    ## the provide water mask image should full cover the tiles extent
  path_out=data/rgi60/tiles/tile-$bottom-$left.tif
  path_out_reproj=data/rgi60/tiles/tile-$bottom-${left}_albers.tif

  echo 'Tile bottom-left corner:' $bottom $left;
  echo 'export file:' $path_out
  tile_res=1  # tile resolution, default is 1.
  right=$(expr $left + $tile_res)
  up=$(expr $bottom + $tile_res)
  extent="$left $up $right $bottom"  ## e.g., extent='72 38 84 34'
  ## cropping
  gdal_translate -projwin $extent -co COMPRESS=LZW $path_in $path_out 
  ## reprojection
  gdalwarp -overwrite -s_srs EPSG:4326 -t_srs "$proj_albers_china" -tr 30 30 -r bilinear -co COMPRESS=LZW -co TILED=YES $path_out $path_out_reproj 

  done



