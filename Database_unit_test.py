import DATABASE as db

# to test:

testUser = "TestUser1"
testTicker = "TEST"

# create_user
try:
  print("Create User: ")
  db.create_user(testUser)
except Exception as error:
  print(error)

# find_user
try:
  print("find user: ")
  print(db.find_user(testUser))
except Exception as error:
  print("Error:")
  print(error)

# find_user_id
try:
  print("User Id: ")
  print(db.find_user_id(testUser))
except Exception as error:
  print("Error:")
  print(error)

# open_position
try:
  print("Open position")
  db.open_position(testUser, testTicker, 100.00)
except Exception as error:
  print("Error:")
  print(error)

# get_positions
try:
  print("Get Positions: ")
  print(db.get_positions(testUser))
except Exception as error:
  print("Error:")
  print(error)

# get_open_positions
try:
  print("Get open positions: ")
  print(db.get_open_positions(testUser))
except Exception as error:
  print("Error:")
  print(error)

# get_open_ticker
try:
  print("Get Open Ticker: ")
  print(db.get_open_ticker(testUser, testTicker))
except Exception as error:
  print("Error:")
  print(error)

# close_position
try:
  print("Closing position")
  db.close_position(testUser, testTicker, 110.00, 10)
except Exception as error:
  print("Error:")
  print(error)

# get_positions
try:
  print("get positions: ")
  print(db.get_positions(testUser))
except Exception as error:
  print("Error:")
  print(error)

# get_open_positions
try:
  print("Get open positions: ")
  print(db.get_open_positions(testUser))
except Exception as error:
  print("Error:")
  print(error)

# get_open_ticker
try:
  print("Get Open Ticker: ")
  print(db.get_open_ticker(testUser, testTicker))
except Exception as error:
  print("Error:")
  print(error)

try:
  print("Get score: ")
  print(db.get_score(testUser))
except Exception as error:
  print("Error:")
  print(error)

# replace_score
try:
  print("replace score: ")
  db.replace_score(testUser, 1000)
except Exception as error:
  print("Error:")
  print(error)

try:
  print("Get score: ")
  print(db.get_score(testUser))
except Exception as error:
  print("Error:")
  print(error)

# add_score
try:
  print("add score: ")
  db.add_score(testUser, 10)
except Exception as error:
  print("Error:")
  print(error)

# get_score
try:
  print("Get score: ")
  print(db.get_score(testUser))
except Exception as error:
  print("Error:")
  print(error)
