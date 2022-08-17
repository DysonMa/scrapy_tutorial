import requests as rq
import re

proxy_url = "https://free-proxy-list.net/"
api_url = "https://www.ipify.org/?format=json"

res =rq.get(proxy_url)
proxies = re.findall("\d+\.\d+\.\d+\.\d+:\d+", res.text)  # ex: 41.58.144.126:9812

valid_proxies = []
for proxy in proxies:
    try:
        res = rq.get(api_url, proxies={"http": proxy, "https": proxy}, timeout=5)
        valid_proxies.append(proxy)
        print(res.json())
    except:
        print(f"Invalid: {proxy}")

print(valid_proxies)


