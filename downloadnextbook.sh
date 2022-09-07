#!/bin/sh
nextbook=`./findnextbook.sh`
echo searching for $nextbook
res=`./downloadbook.sh "$nextbook"`
echo $res



