import futuquant as ft
import os
import time
import tkinter as tk
import requests
import easyquotation
quotation  = easyquotation.use("hkquote")
import pandas as pd
import threading
import numpy as np
import random

root = tk.Tk()
root.wm_attributes("-topmost", 1)
maxleverage = 0
date='2019/03/25'
hsip = 28700
#http://qt.gtimg.cn/?q=s_hk58940,s_hk65239,s_hk65836,s_hk65312,s_hk65040,s_hk66028,s_hk66491,s_hk62048,s_hk00700,s_hkHSI&_=1539367134081
#2318 淡
def _random(n=13) -> str:
    start = 10 ** (n - 1)
    end = (10 ** n) - 1
    return str(random.randint(start, end))

def getwarrant(warrantcode,index,code):
    global validwarrant
    if warrantcode == "60359":
        print("yeah")
    while(validwarrant[code].iloc[index]['leverage'] == 1):
        rnd = _random()
        url = 'http://web.ifzq.gtimg.cn/appstock/app/HkWarrant/hkw?code='+warrantcode+f'&_callback=jQuery{_random(21)}_{rnd}&_={str(int(rnd)+1)}'
        resp = requests.get(url=url)
        leverage = 1
        if resp.status_code == requests.codes.ok:
            pos = resp.text.find('"hsj":')+7
            strike_price = 0
            if pos>=7:
                hsj = resp.text[pos:]
                recovery_price = float(hsj[:hsj.find('",')])
            else:
                recovery_price = 0
            extract = resp.text[resp.text.find('"jhl":')+6:]
            streetvol = 0
            if extract.find("\\u4ebf\\u80a1")>0:
                num = extract[1:extract.find('\\u4ebf\\u80a1')]
                streetvol = float(num)*100000000
                start = resp.text.find('"ggbl":"')+8
                tmp = resp.text[start:resp.text.find('\\u500d',start)].replace(",","")
                leverage = float(tmp)
                dcztext = resp.text.find('"dcz":"')+7
                if dcztext>=8:
                    dcz = float(resp.text[dcztext:resp.text.find('%',dcztext)])*0.01
                    leverage = leverage*dcz
                    tmppos = resp.text.find('"xqjg":"')
                    #strike_price = float(resp.text[tmppos+8:tmppos+15])
            elif extract.find("null")>=0 or extract.find("--") >= 0:
                streetvol = 0
                dcztext = resp.text.find('"dcz":"')+7
                if dcztext<7:
                    start = resp.text.find('"ggbl":"')+8
                    tmp = resp.text[start:resp.text.find('\\u500d',start)].replace(",","")
                    leverage = float(tmp)
                    tmppos = resp.text.find('"xqjg":"')
                    #strike_price = float(resp.text[tmppos+8:tmppos+15])
                else:
                    leverage = 0
            elif extract.find("\\u4e07\\u80a1")>0:
                num = extract[1:extract.find('\\u4e07\\u80a1')].replace(",","")
                streetvol = float(num)*10000
                start = resp.text.find('"ggbl":"')+8
                tmp = resp.text[start:resp.text.find('\\u500d',start)].replace(",","")
                leverage = float(tmp)
                dcztext = resp.text.find('"dcz":"')+7
                if dcztext>=8:
                    dcz = float(resp.text[dcztext:resp.text.find('%',dcztext)])*0.01
                    leverage = leverage*dcz
                    tmppos = resp.text.find('"xqjg":"')
                    #strike_price = float(resp.text[tmppos+8:tmppos+15])
            else:
                print("exception",warrantcode)
            validwarrant[code].at[index,'streetvol'] = streetvol
            validwarrant[code].at[index,'leverage'] = leverage
            validwarrant[code].at[index,'recovery_price'] = recovery_price
            validwarrant[code].at[index,'strike_price'] = strike_price
            validwarrant[code].at[index,'val'] = int(float(leverage*streetvol*validwarrant[code].iloc[index]['price'])/1000000*9/16)
        time.sleep(0.1) 
def fund(code):
        base = '{"iv":"2","sid":"","appType":"32","clientType":"1","theme":"light","imei":"865166027375099","agentId":"1000191","lang":"zh_CN","version":"2.0.601","timestamp":"1545834427769","macAdrs":""}'
        buzz1 = '{"dataType":10004,"securityCode":"'
        buzz2='.HK"}'
        sign = "ai0WwMLUyQp3AuTFoiel7Ux6I7g%3D"
        url = 'https://gzhqinterface.hstong.com/hq/fundFlowTimeSharing'
        resp = requests.post(url=url, data={'base': base, 'buzz': buzz1+code+buzz2, 'format': 'json','sign':sign})
        time = []
        flow = []
        obj = resp.json()
        for key in obj['data']:
            time.append(key.split(' ')[0])
            flow.append(float(key.split(' ')[1]))
        funddf = pd.DataFrame({'time':time,'flow':flow})
        return(funddf)
