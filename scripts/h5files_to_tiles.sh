#! /bin/bash 
## author: xin luo;
## create: 2023.03.10;
## des: batch processing to generate the tile-based icesat data from the read-out icesat .h5 data. 
##   1) search the icesat files which are fall in the range of given tile.
##   2) merge the searched icesat .h5 icesat data.
##   3) subset the merge data to the given tile.

cd /home/xin/Developer-luo/Glacier-in-SETP

lefts=(91 92 93 94 95 91 92 93 94 95 96 97 91 92 93 94 95 96 97 98 94 95 96 97 98 96 97 98)
bottoms=(31 31 31 31 31 30 30 30 30 30 30 30 29 29 29 29 29 29 29 29 28 28 28 28 28 27 27 27)
# year=(2006 2007 2008 2009 2018 2019 2020 2021 2022)
# lefts=(98); bottoms=(29); 
year=2006

if [[ "2006 2007 2008 2009" == *"$year"* ]]; then          ### if the data type is GLAH14
  dir_data=data/icesat-1/GLAH14-$year
else                                                   
  dir_data=data/icesat-2/ATL06-$year
fi

for (( i=0; i<${#lefts[@]}; i++))
  do
  left=${lefts[i]}; bottom=${bottoms[i]}; right=$(expr $left + 1); up=$(expr $bottom + 1)
  ###  -- 1. search the icesat files that falls in the tile.
  h5files_tile=$(python utils/h5files_in_extent.py -h5files $dir_data/data-readout/*.h5 -e $left $right $bottom $up)
  echo $h5files_tile

  ###  -- 2. Merge all data files
  path_merge=$dir_data/tile_readout_merge.h5
  if [ -f $path_merge ]; then rm $path_merge; fi
  python utils/merge_files.py $h5files_tile -o $path_merge

  ### -- 3. data subsetting with given region
  path_tile_save=$dir_data/data-tiles/tile_${bottom}_$left.h5
  if [ ! -d $dir_data/data-tiles ]; then mkdir $dir_data/data-tiles
  fi
  python utils/subset_file.py $path_merge -r $left $right $bottom $up -o $path_tile_save

  ## -- 4. delete medium files
  rm $path_merge

  done