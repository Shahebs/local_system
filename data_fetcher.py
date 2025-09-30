import yfinance as yf
import pandas as pd

def fetch_data(stock_symbol, period="1y", interval="1d"):
    """
    Fetches historical stock data from Yahoo Finance.
    """
    ticker = yf.Ticker(stock_symbol)
    data = ticker.history(period=period, interval=interval)
    return data