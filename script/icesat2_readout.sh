#! /bin/bash 
## author: xin luo;
## create: 2022.05.15;
## des: read the download icesat2 data and write out.


cd /Users/luo/Library/CloudStorage/OneDrive-Personal/GitHub/Glacier-in-RGI1305

data_name=ATL03
date=202002
dir_downdata=data/icesat2/download-${data_name}/data_${date}
dir_procdata=data/icesat2/processed-${data_name}
path_subs_mask=data/rgi60-wkunlun/rgi60_1305_selected_mask.tif

orbits='A D'
spots='spot1 spot2 spot3 spot4 spot5 spot6'

if [ ! -d $dir_procdata ]; 
then
  mkdir $dir_procdata
fi

### ---- 1. split icesat2 data into different beams and orbits(ascending/descending).
if [ "$data_name" == "ATL03" ]; 
then
  python utils/readout03.py $dir_downdata/*${data_name}*.h5 -o $dir_procdata -n 4
elif [ "$data_name" == "ATL06" ]; 
then
  python utils/readout06.py $dir_downdata/*${data_name}*.h5 -o $dir_procdata -n 4
fi

# ### ---- 2. data merge
# ##  ---- 2.1. merge multitemporal data

for orbit in $orbits
do
  for spot in $spots
  do
    python utils/merge_files.py $dir_procdata/*${data_name}*_${spot}_${orbit}*.h5 -o $dir_procdata/${data_name}_${spot}_${orbit}.h5
  done
done

# ##  ---- 2.2. Merge beames.
for orbit in $orbits
do
  python utils/merge_files.py $dir_procdata/${data_name}_spot?_${orbit}.h5 -o $dir_procdata/${data_name}_${orbit}.h5
done

##  ---- 2.3. Merge all beams and orbits
for orbit in $orbits
do
  python utils/merge_files.py $dir_procdata/*${data_name}*_spot*.h5 -o $dir_procdata/${data_name}_${date}.h5  
done

### ---- 3. data subset
python utils/subset_file.py $dir_procdata/${data_name}_${date}.h5 -m $path_subs_mask

### ---- 4. delete medium files
rm $dir_procdata/*A.h5 $dir_procdata/*D.h5 $dir_procdata/*${date}.h5

