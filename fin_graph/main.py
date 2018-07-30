import fix_yahoo_finance as yf
from pandas_datareader import data

yf.pdr_override()
df = data.get_data_yahoo(tickers = 'GOOG', start = start, end = end)