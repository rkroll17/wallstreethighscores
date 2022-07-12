# The Cloud SQL Python Connector can be used along with SQLAlchemy using the
# 'creator' argument to 'create_engine'

import os
import pymysql
from google.cloud.sql.connector import Connector, IPTypes
import sqlalchemy
from google.cloud import storage
from keys import database_keys

# authentication to the google cloud
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "keys\google_auth.json"


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

# #connect and run queries
# with pool.connect() as db_conn:
#     results = db_conn.execute("SELECT * FROM Users").fetchall()
#     # show results
#     print(results)
#     for row in results:
#         print(row)



# userHandle = Username, joinDate(optional) = date opt in, score(optional) = score, status(optional) = boolean
# joinDate format: YYYY-MM-DD hh:mm:ss
def create_user(userHandle, joinDate = None, score = None, status = True):
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
        result = db.execute("SELECT UserHandle FROM Users WHERE UserHandle = %s;", (userHandle,)).fetchall()
        if result:
            print("Error: User already exists")
        else:
            db.execute(command + values, escape)


# finds a user with a given user handle. Returns null if not found
def find_user(userHandle):
    command = "SELECT * FROM Users WHERE UserHandle = %s"
    with pool.connect() as db:
        result = db.execute(command, (userHandle,)).fetchall()
        if result:
            return result
        else:
            return Null

# gets a user's internal ID using thier userHandle
def find_user_id(userHandle):
    result = find_user(userHandle)
    if result:
        return result[0][0]
    else:
        return Null

# Opens a position given a userHandle, ticker, and openPrice; with optional openDate, confidence, and submissionID
# openDate format: YYYY-MM-DD hh:mm:ss
# confidence is INT -1 = low, 0 = neutral, 1 = high
def open_position(userHandle, ticker, openPrice,  openDate = None, confidence = None, submissionID = None):

    if get_open_ticker(userHandle, ticker):
        return #that position is already open

    command = "INSERT INTO Positions ( UserID, Ticker, OpenPrice"
    values = "VALUES (" + str(find_user_id(userHandle)) + ", %s, " + str(openPrice)
    escape = [ticker]
    if openDate:
        command += ", OpenDate"
        values += ", '" + openDate + "'"
    if confidence:
        command += ", Confidence"
        values += ", '" + str(confidence) + "'"
    if submissionID:
        command += ", SubmissionID"
        values += ", %s"
        escape += [submissionID]
    
    command += ") "
    values += ")"
    with pool.connect() as db:
        db.execute(command + values, escape)

# Gets all positions of a user, returns Null if none found
def get_positions(userHandle):
    command = "SELECT * FROM Positions WHERE UserID = " + str(find_user(userHandle))
    with pool.connect() as db:
        results = db.execute(command).fetchall()
        if results:
            return results
        else:
            # none found
            return Null

# Gets all open positions of a user, returns Null if none found
def get_open_positions(userHandle):
    command = "SELECT * FROM Positions WHERE UserID = " + str(find_user(userHandle)) + " AND PositionStatus = 1"
    with pool.connect() as db:
        results = db.execute(command).fetchall()
        if results:
            return results
        else:
            # none found
            return Null

#gets open positions with a specific ticker for a user
def get_open_ticker(userHandle, ticker):
    command = "SELECT * FROM Positions WHERE UserID = " + str(find_user_id(userHandle)) + " AND Ticker = %s AND PositionStatus = 1"
    with pool.connect() as db:
        results = db.execute(command, (ticker,)).fetchall()
        if results:
            return results
        else:
            # none found
            return Null

# TO-DO: close_position()

# gets the score of a user given a userHandle
def get_score(userHandle):
    command = "SELECT Score from Users WHERE UserHandle = %s"
    with pool.connect() as db:
        result = db.execute(command, (userHandle,))
        if result:
            return result
        else:
            return Null


#when we're done close the connection
connector.close()