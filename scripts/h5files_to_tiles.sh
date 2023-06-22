#! /bin/bash 
## author: xin luo;
## create: 2023.03.10;
## des: batch processing to generate the tile-based .h5 files from the read-out .h5 files. 
##   1) search the .h5 files that are fall in the given tile.
##   2) merge the searched .h5 files.
##   3) subset the merge data to the given tile.
## usage: ./scripts/h5files_to_tiles.sh -d data/icesat-1/GLAH14-2006

cd /home/xin/Developer-luo/Glacier-in-SETP

# dir_h5files=data/icesat-1/GLAH14-2006   ### default data directory
# dir_h5files=data/icesat-2/ATL06-2022   ## optional directory
dir_h5files=data/cryosat-2/eolis-point-2019    ## optional directory

# Get the options
while getopts "d:" arg; do
   case $arg in
      d) # enter a directory
         dir_h5files=$OPTARG;;
      ?) # Invalid argment
         echo "Error: Invalid argment"
         exit;;
   esac
done

lefts=(91 92 93 94 95 91 92 93 94 95 96 97 91 92 93 94 95 96 97 98 94 95 96 97 98 96 97 98)
bottoms=(31 31 31 31 31 30 30 30 30 30 30 30 29 29 29 29 29 29 29 29 28 28 28 28 28 27 27 27)
# year=(2006 2007 2008 2009 2018 2019 2020 2021 2022)
# lefts=(96); bottoms=(27); 

for (( i=0; i<${#lefts[@]}; i++))
  do
  left=${lefts[i]}; bottom=${bottoms[i]}; right=$(expr $left + 1); up=$(expr $bottom + 1)
  ###  -- 1. search the icesat files that falls in the tile.
  h5files_tile=$(python utils/h5files_in_extent.py -h5files $dir_h5files/readout/*.h5 -e $left $right $bottom $up)
  if [ -z "$h5files_tile" ]; then echo "Files in the tile is empty!" && continue
  else echo -e "Files in the tile are:\n $h5files_tile"
  fi

  ###  -- 2. Merge all data files
  path_merge=$dir_h5files/tile_readout_merge.h5
  if [ -f $path_merge ]; then rm $path_merge; fi
  python utils/merge_files.py $h5files_tile -o $path_merge

  ### -- 3. data subsetting with given region
  path_tile_save=$dir_h5files/tiles/tile_${bottom}_$left.h5
  if [ ! -d $dir_h5files/data-tiles ]; then mkdir $dir_h5files/tiles
  fi
  python utils/subset_file.py $path_merge -r $left $right $bottom $up -o $path_tile_save

  ## -- 4. delete medium files
  rm $path_merge

  done