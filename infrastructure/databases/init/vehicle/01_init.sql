-- Vehicle Service Database Schema
-- Fleet Tracker Vehicle Management Service

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Vehicle types enum
CREATE TYPE vehicle_type AS ENUM ('car', 'truck', 'motorcycle', 'van', 'bus', 'other');
CREATE TYPE vehicle_status AS ENUM ('active', 'inactive', 'maintenance', 'decommissioned');
CREATE TYPE device_status AS ENUM ('active', 'inactive', 'faulty', 'offline');

-- Vehicles table
CREATE TABLE vehicles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    license_plate VARCHAR(20) UNIQUE NOT NULL,
    vin VARCHAR(17) UNIQUE,
    make VARCHAR(100),
    model VARCHAR(100),
    year INTEGER,
    color VARCHAR(50),
    type vehicle_type NOT NULL DEFAULT 'car',
    status vehicle_status NOT NULL DEFAULT 'active',
    fuel_type VARCHAR(50), -- gasoline, diesel, electric, hybrid
    fuel_capacity DECIMAL(8,2),
    max_speed INTEGER,
    owner_id UUID, -- Reference to user who owns this vehicle
    driver_id UUID, -- Reference to currently assigned driver
    fleet_id UUID, -- Reference to fleet group
    insurance_number VARCHAR(100),
    insurance_expires_at DATE,
    registration_expires_at DATE,
    purchase_date DATE,
    purchase_price DECIMAL(12,2),
    odometer_reading INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Devices table (GPS trackers)
CREATE TABLE devices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    imei VARCHAR(50) UNIQUE NOT NULL,
    serial_number VARCHAR(100),
    manufacturer VARCHAR(100),
    model VARCHAR(100),
    firmware_version VARCHAR(50),
    sim_card VARCHAR(50),
    phone_number VARCHAR(20),
    status device_status NOT NULL DEFAULT 'active',
    vehicle_id UUID REFERENCES vehicles(id) ON DELETE SET NULL,
    installation_date DATE,
    last_heartbeat TIMESTAMP WITH TIME ZONE,
    battery_level INTEGER, -- 0-100
    signal_strength INTEGER, -- 0-100
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Vehicle assignments (driver assignments history)
CREATE TABLE vehicle_assignments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vehicle_id UUID NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    user_id UUID NOT NULL, -- Driver user ID from auth service
    role VARCHAR(50) NOT NULL DEFAULT 'driver', -- driver, mechanic, inspector
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    unassigned_at TIMESTAMP WITH TIME ZONE,
    assigned_by UUID, -- User who made the assignment
    notes TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Maintenance records
CREATE TABLE maintenance_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vehicle_id UUID NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL, -- scheduled, repair, inspection, service
    description TEXT NOT NULL,
    scheduled_date DATE,
    completed_date DATE,
    cost DECIMAL(10,2),
    odometer_reading INTEGER,
    service_provider VARCHAR(255),
    technician_name VARCHAR(255),
    parts_used TEXT,
    status VARCHAR(20) DEFAULT 'scheduled', -- scheduled, in_progress, completed, cancelled
    next_service_date DATE,
    next_service_odometer INTEGER,
    notes TEXT,
    attachments JSONB DEFAULT '[]', -- File references
    created_by UUID, -- User who created the record
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Fleet groups for organizing vehicles
CREATE TABLE fleets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    manager_id UUID, -- Fleet manager user ID
    department VARCHAR(100),
    location VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Fuel records
CREATE TABLE fuel_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vehicle_id UUID NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    fuel_type VARCHAR(50) NOT NULL,
    quantity DECIMAL(8,2) NOT NULL, -- Liters or gallons
    cost DECIMAL(10,2) NOT NULL,
    price_per_unit DECIMAL(8,4),
    odometer_reading INTEGER,
    location VARCHAR(255),
    station_name VARCHAR(255),
    receipt_number VARCHAR(100),
    filled_by UUID, -- User who filled the fuel
    filled_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Vehicle status history for tracking changes
