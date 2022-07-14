# The Cloud SQL Python Connector can be used along with SQLAlchemy using the
# 'creator' argument to 'create_engine'

import os
import pymysql
from google.cloud.sql.connector import Connector, IPTypes
import sqlalchemy
from google.cloud import storage
from keys import database_keys

# authentication to the google cloud
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "google_auth.json"


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
    
    if score:
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
def open_position(userHandle, ticker, openPrice,  openDate = None, confidence = None, submissionID = None):

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
        values += ", '" + str(confidence) + "'"
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

# Closes the position given the userHandle (string), ticker (string), close price (double),
# points (int) the position was worth, and optionally the close date (format: YYYY-MM-DD hh:mm:ss)
def close_position(userHandle, ticker, closePrice, points, closeDate = None, submissionID = None):
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


#when we're done close the connection
connector.close()