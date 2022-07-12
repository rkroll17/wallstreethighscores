import STAPI as st
import reddit_skimmer as rs

def get_new_posts():
    # posts = rs.search_parse_command()
    pass
    
def buy_stock(id, ticker, user):
    #print(id, " bought ", ticker)
    ticker_price = st.get_stock_price(ticker)
    if ticker_price == 0:
        reply_text = "Sorry, " + user + ". " + ticker + " is an invalid ticker or is not supported by our bot."
    else:
        reply_text = user + ", you have bought " + ticker + " @ $" + str(ticker_price) + "\n\n" + get_stock_summary(ticker)
    print(reply_text)
    #rs.reply_submission(id, reply_text)
    
def sell_stock(id, ticker, user):
    #print(id, " sold ", ticker)
    ticker_price = st.get_stock_price(ticker)
    reply_text = user + ", you have sold " + ticker + " @ $" + str(ticker_price) + "\n\n" + get_stock_summary(ticker)
    print(reply_text)
    #rs.reply_submission(id, reply_text)

def get_user_overview(user):
    overview = user + "\'s overview"
    return overview

def get_stock_summary(ticker):
    profile = st.get_stock_profile(ticker)
    summary = str(profile['name']) + " is a " + str(profile['finnhubIndustry']) + " company and exchanges on the " + str(profile['exchange']) + ". It is based out of " + str(profile['country']) + " and had its initial public offering on " + str(profile['ipo']) + ". For more information visit " + str(profile['weburl'])
    return summary
    
def invalid_command(id, command, user):
    print("Sorry ", user, ", ", command, " is not a valid command")
    reply_text = "Sorry " + user + ": " + command + " is not a valid command"
    #rs.reply_submission(id, reply_text)
    
def read_posts():
    posts = rs.search_parse_command()
    #posts = [['dfjsld', '!my_score', '', 'john_cena']]
    
    for p in posts:
        if p[1].upper() == "!BUY":
            buy_stock(p[0], p[2], p[3])
        elif p[1].upper() == "!SELL":
            sell_stock(p[0], p[2], p[3])
        elif p[1].upper() == "!MY_SCORE":
            print(get_user_overview(p[3]))
            #rs.reply_submission(p[0], get_overview(p[3]))
        else:
            invalid_command(p[0], p[1], p[3])
            
read_posts()
            
    