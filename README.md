# Glacier-in-SETP
Glacier change monitoring for the Southeastern Tibetan Plateau by using aster stereo image and icesat-2 and satellite images.

### 1. data preparation
#### - 1.1 download aster stereo images on the website: https://search.earthdata.nasa.gov/search.
#### - 1.2 download icesat1 data by using scripts/icesat_download.sh, 
#### - 1.3 download icesat2 data by using scripts/download_icesat2.py. 
#### - 1.4 download tandem data from the website: https://download.geoservice.dlr.de/TDM90/ 
#### - 1.5 download srtm dem data by using scripts/get_srtm.sh. the srtm dem data is used as base map in our paper.


### 2. Icesat data processing (including both icesat-1 and icesat-2 data)
#### - 2.1 icesat data read out and subset to tiles.
- Step1: raw data read in and write out to the specific region data, by using scripts/readout.sh.  
- Step2: subset data to tiles by using scrpits/h5files/tiles.sh. the processing including:   
- 1) Search the .h5 files fall in the range of tiles.  
- 2) Merge the searched .h5 files.   
- 3) Subset the merged .h5 file to given tile.
#### - 2.2 obtain tiles-based elevation difference value.
- 1) The elevation difference is calculated by using srtm dem data.   
- 2) The statistic of elevation difference (mean and std, et al.) for each tile of each year is obtianed.   


### 3. Cyrosat-2 data processing
#### - 3.1 cryosat-2 tempo_points data read out and subset to tiles.
- Step1: raw data read in and write out to the specific region data, by using scripts/readout.sh.  
- Step2: subset data to tiles by using scrpits/h5files/tiles.sh. the processing including:   
- 1) Search the .h5 files fall in the range of tiles.  
- 2) Merge the searched .h5 files.   
- 3) Subset the merged .h5 file to given tile.
#### - 3.1 xxx

### 4. Aster stereo image-based dem processing
#### 4.1 Aster dem generation by using script/aster_dem_batch.sh
#### 4.2. post-processing for the aster dem data
#### 4.3. aster dem coregistration with the srtm data.
#### 4.4. calculate the dems difference map with with the srtm data.

### 5. data evaluation 
#### 5.1 Aster dem evaluation by using the notebooks/dem_evaluate_atl06.ipynb and notebooks/dem_evaluate_galh14.ipynb.

## To do
1) mask out the data/cryotempo-points/2021/cryotempo_points_merge.h5 by using data/rgi60/rgi60_setp_mask.tif

