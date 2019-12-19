#!/usr/bin/env python3

import requests
import time
from pymongo import MongoClient

staturl = "https://api.socialblade.com/v2/youtube/statistics"

headers = {
    'cookie': "__cfduid=dde9d364a7c40f9bbc07b0c89713d15be1576774828",
    'user-agent': "foobar3000"
    }

headers_post = {
    'cookie': "__cfduid=dde9d364a7c40f9bbc07b0c89713d15be1576774828",
    'user-agent': "foobar3000",
    'content-type': "application/x-www-form-urlencoded"
    }


#Get guest auth token
res = requests.get("https://api.socialblade.com/v2/auth/guest", headers=headers)
apikey = res.json()["key"]

print(f"using guest api key: {apikey}")


query = {"guest":apikey,
               "amount":"5000",
               "query":"top",
               "top_type":"mostsubscribed"}

print("fetching toplist")
res = requests.get(staturl, params=query, headers=headers)
print("done")
rj = res.json()
tlist = rj["result"]

print(f"fetched {len(tlist)} results.")

print("connecting to mongodb")
client = MongoClient()

db = client.socblddb
rd = db.rd

ct = int(time.time())
for t in tlist:
    t["seen_at"] = [{"time":ct, "rank_subs":t["rank_subscribers"]}]
    print(f"Updating {t['channelid']}: ", end="")

    sel = {"channelid":t["channelid"]}
    if rd.count_documents(sel) > 0:
        r = rd.update_one(sel,
                        {"$push":
                        {"seen_at":{"time":ct,
                                    "rank_subs":t["rank_subscribers"]}}
                        })

        print(str(r.modified_count))
    else:
        rd.insert_one(t)
        print("inserted")

print(f"data from {ct} inserted.")

nrec = rd.count()
crec = 0
for rec in rd.find({}):
    crec += 1
    print(f"[{crec:4}/{nrec:4}] {rec['username']} : {rec['channelid']} ; ", end="")

    payload=f"channelid={rec['channelid']}"
    print("requesting ;", end="")
    res = requests.post("https://socialblade.com/js/class/youtube-video-recent", data=payload, headers=headers_post)
    try:
        rj = res.json()
    except:
        print("FUCKING COULDFLARE")
        exit(1)
    print(f"found {len(rj)} videos ; ", end="")

    sel = {"channelid":rec["channelid"]}

    r = rd.update_one(sel,
                    {"$push":
                    {"recent-videos":{"time":ct,
                                "videos":rj}}
                    })

    print(str(r.modified_count))
