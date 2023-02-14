#! /bin/bash 

cd /home/xin/Developer-luo/Glacier-in-SETP

# bottoms=(31 31 31 31 31 30 30 30 30 30 30 30 29 29 29 29 29 29 29 29 28 28 28 28 28 27 27 27)
# lefts=(91 92 93 94 95 91 92 93 94 95 96 97 91 92 93 94 95 96 97 98 94 95 96 97 98 96 97 98)
bottoms=(30); 
lefts=(96); 
year=2006
date_start=$year-01-01; date_end=$year-12-31
for (( i=0; i<${#lefts[@]}; i++))
  do
  left=${lefts[i]}; bottom=${bottoms[i]}
  right=$(expr $left + 1); up=$(expr $bottom + 1)
  if [[ "2006 2007 2008 2009" == *"$year"* ]]; then          ### if the data type is GLAH14
    echo "Download the icesat1 GLAH14 data..."
    dir_out=data/icesat/GLAH14-$year/tile-$bottom-$left
    python utils/down_icesat1.py -e $left $bottom $right $up -t $date_start $date_end -o $dir_out
  else                                                       ### if the data type is GLAH14
    echo "Download the icesat2 ATL06 data..."
    dir_out=data/icesat/ATL06-$year/tile-$bottom-$left
    python utils/down_icesat2.py -e $left $bottom $right $up -t $date_start $date_end -o $dir_out
  fi
  done

