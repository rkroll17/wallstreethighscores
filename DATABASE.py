#see https://github.com/GoogleCloudPlatform/cloud-sql-python-connector for more info

# The Cloud SQL Python Connector can be used along with SQLAlchemy using the
# 'creator' argument to 'create_engine'

import os
import pymysql
from google.cloud.sql.connector import Connector, IPTypes
import sqlalchemy
from google.cloud import storage
from keys import database_keys

# authentication to the google cloud
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "keys/google_auth.json"


# authentication to the SQL database
MYSQL_CONNECTION_NAME = database_keys.MYSQL_CONNECTION_NAME
MYSQL_USER = database_keys.MYSQL_USER
MYSQL_PASS = database_keys.MYSQL_PASS
MYSQL_DB = database_keys.MYSQL_DB

# initialize Connector object
connector = Connector()

# function to return the database connection object
def getconn():
    conn = connector.connect(
        MYSQL_CONNECTION_NAME,
        "pymysql",
        user=MYSQL_USER,
        password=MYSQL_PASS,
        db="WallStreetHighscores"
    )
    return conn

# create connection pool with 'creator' argument to our connection object function
pool = sqlalchemy.create_engine(
    "mysql+pymysql://",
    creator=getconn,
)


# userHandle = Username, joinDate(optional) = date opt in, score(optional) = score, status(optional) = boolean
# joinDate format: YYYY-MM-DD hh:mm:ss
def create_user(userHandle, score = 0, joinDate = None, status = True):
    if (find_user(userHandle)):
        raise Exception("User Already Exists")
    command = "INSERT INTO Users (UserHandle"
    values = " VALUES (%s"
    escape = [userHandle]
    if joinDate:
        command+=", JoinDate"
        values+=", %s"
        escape+=[joinDate]
    
    command+=", Score"
    values+=", %s"
    escape+=[score]

    command+=", Status)"
    if status:
        values+=", '1')"
    else:
        values=+", ' 0')"

    with pool.connect() as db:
        result = db.execute(command + values, escape)
        if not result:
            raise Exception("Invalid input, Database Error")


# finds a user with a given user handle. Returns None if not found
def find_user(userHandle):
    command = "SELECT * FROM Users WHERE UserHandle = %s"
    with pool.connect() as db:
        result = db.execute(command, (userHandle,)).fetchall()
        if result:
            return result
        else:
            return None

# gets a user's internal ID using thier userHandle
def find_user_id(userHandle):
    try:
        result = find_user(userHandle)
    except:
        raise
    if result:
        return result[0][0]
    else:
        return None

# Opens a position given a userHandle, ticker, and openPrice; with optional openDate, confidence, and submissionID
# openDate format: YYYY-MM-DD hh:mm:ss
# confidence is INT -1 = low, 0 = neutral, 1 = high
def open_position(userHandle, ticker, openPrice, submissionID, openDate = None, confidence = None):

    try:
        if get_open_ticker(userHandle, ticker):
            raise Exception("Position already open")
    except:
        raise

    command = "INSERT INTO Positions ( UserID, Ticker, OpenPrice"
    try:
        values = "VALUES (" + str(find_user_id(userHandle)) + ", %s, " + str(openPrice)
    except:
        raise
    escape = [ticker]
    if openDate:
        command += ", OpenDate"
        values += ", '" + openDate + "'"
    if confidence:
        command += ", Confidence"
        values += ", " + str(confidence)
    else:
        command += ", Confidence"
        values += ", 0"
    if submissionID:
        command += ", OpenID"
        values += ", %s"
        escape += [submissionID]
    
    command += ") "
    values += ")"
    with pool.connect() as db:
        result = db.execute(command + values, escape)
        if not result:
            raise Exception("Invalid input, Database error")



# Gets all positions of a user, returns None if none found
def get_positions(userHandle):
    try:
        command = "SELECT * FROM Positions WHERE UserID = " + str(find_user_id(userHandle))
    except:
        raise
    with pool.connect() as db:
        results = db.execute(command).fetchall()
        if results:
            return results
        else:
            # none found
            return None

# Gets number of position of a user. Returns 0 if none found
def get_num_positions(userHandle):
    try:
        command = "SELECT COUNT(PositionID) FROM Positions WHERE UserID = " + str(find_user_id(userHandle))
    except:
        raise
    with pool.connect() as db:
        results = db.execute(command).fetchall()
        if results:
            return results[0][0]
        else:
            # none found
            return 0

