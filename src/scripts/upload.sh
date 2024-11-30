#!/bin/bash
python3 upload.py -v -H10.0.0.1 -p12000 -s./files -n$1

diff ./files/$1 ./server_storage/$1

wc -c ./files/$1

wc -c ./server_storage/$1

#rm ./server_storage/$1
