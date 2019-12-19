#!/bin/env python3

# CURSE YOU SOCIALBLADE!
# YOUR PILE OF DOGSHITE IS THE WORST SITE I HAVE EVER HAD TO WORK WITH!
# HAVE YOU EVER HEARD OF NESTED LAYOUT!?
# WHY ARE YOUR "TABLES" AN ENDLESS PILE OF FLOATS WITH ABSOLUTE POSITIONING!?
# HAVE YOU NEVER HEARD OF .css FILES???? WHAT IS THIS INLINE STYLE NONSENSE?


from bs4 import BeautifulSoup
import sys
import json

channel = {}

inp = sys.stdin.read()

soup = BeautifulSoup(inp, "html.parser")
topInfo = soup.find(id="YouTubeUserTopInfoBlockTop")
try:
    channel["name"] = topInfo.find("div").find("h1").contents[0]
except:
    channel["name"] = "NULL"

try:
    t_infos = topInfo.find(id="YouTubeUserTopInfoBlock").findAll("div")
except:
    channel["ERROR"] = "Failed to find info on channel."
try:
    channel["views"] = t_infos[4].findChildren("span")[2].contents[0]
except:
    channel["views"] = "NULL"
try:
    channel["uploads"] = t_infos[2].findChildren("span")[2].contents[0]
except:
    channel["uploads"] = "NULL"
try:
    channel["subs"] = t_infos[3].findChildren("span")[2].contents[0]
except:
    channel["subs"] = "NULL"
try:
    channel["countryCode"] = t_infos[5].findChildren("span")[2].contents[0]
except:
    channel["countryCode"] = "NULL"
try:
    channel["contentCateogry"] = t_infos[6].findChildren("span")[2].find("a").contents[0]
except:
    channel["contentCategory"] = "NULL"

vw = soup.find(id="YouTube-Video-Wrap")

try:
    chid = vw.attrs["class"][0]
except:
    chid = "NONE"
channel["id"] = chid

je = json.JSONEncoder()

print(str(je.encode(channel)))

