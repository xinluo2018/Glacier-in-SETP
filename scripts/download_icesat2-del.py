## author: xin luo;
## create: 2022.8.7;
## des: download icesat2 data with given region and data type.
## the user should login on the earthdata website firstly.

import os
import icepyx as ipx
import glob
from pprint import pprint

root_proj = '/Users/luo/OneDrive/GitHub/Glacier-in-RGI1305'
os.chdir(root_proj)

earthdata_uid = '411795604'
email = 'xinluo_xin@163.com'
data_type = 'ATL06'
spatial_extent = [91, 27, 92, 28]     # rgi13_05
date_range = ['2020-01-01','2020-12-31']
dir_save = 'data/icesat/atl06-download/2020/tile-27-91'

data_region = ipx.Query(data_type, spatial_extent, date_range)
print('Product:', data_region.product)
print('Version:', data_region.product_version)
pprint(data_region.avail_granules())

data_region.earthdata_login(earthdata_uid, email)
data_region.order_granules(email=False)

if not os.path.exists(dir_save):  
  os.makedirs(dir_save)
  print("The new directory is created!")

data_region.download_granules(dir_save)

