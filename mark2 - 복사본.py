# -*- coding: utf-8 -*-
"""
Created on Wed Mar 30 01:51:33 2022

@author: 고종민
"""

import requests
import time
import math
import pyupbit
import datetime


 




import search
import isgoodtime
#responsee=requests.get('https://api.coinmarketcap.com/data-api/v3/top/rank').text
#jsonObject=json.loads(responsee)['data']
#print(responsee)
#for i in range(10):
    #print(jsonObject['cryptoTopSearchRanks'][i]['marketCap'],jsonObject['cryptoTopSearchRanks'][i]['name'])


access = "5QtDCYud86l4xzBq6Zv1d7W3c2C6ox0xVbOxHMRM"
secret = "iJ03CoqjVZqf95lJDAvgkTxrA5aGDZJdH8FHZVZ7"
upbit=pyupbit.Upbit(access,secret)
selllist=[]





def checkprice(ticker):


    url = "https://api.upbit.com/v1/candles/days?market="+ticker+"&count=1&convertingPriceUnit=KRW"

    headers = {"Accept": "application/json"}

    response = requests.request("GET", url, headers=headers).json()
    a=response[0]
    #print(a["opening_price"]/pyupbit.get_current_price(ticker))
    return pyupbit.get_current_price(ticker)/a["opening_price"]

def get_balance(ticker):
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0


def get_price(ticker):
    balances=upbit.get_balances()
    ticker=ticker.lstrip("KRW")
    ticker=ticker.strip("-")
    for b in balances:
        if b['currency'] == ticker:
            #print(b['avg_buy_price'])
            if b['avg_buy_price'] is not None:
                return b['avg_buy_price']
            else:
                return 0
    return 0

def get_current_price(ticker):
    
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]

def get_all_money():
    a=upbit.get_balances()
    allmoney=0.0
    for i in range(len(a)):
        if a[i]["currency"]=="KRW":
            allmoney+=float(a[i]["balance"])
        else:
            if a[i]["currency"]=="VTHO":
                print("VTHO")
            else:
                allmoney+=float(a[i]["balance"])*float(get_current_price("KRW-"+a[i]["currency"]))
    return allmoney
def timinggoodnow():
    url = "https://api.upbit.com/v1/market/all?isDetails=false"
    headers = {"Accept": "application/json"}
    a=0
    response = requests.request("GET", url, headers=headers).json()
#print(response)
    for i in response:
        time.sleep(0.1)
        if checkprice(i["market"])>=1.001:
            a+=1
            
    b=(a/len(response))
    if b>=0.5:
        return 1
    return 0

def buy(keys,money,buylist,selllist,allmoney):

    url = "https://api.upbit.com/v1/market/all?isDetails=false"
    headers = {"Accept": "application/json"}

    response = requests.request("GET", url, headers=headers).json()
    invest=[]
    for k in keys: 
        #print(buylist)
        for i in response:
            #invest=[]
            if k in i['korean_name']:
                if "KRW" in i["market"]:
                    if (k not in buylist):
                        print(i["market"])
                        res = requests.request("GET", 'https://api.upbit.com/v1/ticker', params={'markets':i["market"]}).json()
                        print(res[0]["acc_trade_price_24h"])
                        if (res[0]["acc_trade_price_24h"]>=4000000000):
                            if checkprice(i["market"])<=1.10: 
                                if  i["market"] in selllist:
                                    print(i["market"],"은 이미 판매했던 코인")
                                else:
                                    isgood=isgoodtime.isgoodnow(i["market"])
                                    if isgood!=-1:
                                        if upbit.get_balance(ticker=i["market"])*pyupbit.get_current_price(i["market"])<=allmoney*0.35:
                                            if i["market"]!="KRW-BTT":    
                                                invest+=[i["market"]]
                                    else:
                                        print("매수 부적합")
                                    #upbit.buy_market_order(response[i]['market'], (0.990*money/(len(keys))))
                                    #print(response[i]['korean_name'],float(math.floor(money/(len(keys)))*0.990),"구매 완료")
                                    #if response[i]["market"] not in buylist:
                                        #buylist+=[response[i]["market"]]
                            else:
                                print(i['market'],"현재 너무 많이 올랐음.")
    if invest is None:
        return 0
    buymoney=(0.995*money)/len(invest)
    for l in invest:
        if buymoney>=allmoney*0.4:
            if buymoney>=allmoney*0.8:
                buymoney=buymoney*0.5
            else:
                buymoney=buymoney*0.75
        upbit.buy_market_order(l, buymoney)
        file = open("log.txt", mode="a", encoding="utf-8")
        file.writelines([l,str(float(math.floor(money/(len(invest)))*0.990)),"구매 완료\n"])
        file.close()
        print(l,float(math.floor(money/(len(invest)))*0.990),"구매 완료")
        if l not in buylist:    
            buylist+=[l]
    print("구매목록:",invest)
    return 0


