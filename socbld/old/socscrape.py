#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup as Soup

listurl = "https://socialblade.com/youtube/top/5000/mostsubscribed"

res = requests.get(listurl).text

bs = Soup(res, "html.parser")
print(bs)
