#!./venv/bin/python3

########
# Author: /u/anonymous_rocketeer
# THIS PROGRAM COMES WITH ABSOLUTELY NO WARRANTY
# Please download only public domain books ;)
######## 

"""
A Simple Ebook downloading bot. 
Much credit to Joel Rosdahl for his irc package:
https://github.com/jaraco/irc
This bot searches irc.irchighway.net only, and is meant only to streamline the somewhat clunky download process. 
This code is of debatable quality, but as far as I can tell, it works.
Use at your own risk

Calling this program:

python3 downloader.py
OR:

python3 downloader.py <nickname> <searchterm>

KNOWN BUGS: If there are no search results, it hangs forever. Sorry.
"""

#Settings:
#Preferred filetype:
filetypes = ".mobi,.epub"
searchtimeout = 20
starttimeout = 20
alwaysoverwrite = True
acceptfirst = True

#Preferred nickname:
nickname = "" #leave blank to be prompted
#TODO: Set custom path to save file?
import requests
import random
import json
import irc.bot
import irc.strings
from irc.client import ip_numstr_to_quad, ip_quad_to_numstr
import re
import zipfile
import os
import struct
import sys
import time
import argparse
import shlex
from time import sleep
import jaraco.logging
from jaraco.stream import buffer
import six
from six.moves import socketserver
import irc.client
from os import listdir
from os.path import isfile, join
import shutil

def get_script_path():
    return os.path.dirname(os.path.realpath(sys.argv[0]))

#Prevents a common UnicodeDecodeError when downloading from many sources that don't use utf-8
irc.client.ServerConnection.buffer_class = buffer.LenientDecodingLineBuffer


def userselect(filename):
    """
    This reads searchbot's results line by line, 
    outputting only the ones that are in the preferred format
    It then asks the user to make a selection
    If the user declines all entries in the preferred format, 
    it lists all available files regardless of filetype.
    """
    ftypes= filetypes.split(",")
    for ftype in ftypes:
        with zipfile.ZipFile(filename, "r") as z:
            with z.open(z.namelist()[0]) as fin:

                answer = "n"

                for line in fin:
                    line = str(line)[2:-5]
                    if ftype in line.lower():
                        if acceptfirst:
                            print("Auto downloading file " + line)
                            return line.split("::")[0]
                        answer = input(line + " (y/n/q?)\n")
                    if answer == "y":
                        return line.split("::")[0]
                    if answer == "q":
                        return ""

class TestBot(irc.bot.SingleServerIRCBot):
    def __init__(self, searchterm,  localfolder, channel, nickname, server, port=6667,):
        irc.bot.SingleServerIRCBot.__init__(
            self, [(server, port)], nickname, nickname)
        self.channel = channel
        self.searchterm = searchterm
        self.received_bytes = 0
        self.havebook = False
        self.havesearchresults = False
        self.localfolder = localfolder
        
    def on_nicknameinuse(self, c, e): #handle username conflicts
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        c.join(self.channel)
        print ("waiting after join")
        time.sleep(starttimeout)
        print("Searching for " + self.searchterm + "..\n")
        self.connection.privmsg(self.channel, "@search " + self.searchterm)
        time.sleep(searchtimeout)
        if not self.havesearchresults:
            print("No search results found")
            self.die()

    def on_ctcp(self, connection, event):
        #Handle the actual download
        payload = event.arguments[1]
        parts = shlex.split(payload)

        if len(parts) != 5: #Check if it's a DCC SEND 
            return  #If not, we don't care what it is

        print("Receiving Data:")
        print(payload)
        command, filename, peer_address, peer_port, size = parts
        if command != "SEND":
            return
        print("peer sending file on port" + str(peer_port))
        #self.filename = os.path.basename(filename)
        self.filename = self.localfolder + "/" + filename
        if os.path.exists(self.filename) and not alwaysoverwrite:
            answer = input(
                "A file named", self.filename,
                "already exists. Overwrite? (y/n)")
            if answer != "y":
                print("Refusing to overwrite. Edit filenames and try again.\n")
                self.die()
                return
            print("Overwriting ... \n")
        printf("writing file " + self.filename)
        self.file = open(self.filename, "wb")
        peer_address = irc.client.ip_numstr_to_quad(peer_address)
        peer_port = int(peer_port)
        self.my_dcc = self.dcc("raw")
        self.my_dcc.connect(peer_address, peer_port)
        
    def on_dccmsg(self, connection, event):
        data = event.arguments[0]
        self.file.write(data)
        self.received_bytes = self.received_bytes + len(data) 
        ##TODO: Write progress bar here?
        self.my_dcc.send_bytes(struct.pack("!I", self.received_bytes))

    def on_dcc_disconnect(self, connection, event):
        self.file.close()
        print("Received file %s (%d bytes).\n" % (self.filename,
                                                self.received_bytes))
        #self.connection.quit()
        #Download actual book:
        #Have the user pick which one to download:
        if not self.havebook:
            self.havesearchresults =True
            if not acceptfirst:
                print("Search Complete. Please select file to download:\n")
            book = userselect(self.filename)
            if book != "":
                self.received_bytes = 0
                self.connection.privmsg(self.channel, book)
                self.havebook = True
                print("Removing File: " + self.filename)
                os.remove(self.filename) #remove the search .zip
                print("Submitting request for " + book)
            else:
                self.die() #end if user picked quit
        else:
            self.die() #end program when the book disconnect finishes

    def search(self, searchterm):
        self.connection.privmsg(self.channel, searchterm)


