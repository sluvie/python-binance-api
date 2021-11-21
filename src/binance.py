import hmac
import hashlib
import logging
import requests
import time

try:
   from urllib import urlencode
# for python3
except ImportError:
   from urllib.parse import urlencode
   
# local
from config.settings import BINANCE_SETTINGS


class BinanceAPI:
   
   options = {}
   
   def __init__(self):
      """Set API key and secret.

      Must be called before any making any signed API calls.
      """
      self.options["apiKey"] = BINANCE_SETTINGS["key"]
      self.options["secret"] = BINANCE_SETTINGS["secret"]
      
      
   def serverTime(self):
      resp = requests.request("GET", BINANCE_SETTINGS["endpoint"] + "/api/v3/time")
      data = resp.json()
      return data["serverTime"]
   

   def request(self, method, path, params=None):
         resp = requests.request(method, BINANCE_SETTINGS["endpoint"] + path, params=params)
         data = resp.json()
         if "msg" in data:
            logging.error(data['msg'])
         return data
      
      
   def signedRequest(self, method, path, params):
      if "apiKey" not in self.options or "secret" not in self.options:
         raise ValueError("Api key and secret must be set")

      timestamp = self.serverTime()

      query = urlencode(sorted(params.items()))
      query += "&timestamp={}".format(timestamp)
      secret = bytes(self.options["secret"].encode("utf-8"))
      signature = hmac.new(secret, query.encode("utf-8"),
                        hashlib.sha256).hexdigest()
      query += "&signature={}".format(signature)

      resp = requests.request(method,
                              BINANCE_SETTINGS["endpoint"] + path + "?" + query,
                              headers={"X-MBX-APIKEY": self.options["apiKey"]})
      data = resp.json()
      if "msg" in data:
         logging.error(data['msg'])
      return data
      
   
   def prices(self):
      """Get latest prices for all symbols."""
      data = self.request("GET", "/api/v1/ticker/allPrices")
      return {d["symbol"]: d["price"] for d in data}
   
   
   def tickers(self):
      """Get best price/qty on the order book for all symbols."""
      data = self.request("GET", "/api/v1/ticker/allBookTickers")
      return {d["symbol"]: {
         "bid": d["bidPrice"],
         "ask": d["askPrice"],
         "bidQty": d["bidQty"],
         "askQty": d["askQty"],
      } for d in data}
      
      
   def depth(self, symbol, **kwargs):
      """Get order book.

      Args:
         symbol (str)
         limit (int, optional): Default 100. Must be one of 50, 20, 100, 500, 5,
            200, 10.

      """
      params = {"symbol": symbol}
      params.update(kwargs)
      data = self.request("GET", "/api/v1/depth", params)
      return {
         "bids": {px: qty for px, qty in data["bids"]},
         "asks": {px: qty for px, qty in data["asks"]},
      }
      
   
   def klines(self, symbol, interval, **kwargs):
      """Get kline/candlestick bars for a symbol.

      Klines are uniquely identified by their open time. If startTime and endTime
      are not sent, the most recent klines are returned.

      Args:
         symbol (str)
         interval (str)
         limit (int, optional): Default 500; max 500.
         startTime (int, optional)
         endTime (int, optional)

      """
      params = {"symbol": symbol, "interval": interval}
      params.update(kwargs)
      data = self.request("GET", "/api/v1/klines", params)
      return [{
         "openTime": d[0],
         "open": d[1],
         "high": d[2],
         "low": d[3],
         "close": d[4],
         "volume": d[5],
         "closeTime": d[6],
         "quoteVolume": d[7],
         "numTrades": d[8],
      } for d in data]
      
      
   def balances(self):
      """Get current balances for all symbols."""
      data = self.signedRequest("GET", "/api/v3/account", {})
      if 'msg' in data:
         raise ValueError("Error from exchange: {}".format(data['msg']))

      return {d["asset"]: {
         "free": d["free"],
         "locked": d["locked"],
      } for d in data.get("balances", [])}