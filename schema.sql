USE plants;
go
DROP TABLE s_alpha.recording_event;


CREATE TABLE s_alpha.recording_event (
    recording_id INT NOT NULL IDENTITY(1, 1) PRIMARY KEY,
    plant_id INT NOT NULL,
    botanist_id INT NOT NULL,
    soil_moisture FLOAT NOT NULL,
    temperature FLOAT NOT NULL,
    recording_taken DATETIME NOT NULL,
    last_watered DATETIME NOT NULL
    );

go

-- INSERT INTO s_alpha.recording_event
--     (plant_id, botanist_id, soil_moisture, temperature, recording_taken, last_watered) 
-- VALUES 
--     ();

-- go