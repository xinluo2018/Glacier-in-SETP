#! /bin/bash 
## author: xin luo;
## create: 2022.05.15;
## des: 1) readout the download icesat2 data by tile, and
##      2) subset and write out.

cd /Users/luo/Library/CloudStorage/OneDrive-Personal/GitHub/Glacier-in-RGI1305

date=2020
lat_0=27; lon_0=91
tile=tile-${lat_0}-${lon_0}
data_name=ATL06
dir_downdata=./data/icesat/${data_name}-download/$date/${tile}-month
dir_readout=./data/icesat/${data_name}-readout/$date/${tile}-month

# path_subs_mask=data/rgi60-setp/rgi60_1305_selected_mask.tif   ## mask file
if [ ! -d $dir_readout ]; then mkdir $dir_readout; fi

### -- 1. readout icesat2 atl03 and atl06 data (selected variables).
if [ "$data_name" == "ATL03" ]; 
then
  python utils/read_atl03.py $dir_downdata/*${data_name}*.h5 -o $dir_readout -n 4
elif [ "$data_name" == "ATL06" ]; 
then
  python utils/read_atl06.py $dir_downdata/*${data_name}*.h5 -o $dir_readout -n 4
fi

##  -- 2. Merge all data files
path_in=$dir_readout/*${data_name}*.h5
path_out=$dir_readout/${data_name}_${date}.h5 
if [ -f $path_out ]; then rm $path_out; fi
python utils/merge_files.py $path_in -o $path_out

# ### -- 3. data subset with rgi60 glacier data 
# python utils/subset_file.py $dir_readout/${data_name}_${date}.h5 -m $path_subs_mask

## -- 4. delete medium files
rm $dir_readout/*_readout.h5

