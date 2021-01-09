## main.py

- Includes telegram bot
- driver program

## gettickerprice.py

- alpha vantage interface
- query stock price

## transactions.py

- interaction with mongodb
- fires queries
- continuously screens stock price with __gettickerprice.py__

## sendalert.py

- send alert message to user on trigger satisfaction