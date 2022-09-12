# Glacier-in-RGI1305
Glacier change monitoring by using aster stereo image and icesat-2 and satellite images.

## Public dem data download
### 1. srtm-c dem: script/get_srtm.sh
### 2. srtm-x dem: https://download.geoservice.dlr.de/SRTM_XSAR/
### 3. tandem-x dem: https://download.geoservice.dlr.de/TDM90/#download

## To do
### 1. modify the notebooks/dem_evaluate_atl06.ipynb and notebooks/dem_evaluate_glah14.ipynb.
### 2. try to merge the notebooks/dem_evaluate_atl06.ipynb and notebooks/dem_evaluate_glah14.ipynb into one.
### 3. try to merge the notebooks/dem_dif_infer_atl06.ipynb and notebooks/dem_dif_infer_glah14.ipynb into one.

## Workflow
### 1. data prepare
#### - 1.1 download aster stereo images on the website: https://search.earthdata.nasa.gov/search.
#### - 1.2 download icesat1 data by using script/download_GLAH14.py, and icesat2 data by using script/download_icesat2.py. 
#### 1.3 download tandem data from the website: https://download.geoservice.dlr.de/TDM90/ 

### 2. Icesat data processing 
#### 2.1 icesat1 data processing by using script/icesat1_readout.sh
#### 2.2 icesat2 data processing by using script/icesat2_readout.sh

### 3. Aster dem generation 
#### - By using script/aster_dem_batch.sh

### 4. post-processing for the aster dem data
#### - 3.1 Aster dem co-registration with the tandem data by using notebooks/dems_coreg_demo. 
#### - 3.2 Aster dem improvement with the icesat data by using notebooks/dem_dif_infer_atl06.ipynb and notebooks/dem_dif_infer_glah14.ipynb.

### 5. Aster dem evaluation
#### - By using the notebooks/dem_evaluate_atl06.ipynb and notebooks/dem_evaluate_galh14.ipynb.

