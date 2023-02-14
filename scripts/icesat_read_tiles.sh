#! /bin/bash 
## author: xin luo;
## create: 2022.05.15;
## des: 1) readout the download icesat1 glas14 data by tile, and
##      2) subset and write out.

cd /home/xin/Developer-luo/Glacier-in-SETP

# lefts=(91 92 93 94 95 91 92 93 94 95 96 97 91 92 93 94 95 96 97 98 94 95 96 97 98 96 97 98)
# bottoms=(31 31 31 31 31 30 30 30 30 30 30 30 29 29 29 29 29 29 29 29 28 28 28 28 28 27 27 27)
lefts=(98); 
bottoms=(29); 
year=2009

for (( i=0; i<${#lefts[@]}; i++)) 
  do
  ### -- 1. readout icesat GLAH14/ATL06 data (selected variables).
  left=${lefts[i]}; bottom=${bottoms[i]}
  if [[ "2006 2007 2008 2009" == *"$year"* ]]; then         ### if the data type is GLAH14
    dir_data=data/icesat/GLAH14-$year/tile-$bottom-$left
    paths_file=$(ls $dir_data/*0001.H5)
    if [ -z "$paths_file" ]; then
      echo "!!!There is not icesat data to be read."
      continue
    fi
    python utils/read_glah14.py $paths_file -o $dir_data -n 4 
  else                                                      ### if the data type is ATL06
    dir_data=data/icesat/ATL06-$year/tile-$bottom-$left     
    paths_file=$(ls $dir_data/*01.h5)
    if [ -z "$paths_file" ]; then
      echo "!!!There is not icesat data to be read."
      continue
    fi
    python utils/read_atl06.py $paths_file -o $dir_data -n 4
  fi

  ##  -- 2. Merge all data files
  path_merge=$dir_data/data_readout_merge.h5
  if [ -f $path_merge ]; then rm $path_merge; fi
  python utils/merge_files.py $dir_data/*_readout.h5 -o $path_merge

  ### -- 3. data subset with given region
  right=$[ $left+1 ]; up=$[ $bottom+1 ];
  python utils/subset_file.py $path_merge -r $left $right $bottom $up

  ## -- 4. delete medium files
  rm $dir_data/*_readout.h5 $dir_data/*merge.h5 

  done