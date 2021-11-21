from src import *

# get server binance time (timestamp)
# servertime = binance_api.serverTime()
# print(servertime)

# get all latest prices
# latestprices = binance_api.prices()
# print(latestprices)

# get all book tickers
# tickers = binance_api.tickers()
# print(tickers)

# get depth / order book
# order_book = binance_api.depth("SOLUSDT")
# print(order_book)

# get candlestick data
# data = binance_api.klines("SOLUSDT", "30m")
# print(data)

# get balances
# balances = binance_api.balances()
# print(balances)

# order
# response = binance_api.order("SOLUSDT", binance_api.BUY, 0.001, binance_api.LIMIT, binance_api.GTC, True)

# order status
response = binance_api.orderStatus("SOLUSDT")