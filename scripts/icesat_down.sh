#! /bin/bash 
# author: xin luo
# create: 2023.3.10
# des: icesat data downloading, for both icesat-1 and icesat-2 data.
### the user name and password will be required before the data downloading. (my username: 411795604; login website: https://urs.earthdata.nasa.gov)

cd /home/xin/Developer-luo/Glacier-in-SETP

bottom=27; up=32; left=91; right=99;
year=2005
date_start=$year-01-01; date_end=$year-12-31
if [[ "2003 2004 2005 2006 2007 2008 2009" == *"$year"* ]]; then          ### if the data type is GLAH14
  echo "Download the icesat1 GLAH14 data..."
  dir_out=data/icesat-1/GLAH14-$year/raw
  python utils/down_icesat1.py -e $left $bottom $right $up -t $date_start $date_end -o $dir_out
else                                                       ### if the data type is ATL06
  echo "Download the icesat2 ATL06 data..."
  dir_out=data/icesat-2/ATL06-$year/raw
  python utils/down_icesat2.py -e $left $bottom $right $up -t $date_start $date_end -o $dir_out
fi





