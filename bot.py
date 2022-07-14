from turtle import position
import STAPI as st
import reddit_skimmer as rs
import DATABASE as db

reddit_rq_counter = int
    
# send position to database and build/send reply comment
def buy_stock(id, ticker, user):
    ticker_price = st.get_stock_price(ticker)
    if ticker_price == 0:
        reply_text = "Sorry, " + user + ". " + ticker + " is an invalid ticker or is not supported by our bot."
    else:
        db.open_position(user, ticker, ticker_price, submissionID=id)
        reply_text = user + ", you have bought " + ticker + " @ $" + str(ticker_price) + "\n\n" + get_stock_summary(ticker)
    print(reply_text)
    #rs.reply_submission(id, reply_text)
    
    
# send position to database and build/send reply comment
def sell_stock(id, ticker, user):
    ticker_price = st.get_stock_price(ticker)
    reply_text = user + ", you have sold " + ticker + " @ $" + str(ticker_price) + "\n\n" + get_stock_summary(ticker)
    print(reply_text)
    #rs.reply_submission(id, reply_text)
    

def get_user_overview(user):
    try:
        positions = db.get_positions(user)
        overview = user + "\'s account overview: \n\n"
        overview += f"Score: {db.get_score(user)}\n"
        overview += f"Total # of positions: {db.get_num_positions(user)}\n"
        overview += f"Total # of open positions: {db.get_num_open_positions(user)}\n"
        overview += "Last 10 positions:\n"
        overview += "Ticker | Status | Open Price | Close Price \n"
        overview += ":--:|:--:|:--:|:--:\n"
        i = 0
        for pos in positions:
            if pos[6] == "Null":
                status = "Open"
                close_price = "-"
            else:
                status = "Closed"
                close_price = str(pos[6])
            overview += f"{pos[2]} | {status} | {str(pos[4])} | {close_price}\n"
            i += 1
            if i > 9:
                break
        else:
            overview = overview[:-1]
    except Exception as err:
        print(err)
        overview = "Could not fetch overview for " + user
    print(overview)
    return overview

def get_stock_summary(ticker):
    profile = st.get_stock_profile(ticker)
    summary = str(profile['name']) + " is a " + str(profile['finnhubIndustry']) + " company and exchanges on the " + str(profile['exchange']) + ". It is based out of " + str(profile['country']) + " and had its initial public offering on " + str(profile['ipo']) + ". For more information visit " + str(profile['weburl'])
    return summary
    
def invalid_command(id, command, user):
    print("Sorry ", user, ", ", command, " is not a valid command")
    reply_text = "Sorry " + user + ": " + command + " is not a valid command"
    #rs.reply_submission(id, reply_text)
    
    
def read_posts(count):
    reddit_rq_counter = count
    posts = rs.search_parse_command()
    reddit_rq_counter += 1
    #posts = [['dfjsld', '!my_score', '', 'john_cena']]
    
    for p in posts:
        if reddit_rq_counter < 60:
            if p[1].upper() == "!BUY":
                buy_stock(p[0], p[2], p[3])
            elif p[1].upper() == "!SELL":
                sell_stock(p[0], p[2], p[3])
            elif p[1].upper() == "!MY_SCORE":
                print(get_user_overview(p[3]))
                #rs.reply_submission(p[0], get_overview(p[3]))
            else:
                invalid_command(p[0], p[1], p[3])
            reddit_rq_counter += 1
        else:
            return
            
#read_posts()
#get_user_overview("TestUser1")
            
    