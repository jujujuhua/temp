CREATE TABLE User
(
username varchar(20),
firstname varchar(20),
lastname varchar(20),
password varchar(20),
email varchar(40),
PRIMARY KEY(username)
);

CREATE TABLE Album
(
albumid int AUTO_INCREMENT,
title varchar(50),
created date,
lastupdated date,
username varchar(20),
access varchar(7),
PRIMARY KEY (albumid),
FOREIGN KEY (username) REFERENCES User(username)
);

CREATE TABLE Photo
(
picid varchar(40),
url varchar(255),
format char(3),
date date,
PRIMARY KEY(picid)
);

CREATE TABLE Contain
(
albumid int,
picid varchar(40),
caption varchar(255),
sequencenum int,
PRIMARY KEY(albumid, picid),
FOREIGN KEY(albumid) REFERENCES Album(albumid),
FOREIGN KEY(picid) REFERENCES Photo(picid)
);

CREATE TABLE AlbumAccess 
( 
albumid int, 
username varchar(20),
PRIMARY KEY(albumid, username),
FOREIGN KEY(albumid) REFERENCES Album(albumid),
FOREIGN KEY (username) REFERENCES User(username)
);

