#! /bin/bash
cd /home/xin/Developer-luo/Glacier-in-SETP

years=(2012 2013 2014 2015 2016 2017 )
for (( i=0; i<${#years[@]}; i++)) 
  do
  year=${years[i]}
  ./scripts/aster_dem_post.sh -y $year
  python ./scripts/dem_coregis.py -year $year
  ./scripts/dems2tiles.sh -y $year
done
