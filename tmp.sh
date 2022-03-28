#! /bin/bash
lon1=-122.36; lon2=-123.12
lon=$(echo "scale=3; $lon1 / 2 + $lon2 / 2" | bc)
utm_zone=$(echo $lon / 6 + 31 | bc)
echo $utm_zone

