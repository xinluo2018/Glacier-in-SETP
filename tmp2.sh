
# years=(2007 2008 2009 2010 2011 2012 2013 2014 2015 2016 2017 2018 2019 2020 2021)

# for year in ${years[@]}
#   do
#   python ./scripts/dem_coregis.py -year $year
#   echo $year

#   done

python ./scripts/dems_dif_map.py
./scripts/reproj2albers.sh