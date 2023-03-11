#! /bin/bash 
## author: xin luo;
## create: 2022.05.15;
## des: 1) readout the download icesat1 glas14 data by tile, and
##      2) subset and write out.

cd /home/xin/Developer-luo/Glacier-in-SETP

bottom=27; up=32; left=91; right=99;
year=2018

### -- 1. readout icesat GLAH14/ATL06 data (selected variables).
### 1.1. if the data type is GLAH14
if [[ "2006 2007 2008 2009" == *"$year"* ]]; then      
  dir_data=data/icesat-1/GLAH14-$year/data-raw
  paths_file=$(ls $dir_data/*0001.H5)
  dir_out=data/icesat-1/GLAH14-$year/data-readout
  if [ -z "$paths_file" ]; then
    echo "!!!There is not icesat data to be read."
    continue
  fi
  python utils/read_glah14.py $paths_file -o $dir_out -n 4 

### 1.2. if the data type is ATL06
else                                                   
  dir_data=data/icesat-2/ATL06-$year/data-raw     
  paths_file=$(ls $dir_data/*01.h5)
  dir_out=data/icesat-2/ATL06-$year/data-readout
  if [ -z "$paths_file" ]; then
    echo "!!!There is not icesat data to be read."
    continue
  fi
  python utils/read_atl06.py $paths_file -o $dir_out -n 4
fi

## -- 2. subset to the tile region
python utils/subset_file.py $dir_out/*_readout.h5 -r $left $right $bottom $up      

## -- 3. delete medium files
rm $dir_out/*_readout.h5