def warrant(quote_ctx,code):
    global bullvalue,bearvalue,putvalue,callvalue,suggest,CALL,PUT
    threads = []
    maxthread = 100
    for index,row in validwarrant[code].iterrows():
        threads.append(threading.Thread(target = getwarrant, args = (row['code'].replace("HK.",""),index,code,)))
        threads[index%maxthread].start()
        if (index+1) % (maxthread) == 0:
            for i in range(maxthread):
                threads[i].join(5)
            if (validwarrant[code].iloc[index]['leverage'] == 1):
                threading.Thread(target = getwarrant, args = (row['code'].replace("HK.",""),index,code,)).start()
            threads = []
            root.update()
    time.sleep(1)
    BULL = validwarrant[code].loc[validwarrant[code]['type'] == 'BULL']
    BEAR = validwarrant[code].loc[validwarrant[code]['type'] == 'BEAR']
    CALL = validwarrant[code].loc[validwarrant[code]['type'] == 'CALL']
    PUT = validwarrant[code].loc[validwarrant[code]['type'] == 'PUT']
    bullvalue = 0
    bearvalue = 0
    callvalue = 0
    putvalue = 0
    for index,row in BULL.iterrows():
        bullvalue += row['val']
    for index,row in BEAR.iterrows():
        bearvalue += row['val']
    for index,row in CALL.iterrows():
        callvalue += row['val'] 
    for index,row in PUT.iterrows():
        putvalue += row['val'] 
    """tot = bullvalue + bearvalue
    print(code,"=============")
    more = bullvalue + callvalue
    less = bearvalue + putvalue
    tot2 = more + less
    print("BULLBEAR: ",bullvalue/ tot, bearvalue/ tot," / ",more/tot2,less/tot2)"""
    suggest = 'BULL:'+ BULL.loc[BULL['leverage']==BULL['leverage'].max(),['code','leverage']].to_string(header=False,
                  index=False,
                  index_names=False)
    suggest += '\nBEAR:' + BEAR.loc[BEAR['leverage']==BEAR['leverage'].max(),['code','leverage']].to_string(header=False,
                  index=False,
                  index_names=False)
    """
    quote_ctx.subscribe('HK.800000', [ft.SubType.QUOTE])
    ret_status, data = quote_ctx.get_stock_quote('HK.800000')
    HSIprice = float(data['last_price'])
    print(HSIprice)
    index = 0
    while index<len(HSI):
        ret_status, ret_data = quote_ctx.get_market_snapshot(HSI[index:index+300]['code'].tolist())
        for i,row in ret_data.iterrows():
            leverage = HSIprice / (float(row['last_price'])*float(row['wrt_conversion_ratio']))
            streetvol = int(row['wrt_street_ratio'])
            HSI.loc[HSI['code'] == row['code'],'streetvol'] = streetvol
            HSI.loc[HSI['code'] == row['code'],'leverage'] = leverage
        index += 300
    print(HSI)"""
    