CREATE TABLE vehicle_status_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vehicle_id UUID NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    old_status vehicle_status,
    new_status vehicle_status NOT NULL,
    reason TEXT,
    changed_by UUID, -- User who changed the status
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_vehicles_license_plate ON vehicles(license_plate);
CREATE INDEX idx_vehicles_status ON vehicles(status);
CREATE INDEX idx_vehicles_type ON vehicles(type);
CREATE INDEX idx_vehicles_owner_id ON vehicles(owner_id);
CREATE INDEX idx_vehicles_driver_id ON vehicles(driver_id);
CREATE INDEX idx_vehicles_fleet_id ON vehicles(fleet_id);
CREATE INDEX idx_devices_imei ON devices(imei);
CREATE INDEX idx_devices_vehicle_id ON devices(vehicle_id);
CREATE INDEX idx_devices_status ON devices(status);
CREATE INDEX idx_vehicle_assignments_vehicle_id ON vehicle_assignments(vehicle_id);
CREATE INDEX idx_vehicle_assignments_user_id ON vehicle_assignments(user_id);
CREATE INDEX idx_vehicle_assignments_active ON vehicle_assignments(is_active);
CREATE INDEX idx_maintenance_records_vehicle_id ON maintenance_records(vehicle_id);
CREATE INDEX idx_maintenance_records_status ON maintenance_records(status);
CREATE INDEX idx_maintenance_records_scheduled_date ON maintenance_records(scheduled_date);
CREATE INDEX idx_fuel_records_vehicle_id ON fuel_records(vehicle_id);
CREATE INDEX idx_fuel_records_filled_at ON fuel_records(filled_at);
CREATE INDEX idx_vehicle_status_history_vehicle_id ON vehicle_status_history(vehicle_id);

-- Updated at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE 'plpgsql';

-- Apply updated_at triggers
CREATE TRIGGER update_vehicles_updated_at BEFORE UPDATE ON vehicles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_devices_updated_at BEFORE UPDATE ON devices
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_maintenance_records_updated_at BEFORE UPDATE ON maintenance_records
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_fleets_updated_at BEFORE UPDATE ON fleets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Status change trigger to log history
CREATE OR REPLACE FUNCTION log_vehicle_status_change()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.status IS DISTINCT FROM NEW.status THEN
        INSERT INTO vehicle_status_history (vehicle_id, old_status, new_status, changed_at)
        VALUES (NEW.id, OLD.status, NEW.status, CURRENT_TIMESTAMP);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE 'plpgsql';

CREATE TRIGGER vehicle_status_change_trigger AFTER UPDATE ON vehicles
    FOR EACH ROW EXECUTE FUNCTION log_vehicle_status_change();

-- Function to get vehicle utilization stats
CREATE OR REPLACE FUNCTION get_vehicle_stats(vehicle_uuid UUID)
RETURNS JSON AS $$
DECLARE
    result JSON;
BEGIN
    SELECT json_build_object(
        'total_maintenance_cost', COALESCE(SUM(mr.cost), 0),
        'total_fuel_cost', COALESCE(SUM(fr.cost), 0),
        'total_fuel_quantity', COALESCE(SUM(fr.quantity), 0),
        'maintenance_count', COUNT(DISTINCT mr.id),
        'fuel_records_count', COUNT(DISTINCT fr.id)
    ) INTO result
    FROM vehicles v
    LEFT JOIN maintenance_records mr ON v.id = mr.vehicle_id
    LEFT JOIN fuel_records fr ON v.id = fr.vehicle_id
    WHERE v.id = vehicle_uuid;
    
    RETURN result;
END;
$$ LANGUAGE 'plpgsql';

-- Insert default fleet
INSERT INTO fleets (name, description) VALUES 
    ('Default Fleet', 'Default fleet for unassigned vehicles');