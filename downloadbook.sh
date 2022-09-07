#!/bin/sh
echo Downloading $1
CONTAINER_NAME=$(uuidgen)
#docker run --rm -t -v /volume1/docker/ircbooks:/ircbooks -e "SEARCH_TERM=$1" -e "NICK=Tailslide" -e "LOCAL_TEMP_FOLDER=/ircbooks" --pull always --net=container:wireguard-qbittorrent_vpn_1  tailslide/book-downloader:latest
#(sleep 28800 ; sudo docker stop $CONTAINER_NAME)& docker run  --rm --name $CONTAINER_NAME --pull=always --label=com.centurylinklabs.watchtower.enable=false  --env-file excludarr.env haijeploeg/excludarr:latest radarr exclude -a delete -y -e

(sleep 28800 ; sudo docker stop $CONTAINER_NAME)& docker run --rm  --name $CONTAINER_NAME -t -v /volume1/docker/ircbooks:/ircbooks -e "SEARCH_TERM=$1" -e "NICK=Tailslide" -e "LOCAL_TEMP_FOLDER=/ircbooks" --pull always --label=com.centurylinklabs.watchtower.enable=false --net=container:wireguard-qbittorrent_vpn_1  tailslide/book-downloader:latest
