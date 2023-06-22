#! /bin/bash
cd /home/xin/Developer-luo/Glacier-in-SETP

python scripts/stat_dif_isat1.py
python scripts/stat_dif_altimeter.py -dtype icesat-2
python scripts/stat_dif_altimeter.py -dtype cryosat-2
python ./scripts/stat_dif_dems.py

