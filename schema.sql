USE plants;
GO

DROP TABLE s_alpha.plant;
DROP TABLE s_alpha.recording_event;
DROP TABLE s_alpha.botanist;
DROP TABLE s_alpha.origin_location;
GO


CREATE TABLE s_alpha.origin_location (
    origin_location_id INT IDENTITY(1,1) NOT NULL,
    longitude FLOAT NOT NULL,
    latitude FLOAT NOT NULL,
    town VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    country_abbreviation VARCHAR(3) NOT NULL,
    continent VARCHAR(100) NOT NULL,
    PRIMARY KEY (origin_location_id)
);
GO


CREATE TABLE s_alpha.plant (
    plant_id INT IDENTITY(1,1) NOT NULL,
    name VARCHAR(100) NOT NULL,
    scientific_name VARCHAR(100) NULL,
    origin_location_id INT NOT NULL,
    image_url VARCHAR(300) NULL,
    PRIMARY KEY (plant_id),
    FOREIGN KEY (origin_location_id) REFERENCES s_alpha.origin_location(origin_location_id)
);
GO

CREATE TABLE s_alpha.botanist (
    botanist_id INT IDENTITY(1,1) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    phone_number VARCHAR(30) NOT NULL,
    PRIMARY KEY (botanist_id)
    );
GO

CREATE TABLE s_alpha.recording_event (
    recording_id INT NOT NULL IDENTITY(1, 1),
    plant_id INT NOT NULL,
    botanist_id INT NOT NULL,
    soil_moisture FLOAT NOT NULL,
    temperature FLOAT NOT NULL,
    recording_taken DATETIME NOT NULL,
    last_watered DATETIME NOT NULL,
    PRIMARY KEY (recording_id),
    FOREIGN KEY (plant_id) REFERENCES s_alpha.plant(plant_id),
    FOREIGN KEY (botanist_id) REFERENCES s_alpha.botanist(botanist_id)
    );
GO
