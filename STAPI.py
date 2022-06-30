import os
import finnhub
import API_key_getter

my_api_key = API_key_getter.get_finn_key()
finnhub_client = finnhub.Client(api_key=my_api_key)

# Get price of stock using ticker as input.
# Finnhub does not update by the minute
def get_stock_price(ticker):
    return finnhub_client.quote(ticker)["c"]