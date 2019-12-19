#!/usr/bin/env python3

import requests
import sys
import hashlib
import json

baseurl = "https://api.socialblade.com/v2"
headers = {'cookie': '__cfduid=dc6d96ce2253fa2d2e687aaa773516c841575116802', 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36', "Upgrade-Insecure-Requests": "1","DNT": "1","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8","Accept-Language": "en-US,en;q=0.5","Accept-Encoding": "gzip, deflate"}


jd = json.JSONDecoder()

def login(email, pw):
    print(f"logging in with {email} and {pw}")
    ph = hashlib.md5(pw.encode()).hexdigest()
    print(f"request: ph: {ph}")
    res = requests.get(baseurl + "/bridge", headers=headers, params={"email":email, "password":ph})
    print("response")
    if res.status_code != 200:
        print("failed to log in.")

    print(res.text)
    rj = jd.decode(res.text)
    print(rj["id"]["token"])


#login(sys.argv[1], sys.argv[2])
token = "03127649aad40b1cc050269db05bc7d5d8f7e23cdba9f364f53ee71dfe46382614d679de8b22debf23be8fa3baed75ee96d63925cd7cdda8111ba4ef534d8741"

def get_list():
    lst = requests.get(baseurl + "/youtube/top/5000/mostsubscribed", headers=headers, params={"token": token})
    print(lst.text)

get_list()
