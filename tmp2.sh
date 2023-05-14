cd /home/xin/Desktop/developer-luo/Glacier-in-SETP

lefts=(91 92 93 94 95 91 92 93 94 95 96 97 91 92 93 94 95 96 97 98 94 95 96 97 98 96 97 98)
bottoms=(31 31 31 31 31 30 30 30 30 30 30 30 29 29 29 29 29 29 29 29 28 28 28 28 28 27 27 27)
proj_albers_china="+proj=aea +ellps=krass +lon_0=105 +lat_1=25 +lat_2=47"   ## Equal area projection for China


# ## reprojection
for (( i=0; i<${#lefts[@]}; i++)) 
  do
  left=${lefts[i]}; bottom=${bottoms[i]}
  path_out=data/aster-stereo/tiles-dif-map/tile_${bottom}_${left}.tif
  path_out_reproj=data/aster-stereo/tiles-dif-map/tile_${bottom}_${left}_albers.tif
  gdalwarp -overwrite -s_srs EPSG:4326 -t_srs "$proj_albers_china" -tr 30 30 -r bilinear -co COMPRESS=LZW -co TILED=YES $path_out $path_out_reproj 
  done




