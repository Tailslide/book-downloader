#!/bin/sh
umask 002
READARR_URL=http://192.168.12.148:8787 READARR_API_KEY=c7867b46e6ff45999cd676c38b2b9535 OS_TEMP_FOLDER=/volume1/docker/ircbooks LOCAL_TEMP_FOLDER=/ircbooks ./downloader.py IMPORTFILES
sudo chown plex /volume1/docker/ircbooks/*
sudo chgrp users /volume1/docker/ircbooks/*
READARR_URL=http://192.168.12.148:8787 READARR_API_KEY=c7867b46e6ff45999cd676c38b2b9535 OS_TEMP_FOLDER=/volume1/docker/ircbooks LOCAL_TEMP_FOLDER=/ircbooks ./downloader.py IMPORTFILES
