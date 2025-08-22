-- Fleet Tracker Database Functions
-- Common functions for the Fleet Tracker system

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Function to calculate distance between two points (in meters)
CREATE OR REPLACE FUNCTION calculate_distance(
    lat1 DOUBLE PRECISION,
    lon1 DOUBLE PRECISION,
    lat2 DOUBLE PRECISION,
    lon2 DOUBLE PRECISION
)
RETURNS DOUBLE PRECISION AS $$
BEGIN
    -- Using PostGIS ST_Distance with geography type
    RETURN ST_Distance(
        ST_GeogFromText('POINT(' || lon1 || ' ' || lat1 || ')'),
        ST_GeogFromText('POINT(' || lon2 || ' ' || lat2 || ')')
    );
END;
$$ LANGUAGE plpgsql;

-- Function to calculate speed based on distance and time
CREATE OR REPLACE FUNCTION calculate_speed(
    distance_meters DOUBLE PRECISION,
    time_seconds INTEGER
)
RETURNS DOUBLE PRECISION AS $$
BEGIN
    -- Return speed in km/h
    IF time_seconds <= 0 THEN
        RETURN 0;
    END IF;
    
    RETURN (distance_meters / time_seconds) * 3.6; -- Convert m/s to km/h
END;
$$ LANGUAGE plpgsql;

-- Function to check if coordinates are valid
CREATE OR REPLACE FUNCTION is_valid_coordinates(
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION
)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN (
        latitude BETWEEN -90 AND 90 AND
        longitude BETWEEN -180 AND 180
    );
END;
$$ LANGUAGE plpgsql;
