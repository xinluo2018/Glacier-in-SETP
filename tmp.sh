#! /bin/bash
cd /home/xin/Developer-luo/Glacier-in-SETP

years=(2000 2001 2002 2003 2004 2005 2005 2006 2007 2008 2009 2010 2011 2012 2013 2014 2015 2016 2017 2018 2019 2020 2021)

for year in ${years[@]}
  do
  # ./scripts/aster_dem_batch.sh -y $year
  # ./scripts/aster_dem_post.sh -y $year
  # python ./scripts/dem_coregis.py -year $year
  ./scripts/dems2tiles.sh -y $year
done


