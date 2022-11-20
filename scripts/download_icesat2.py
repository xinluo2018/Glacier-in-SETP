## author: xin luo;
## create: 2022.8.7;
## des: download icesat2 data with given region and data type.
## !!!note: the user should login on the earthdata website firstly. 
##          the internet is important, try different VPN。
## usage: python download_icesat2.py or python download_icesat2.py -e 91 27 92 28 -t 2020-01-01 2020-12-31

import os
import icepyx as ipx
import glob
import argparse
from pprint import pprint

def get_args():
    description = "download the icesat2 data."
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
            '-e', metavar=('w','s','e','n'), dest='extent', type=float, nargs=4,
            help=('extent for data downloading'),
            default=[91, 27, 92, 28])
    parser.add_argument(
            '-t', metavar=('start','end'), dest='time', type=str, nargs=2,
            help=('temporal interval for data downloading'),
            default=['2020-01-01', '2020-12-31'])
    return parser.parse_args()

if __name__ == '__main__':
    args = get_args() 
    lon_min, lat_min, lon_max, lat_max = args.extent[0],\
                            args.extent[1], args.extent[2], args.extent[3]
    bounding_box = [lon_min, lat_min, lon_max, lat_max]
    time_start, time_end = args.time[0], args.time[1]
    date_range = [time_start, time_end]
    print('bounding_box:', bounding_box)
    print('date range:', date_range)
    earthdata_uid = '411795604'
    email = 'xinluo_xin@163.com'
    data_type = 'ATL06'
    dir_save = 'data/icesat/' + data_type + '-download/2020/tile-'+str(bounding_box[1])+'-'+str(bounding_box[0])
    # dir_save = 'data/icesat/' + data_type + '-download/2020/tile-27-91-month'   ##
    if not os.path.exists(dir_save):os.makedirs(dir_save)
    data_region = ipx.Query(data_type, bounding_box, date_range)
    print('Product:', data_region.product)
    print('Version:', data_region.product_version)
    pprint(data_region.avail_granules())

    data_region.earthdata_login(earthdata_uid, email)
    data_region.order_granules(email=False)
    data_region.download_granules(dir_save)

