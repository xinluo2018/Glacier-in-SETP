
path_in=./data/icesat2/atl03-download/data_202001/*.h5
dir_out=./data/icesat2/atl03-readout
python utils/read_atl03.py $path_in -o $dir_out -n 4


