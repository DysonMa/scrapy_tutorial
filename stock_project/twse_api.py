import requests as rq

# twse api: https://openapi.twse.com.tw/#/
# limit: 3 request/5 sec

# api example 1
res = rq.get('https://openapi.twse.com.tw/v1/exchangeReport/BWIBBU_ALL')
info = res.json()[0]
print(info)
print("Name:", info['Name'])
print("DividendYield: ", info['DividendYield'])
print("PBratio: ", info['PBratio'])

# api example 2
res = rq.get('https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_AVG_ALL')
info = res.json()[0]
print(info)
