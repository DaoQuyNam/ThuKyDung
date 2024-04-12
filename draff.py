
"""
import okx.Account as Account
# API initialization
apikey = "ac14f6b7-c0d2-4c5c-bcd7-6e37033ba157"
secretkey = "E3CCC6D5FC337211764867A56F801D44"
passphrase = "Abc@123456"

flag = "0"  # Production trading:0 , demo trading:1

accountAPI = Account.AccountAPI(apikey, secretkey, passphrase, False, flag)

# Get account balance
result = accountAPI.get_account_balance()
print(result)
"""
###################
import ccxt
import pandas
from datetime import datetime

#Khai bao env
apiKey = 'm6nFjCJbcdNVseXSBcUjlKbra6TTiNSsvCDhDxiEJjImPvvKwgvAXhlCJqkFOVHM'
secret = 'PR6XrhRrBm6orSSOWu5WnhR6vJaU0jICsMsy0jwKTZ3GbilffeA7qWiY56GntgMl'
#binance = binance = ccxt.binance({'apiKey': apiKey,'secret': secret})
#binance.set_sandbox_mode(True)
binance = binance = ccxt.binance()
def get_price_1m(sym):
    price = binance.fetch_ohlcv(sym, '1m',limit=6,)
    return price


def print_balance():
    balance = binance.fetch_balance()
    return balance

price1p = get_price_1m('BTC/USDT')
print(price1p)
print(type(price1p))