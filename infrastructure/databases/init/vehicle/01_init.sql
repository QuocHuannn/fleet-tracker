-- Vehicle Service Database Initialization

-- Vehicle types enum
CREATE TYPE vehicle_type AS ENUM ('car', 'truck', 'van', 'bus', 'motorcycle', 'other');

-- Vehicle status enum
CREATE TYPE vehicle_status AS ENUM ('active', 'inactive', 'maintenance', 'out_of_service');

-- Vehicles table
CREATE TABLE IF NOT EXISTS vehicles (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    license_plate VARCHAR(20) UNIQUE NOT NULL,
    type vehicle_type NOT NULL,
    status vehicle_status DEFAULT 'active',
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Device status enum
CREATE TYPE device_status AS ENUM ('active', 'inactive', 'maintenance', 'disconnected');

-- Devices table
CREATE TABLE IF NOT EXISTS devices (
    id UUID PRIMARY KEY,
    vehicle_id UUID REFERENCES vehicles(id) NOT NULL,
    imei VARCHAR(50) UNIQUE NOT NULL,
    sim_card VARCHAR(50),
    model VARCHAR(100),
    status device_status DEFAULT 'active',
    last_heartbeat TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_vehicles_license_plate ON vehicles(license_plate);
CREATE INDEX IF NOT EXISTS idx_vehicles_status ON vehicles(status);
CREATE INDEX IF NOT EXISTS idx_devices_vehicle_id ON devices(vehicle_id);
CREATE INDEX IF NOT EXISTS idx_devices_imei ON devices(imei);
