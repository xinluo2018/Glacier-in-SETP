#! /bin/bash 
## author: xin luo;
## create: 2022.05.15;
## des: 1) readout the download icesat1 glas14 data by tile, and
##      2) subset and write out.

cd /Users/luo/Library/CloudStorage/OneDrive-Personal/GitHub/Glacier-in-RGI1305

### -- 1. readout icesat1 glah14 data (selected variables).
date=2009
lat_0=27; lon_0=91
lat_1=$[ $lat_0+1 ]; lon_1=$[ $lon_0+1 ]
tile=tile-${lat_0}-${lon_0}
data_name=GLAH14
dir_downdata=./data/icesat/${data_name}-download/${date}/$tile
dir_readout=./data/icesat/${data_name}-readout/${date}/$tile
if [ ! -d $dir_readout ]; then mkdir $dir_readout; fi

python utils/read_glah14.py $dir_downdata/$data_name*.H5 -o $dir_readout -n 4 

##  -- 2. Merge all data files
path_in=$dir_readout/$data_name*_readout.H5
path_out=$dir_readout/${data_name}_${date}.H5 
if [ -f $path_out ]; then rm $path_out; fi
python utils/merge_files.py $path_in -o $path_out

# ### -- 3. data subset with given region
python utils/subset_icesat.py $dir_readout/${data_name}_${date}.H5 -r $lon_0 $lon_1 $lat_0 $lat_1

## -- 4. delete medium files
rm $dir_readout/*_readout.H5 $dir_readout/${data_name}_${date}.H5

