import requests
import pandas as pd
import numpy as np
import os
import twstock

LINE_NOTIFY_TOKEN = os.environ['LINE_NOTIFY_TOKEN']
stockList = open('stock_watchList.txt','r').read().strip().split(',')

def format_to_two_decimals(value):
    return f"{value:.2f}"

def GetStockInfo(stockList):
    stockInfo_dataframe = pd.DataFrame(columns=['ticker',
                                                'stockName',
                                                'stockOpen',
                                                'stockNow',
                                                'stockHigh',
                                                'stockLow',
                                                'stockVolume'])

    stockInfo_dataframe['ticker'] = stockList

    for i in range(len(stockList)):
        try:
            stock_rt = twstock.realtime.get(stockList[i])
            stock_name = stock_rt['info']['name']
            stock_open = format_to_two_decimals(float(stock_rt['realtime']['open'])) if stock_rt['realtime']['open'] else None
            stock_now = format_to_two_decimals(float(stock_rt['realtime']['latest_trade_price'])) if stock_rt['realtime']['latest_trade_price'] else None
            stock_high = format_to_two_decimals(float(stock_rt['realtime']['high'])) if stock_rt['realtime']['high'] else None
            stock_low = format_to_two_decimals(float(stock_rt['realtime']['low'])) if stock_rt['realtime']['low'] else None
            stock_volume = int(stock_rt['realtime']['accumulate_trade_volume']) if stock_rt['realtime']['accumulate_trade_volume'] else None

            stock_history = twstock.Stock(stockList[i])[-1]
            stockChange = stock_history.change[-1]
            if(stockChange>= 0):
                _stockChange = "▲" + str(abs(stockChange))
            else:
                _stockChange = "▼" + str(abs(stockChange))    

            stockInfo_dataframe['stockName'][i] = stock_name
            stockInfo_dataframe['stockOpen'][i] = stock_open
            stockInfo_dataframe['stockNow'][i] = f"{stock_now}+({_stockChange})"
            stockInfo_dataframe['stockHigh'][i] = stock_high
            stockInfo_dataframe['stockLow'][i] = stock_low
            stockInfo_dataframe['stockVolume'][i] = stock_volume
        except Exception as e:
            print(f"Error: {e}")

    return stockInfo_dataframe

def generate_message(stockInfo_dataframe):
    for i in range(len(stockInfo_dataframe)):
        message = f"{stockInfo_dataframe['stockName'][i]}({stockInfo_dataframe['ticker'][i]}) \n 現價：{stockInfo_dataframe['stockNow'][i]} \n 開盤：{stockInfo_dataframe['stockOpen'][i]} \n 最高價：{stockInfo_dataframe['stockHigh'][i]} \n 最低價：{stockInfo_dataframe['stockLow'][i]} \n 交易量：{stockInfo_dataframe['stockVolume'][i]} \n"
        status = lineNotifyMessage(LINE_NOTIFY_TOKEN, message)
        print(status)

def lineNotifyMessage(token, msg):
    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    payload = {'message': msg}
    r = requests.post("https://notify-api.line.me/api/notify", headers = headers, params = payload)
    return r.status_code

stockInfo_dataframe = GetStockInfo(stockList)
generate_message(stockInfo_dataframe)
