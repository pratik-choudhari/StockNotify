import yfinance as yf

sym = "COLPAL"
print(type('{0:.2f}'.format(yf.Ticker(sym + ".NS").history(period='1d').iloc[0, 3])))