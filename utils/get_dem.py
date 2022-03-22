## reference: https://github.com/uw-cryo/asp-binder-demo/blob/master/asp_binder_utils.py
## creat: 2022.3.18 # modify: xxxx
## des: download dem data from OpenTopography World DEM

import os
import sys
import requests

def get_dem(demtype, bounds, apikey, path_out=None):
    """
    download a DEM of choice from OpenTopography World DEM
    Parameters
        demtype: str, type of DEM to fetch (e.g., COP30, SRTMGL1, SRTMGL1_E(SRTMGL1 Ellipsoidal), SRTMGL3 etc)
        bounds: list, geographic aoi extent in format (minlon,maxlon,minlat,maxlat)
        apikey: str, opentopography api key(obtain from: https://opentopography.org/)        
        path_out: str, path to output filename        
    """

    base_url="https://portal.opentopography.org/API/globaldem?demtype={}&west={}&east={}&south={}&north={}&outputFormat=GTiff&API_Key={}"
    if path_out is None:
        path_out = '{}.tif'.format(demtype)
    if not os.path.exists(path_out):
        #Prepare API request url
        url = base_url.format(demtype, *bounds, apikey)
        print(url)
        #Get
        response = requests.get(url)
        #Check for 200
        if response.ok:
            print ('DEM data have been downloaded!')
        else:
            print ('Query failed')
            sys.exit()
        #Write to disk
        open(path_out, 'wb').write(response.content)
    else:
        print('!!Output file has been existed.')

