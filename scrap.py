import requests
import pandas as pd
import numpy as np

INDEXS = 25000
INDEXE = 30000

url = 'https://www.hkex.com.hk/eng/stat/dmstat/dayrpt/hsio190226.csv'
resp = requests.get(url=url)
if resp.status_code == requests.codes.ok:
	#print(resp.text)
	data=resp.text

start = data.find("CONTRACT MONTH")
end = data.find(',,,,,"',start)
callfile = open('call.csv', 'w')
callfile.write(data[start-1:end-1])
callfile.close() 

start = data.find("CONTRACT MONTH",end)
end = data.find(',,,,,"',start)
putfile = open('put.csv', 'w')
putfile.write(data[start-1:end-1])
putfile.close()

calldata = pd.DataFrame.from_csv('call.csv')
putdata = pd.DataFrame.from_csv('put.csv')

for value in range(INDEXS,INDEXE,100):
    iv=0
    for i,row in calldata.iterrows():
            if value>int(row['STRIKE PRICE']):
                point = (value-int(row['STRIKE PRICE']))
                iv+=point*int(row['OPEN INTEREST']) #*int(row['VOLUME.2'])
    niv=0
    for i,row in putdata.iterrows():
            if value<int(row['STRIKE PRICE']):
                point = (int(row['STRIKE PRICE'])-value)
                niv+=point*int(row['OPEN INTEREST']) #*int(row['VOLUME.2'])
    print(value,(iv+niv)/10000000000)

	