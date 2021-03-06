CREATE DATABASE WallStreetHighscores;

CREATE TABLE IF NOT EXISTS Users (
  UserID INT NOT NULL AUTO_INCREMENT,
  UserHandle VARCHAR(20) NOT NULL,
  JoinDate DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  Score BIGINT,
  Status BOOL,
  ActiveFlare BOOL DEFAULT FALSE,
  PRIMARY KEY (UserID)
);

CREATE TABLE IF NOT EXISTS Positions (
  PositionID INT NOT NULL AUTO_INCREMENT,
  UserID INT NOT NULL,
  Ticker VARCHAR(5) NOT NULL,
  OpenDate DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  OpenPrice DOUBLE(10,4) NOT NULL,
  CloseDate DATETIME,
  ClosePrice DOUBLE(10,4),
  Points BIGINT,
  Confidence INT(1),
  PositionStatus BOOL NOT NULL DEFAULT TRUE,
  OpenID VARCHAR(6),
  CloseID VARCHAR(6),
  PRIMARY KEY (PositionID),
  FOREIGN KEY (UserID) REFERENCES Users(UserID)
);

CREATE TABLE IF NOT EXISTS Posts (
  PostID VARCHAR(6) NOT NULL,
  Checked BOOL NOT NULL DEFAULT TRUE,
  CheckedDate DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (PostID)
)