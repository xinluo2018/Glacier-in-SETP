#! /bin/bash 
## author: xin luo;
## create: 2022.05.15;
## des: 1) readout the download icesat1 glas14 data by tile, and
##      2) subset and write out.

cd /home/xin/Developer-luo/Glacier-in-SETP

bottom=27; up=32; left=91; right=99;
year=2021

### -- 1. readout icesat GLAH14/ATL06 data (selected variables).
### setting
dir_data_raw=data/cryosat-2/tempopoints-$year
func_read=utils/read_cryotempo.py
paths_file_raw=$(ls $dir_data_raw/data-raw/*)


echo $paths_file_raw
dir_readout=data/cryotempo-points/$year/data-readout
if [ ! -d $dir_readout ]; then mkdir $dir_readout 
fi

### 1.readout the icesat data
python $func_read $paths_file_raw -o $dir_readout -n 4 

### -- 2. subset to the specific region
python utils/subset_file.py $dir_readout/*_readout.h5 -r $left $right $bottom $up      

### -- 3. delete medium files
rm $dir_readout/*_readout.h5

