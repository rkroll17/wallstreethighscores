# --------------------------------------
# module is designed to obsficate keys
# it assumes that the files are in the same folder as this module
# ---------------------------------------

finn_filename = 'keys/FinnHubAPIKey.txt' # file that contains finnhub
reddit_filename = 'keys/reddit_key.txt' # file that contains reddit info


def get_finn_key():
    #code gotten from https://github.com/dylburger/reading-api-key-from-file/blob/master/Keeping%20API%20Keys%20Secret.ipynb
    """ Given a filename,
        return the contents of that file
    """
    try:
        with open(finn_filename, 'r') as f:
            # It's assumed our file contains a single line,
            # with our API key
            return f.read().strip()
    except FileNotFoundError:
        print("'%s' file not found" % finn_filename)

#retrives all the content from reddit_key file
#it is assumed that every piece of information is on separate lines
#and in the following order:
#0: subreddit name
#1: reddit_username
#2: reddit_password
#3: client id
#4: secret_key
#5: user_agent
try:
    with open(reddit_filename, 'r') as f:
        info = f.readlines()
except FileNotFoundError:
    print("'%s' file not found" % reddit_filename)

def get_reddit_subreddit():
    return info[0].strip()

def get_reddit_bot_username():
    return info[1].strip()

def get_reddit_bot_password():
    return info[2].strip()

def get_reddit_client_id():
    return info[3].strip()

def get_reddit_secret_key():
    return info[4].strip()

def get_reddit_user_agent():
    return info[5].strip()

