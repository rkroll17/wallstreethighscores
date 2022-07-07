import API_key_getter as API
import praw
import re

subreddit_name = API.get_reddit_subreddit()
redd_username = API.get_reddit_bot_username()
redd_password = API.get_reddit_bot_password()
CLIENT_ID = API.get_reddit_client_id()
SECRET_KEY = API.get_reddit_secret_key()
USER_AGENT = API.get_reddit_user_agent()

buy_text = "![bB][uU][yY] \w\w\w\w"
sell_text = "![sS][eE][lL][lL] \w\w\w\w"
regex_buy = re.compile(buy_text)
regex_sell = re.compile(sell_text)

reddit = praw.Reddit(
    client_id= CLIENT_ID,
    client_secret= SECRET_KEY,
    user_agent = USER_AGENT,
    password = redd_password,
    username = redd_username
)

subreddit = reddit.subreddit(subreddit_name)

# retrieves all new submissions
# they are ordered from newest to oldest
# TODO: Need to filter out posts that have already been responded to
def search_parse_command():
    submission_list = []
    command = ''
    for submission in reddit.subreddit(subreddit_name).new():
        submission = reddit.submission(submission.id)
        submission_body = submission.selftext
        submission_title = submission.title
        submission_user = submission.author.name

        # checks for buy command
        command = regex_buy.search(submission_body)
        command_title = regex_buy.search(submission_title)
        
        duplicate_flag = False
        if command_title or command:
            if command and not duplicate_flag:
                text = command[0].split()
                submission_list.append([submission.id, text[0], text[1], submission_user])
                duplicate_flag = True
            if command_title and not duplicate_flag:
                text = command_title[0].split()
                submission_list.append([submission.id, text[0], text[1], submission_user])
                duplicate_flag = True
        # checks for sell command
        command = regex_sell.search(submission_body)
        command_title = regex_sell.search(submission_title)
        duplicate_flag = False
        if command_title or command:
            if command and not duplicate_flag:
                text = command[0].split()
                submission_list.append([submission.id, text[0], text[1], submission_user])
                duplicate_flag = True
            if command_title and not duplicate_flag:
                text = command_title[0].split()
                submission_list.append([submission.id, text[0], text[1], submission_user])
                duplicate_flag = True
    return submission_list

# replys to a specific submission. requires ID and reply text
# does not generate a toast to indicate that action completed successfully
def reply_submission(post_ID, reply_text):
    submission = reddit.submission(post_ID)
    submission.reply(body = reply_text)