def processfiles(readarrUrl, readarrApiKey, localfolder, containerfolder):
    thispath = get_script_path()
    onlyfiles = [f for f in listdir(thispath) if isfile(join(thispath, f)) and f.endswith(tuple(filetypes.split(",")))]
    for f in onlyfiles:
        print("Importing: " + f + " to " + localfolder + " (container folder "+ containerfolder + ")")
        shutil.move(f, localfolder)
        headers = {'X-Api-Key': readarrApiKey, 'Content-Type': 'application/json'}
        body = {"name": "DownloadedBooksScan", "path": containerfolder}
        response = requests.post(readarrUrl + "/api/v1/command", data=json.dumps(body), headers=headers)
        print(response)
        print(response.json())
def main():

    global nickname
    searchterm = ""
    #readarrUrl = os.getenv('READARR_URL')
    #readarrApiKey = os.getenv('READARR_API_KEY')
    nickname = os.getenv('NICK')
    localfolder = os.getenv('LOCAL_TEMP_FOLDER')
    #containerfolder = os.getenv('READARR_TEMP_FOLDER')
    searchterm = os.getenv('SEARCH_TERM')
#    if len(sys.argv) == 6:
#        nickname = sys.argv[1]
#        readarrUrl = sys.argv[2]
#        readarrApiKey = sys.argv[3]
#        localfolder = sys.argv[4]
#        containerfolder = sys.argv[5]
#    elif len(sys.argv) == 3:
    if len(sys.argv) == 4:
        searchterm = sys.argv[1]
        nickname = sys.argv[2]
        localfolder = sys.argv[3]
    if searchterm == "" or searchterm == None:
        print("Usage: testbot [<searchterm> <nickname> <localfolder>]")
    else:
        #        if (readarrUrl == "" or readarrUrl == None):
        #            print("Usage: testbot [<searchterm> <nickname>] | [<nickname> <readarrUrl> <readarrApiKey> <localfolder> <containerfolder>]")
        #            searchterm = input("Enter Search Term(s):\n")
        #            if nickname == "":
        #                nickname = input("Enter Nickname:\n")
        #     print (readarrUrl)
        #     if (readarrUrl != "" and readarrUrl != None):
        #         processfiles(readarrUrl, readarrApiKey, localfolder, containerfolder)
        #         headers = {'X-Api-Key': readarrApiKey}
        #         page=1
        #         wanted = []
        #         while True:
        #             response = requests.get(readarrUrl + "/api/v1/wanted/missing?includeAuthor=false&pageSize=10&page=" + str(page),
        #                                     headers=headers)
        #             if response != 200:
        #                 data = response.json()
        #                 recs = data["records"]
        #                 if len(recs) == 0:
        #                     break
        #                 wanted = wanted + recs
        #             else:
        #                 print("Error:" + str(response))
        #                 break
        #             page = page+1
        #         print("Wanted Books:")
        #         for r in wanted:
        #             print("\t" + r["author"]["authorName"] + " - " + r["title"])
        #         w = random.choice(wanted)
        #         searchterm = w["author"]["authorName"] + " - " + w["title"]
        #         print("\nRandomly selected:" +searchterm)
        #return
        #searchterm = "Kurt Vonnegut Jr. - God Bless You, Dr. Kevorkian" #this has no results
        server = "irc.irchighway.net"
        port = 6667
        channel = "#ebooks"
        bot = TestBot(searchterm, localfolder, channel, nickname, server, port)
        bot.start()
        print("Downloaded:" + bot.filename)
        #processfiles(readarrUrl, readarrApiKey, localfolder, containerfolder)

if __name__ == "__main__":
    main()

