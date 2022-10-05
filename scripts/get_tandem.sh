#! /bin/bash 
## author: xin luo;
## create: 2022.08.30;
## des: download multiply tandem tiles data by using links file and unzip.
## note: the download links list file should be prepared firstly.

path_root=/Users/luo/Library/CloudStorage/OneDrive-Personal/GitHub/Glacier-in-RGI1305
path_links_file=${path_root}/data/dem-data/tandem-x/TDM90-url-list.txt
dir_save=${path_root}/data/dem-data/tandem-x

### 1. download tandem
cat $path_links_file | while read -r line || [ -n "$line" ]
do
  echo $line
  data_name=$(echo `basename $line`)
  path_save=${dir_save}/${data_name}
  if [ ! -f $path_save ]; then
    wget -O $path_save $line --auth-no-challenge --user='xinluo_xin@163.com' --password='luo_513812'
  fi
done

### 2. unzip tandem data
paths_zip=$(ls ${dir_save}/*.zip)

for path_zip in $paths_zip;
do
  echo --$path_zip
  zip_name=$(echo `basename $path_zip`)
  zip_name=$(echo $zip_name | cut -d . -f1)  # remove extension
  if [ ! -d ${dir_save}/${zip_name}_V0?_C ]; then
    unzip $path_zip -d $dir_save
    echo $path_zip
  fi
done