if __name__ == "__main__":
    global validwarrant
    quote_context = ft.OpenQuoteContext(host='127.0.0.1', port=11111)
    labela = []
    labelb = []
    labelc = []
    label = []
    warrantlist = ["HK.800000"]
    for i, wcode in enumerate(warrantlist):
        label.append(tk.Label(root, 
        text= wcode,
        fg = "black",
        font = "Helvetica 12 bold italic"))
        label[i].grid(row=0+i*2, rowspan=2)
        labela.append(tk.Label(root, 
        text="HSI",
        font = "Verdana 9 bold"))
        labela[i].grid(row=0+i*2,column=1)
        labelb.append(tk.Label(root, 
        text="HSI",
        font = "Verdana 9"))
        labelb[i].grid(row=1+i*2,column=1)
        labelc.append(tk.Label(root, 
         text="",
         fg = "black",
         font = "Helvetica 10 bold italic"))
        labelc[i].grid(row=0+i*2,column=2)
    validwarrant = {}
    for wcode in warrantlist:
        ret_status, hsidata = quote_context.get_referencestock_list(wcode, ft.SecurityReferenceType.WARRANT)
        print(wcode,"\nall: ",len(hsidata))
        data = quotation.real(hsidata['code'].tolist())
        validwarrant[wcode] = pd.DataFrame(columns=('code','price','leverage','streetvol','type','recovery_price','strike_price','val'))
        for key, item in data.items():
            if item['status'] == "" and item['price']>0.01 and item['time'].find(date)>= 0:
                if item['name'].find('牛')>= 0:
                    warranttype = 'BULL'
                elif item['name'].find('购')>= 0:
                    warranttype = 'CALL'
                elif item['name'].find('熊')>= 0:
                    warranttype = 'BEAR'
                elif item['name'].find('沽')>= 0:
                    warranttype = 'PUT'
                validwarrant[wcode] = validwarrant[wcode].append({'code' : "HK."+ key,'price' : item['price'],'type': warranttype,'leverage': 1}, ignore_index=True)
        print("valid: ",len(validwarrant[wcode]))
    while(1==1):
        for i, wcode in enumerate(warrantlist):
            warrant(quote_context,wcode)
            tot = bullvalue + bearvalue+1
            more = bullvalue + callvalue
            less = bearvalue + putvalue
            tot2 = callvalue + putvalue+1
            if more>less:
                labela[i].config(fg="green",text="%.3f" % (bearvalue/tot))
                labelb[i].config(fg="green",text="%.3f" % (putvalue/tot2))
                label[i].config(fg="green",text="%s\n(%.3f)" % (wcode,less/(more+less)))
            else:
                labela[i].config(fg="red",text="%.3f" % (bullvalue/tot))
                labelb[i].config(fg="red",text="%.3f" % (callvalue/tot2))
                label[i].config(fg="red",text="%s\n(%.3f)" % (wcode,more/(more+less)))
            labelc[i].config(text=suggest)
            validwarrant[wcode]['leverage'] = 1
            root.update()
            print(validwarrant[wcode].loc[validwarrant[wcode]['code'] == '60359'])
            #maxp = int(round(validwarrant[wcode]['recovery_price'].max(),-2))
            #minp = int(round(validwarrant[wcode]['recovery_price'][validwarrant[wcode]['recovery_price']!=0].min(),-2))
            #quote_context.subscribe('HK.800000', [ft.SubType.QUOTE])
            #ret_status, data = quote_context.get_stock_quote('HK.800000')
            HSIprice = hsip
            print(HSIprice)
            maxp = HSIprice+2000
            minp = HSIprice-2000
            bullc = 0
            bearc = 0
            print("BULL=======================")
            for j in range(HSIprice,minp,-100):
                resultdf = validwarrant[wcode][validwarrant[wcode]['recovery_price'].between(j, j+99, inclusive=True)]
                valsum = resultdf['val'].sum()
                maxvol = resultdf[resultdf['val']==resultdf['val'].max()]
                if valsum>0:
                    if (bullc<8):
                        bullc+=1
                        print(j,j+100,valsum,' max:',int(maxvol['recovery_price']))
            print("==========================\nHSI: ",HSIprice)
            print("BEAR=======================")
            for j in range(HSIprice+100,maxp,100):
                resultdf = validwarrant[wcode][validwarrant[wcode]['recovery_price'].between(j, j+99, inclusive=True)]
                maxvol = resultdf[resultdf['val']==resultdf['val'].max()]
                valsum = resultdf['val'].sum()
                if valsum>0:
                    if (bearc<8):
                        bearc+=1
                        print(j,j+100,valsum,' max:',int(maxvol['recovery_price']))
            print("===========================")
            callstrike = 0
            callamount = 0
            for index,row in CALL.iterrows():
                if row['price'] < 0.02:
                    price = 0
                else:
                    price = row['price']
                val = row['streetvol'] * price
                callamount += val
                callstrike += row['strike_price']* val
            putstrike = 0
            putamount = 0
            for index,row in PUT.iterrows():
                if row['price'] < 0.02:
                    price = 0
                else:
                    price = row['price']
                val = row['streetvol'] * price
                putamount += val
                putstrike += row['strike_price']* val
            print("CALL(avg): ",callstrike/callamount)
            print("PUT(avg): ",putstrike/putamount)
            print(validwarrant[wcode].sort_values(['streetvol'], ascending=False))
            """
            j = 27500
            resdf = validwarrant[wcode][validwarrant[wcode]['recovery_price'].between(j, j+99, inclusive=True)]
            funddict = {}
            i=0
            for x,item in resdf.iterrows():
                ccode = item['code'].replace("HK.","")
                tmp = fund(ccode)
                funddict[ccode] = tmp
                if i==0:
                    totalfund = tmp
                else:
                    totalfund = totalfund.set_index('time').add(tmp.set_index('time'), fill_value=0).reset_index()
                i+=1
            print(funddict)
            print(totalfund)
            """
            time.sleep(200)
    quote_context.close()