#! /bin/bash
## author: xin luo; xxxx
## create: 2023.06.19;
## des: Batch processing from altimeter-derived and dems-derived elevation data to statistic data.
##      this scripts is used for icesat-1, icesat-2, cryosat-2 and aster stereo imagey-derived elevation data.
## usage: ./scripts/batch_process_ele2stat.sh




cd /home/xin/Developer-luo/Glacier-in-SETP


# # ## icesat-1
# years_isat1=(2003 2004 2005 2005 2006 2007 2008 2009)
# for year_isat1 in ${years_isat1[@]}
#   do
#   ./scripts/icesat_readout.sh -y $year_isat1
#   ./scripts/h5files_to_tiles.sh -d data/icesat-1/GLAH14-$year_isat1
# done
# python scripts/dif_altimeter_srtm.py -dtype icesat-1
# python ./scripts/stat_dif_altimeter.py -dtype icesat-1


# # ### icesat-2
# years_isat2=(2018 2019 2020 2021 2022)
# for year_isat2 in ${years_isat2[@]}
#   do
#   ./scripts/icesat_readout.sh -y $year_isat2
#   ./scripts/h5files_to_tiles.sh -d data/icesat-2/ATL06-$year_isat2
# done
# python scripts/dif_altimeter_srtm.py -dtype icesat-2
# python ./scripts/stat_dif_altimeter.py -dtype icesat-2


# # ### cryosat-2
# years_cryo2=(2010 2011 2012 2013 2014 2015 2016 2017 2018 2019 2020)
# for year_cryo2 in ${years_cryo2[@]}
#   do
#   ./scripts/cryo2_readout.sh -y $year_cryo2
#   ./scripts/h5files_to_tiles.sh -d data/cryosat-2/eolis-point-$year_cryo2
# done
# python scripts/dif_altimeter_srtm.py -dtype cryosat-2
# python ./scripts/stat_dif_altimeter.py -dtype cryosat-2


# ### aster dems
# years_dems=(2000 2001 2002 2003 2004 2005 2006 2007 2008 2009 2010 2011 2012 2013 2014 2015 2016 2017 2018 2019 2020 2021 2022)
years_dems=(2022)
for year_dems in ${years_dems[@]}
  do
  ./scripts/aster_dem_post.sh -y $year_dems
  python ./scripts/dem_coregis.py -year $year_dems
  ./scripts/dems2tiles.sh -y $year_dems
done
python scripts/dif_dems_srtm.py
python scripts/stat_dif_dems.py


