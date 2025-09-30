import pandas as pd

def add_indicators(data):
    """
    Adds technical indicators to the dataframe.
    """
    # Simple Moving Average (SMA)
    data['SMA_20'] = data['Close'].rolling(window=20).mean()

    # Exponential Moving Average (EMA)
    data['EMA_20'] = data['Close'].ewm(span=20, adjust=False).mean()

    data.dropna(inplace=True)
    return data

def create_labels(data, threshold=0.05):
    """
    Creates labels for supervised learning based on future returns.
    Label is 1 if the future return is > threshold, else 0.
    """
    data['Future_Close'] = data['Close'].shift(-1)
    data['Return'] = (data['Future_Close'] - data['Close']) / data['Close']
    data['label'] = (data['Return'] > threshold).astype(int)
    data.dropna(inplace=True)
    return data