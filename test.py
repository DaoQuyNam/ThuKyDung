from noti import TelegramNotifier
import ccxt
import pandas
import time
import sys
import numpy
from datetime import datetime
#import logs
import tulipy
from conf import Configuration
from exchange import ExchangeInterface
from analyzers.indicators.rsi import RSI
from analyzers.informants.sma import SMA
import talib

#hàm get ohlc
def get_ohlc(exchange_interface, market_pair, timeframe):
    data_ohlc = exchange_interface.get_historical_data(market_pair,'binance',timeframe)
    return data_ohlc
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



#def convert_to_dataframe(historical_data):
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


def bollinger_fibo(dataframe, period_count = 20):
    #input dataframe giá, số phiên nến
    close_data = numpy.array(dataframe['close'])
    high_data = numpy.array(dataframe['high'])
    low_data = numpy.array(dataframe['low'])
    atr_data = tulipy.atr(high_data, low_data, close_data, period_count)
    sma_data = tulipy.sma(close_data,period_count)

    top1_prev = sma_data[-2] + atr_data[-2] * 1.618
    top2_prev = sma_data[-2] + atr_data[-2] * 2.618
    top3_prev = sma_data[-2] + atr_data[-2] * 4.236
    bot1_prev = sma_data[-2] - atr_data[-2] * 1.618
    bot2_prev = sma_data[-2] - atr_data[-2] * 2.618
    bot3_prev = sma_data[-2] - atr_data[-2] * 4.236
    # tính now
    top1_now = sma_data[-1] + atr_data[-1] * 1.618
    top2_now = sma_data[-1] + atr_data[-1] * 2.618
    top3_now = sma_data[-1] + atr_data[-1] * 4.236
    bot1_now = sma_data[-1] - atr_data[-1] * 1.618
    bot2_now = sma_data[-1] - atr_data[-1] * 2.618
    bot3_now = sma_data[-1] - atr_data[-1] * 4.236
    bb_columns = {
         'top3': [top3_prev, top3_now],
         'top2': [top2_prev, top2_now],
         'top1': [top1_prev, top1_now],
         'sma': [sma_data[-2], sma_data[-1]],
         'bot1': [bot1_prev, bot1_now],
         'bot2': [bot2_prev, bot2_now],
         'bot3': [bot3_prev, bot3_now],
        }

    bb_values = pandas.DataFrame(bb_columns)
    return bb_values

def check_sma200(data_ohlc):
    close_data = numpy.array(data_ohlc['close'])
    sma_data = tulipy.sma(close_data, 200)
    print("SMA: " + str(sma_data[-1]))
    sma_now = sma_data[-1]
    msg = str(sma_now)
    if (sma_now * 0.99) <= data_ohlc.iloc[-1]['close'] <= (sma_now * 1.01):
        msg =  "\n Giá gần vùng SMA 200: " + str(sma_now)
    return msg

config = Configuration()

exchange_interface = ExchangeInterface(config.exchanges)
data_ohlc = get_ohlc(exchange_interface, "BTCUSDT", "1h")
data_conver = convert_to_dataframe(data_ohlc)
print(data_conver.iloc[-1])
msg = check_sma200(data_conver)

print(msg)



