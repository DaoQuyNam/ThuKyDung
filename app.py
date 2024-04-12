#File chinh
from noti import TelegramNotifier
import ccxt
import pandas
import time
import sys
import numpy
import datetime
import tulipy
from conf import Configuration
from exchange import ExchangeInterface
from analyzers.indicators.rsi import RSI
#from analyzers.informants.sma import SMA
from datetime import datetime
import talib
import os

###
binance_ex = ccxt.binance()
#hàm get ohlc
def get_ohlc(exchange_interface, market_pair, timeframe):
    data_ohlc = exchange_interface.get_historical_data(market_pair,'binance',timeframe)
    return data_ohlc
#Hàm get giá hiện tại
def get_current_price(market_pair):
    binance_ex = ccxt.binance()
    current_price = binance_ex.fetch_ticker(market_pair)
    return(current_price['bid'])

#Hàm convert dataframe
def convert_to_dataframe(historical_data):
        """Converts historical data matrix to a pandas dataframe.

        Args:
            historical_data (list): A matrix of historical OHCLV data.

        Returns:
            pandas.DataFrame: Contains the historical data in a pandas dataframe.
        """

        dataframe = pandas.DataFrame(historical_data)
        dataframe.transpose()

        dataframe.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        dataframe['datetime'] = dataframe.timestamp.apply(
            lambda x: pandas.to_datetime(datetime.fromtimestamp(x / 1000).strftime('%c'))
        )

        dataframe.set_index('datetime', inplace=True, drop=True)
        dataframe.drop('timestamp', axis=1, inplace=True)

        return dataframe

#Tính bolliger fibo
def cal_bollinger_fibo(data_ohlc, period_count = 20):
    #input dataframe giá, số phiên nến
    close_data = numpy.array(data_ohlc['close'])
    high_data = numpy.array(data_ohlc['high'])
    low_data = numpy.array(data_ohlc['low'])
    atr_data = tulipy.atr(high_data, low_data, close_data, period_count)
    sma_data = tulipy.sma(close_data,period_count)

    #top1_prev = sma_data[-2] + atr_data[-2] * 1.618
    #top2_prev = sma_data[-2] + atr_data[-2] * 2.618
    #top3_prev = sma_data[-2] + atr_data[-2] * 4.236
    #bot1_prev = sma_data[-2] - atr_data[-2] * 1.618
    #bot2_prev = sma_data[-2] - atr_data[-2] * 2.618
    #bot3_prev = sma_data[-2] - atr_data[-2] * 4.236
    # tính now
    top1_now = sma_data[-1] + atr_data[-1] * 1.618
    top2_now = sma_data[-1] + atr_data[-1] * 2.618
    top3_now = sma_data[-1] + atr_data[-1] * 4.236
    bot1_now = sma_data[-1] - atr_data[-1] * 1.618
    bot2_now = sma_data[-1] - atr_data[-1] * 2.618
    bot3_now = sma_data[-1] - atr_data[-1] * 4.236
    
    return [top1_now, top2_now, top3_now, bot1_now, bot2_now, bot3_now]

def bb_fibo(data_ohlc, period_count = 20):
    point = 0
    top1_now, top2_now, top3_now, bot1_now, bot2_now, bot3_now = cal_bollinger_fibo(data_ohlc, period_count)  
    msg = ""
    price_now = data_ohlc.iloc[-1]['close']
    price_high_now = data_ohlc.iloc[-1]['high']
    price_low_now = data_ohlc.iloc[-1]['low']
    price_prev = data_ohlc.iloc[-2]['close']
    
    #Logic Long
    #Giá hiện tại lớn hơn giá đóng cửa phiên trước
    if price_now > price_prev:
        # Giá thấp nến này chạm band bot 2
        if bot3_now < price_low_now and price_low_now < bot2_now:
            point = point + 0.5
            msg = "\n 🟢Giá chạm band bot 2: " + str(bot2_now)
        if price_low_now < bot3_now:
            point = point + 1
            msg = "\n 🟢Giá chạm band bot 3: " + str(bot3_now)
    # Giá hiện tại nhỏ hơn giá đóng cửa phiên trước
    if price_now <= price_prev:
        if top2_now < price_high_now and price_low_now < top3_now:
            point = point - 0.5
            msg = "\n 🔴Giá chạm band top 2: " + str(top2_now)
        if top3_now < price_high_now:
            point = point - 1
            msg = "\n 🔴Giá chạm band top 3: " + str(top3_now)
    return [point, msg]
        

