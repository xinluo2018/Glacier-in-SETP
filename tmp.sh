
dir_out=data/aster_data/demo
path_srtm_utm=data/aster_data/demo/srtm_dem_utm.tif
parallel_stereo -t astermaprpc --skip-rough-homography --subpixel-mode 1 \
                      $dir_out/VNIR-Band3N_utm.tif $dir_out/VNIR-Band3B_utm.tif \
                      $dir_out/run-Band3N.xml $dir_out/run-Band3B.xml \
                      $dir_out/pc_utm_out/run $path_srtm_utm