
### batch post-processing for the altimeter data.


cd /home/xin/Developer-luo/Glacier-in-SETP

# ## icesat-1
# ./scripts/icesat_readout.sh -y 2003
# ./scripts/h5files_to_tiles.sh -d data/icesat-1/GLAH14-2003
# python ./scripts/altimeter_srtm_dif.py -d data/icesat-1/GLAH14-2003
# python ./scripts/stat_dif_altimeter.py -d data/icesat-1/GLAH14-2003/tiles

# ./scripts/icesat_readout.sh -y 2004
# ./scripts/h5files_to_tiles.sh -d data/icesat-1/GLAH14-2004
# python scripts/altimeter_srtm_dif.py -d data/icesat-1/GLAH14-2004
# python ./scripts/stat_dif_altimeter.py -d data/icesat-1/GLAH14-2004/tiles

# ./scripts/icesat_readout.sh -y 2005
# ./scripts/h5files_to_tiles.sh -d data/icesat-1/GLAH14-2005
# python scripts/altimeter_srtm_dif.py -d data/icesat-1/GLAH14-2005
# python ./scripts/stat_dif_altimeter.py -d data/icesat-1/GLAH14-2005/tiles

# ./scripts/icesat_readout.sh -y 2006
# ./scripts/h5files_to_tiles.sh -d data/icesat-1/GLAH14-2006
# python scripts/altimeter_srtm_dif.py -d data/icesat-1/GLAH14-2006
# python ./scripts/stat_dif_altimeter.py -d data/icesat-1/GLAH14-2006/tiles

# ./scripts/icesat_readout.sh -y 2007
# ./scripts/h5files_to_tiles.sh -d data/icesat-1/GLAH14-2007
# python scripts/altimeter_srtm_dif.py -d data/icesat-1/GLAH14-2007
# python ./scripts/stat_dif_altimeter.py -d data/icesat-1/GLAH14-2007/tiles

# ./scripts/icesat_readout.sh -y 2008
# ./scripts/h5files_to_tiles.sh -d data/icesat-1/GLAH14-2008
# python scripts/altimeter_srtm_dif.py -d data/icesat-1/GLAH14-2008
# python ./scripts/stat_dif_altimeter.py -d data/icesat-1/GLAH14-2008/tiles

# ./scripts/icesat_readout.sh -y 2009
# ./scripts/h5files_to_tiles.sh -d data/icesat-1/GLAH14-2009
# python scripts/altimeter_srtm_dif.py -d data/icesat-1/GLAH14-2009
# python ./scripts/stat_dif_altimeter.py -d data/icesat-1/GLAH14-2009/tiles


# ### icesat-2
# ./scripts/icesat_readout.sh -y 2018
# ./scripts/h5files_to_tiles.sh -d data/icesat-2/ATL06-2018
# python scripts/altimeter_srtm_dif.py -d data/icesat-2/ATL06-2018
python ./scripts/stat_dif_altimeter.py -d data/icesat-2/ATL06-2018/tiles

# ./scripts/icesat_readout.sh -y 2019
# ./scripts/h5files_to_tiles.sh -d data/icesat-2/ATL06-2019
# python scripts/altimeter_srtm_dif.py -d data/icesat-2/ATL06-2019
python ./scripts/stat_dif_altimeter.py -d data/icesat-2/ATL06-2019/tiles

# ./scripts/icesat_readout.sh -y 2020
# ./scripts/h5files_to_tiles.sh -d data/icesat-2/ATL06-2020
# python scripts/altimeter_srtm_dif.py -d data/icesat-2/ATL06-2020
python ./scripts/stat_dif_altimeter.py -d data/icesat-2/ATL06-2020/tiles

# ./scripts/icesat_readout.sh -y 2021
# ./scripts/h5files_to_tiles.sh -d data/icesat-2/ATL06-2021
# python scripts/altimeter_srtm_dif.py -d data/icesat-2/ATL06-2021
python ./scripts/stat_dif_altimeter.py -d data/icesat-2/ATL06-2021/tiles

# ./scripts/icesat_readout.sh -y 2022
# ./scripts/h5files_to_tiles.sh -d data/icesat-2/ATL06-2022
# python scripts/altimeter_srtm_dif.py -d data/icesat-2/ATL06-2022
python ./scripts/stat_dif_altimeter.py -d data/icesat-2/ATL06-2022/tiles

