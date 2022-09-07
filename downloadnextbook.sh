#!/bin/sh
nextbook=`./findnextbook.sh`
echo searching for $nextbook
docker stop "$(sudo docker ps -q --filter ancestor="tailslide/book-downloader:latest" )"
res=`./downloadbook.sh "$nextbook"`
echo $res



