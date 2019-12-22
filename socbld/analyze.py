#!/bin/env python3

from pymongo import MongoClient
import time
import sys
import statistics
from datetime import datetime
import csv

print("connecting to mongodb")
client = MongoClient()

db = client.socblddb
rd = db.rd

def make_vid_lst(vs):
    tmp_d = dict()
    for a in vs:
        for v in a["videos"]:
            tmp_d[v["videoId"]] = v
    return tmp_d.values()


stats = []

nrec = rd.count()
crec = 0
for rec in rd.find({}):
    crec += 1
    print(f"[{crec:4}/{nrec:4}] Rank:{rec['rank_subscribers']} : {rec['displayname']} : {rec['channelid']} ; ", end="")

    videos = make_vid_lst(rec["recent-videos"])

    print(f"{len(videos)} videos; ", end="")

    if len(videos) < 2:
        mean_dt_v = None
        median_dt_v = None
        v_upl_weekdays = None
        print("No stats to be done")
    else:
        v_creation_dates = [datetime.strptime(x["created_at"], "%Y-%m-%d") for x in videos]
        v_ts_diff = []
        v_upl_weekdays = [0] * 7
        for i in range(len(v_creation_dates)-1):
            a = v_creation_dates[i]
            b = v_creation_dates[i+1]
            d = a - b
            ddays = abs(d.days)
            v_ts_diff.append(ddays)

        for v in v_creation_dates:
            v_upl_weekdays[v.weekday()] += 1

        mean_dt_v = statistics.mean(v_ts_diff)
        median_dt_v = statistics.median(v_ts_diff)

    # "username" : "tseries", "channelid" : "UCq-Fj5jknLsUf-MWSy4_brA", "cusername" : "tseriesmusic", "displayname" : "T-Series", "subscribers" : "122000000", "vidviews" : "92550818884", "uploads" : "14191", "created_at" : "2006-03-13", "channeltype" : "music", "country" : "IN", "avgdailyviews" : "104915000", "views30" : "3291253565", "views365" : "36300067604", "sbrank" : "1", "rank_subscribers" : 1, "rank_views" : "1"
    print(f"mean dt={mean_dt_v}, median dt={median_dt_v}, uploads by weekday={v_upl_weekdays}")
    sobj = rec
    del sobj["seen_at"]
    del sobj["_id"]
    del sobj["recent-videos"]
    del sobj["estimated_earnings"]
    sobj["mean_dt_videos"] = mean_dt_v
    sobj["median_dt_videos"] = median_dt_v
    sobj["uploads_per_weekday"] = v_upl_weekdays
    stats.append(sobj)

stats.sort(key=lambda k: k["rank_subscribers"])

#print(stats[0].keys())

keys = [
    'rank_subscribers',
    'rank_views',
    'sbrank',
    'channeltype',
    'channelid',
    'username',
    'cusername',
    'displayname',
    'created_at',
    'country',
    'subscribers',
    'uploads',
    'vidviews',
    'mean_dt_videos',
    'median_dt_videos',
    'uploads_per_weekday',
    'avgdailyviews',
    'views30',
    'views365',
]
with open(sys.argv[1],'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=keys)

    writer.writeheader()
    for s in stats:
        writer.writerow(s)
