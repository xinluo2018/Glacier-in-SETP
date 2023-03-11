#! /bin/bash 
## author: xin luo;
## create: 2023.1.18;
## des: Crop one large file (dictionary-like .h5 file) to multiple-tile files. 
##      This script can be used for cropping of dictionary-like .h5 file, including cryosat eolis points data. 


cd /home/xin/Developer-luo/Glacier-in-SETP

year=2021

### data read in and write out (.nc -> .h5 file).
dir_data=data/cryotempo-points/$year
python utils/read_cryotempo_points.py $dir_data/raw-files/*.nc -o $dir_data/raw-files -n 4
### merge multiple .h5 files into one.
python utils/merge_files.py $dir_data/raw-files/*_readout.h5 -o $dir_data/cryotempo_points_merge.h5
rm $dir_data/raw-files/*_readout.h5     ## remove the media files.

### Subset file into tiles.
lefts=(91 92 93 94 95 91 92 93 94 95 96 97 91 92 93 94 95 96 97 98 94 95 96 97 98 96 97 98)
bottoms=(31 31 31 31 31 30 30 30 30 30 30 30 29 29 29 29 29 29 29 29 28 28 28 28 28 27 27 27)
path_in=$dir_data/cryotempo_points_merge.h5
for (( i=0; i<${#lefts[@]}; i++)) 
  do
  left=${lefts[i]}; bottom=${bottoms[i]}
  # left=93; bottom=30
  right=$(expr $left + 1); up=$(expr $bottom + 1)  
  extent="$left $right $bottom $up"   ## e.g., extent='72 84 34 38'
  path_out=$dir_data/tiles/tile_${bottom}_${left}.h5
  echo 'Tile bottom-left corner:' $bottom $left;
  echo 'export file:' $path_out
  python utils/subset_file.py $path_in -r $extent -c lon lat -o $path_out

  done




