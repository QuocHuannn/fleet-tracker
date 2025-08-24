-- Location Service Database Schema
-- Fleet Tracker Location and Spatial Operations Service

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- Set up spatial reference systems if needed
-- EPSG:4326 (WGS84) is default for GPS coordinates

-- Location data table for storing GPS coordinates
CREATE TABLE locations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vehicle_id UUID NOT NULL, -- Reference to vehicle in vehicle-service
    device_id UUID, -- Reference to device that sent the location
    position GEOMETRY(Point, 4326) NOT NULL, -- GPS coordinates (longitude, latitude)
    altitude DECIMAL(8,2), -- Altitude in meters
    speed DECIMAL(8,2), -- Speed in km/h
    heading INTEGER, -- Direction in degrees (0-360)
    accuracy DECIMAL(8,2), -- GPS accuracy in meters
    satellites INTEGER, -- Number of satellites used
    hdop DECIMAL(4,2), -- Horizontal dilution of precision
    odometer DECIMAL(12,2), -- Odometer reading
    fuel_level DECIMAL(5,2), -- Fuel level percentage (0-100)
    engine_status VARCHAR(20), -- on, off, idle
    battery_voltage DECIMAL(5,2), -- Vehicle battery voltage
    temperature DECIMAL(6,2), -- Temperature reading if available
    address TEXT, -- Reverse geocoded address
    raw_data JSONB, -- Raw GPS data from device
    recorded_at TIMESTAMP WITH TIME ZONE NOT NULL, -- When GPS was recorded
    received_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- When received by service
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Current location cache for real-time queries (one record per vehicle)
CREATE TABLE current_locations (
    vehicle_id UUID PRIMARY KEY, -- Reference to vehicle in vehicle-service
    position GEOMETRY(Point, 4326) NOT NULL,
    speed DECIMAL(8,2),
    heading INTEGER,
    address TEXT,
    last_update TIMESTAMP WITH TIME ZONE NOT NULL,
    is_online BOOLEAN DEFAULT TRUE,
    signal_quality INTEGER, -- 0-100
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Geofences for spatial monitoring
CREATE TABLE geofences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    boundary GEOMETRY(Polygon, 4326) NOT NULL, -- Polygon defining the geofence
    type VARCHAR(20) DEFAULT 'inclusion', -- inclusion, exclusion
    buffer_distance DECIMAL(10,2) DEFAULT 0, -- Buffer in meters
    is_active BOOLEAN DEFAULT TRUE,
    alert_on_entry BOOLEAN DEFAULT TRUE,
    alert_on_exit BOOLEAN DEFAULT TRUE,
    max_speed DECIMAL(8,2), -- Speed limit within geofence
    created_by UUID, -- User who created the geofence
    tags JSONB DEFAULT '[]', -- Tags for categorization
    schedule JSONB, -- Time-based activation schedule
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Geofence violations tracking
CREATE TABLE geofence_violations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vehicle_id UUID NOT NULL,
    geofence_id UUID NOT NULL REFERENCES geofences(id) ON DELETE CASCADE,
    violation_type VARCHAR(20) NOT NULL, -- entry, exit, speed_violation
    location_id UUID REFERENCES locations(id),
    position GEOMETRY(Point, 4326) NOT NULL,
    speed DECIMAL(8,2),
    duration_seconds INTEGER, -- How long the violation lasted
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_by UUID, -- User who acknowledged
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    severity VARCHAR(20) DEFAULT 'medium', -- low, medium, high, critical
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Trip detection and management
CREATE TABLE trips (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vehicle_id UUID NOT NULL,
    start_location_id UUID REFERENCES locations(id),
    end_location_id UUID REFERENCES locations(id),
    start_position GEOMETRY(Point, 4326) NOT NULL,
    end_position GEOMETRY(Point, 4326),
    start_address TEXT,
    end_address TEXT,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER,
    distance_km DECIMAL(10,3),
    max_speed DECIMAL(8,2),
    avg_speed DECIMAL(8,2),
    idle_time_seconds INTEGER,
    fuel_consumed DECIMAL(8,2),
    driver_id UUID, -- Driver during this trip
    status VARCHAR(20) DEFAULT 'active', -- active, completed, cancelled
    route_polyline TEXT, -- Encoded polyline of the route
    stop_count INTEGER DEFAULT 0,
    harsh_acceleration_count INTEGER DEFAULT 0,
    harsh_braking_count INTEGER DEFAULT 0,
    speeding_duration_seconds INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Stops within trips
CREATE TABLE trip_stops (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    trip_id UUID NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    position GEOMETRY(Point, 4326) NOT NULL,
    address TEXT,
    arrival_time TIMESTAMP WITH TIME ZONE NOT NULL,
    departure_time TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER,
    stop_reason VARCHAR(50), -- scheduled, unscheduled, fuel, maintenance, delivery
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Driving behavior analysis
CREATE TABLE driving_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vehicle_id UUID NOT NULL,
    trip_id UUID REFERENCES trips(id),
    location_id UUID REFERENCES locations(id),
    event_type VARCHAR(50) NOT NULL, -- harsh_acceleration, harsh_braking, speeding, rapid_cornering
    position GEOMETRY(Point, 4326) NOT NULL,
    speed_before DECIMAL(8,2),
    speed_after DECIMAL(8,2),
    acceleration DECIMAL(6,3), -- m/s²
    severity VARCHAR(20) DEFAULT 'medium', -- low, medium, high
    duration_seconds INTEGER,
    threshold_value DECIMAL(8,3), -- The threshold that was exceeded
    actual_value DECIMAL(8,3), -- The actual measured value
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Route optimization and planning
CREATE TABLE routes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    waypoints GEOMETRY(MultiPoint, 4326) NOT NULL,
    route_polyline TEXT, -- Encoded polyline
    estimated_distance_km DECIMAL(10,3),
    estimated_duration_seconds INTEGER,
    vehicle_types TEXT[], -- Which vehicle types can use this route
    is_optimized BOOLEAN DEFAULT FALSE,
    optimization_date TIMESTAMP WITH TIME ZONE,
    created_by UUID,
    tags JSONB DEFAULT '[]',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Spatial indexes for performance
CREATE INDEX idx_locations_vehicle_time ON locations(vehicle_id, recorded_at DESC);
CREATE INDEX idx_locations_position ON locations USING GIST(position);
CREATE INDEX idx_locations_recorded_at ON locations(recorded_at);

CREATE INDEX idx_current_locations_position ON current_locations USING GIST(position);
CREATE INDEX idx_current_locations_updated ON current_locations(last_update);

CREATE INDEX idx_geofences_boundary ON geofences USING GIST(boundary);
CREATE INDEX idx_geofences_active ON geofences(is_active);

CREATE INDEX idx_geofence_violations_vehicle ON geofence_violations(vehicle_id);
CREATE INDEX idx_geofence_violations_geofence ON geofence_violations(geofence_id);
CREATE INDEX idx_geofence_violations_created ON geofence_violations(created_at);

CREATE INDEX idx_trips_vehicle_id ON trips(vehicle_id);
CREATE INDEX idx_trips_start_time ON trips(start_time);
CREATE INDEX idx_trips_status ON trips(status);

CREATE INDEX idx_trip_stops_trip_id ON trip_stops(trip_id);
CREATE INDEX idx_driving_events_vehicle_trip ON driving_events(vehicle_id, trip_id);
CREATE INDEX idx_driving_events_type ON driving_events(event_type);

CREATE INDEX idx_routes_waypoints ON routes USING GIST(waypoints);

-- Updated at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE 'plpgsql';

-- Apply updated_at triggers
CREATE TRIGGER update_current_locations_updated_at BEFORE UPDATE ON current_locations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_geofences_updated_at BEFORE UPDATE ON geofences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_trips_updated_at BEFORE UPDATE ON trips
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_routes_updated_at BEFORE UPDATE ON routes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to update current location from new GPS data
CREATE OR REPLACE FUNCTION update_current_location()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO current_locations (
        vehicle_id, 
        position, 
        speed, 
        heading, 
        address, 
        last_update,
        is_online,
        signal_quality
    ) VALUES (
        NEW.vehicle_id,
        NEW.position,
        NEW.speed,
        NEW.heading,
        NEW.address,
        NEW.recorded_at,
        TRUE,
        CASE 
            WHEN NEW.satellites >= 8 THEN 95
            WHEN NEW.satellites >= 6 THEN 80
            WHEN NEW.satellites >= 4 THEN 60
            ELSE 30
        END
    )
    ON CONFLICT (vehicle_id) DO UPDATE SET
        position = EXCLUDED.position,
        speed = EXCLUDED.speed,
        heading = EXCLUDED.heading,
        address = EXCLUDED.address,
        last_update = EXCLUDED.last_update,
        is_online = EXCLUDED.is_online,
        signal_quality = EXCLUDED.signal_quality,
        updated_at = CURRENT_TIMESTAMP;
    
    RETURN NEW;
END;
$$ LANGUAGE 'plpgsql';

-- Trigger to update current location when new GPS data arrives
CREATE TRIGGER update_current_location_trigger
    AFTER INSERT ON locations
    FOR EACH ROW
    EXECUTE FUNCTION update_current_location();

-- Function to check geofence violations
CREATE OR REPLACE FUNCTION check_geofence_violations(vehicle_uuid UUID, location_point GEOMETRY)
RETURNS VOID AS $$
DECLARE
    geofence_record RECORD;
    is_inside BOOLEAN;
    prev_location GEOMETRY;
    was_inside BOOLEAN;
BEGIN
    -- Get previous location for comparison
    SELECT position INTO prev_location
    FROM current_locations
    WHERE vehicle_id = vehicle_uuid;
    
    -- Check each active geofence
    FOR geofence_record IN 
        SELECT id, boundary, type, alert_on_entry, alert_on_exit
        FROM geofences 
        WHERE is_active = TRUE
    LOOP
        -- Check if vehicle is inside geofence
        is_inside := ST_Within(location_point, geofence_record.boundary);
        
        -- Check if vehicle was inside previously
        IF prev_location IS NOT NULL THEN
            was_inside := ST_Within(prev_location, geofence_record.boundary);
            
            -- Entry violation
            IF is_inside AND NOT was_inside AND geofence_record.alert_on_entry THEN
                INSERT INTO geofence_violations (
                    vehicle_id, geofence_id, violation_type, position
                ) VALUES (
                    vehicle_uuid, geofence_record.id, 'entry', location_point
                );
            END IF;
            
            -- Exit violation
            IF NOT is_inside AND was_inside AND geofence_record.alert_on_exit THEN
                INSERT INTO geofence_violations (
                    vehicle_id, geofence_id, violation_type, position
                ) VALUES (
                    vehicle_uuid, geofence_record.id, 'exit', location_point
                );
            END IF;
        END IF;
    END LOOP;
END;
$$ LANGUAGE 'plpgsql';

-- Function to calculate distance between two points
CREATE OR REPLACE FUNCTION calculate_distance_km(point1 GEOMETRY, point2 GEOMETRY)
RETURNS DECIMAL AS $$
BEGIN
    RETURN ST_DistanceSphere(point1, point2) / 1000.0;
END;
$$ LANGUAGE 'plpgsql';

-- Function to get vehicles within radius
CREATE OR REPLACE FUNCTION get_vehicles_within_radius(
    center_lat DECIMAL, 
    center_lng DECIMAL, 
    radius_km DECIMAL
)
RETURNS TABLE(vehicle_id UUID, distance_km DECIMAL) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        cl.vehicle_id,
        (ST_DistanceSphere(
            cl.position, 
            ST_SetSRID(ST_MakePoint(center_lng, center_lat), 4326)
        ) / 1000.0)::DECIMAL as distance_km
    FROM current_locations cl
    WHERE ST_DWithin(
        cl.position::geography,
        ST_SetSRID(ST_MakePoint(center_lng, center_lat), 4326)::geography,
        radius_km * 1000
    )
    ORDER BY distance_km;
END;
$$ LANGUAGE 'plpgsql';