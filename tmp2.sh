

lefts=(91 92 93 94 95 91 92 93 94 95 96 97 91 92 93 94 95 96 97 98 94 95 96 97 98 96 97 98)
bottoms=(31 31 31 31 31 30 30 30 30 30 30 30 29 29 29 29 29 29 29 29 28 28 28 28 28 27 27 27)


# input_dem=data/dem-data/srtm-c/tiles/tile_27_96.tif
# output_dem_slope=data/dem-data/srtm-c/tiles-slope/tile_27_96.tif
# gdaldem slope $input_dem $output_dem_slope -s 111120 -compute_edges

# ## reprojection
for (( i=0; i<${#lefts[@]}; i++)) 
  do
  left=${lefts[i]}; bottom=${bottoms[i]}
  input_dem=data/dem-data/srtm-c/tiles/tile_${bottom}_${left}.tif
  output_dem_slope=data/dem-data/srtm-c/tiles-slope/tile_${bottom}_${left}.tif
  gdaldem slope $input_dem $output_dem_slope -s 111120 -compute_edges
  done






