import reddit_skimmer as rs
#import DATABASE
import bot
import sched, time

reddit_limiter = 0

s = sched.scheduler(time.time, time.sleep)
def do_something(sc, reddit_limiter): 
    print("Doing stuff...")
    
    
    bot.read_posts(0)
    s.enter(120, 1, bot.post_daily_leaderboard, ())
    s.enter(180, 1, bot.post_weekly_leaderboard, ())
    s.enter(240, 1, bot.post_monthly_leaderboard, ())
    s.enter(270, 1 , bot.post_yearly_leaderboard, ())
    s.enter(180, 1, bot.post_alltime_leaderboard, ())
    #first variable is how long in seconds the scheduler runs
    sc.enter(60, 1, do_something, (sc, reddit_limiter,))

#first variable is how long in seconds the scheduler runs
s.enter(60, 1, do_something, (s, reddit_limiter, ))
s.run()

# s1 = sched.scheduler(time.time, time.sleep)

# #first variable is how long in seconds the scheduler runs
# s1.enter(60, 1, bot.post_alltime_leaderboard, ( ))
# s1.run()
#code sourced from 
# https://stackoverflow.com/questions/474528/what-is-the-best-way-to-repeatedly-execute-a-function-every-x-seconds