#hàm cảnh báo SMA
def check_sma200(data_ohlc):
    close_data = numpy.array(data_ohlc['close'])
    #print(close_data.size)
    sma_data = tulipy.sma(close_data, 200)
    #print("tới đây ok")
    #print("SMA: " + str(sma_data[-1]))
    sma_now = sma_data[-1]
    msg = ""
    if (sma_now * 0.99) <= data_ohlc.iloc[-1]['close'] <= (sma_now * 1.01):
        msg =  "\n Giá gần vùng SMA 200: " + str(sma_now)
    else:
        msg =  "\n Khung 1h SMA 200: " + str(sma_now)
    return msg


# rsi adv
def rsi_adv(data_ohlc):
    rsi = RSI()
    point = 0
    msg = ""
    #data_ohlc = exchange_interface.get_historical_data(market_pair,'binance','1h')
    #current_price = binance_ex.fetch_ticker(market_pair)
    rsi10 = rsi.analyze_2(data_ohlc,10).sort_index(ascending=False) # tính giá trị Rsi 10
    ma2_now = round(rsi10.iloc[0:2, :].mean(), 2) # MA2 của rsi hiện tại
    ma7_now = round(rsi10.iloc[0:7, :].mean(), 2) # MA7 của rsi hiện tại
    ma2_prev_1 = round(rsi10.iloc[1:3, :].mean(), 2) # MA2 của rsi nến trước
    ma2_prev_2 = round(rsi10.iloc[2:4, :].mean(), 2)
    ma7_prev = round(rsi10.iloc[1:8, :].mean(),  2) # MA7 của rsi nến trước
    # 4 case:
    #Case 1: Long - rs2 cat len rsi 7: Cong 1 point
    if (ma2_now[0] > ma7_now[0]) and (ma2_prev_1[0] < ma7_prev[0]):
        point = point + 0.5
        msg = msg + "\n 🟢 MA2_RSI cắt lên MA7_RSI"
    #Case 2: Long - rs2 tang 6,8 point
    if (ma2_now[0] - ma2_prev_1[0]) > 6.8:
        point = point + 0.5
        sub = round(ma2_now[0] - ma2_prev_1[0], 2)
        msg = msg + "\n 🟢 MA2_RSI tăng mạnh, tăng " + str(sub) + "điểm"
    if (ma2_prev_1[0] < 32) or (ma2_now[0] < 32):
        point = point + 0.5
        msg = msg + "\n 🟢 MA2_RSI vùng 32 "
        #Case 3: Short - rs2 cat xuong rsi 7: Cong 1 point
    if (ma2_now[0] < ma7_now[0]) and (ma2_prev_1[0] > ma7_prev[0]):
        point = point - 0.5
        msg = msg + "\n 🔴 MA2_RSI cắt xuống MA7_RSI"
    #Case 2: Long - rs2 tang 6,8 point
    if (ma2_prev_1[0] - ma2_now[0]) > 6.8:
        point = point - 0.5
        sub = round(ma2_prev_1[0] - ma2_now[0], 2)
        msg = msg + "\n 🔴 MA2_RSI giảm mạnh, giảm " + str(sub) + "điểm"
    if (ma2_prev_1[0] > 68) or (ma2_now[0] > 68):
        point = point + 0.5
        msg = msg + "\n 🔴 MA2_RSI vùng 68 "
    return [point, msg]
    



def main():
    """Initializes the application
    """
     # Load settings and create the config object
    config = Configuration()
    settings = config.settings
    noti = config.notifiers['telegram']
    rsi = RSI()
    bot = TelegramNotifier(noti)
    exchange_interface = ExchangeInterface(config.exchanges)


    while True:
        for market_pairs in settings['market_pairs']:
            get_data = get_ohlc(exchange_interface, market_pairs, "15m")
            data_ohlc = convert_to_dataframe(get_data)
            point_rsi, msg_rsi = rsi_adv(data_ohlc)
            point_bbfibo, msg_bbfibo = bb_fibo(data_ohlc,20)
            #msg_bbfibo = cal_bollinger_fibo(data_ohlc, 20)
            #print(msg_bbfibo)
            get_data_1h = get_ohlc(exchange_interface, market_pairs, "1h")
            data_ohlc_1h = convert_to_dataframe(get_data_1h)
            if (data_ohlc_1h.size > 200):
                msg_sma200 = check_sma200(data_ohlc_1h)
            else:
                msg_sma200 = ""
            #msg_sma200 = check_sma200(data_ohlc)
            header = market_pairs + "- price: " + str(data_ohlc.iloc[-1]['close'])
            #print (header)
            #print(data_ohlc_1h.size)
            point = 0
            point = point_rsi + point_bbfibo

            if point > 1:
                msg = header + " - Point: " + str(point) + msg_rsi + msg_bbfibo + msg_sma200
                #msg = header + " - Point: " + str(point) + msg_rsi + msg_sma200
                bot.send(msg)
        #bot.send("Check done")
        print("Sleeping for " + str(settings['update_interval']) + " seconds")
        time.sleep(settings['update_interval'])

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)

