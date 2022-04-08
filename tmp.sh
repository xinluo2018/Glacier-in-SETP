#! /bin/bash

echo "pid is $$"
while (( COUNT < 10 ))
do
  sleep 1
  (( COUNT ++ ))
  echo $COUNT
done
exit 0