# Gets number of open position of a user. Returns 0 if none found
def get_num_open_positions(userHandle):
    try:
        command = "SELECT COUNT(PositionID) FROM Positions WHERE UserID = " + str(find_user_id(userHandle)) + " AND PositionStatus = TRUE"
    except:
        raise
    with pool.connect() as db:
        results = db.execute(command).fetchall()
        if results:
            return results[0][0]
        else:
            # none found
            return 0

# Gets all open positions of a user, returns None if none found
def get_open_positions(userHandle):
    try:
        command = "SELECT * FROM Positions WHERE UserID = " + str(find_user_id(userHandle)) + " AND PositionStatus = 1"
    except:
        raise
    with pool.connect() as db:
        results = db.execute(command).fetchall()
        if results:
            return results
        else:
            # none found
            return None

#gets open positions with a specific ticker for a user
def get_open_ticker(userHandle, ticker):
    try:
        command = "SELECT * FROM Positions WHERE UserID = " + str(find_user_id(userHandle)) + " AND Ticker = %s AND PositionStatus = 1"
    except:
        raise
    with pool.connect() as db:
        results = db.execute(command, (ticker,)).fetchall()
        if results:
            return results
        else:
            # none found
            return None

# gets the open price of an open position
def get_open_price(userHandle, ticker):
    try:
        result = get_open_ticker(userHandle, ticker)
    except:
        raise
    return result[0][4]

def get_open_confidence(userHandle, ticker):
    try:
        result = get_open_ticker(userHandle, ticker)
    except:
        raise
    return result[0][8]

# Closes the position given the userHandle (string), ticker (string), close price (double),
# points (int) the position was worth, and optionally the close date (format: YYYY-MM-DD hh:mm:ss)
def close_position(userHandle, ticker, closePrice, points, submissionID, closeDate = None):
    command = "UPDATE Positions SET ClosePrice = %s, Points = %s, PositionStatus = FALSE"
    escape = [closePrice, points]
    if closeDate:
        command += ", CloseDate = %s"
        escape += [closeDate]
    else:
        command +=", CloseDate = CURRENT_TIMESTAMP"
    if submissionID:
        command += ", CloseID = %s"
        escape += [submissionID]
    try:
        values = " WHERE UserID = " + str(find_user_id(userHandle)) + " AND Ticker = %s AND PositionStatus = 1"
    except:
        raise
    escape += [ticker]
    

    with pool.connect() as db:
        results = db.execute(command+values, escape)
        if not results:
            raise Exception("No affected rows, or input/database error")
        try:
            add_score(userHandle, points)
        except:
            raise

# Replaces a user score when given the user handle (string), and the new score (int)
def replace_score(userHandle, newScore):
    try:
        command = "UPDATE Users Set Score = " + str(newScore) + " WHERE UserHandle = %s"
    except:
        raise
    escape = (userHandle,)
    with pool.connect() as db:
        results = db.execute(command, escape)
        if not results:
            raise Exception("Invalid input/database error")

# Adds to a users score given a user handle (string) and the score (int) to be added.
def add_score(userHandle, addScore):
    try:
        command = "UPDATE Users Set Score = " + str(get_score(userHandle) + addScore) + " WHERE UserHandle = %s"
    except:
        raise
    escape = (userHandle,)
    with pool.connect() as db:
        result = db.execute(command, escape)
        if not result:
            raise Exception("No result/invalid input/database error")

# gets the score of a user given a userHandle
def get_score(userHandle):
    command = "SELECT Score from Users WHERE UserHandle = %s"
    with pool.connect() as db:
        result = db.execute(command, (userHandle,)).fetchall()
        if result:
            return result[0][0]
        else:
            return None

# looks for a given post ID in the database and returns true if found or false if none.
def find_id(submissionID):
    command = "SELECT COUNT(PostID) FROM Posts WHERE PostID = %s"
    escape = (submissionID)
    with pool.connect() as db:
        result = db.execute(command, escape).fetchall()
        if result[0][0] == 0:
            return False
        return True

