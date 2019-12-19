#!/bin/env python3

import statistics
import math
import os
import googleapiclient.discovery
import json
import sys

jd = json.JSONDecoder()

channels = []
with open(sys.argv[1], "r") as f:
    for l in f:
        channels.append(jd.decode(l))

n = 0

fc = []

for c in channels:
    if "last50uploads" not in c or (c["last50uploads"] == [] and c["uploads"] != 0)\
            or ("subs" in c and "M" not in c["subs"]):
        print(str(c))
        fc.append(c)
        n += 1

print("---------------- [%d] ---------------" % n)




def ytapi():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=YT_API_KEY)

    lines = []
    with open("chl.txt") as f:
        lines = f.readlines()

    with open("tofixl.txt","a") as f:
        for c in fc:
            if c["toplistindex"] <= 313:
                print("already checked")
                continue
            print(c)
            if "failedToOpen" in c:
                furl = c["url"]
                cn = furl.split('/')[5]
            elif ("ERROR" in c and c["ERROR"] == "Failed to find info on channel.") \
                    or ("name" in c and c["name"] == "NULL"):
                furl = lines[c["toplistindex"]]
                cn = furl.split('/')[3]
            else:
                cn = c["name"]
            print("cname: %s " % cn)

            request = youtube.search().list(
                part="id",
                maxResults=1,
                q=cn,
                type="channel"
            )

            response = request.execute()
            chid = response["items"][0]["id"]["channelId"]
            f.write("{} ; {}\n".format(c["toplistindex"], chid))


#ytapi()

import dateutil.parser as p
for c in channels:
    if "last50uploads" in c and len(c["last50uploads"]) > 1:
        u = c["last50uploads"]
        d = [(p.parse(b) - p.parse(a)).days for a,b in zip(u,u[1:])]
        c["meantbu"] = statistics.mean(d)
        c["mediantbu"] = statistics.median(d)
        print("{} : {} : {} : {} : {}".format(c["toplistindex"], c["name"],u , c["meantbu"], c["mediantbu"]))
    else:
        c["meantbu"] = "NONE"

exportkeys = ("toplistindex","id", "name", "subs","views","uploads",
              "countryCode","contentCategory","meantbu","mediantbu")

with open("res.csv","w") as f:
    f.write(",".join(exportkeys) + ",\n")
    for c in channels:
        f.write(",".join(str(c.get(a)) for a in exportkeys) + ",\n")


print(channels[0].keys())
