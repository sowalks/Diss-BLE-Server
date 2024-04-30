USE Tag_Tracking;


-- For 3NF, while all 3 iBeacon fields have to be a unique combinaiton,
-- each field is only dependent on the TagID.
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

--DevicePosition, although seemingly only depends on logID and time,
--Would depend on tagID when using standard encryption for tracking tags.
--To be extensible to this, it is useful to assume  deviceposition also depends on tagID.
-- This additionally solves if a log marks two entries at the same time but at different positions,
-- If device location was updated in between adding each entry to the log.
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