# Adds a post to the posts database that it has been checked by the bot
def check_post(postID):
    if find_id(postID):
        raise Exception("Already exists")
    command = "INSERT INTO Posts (PostID) VALUES (%s)"
    escape = (postID,)

    with pool.connect() as db:
        try:
            result = db.execute(command, escape)
        except:
            raise


# Gets the daily 10 highscores. Returns as Username, Points
def daily_high_score():
    statement = """SELECT u.UserHandle, SUM(p.Points) AS total 
    FROM Positions AS p 
    JOIN Users AS u ON p.UserID = u.UserID 
    WHERE CloseDate BETWEEN SUBDATE(CURRENT_TIMESTAMP, 1) AND CURRENT_TIMESTAMP 
    GROUP BY p.UserID ORDER BY total DESC LIMIT 10"""

    with pool.connect() as db:
        result = db.execute(statement).fetchall()
        if result:
            return result
        else:
            return None


# Gets the weekly 10 highscores. Returns as Username, Points
def weekly_high_score():
    statement = """SELECT u.UserHandle, SUM(p.Points) AS total 
    FROM Positions AS p 
    JOIN Users AS u ON p.UserID = u.UserID 
    WHERE CloseDate BETWEEN SUBDATE(CURRENT_TIMESTAMP, 7) AND CURRENT_TIMESTAMP 
    GROUP BY p.UserID ORDER BY total DESC LIMIT 10"""

    with pool.connect() as db:
        result = db.execute(statement).fetchall()
        if result:
            return result
        else:
            return None

# Returns the monthly 10 highscores. Returns as Username, Points
def monthly_high_score():
    statement = """SELECT u.UserHandle, SUM(p.Points) AS total 
    FROM Positions AS p 
    JOIN Users AS u ON p.UserID = u.UserID 
    WHERE CloseDate BETWEEN SUBDATE(CURRENT_TIMESTAMP, INTERVAL 1 MONTH) AND CURRENT_TIMESTAMP 
    GROUP BY p.UserID ORDER BY total DESC LIMIT 50"""

    with pool.connect() as db:
        result = db.execute(statement).fetchall()
        if result:
            return result
        else:
            return None

# Returns the yearly 10 highscores. Returns as Username, Points
def yearly_high_score():
    statement = """SELECT u.UserHandle, SUM(p.Points) AS total 
    FROM Positions AS p 
    JOIN Users AS u ON p.UserID = u.UserID 
    WHERE CloseDate BETWEEN SUBDATE(CURRENT_TIMESTAMP, INTERVAL 1 YEAR) AND CURRENT_TIMESTAMP 
    GROUP BY p.UserID ORDER BY total DESC LIMIT 100"""

    with pool.connect() as db:
        result = db.execute(statement).fetchall()
        if result:
            return result
        else:
            return None

# Returns the all time 10 high scores. Returns as Username, Points
def high_score():
    statement = """SELECT u.UserHandle, SUM(p.Points) AS total 
    FROM Positions AS p 
    JOIN Users AS u ON p.UserID = u.UserID
    WHERE PositionStatus = FALSE 
    GROUP BY p.UserID ORDER BY total DESC LIMIT 100"""

    with pool.connect() as db:
        result = db.execute(statement).fetchall()
        if result:
            return result
        else:
            return None

# adds the ActiveFlare flag from a user in the database
def add_flare(userHandle):
    if not find_user(userHandle):
        raise Exception("User not found")
    statement = "UPDATE Users SET ActiveFlare = TRUE WHERE UserHandle = %s"
    escape = (userHandle,)
    with pool.connect() as db:
        result = db.execute(statement, escape)
        if not result:
            raise Exception("Could not update")

# removes the ActiveFlare flag from a user in the database
def remove_flare(userHandle):
    if not find_user(userHandle):
        raise Exception("User not found")
    statement = "UPDATE Users SET ActiveFlare = FALSE WHERE UserHandle = %s"
    escape = (userHandle,)
    with pool.connect() as db:
        result = db.execute(statement, escape)
        if not result:
            raise Exception("Could not update")

# returns a list of users who currenly have the ActiveFlare flag in the database
def active_flares():
    statement = """SELECT UserHandle 
    FROM Users 
    WHERE ActiveFlare = TRUE"""

    with pool.connect() as db:
        result = db.execute(statement).fetchall()
        return result

#when we're done close the connection
connector.close()