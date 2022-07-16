import bot
import sched, time
from datetime import datetime as dt

reddit_limiter = 0

s = sched.scheduler(time.time, time.sleep)
last_day = 0
last_week = 0
last_month = 0
last_year = 0
# In order to get the events to run at different times
# we wrapped them in a function that then calls said function
def do_something(sc, reddit_limiter, last_day, last_week, last_month, last_year): 
    print("Doing stuff...")
    requests_made = 0
    now = dt.now()
    week_day = dt.today().weekday()
    now_str = now.strftime("%d %m %Y %H %M %S").split()
    day = int(now_str[0])
    month = int(now_str[1])
    year = int(now_str[2])
    hour = int(now_str[3])
    
    # post daily every weekday @ 2PM MST (stock market close)
    if week_day >= 0 and week_day <= 4 and hour >= 14 and day != last_day:
        bot.post_daily_leaderboard()
        requests_made += 1
        last_day = day
    
    # post weekly and all-time every Friday @ 2PM MST
    if week_day == 4 and hour >= 14 and day != last_week:
        bot.post_weekly_leaderboard()
        bot.post_alltime_leaderboard()
        requests_made += 2
        last_week = day
    
    # post monthly every last Friday of the month @ 2PM MST
    if week_day == 4 and day > 22 and month != last_month and hour >= 14:
        bot.post_monthly_leaderboard()
        requests_made += 1
        last_month = month
    
    # post yearly every January 1st @ 2PM MST
    if day == 1 and month == 1 and year != last_year and hour >= 14:
        bot.post_yearly_leaderboard()
        requests_made += 1
        last_year = year
    
    bot.read_posts(requests_made)

    #first variable is how long in seconds the scheduler runs
    sc.enter(60, 1, do_something, (sc, reddit_limiter, last_day, last_week, last_month, last_year,))

#first variable is how long in seconds the scheduler runs
s.enter(60, 1, do_something, (s, reddit_limiter, last_day, last_week, last_month, last_year, ))
s.run()

#code sourced from 
# https://stackoverflow.com/questions/474528/what-is-the-best-way-to-repeatedly-execute-a-function-every-x-seconds
