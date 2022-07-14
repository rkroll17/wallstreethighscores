import reddit_skimmer as rs
#import DATABASE
# import bot
import sched, time

reddit_limiter = 0

s = sched.scheduler(time.time, time.sleep)
def do_something(sc, reddit_limiter): 
    print("Doing stuff...")
    # do your stuff
    if reddit_limiter < 60:
        reddit_limiter += 1
    else:
        reddit_limiter = 0
    print(reddit_limiter)
    #first variable is how long in seconds the scheduler runs
    sc.enter(60, 1, do_something, (sc, reddit_limiter,))

#first variable is how long in seconds the scheduler runs
s.enter(60, 1, do_something, (s, reddit_limiter, ))
s.run()

#code sourced from 
# https://stackoverflow.com/questions/474528/what-is-the-best-way-to-repeatedly-execute-a-function-every-x-seconds
