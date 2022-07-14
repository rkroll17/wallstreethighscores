import DATABASE as db


db.open_position("TestUser1", "Test1", 100, "Test")
print(db.find_id("Test"))