def sell(buylist,keys,selllist,timelist,fire,allmoney):
    #url = "https://api.upbit.com/v1/market/all?isDetails=false"

    #headers = {"Accept": "application/json"}

    #response = requests.request("GET", url, headers=headers).json()
    removelist=[]

    if len(buylist)==0:
        return 0
    else:         
        for a in buylist:
            currprice=pyupbit.get_current_price(a)
            buyprice=float(get_price(a))
            isgood=isgoodtime.isgoodnow(a)
            #if fire==1:
                #upbit.sell_market_order(a, upbit.get_balance(ticker=a)) 
                #removelist+=[a]
                #print(a,pyupbit.get_current_price(a),"판매 완료")
                #selllist+=[a]
                #timelist+=[now+datetime.timedelta(hours=1)]
            if fire==1:
                if allmoney*0.35>=currprice*upbit.get_balance(ticker=a):
                    sonjerl=0.97
                else:
                    sonjerl=0.985
            else:
                if allmoney*0.35>=currprice*upbit.get_balance(ticker=a):
                    sonjerl=0.96
                else:
                    sonjerl=0.98
            if currprice<=buyprice*sonjerl:
                if a not in keys:
                    upbit.sell_market_order(a, upbit.get_balance(ticker=a))     
                #print(upbit.get_balance(ticker=a))
                #print(pyupbit.get_current_price(a))    
                #print(float(get_price(a))*1.03)
                    removelist+=[a]
                    file = open("log.txt", mode="a", encoding="utf-8")
                    file.writelines([a,str(pyupbit.get_current_price(a)),"판매 완료\n"])
                    file.close()
                    print(a,pyupbit.get_current_price(a),"판매 완료")
                    selllist+=[a]
                    timelist+=[now+datetime.timedelta(hours=5)]
            if allmoney*0.35>=currprice*upbit.get_balance(ticker=a):
                if isgood==1:
                    ikjerl=1.05
                else:
                    ikjerl=1.028
            else:
                if isgood==1:
                    ikjerl=1.025
                else:
                    ikjerl=1.015
            if currprice>=buyprice*ikjerl:
                if a in keys:
                    if currprice>=buyprice*(ikjerl+0.015):
                        upbit.sell_market_order(a, upbit.get_balance(ticker=a))                          
                        removelist+=[a]
                        file = open("log.txt", mode="a", encoding="utf-8")
                        file.writelines([a,str(pyupbit.get_current_price(a)),"판매 완료\n"])
                        file.close()
                        print(a,pyupbit.get_current_price(a),"판매 완료")
                        selllist+=[a]
                        timelist+=[now+datetime.timedelta(hours=5)]
                else:
                    upbit.sell_market_order(a, upbit.get_balance(ticker=a))                          
                    removelist+=[a]
                    file = open("log.txt", mode="a", encoding="utf-8")
                    file.writelines([a,str(pyupbit.get_current_price(a)),"판매 완료\n"])
                    file.close()
                    print(a,pyupbit.get_current_price(a),"판매 완료")
                    selllist+=[a]
                    timelist+=[now+datetime.timedelta(hours=5)]
        for m in removelist:
            print(removelist)
    return 0

