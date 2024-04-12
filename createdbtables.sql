USE Tag_Tracking;

CREATE TABLE Tag (
    UUID BINARY(16)  NOT NULL,
    Major BINARY(2)  NOT NULL,
    Minor BINARY(2)  NOT NULL,
    TagID int  NOT NULL AUTO_INCREMENT,
    UNIQUE INDEX TagFields (Major,Minor,UUID),
    PRIMARY KEY (TagID)
);

CREATE TABLE Device (
    DeviceID BINARY(16)  NOT NULL,
    PRIMARY KEY (DeviceID)
);

CREATE TABLE LocationHistory (
    TagID int  NOT NULL,
    Time datetime NOT NULL,
    Distance double  NOT NULL,
    DevicePosition point  NOT NULL,
    LogID BIGINT  NOT NULL,
    PRIMARY KEY (LogID,TagID,Time)
);

CREATE TABLE Registration (
    DeviceID BINARY(16)  NOT NULL,
    Mode int  NOT NULL,
    TagID int  NOT NULL,
    PRIMARY KEY (TagID),
     FOREIGN KEY (TagID) REFERENCES Tag(TagID),
     FOREIGN KEY (DeviceID) REFERENCES Device(DeviceID)
);

CREATE VIEW AllBlocked AS 
SELECT blocked.LogID, alltag.TagID FROM LocationHistory alltag
INNER JOIN LocationHistory blocked ON alltag.LogID = blocked.LogID
INNER JOIN Registration r ON r.TagID = blocked.TagID
WHERE r.Mode = 0;
SELECT * FROM ALLBlocked;

