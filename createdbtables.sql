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
    DeviceID int  NOT NULL AUTO_INCREMENT,
    PRIMARY KEY (DeviceID)
);

CREATE TABLE LocationHistory (
    Time datetime  NOT NULL,
    TagID int  NOT NULL,
    Distance int  NOT NULL,
    DevicePosition point  NOT NULL,
    Blocked bool  NOT NULL,
    PRIMARY KEY (Time,TagID)
);

CREATE TABLE Registration (
    DeviceID int  NOT NULL,
    Mode int  NOT NULL,
    TagID int  NOT NULL,
    PRIMARY KEY (TagID),
     FOREIGN KEY (TagID) REFERENCES Tag(TagID),
     FOREIGN KEY (DeviceID) REFERENCES Device(DeviceID)
);

