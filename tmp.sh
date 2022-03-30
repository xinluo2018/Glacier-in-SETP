#! /bin/bash
path_1=data/aster_data/wkunlun-dems/dems_mosaic_2019.tif
path_2=data/aster_data/wkunlun-dems/dems_mosaic_2020.tif
path_3=data/aster_data/wkunlun-dems/dems_mosaic_2020.tif

python utils/lay_stack.py $path_1 $path_2 $path_3 tmp.tif -u False -r 30