now=datetime.datetime.now()
isnine=now.strftime('%H:%M:%S')
timelist=[datetime.datetime.now()]
trade=1
kkk=1
ak=upbit.get_balances()
buylist=[]
#print(listt)          
#buylist=[]
selllist=[]
while True:
    try:
        buylist=[]
        ak=upbit.get_balances()
        for i in range(len(ak)):
            if ak[i]["currency"]!="KRW":
                if ak[i]["currency"]=="VTHO":
                    print("VTHO")
                else:
                    buylist+=["KRW-"+ak[i]["currency"]]
        allmoney=get_all_money()
        #print(pyupbit.get_current_price("krw_eth"))
        money=get_balance("KRW") 
        print(now)
        file = open("log.txt", mode="a", encoding="utf-8")
        file.write(str(now)+"\n")
        file.close()
        now=datetime.datetime.now()
        #print(end_time)
        timing=[]
        keys=search.get_crawl(timing)
        print("현재 구매 대상", keys)
        if "a" in timing:
            goodtime=timinggoodnow()
            if goodtime==1:
                if isnine<"09:00:00" or isnine>"09:05:00":
                    print("현재는 매수 타이밍")
                    file = open("log.txt", mode="a", encoding="utf-8")
                    file.writelines(["현재 구매 대상 ", ",".join(keys)," 현재는 매수 타이밍\n"])
                    file.close()
                    sell(buylist,keys,selllist,timelist,1,allmoney)
                    if money>=10000:
                        buy(keys,money,buylist,selllist,allmoney)
            else:
                print("현재는 매수금지 타이밍")
                file = open("log.txt", mode="a", encoding="utf-8")
                file.writelines(["현재 구매 대상 ", ",".join(keys)," 현재는 매수금지 타이밍\n"])
                file.close()
                sell(buylist,keys,selllist,timelist,0,allmoney)
        else:
            print("현재는 매수금지 타이밍")
            file = open("log.txt", mode="a", encoding="utf-8")
            file.writelines(["현재 구매 대상 ", ",".join(keys)," 현재는 매수금지 타이밍\n"])
            file.close()
            sell(buylist,keys,selllist,timelist,0,allmoney)
        if len(timelist)>=1:
            print(type(timelist[0]))
            if timelist[0]<datetime.datetime.now():
                timelist.pop(0)
                selllist.pop(0)
        #if money>=10000:
            #buy(keys,money,buylist,selllist)
        #if trade==1:
            #if money>=10000:
                #buy(keys,money,buylist)
            #sell(buylist)
            #end_time=now+datetime.timedelta(hours=1)
            #print("다음 거래 시간은",end_time)
        print("현재",buylist,"보유중")
        file = open("log.txt", mode="a", encoding="utf-8")
        file.writelines(["현재 " + ",".join(buylist) + " 보유중\n"])
        file.close()
        for mam in range(len(selllist)):
            print("현재",selllist[mam],timelist[mam],"까지 대기중.")
            
        time.sleep(0.5)
            #trade=0
        #else:
            #if now>=end_time:
                #trade=1
    except Exception as e:
        print(e)
        time.sleep(1)
              
    #buy(keys,money)

                    
#b=response[0]
#b=response[1]
#print(type(b),"입니다")
#print(b)

#a=response.text.split("},")
#print(a[0])
#c=a[0]
#type(c)
#for k in a:
    #if "KRW" in k:
        #k=k.strip("{")
        #k=k.strip("}]")
        #k=k.strip("[{")
        #b+=[k]
        #print(k)
#buy=[]
#for m in b:
    #if m.find("위믹스")!=-1:
        #buy+=[m[10:17]]
#if len(buy)>=2:
    #print("오류")
#res = requests.request("GET", 'https://api.upbit.com/v1/ticker', params={'markets':'KRW-BTC'}).json()
#m=res[0]
#print(m)
#m=m.split(",")
#print(type(m))
#print(buy)
#sichong=["KRW-BTC","KRW-ETH"]
#print(b)
#print(b[0])

#while True:
    
#url = 'https://coinmarketcap.com/coins/'
#resp = requests.get(url)
#bs = BeautifulSoup(resp.text, 'html5lib')

#sel = f"#__next > div > div > div > div > div > div > table > tbody > tr > td:nth-of-type(3) > div > a > div > div > div > p"
#sel = f"#__next > div > div > div > div > div > div > table > tbody > tr > td:nth-of-type(5) > div > p"




#res = bs.select(sel)
#for item in res:
    #print(item.text)


#print(a)
#print(type(a))
#print(a[1])
#for i in keys:
    #b=a.find(i)
    #print(b)
    #if b==-1:
        #print("없노")
    #else:
        #print("있노")
#a=tuple()
#for i in a:
    #print(i)
    #if i["korean_name"] in keys:
        #print("있노")
    #else: