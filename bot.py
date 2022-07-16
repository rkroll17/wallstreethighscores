from turtle import position
import STAPI as st
import reddit_skimmer as rs
import DATABASE as db

reddit_rq_counter = int

def calc_points(open, close):
    points = int((close - open) / open * 10000)
    return points
    
# send position to database and build/send reply comment
def buy_stock(id, ticker, user):
    ticker_price = st.get_stock_price(ticker)
    if ticker_price == 0:
        reply_text = "Sorry, " + user + ". " + ticker + " is an invalid ticker or is not supported by our bot."
    else:
        try:
            if db.find_user(user) == None:
                db.create_user(user)
            db.open_position(user, ticker, ticker_price, id)
            reply_text = user + ", you have bought " + ticker + " @ $" + str(ticker_price) + "\n\n" + get_stock_summary(ticker)
        except Exception as err:
            print(err)
            reply_text = "You already have a position open for " + ticker
    #print(reply_text)
    rs.reply_submission(id, reply_text)
    
    
# send position to database and build/send reply comment
def sell_stock(id, ticker, user):
    try:
        ticker_price = st.get_stock_price(ticker)
        points = calc_points(db.get_open_price(user, ticker), ticker_price)
        db.close_position(user, ticker, ticker_price, points, id)
        reply_text = user + ", you have sold " + ticker + " @ $" + str(ticker_price) + "\n\n" + get_user_overview(user)
    except Exception as err:
        print(err)
        reply_text = "You do not have a position open for " + ticker
    # print(reply_text)
    rs.reply_submission(id, reply_text)
    

def get_user_overview(user):
    try:
        positions = db.get_positions(user)
        overview = f"{user}\'s account overview:\n\n"
        overview += f"Score: {db.get_score(user)}  \n"
        overview += f"Total # of positions: {db.get_num_positions(user)}  \n"
        overview += f"Total # of open positions: {db.get_num_open_positions(user)}  \n"
        overview += f"Last 10 positions:  \n\n"
        
        ov_table = "|Ticker | Status | Open Price | Close Price| Points|  \n"
        ov_table += ":--:|:--:|:--:|:--:|:--:|  \n"
        i = 0
        for pos in positions:
            if pos[9]:
                status = "Open"
                close_price = "-"
                points = "-"
            else:
                status = "Closed"
                close_price = str(pos[6])
                points = str(pos[7])
            ov_table += f"|{pos[2]} | {status} | {str(pos[4])} | {close_price}| {points}  \n"
            i += 1
            if i > 9:
                break
        #else:
            #overview = overview[:-1]
    except Exception as err:
        print(err)
        overview = "Could not fetch overview for " + user
        return overview
    overview += ov_table
    # print(overview)
    return overview

def get_stock_summary(ticker):
    try:
        profile = st.get_stock_profile(ticker)
        summary = str(profile['name']) + " is a " + str(profile['finnhubIndustry']) + " company and exchanges on the " + str(profile['exchange']) + ". It is based out of " + str(profile['country']) + " and had its initial public offering on " + str(profile['ipo']) + ". For more information visit " + str(profile['weburl'])
    except Exception as err:
        summary = "Sorry, I couldn't find stock info for " + ticker
    return summary
    
def invalid_command(id, command, user):
    print("Sorry ", user, ", ", command, " is not a valid command")
    reply_text = "Sorry " + user + ": " + command + " is not a valid command"
    rs.reply_submission(id, reply_text)
    
    
def read_posts(count):
    reddit_rq_counter = count
    posts = rs.search_parse_command()
    reddit_rq_counter += 1
    
    for p in posts:
        if db.find_id(p[0]):
            print(str(p[0]))
        elif reddit_rq_counter < 59:
            if p[1].upper() == "!BUY":
                buy_stock(p[0], p[2], p[3])
            elif p[1].upper() == "!SELL":
                sell_stock(p[0], p[2], p[3])
            elif p[1].upper() == "!MY_SCORE":
                print(get_user_overview(p[3]))
                rs.reply_submission(p[0], get_user_overview(p[3]))
            else:
                invalid_command(p[0], p[1], p[3])
            reddit_rq_counter += 1
            db.check_post(p[0])
        else:
            return

def get_leaderboard(data):
    lb = "|Place | User | Score|  \n"
    lb += ":--:|:--:|:--:|  \n"
    i = 1
    for d in data:
        lb += f"|{i} | {d[0]} | {d[1]}  \n"
        i += 1
    return lb

def post_daily_leaderboard():
    title = "Today's Top 10 Traders "
    selftext = get_leaderboard(db.daily_high_score())
    id = rs.make_post(title, selftext)
    db.check_post(id)

def post_weekly_leaderboard():
    title = "Last Week's Top 10 Traders "
    selftext = get_leaderboard(db.weekly_high_score())
    id = rs.make_post(title, selftext)
    db.check_post(id)

def post_monthly_leaderboard():
    title = "Last Month's Top 10 Traders "
    selftext = get_leaderboard(db.monthly_high_score())
    id = rs.make_post(title, selftext)
    db.check_post(id)

def post_yearly_leaderboard():
    title = "Last Year's Top 10 Traders "
    selftext = get_leaderboard(db.yearly_high_score())
    id = rs.make_post(title, selftext)
    db.check_post(id)

def post_alltime_leaderboard():
    # remove flairs from old high scorers
    old_flairs = db.active_flares()
    for o in old_flairs:
        db.remove_flare(o[0])
        
    #make the post
    title = "Best Traders of All-Time "
    hs_data = db.high_score()
    selftext = get_leaderboard(hs_data)
    
    #add flairs to new high scorers
    i = 0
    for d in hs_data:
        if i == 0:
            rs.award_best_trader_flair(d[0])
            db.add_flare(d[0])
        elif i == 1:
            rs.award_2nd_best_trader_flair(d[0])
            db.add_flare(d[0])
        elif i == 2:
            rs.award_3rd_best_trader_flair(d[0])
            db.add_flare(d[0])
        else:
            rs.award_top_100_trader_flair(d[0])
            db.add_flare(d[0])
        i += 1
        
    rs.make_post(title, selftext)
            
# read_posts(0)
#get_user_overview("TestUser1")
# post_daily_leaderboard()
# post_weekly_leaderboard()
# post_monthly_leaderboard()
# post_yearly_leaderboard()
# post_alltime_leaderboard()
            
    