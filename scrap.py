import numpy as np
import pandas as pd
import requests

def main(date):
    url = 'https://www.hkex.com.hk/eng/stat/dmstat/dayrpt/hsio'+date+'.csv'
    resp = requests.get(url=url)
    if resp.status_code == requests.codes.ok:
        #print(resp.text)
        res=resp.text

    start = res.find("TOP 10 TRADED (BY VOLUME)")-1
    end = res.find("Hang Seng Index Options HK$50 per point",start)-1
    file = open('data.csv', 'w')
    file.write(res[start-1:end-1])
    file.close() 
    data = pd.read_csv('data.csv',index_col=False)
    calldata = data[data["TOP 10 TRADED (BY VOLUME)"]== 'C']
    putdata = data[data["TOP 10 TRADED (BY VOLUME)"]== 'P']

    INDEXS = data["Unnamed: 2"].min()-100
    INDEXE = data["Unnamed: 2"].max()+100

    print(data)
    for value in range(INDEXS,INDEXE,100):

        iv=0
        for i,row in calldata.iterrows():
            #if int(row['STRIKE PRICE'])>=25600:
                if value>int(row['Unnamed: 2']):
                    point = (value-int(row['Unnamed: 2']))
                    iv+=point*int(row['OPEN INTEREST'])
        niv=0
        for i,row in putdata.iterrows():
            #if int(row['STRIKE PRICE'])<=29000:
                if value<int(row['Unnamed: 2']):
                    point = (int(row['Unnamed: 2'])-value)
                    niv+=point*int(row['OPEN INTEREST'])
        loss = (iv+niv)/10000
        print(value,loss)
main('190410')
