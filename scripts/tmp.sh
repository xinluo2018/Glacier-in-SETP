
### batch post-processing for the aster dem.


cd /home/xin/Developer-luo/Glacier-in-SETP

# years=(2006 2007 2008 2009)
years=(2018 2019 2020)

for (( i=0; i<${#years[@]}; i++ )) 
  do
  year=${years[i]}
  echo $year
  # ./scripts/aster_dem_post.sh -y $year    ## dem outlier filtering
  python ./scripts/dem_coregis.py -year $year   ## dem co-registration
  ./scripts/dems2tiles.sh -y $year            ## convert dem images to tiles.
  done 
