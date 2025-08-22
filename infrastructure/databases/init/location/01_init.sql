-- Location Service Database Initialization

-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;

-- Locations table
CREATE TABLE IF NOT EXISTS locations (
    id UUID PRIMARY KEY,
    vehicle_id UUID NOT NULL,
    position GEOMETRY(Point, 4326) NOT NULL,
    speed DECIMAL(5,2),
    heading INTEGER,
    altitude DECIMAL(8,2),
    accuracy DECIMAL(5,2),
    recorded_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Geofence type enum
CREATE TYPE geofence_type AS ENUM ('inclusion', 'exclusion');

-- Geofences table
CREATE TABLE IF NOT EXISTS geofences (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    boundary GEOMETRY(Polygon, 4326) NOT NULL,
    type geofence_type DEFAULT 'inclusion',
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Geofence assignments table
CREATE TABLE IF NOT EXISTS geofence_assignments (
    id UUID PRIMARY KEY,
    geofence_id UUID REFERENCES geofences(id) NOT NULL,
    vehicle_id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_locations_vehicle_time ON locations(vehicle_id, recorded_at);
CREATE INDEX IF NOT EXISTS idx_locations_position ON locations USING GIST(position);
CREATE INDEX IF NOT EXISTS idx_geofences_boundary ON geofences USING GIST(boundary);
CREATE INDEX IF NOT EXISTS idx_geofence_assignments_vehicle ON geofence_assignments(vehicle_id);
CREATE INDEX IF NOT EXISTS idx_geofence_assignments_geofence ON geofence_assignments(geofence_id);
