-- Notification Service Database Schema
-- Fleet Tracker Notification and Alert Management Service

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Alert severity and status enums
CREATE TYPE alert_severity AS ENUM ('low', 'medium', 'high', 'critical');
CREATE TYPE alert_status AS ENUM ('active', 'acknowledged', 'resolved', 'dismissed');
CREATE TYPE notification_channel AS ENUM ('websocket', 'email', 'sms', 'push');
CREATE TYPE notification_status AS ENUM ('pending', 'sent', 'delivered', 'failed', 'read');

-- Main alerts table
CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vehicle_id UUID NOT NULL, -- Reference to vehicle in vehicle-service
    device_id UUID, -- Reference to device that triggered the alert
    type VARCHAR(50) NOT NULL, -- geofence_violation, speed_violation, device_offline, etc.
    category VARCHAR(50) NOT NULL, -- safety, security, maintenance, operational
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    severity alert_severity DEFAULT 'medium',
    status alert_status DEFAULT 'active',
    source_service VARCHAR(50), -- Which service created the alert
    source_event_id UUID, -- Reference to the original event
    latitude DECIMAL(10, 8), -- Latitude coordinate
    longitude DECIMAL(11, 8), -- Longitude coordinate
    address TEXT, -- Human-readable address
    metadata JSONB DEFAULT '{}', -- Additional alert-specific data
    acknowledged_by UUID, -- User who acknowledged the alert
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    resolved_by UUID, -- User who resolved the alert
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolution_notes TEXT,
    auto_resolve BOOLEAN DEFAULT FALSE, -- Whether alert can be auto-resolved
    auto_resolve_timeout INTEGER, -- Minutes after which to auto-resolve
    escalation_level INTEGER DEFAULT 0, -- 0=no escalation, 1+=escalation level
    escalated_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE, -- When alert expires if not resolved
    tags JSONB DEFAULT '[]', -- Tags for categorization and filtering
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Notification rules for determining who gets notified
CREATE TABLE notification_rules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Rule conditions (all must match)
    alert_types TEXT[], -- Which alert types trigger this rule
    alert_categories TEXT[], -- Which alert categories
    severity_levels alert_severity[], -- Which severity levels
    vehicle_ids UUID[], -- Specific vehicles (empty = all vehicles)
    user_ids UUID[], -- Specific users (empty = all users with permission)
    geofence_ids UUID[], -- Alerts from specific geofences
    
    -- Time conditions
    active_hours JSONB, -- When rule is active (e.g., {"start": "09:00", "end": "17:00"})
    active_days INTEGER[], -- Days of week (0=Sunday, 6=Saturday)
    timezone VARCHAR(50) DEFAULT 'UTC',
    
    -- Notification settings
    channels notification_channel[] NOT NULL, -- How to notify
    delay_minutes INTEGER DEFAULT 0, -- Delay before sending notification
    repeat_interval_minutes INTEGER, -- Repeat notification every X minutes
    max_repeats INTEGER DEFAULT 0, -- Maximum number of repeats
    
    -- Escalation
    escalate_after_minutes INTEGER, -- Escalate if not acknowledged
    escalation_user_ids UUID[], -- Users to escalate to
    escalation_channels notification_channel[],
    
    priority INTEGER DEFAULT 1, -- Rule priority (higher = more important)
    created_by UUID NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Notification history
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    alert_id UUID NOT NULL REFERENCES alerts(id) ON DELETE CASCADE,
    rule_id UUID REFERENCES notification_rules(id) ON DELETE SET NULL,
    recipient_user_id UUID, -- User who should receive notification
    channel notification_channel NOT NULL,
    recipient_address TEXT NOT NULL, -- Email, phone, device token, etc.
    subject VARCHAR(500),
    message TEXT NOT NULL,
    status notification_status DEFAULT 'pending',
    
    -- Delivery tracking
    sent_at TIMESTAMP WITH TIME ZONE,
    delivered_at TIMESTAMP WITH TIME ZONE,
    read_at TIMESTAMP WITH TIME ZONE,
    failed_at TIMESTAMP WITH TIME ZONE,
    failure_reason TEXT,
    
    -- Retry logic
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    next_retry_at TIMESTAMP WITH TIME ZONE,
    
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- WebSocket connections tracking
CREATE TABLE websocket_connections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL, -- Connected user
    connection_id VARCHAR(255) NOT NULL, -- WebSocket connection identifier
    client_info JSONB DEFAULT '{}', -- Browser, device info
    ip_address INET,
    connected_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Subscription filters
    subscribed_vehicles UUID[], -- Which vehicles user wants updates for
    subscribed_alert_types TEXT[], -- Which alert types
    subscribed_severities alert_severity[], -- Which severities
    
    UNIQUE(user_id, connection_id)
);

-- Notification templates for different types of alerts
CREATE TABLE notification_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    alert_type VARCHAR(50) NOT NULL,
    channel notification_channel NOT NULL,
    language VARCHAR(5) DEFAULT 'en',
    
    subject_template TEXT, -- Template for subject line
    message_template TEXT NOT NULL, -- Template for message body
    
    -- Template variables available: {vehicle_name}, {alert_message}, {severity}, etc.
    variables JSONB DEFAULT '[]', -- List of available template variables
    
    is_default BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_by UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(alert_type, channel, language, is_default) WHERE is_default = TRUE
);

-- Alert statistics and metrics
CREATE TABLE alert_statistics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    date DATE NOT NULL,
    vehicle_id UUID,
    alert_type VARCHAR(50),
    alert_category VARCHAR(50),
    severity alert_severity,
    
    total_count INTEGER DEFAULT 0,
    resolved_count INTEGER DEFAULT 0,
    average_resolution_time_minutes INTEGER,
    escalated_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(date, vehicle_id, alert_type, alert_category, severity)
);

-- Indexes for performance
CREATE INDEX idx_alerts_vehicle_id ON alerts(vehicle_id);
CREATE INDEX idx_alerts_type ON alerts(type);
CREATE INDEX idx_alerts_category ON alerts(category);
CREATE INDEX idx_alerts_severity ON alerts(severity);
CREATE INDEX idx_alerts_status ON alerts(status);
CREATE INDEX idx_alerts_created_at ON alerts(created_at);
CREATE INDEX idx_alerts_latitude ON alerts(latitude) WHERE latitude IS NOT NULL;
CREATE INDEX idx_alerts_longitude ON alerts(longitude) WHERE longitude IS NOT NULL;

CREATE INDEX idx_notification_rules_active ON notification_rules(is_active);
CREATE INDEX idx_notification_rules_alert_types ON notification_rules USING GIN(alert_types);
CREATE INDEX idx_notification_rules_vehicle_ids ON notification_rules USING GIN(vehicle_ids);

CREATE INDEX idx_notifications_alert_id ON notifications(alert_id);
CREATE INDEX idx_notifications_recipient ON notifications(recipient_user_id);
CREATE INDEX idx_notifications_status ON notifications(status);
CREATE INDEX idx_notifications_created_at ON notifications(created_at);

CREATE INDEX idx_websocket_connections_user_id ON websocket_connections(user_id);
CREATE INDEX idx_websocket_connections_active ON websocket_connections(is_active);
CREATE INDEX idx_websocket_connections_activity ON websocket_connections(last_activity);

CREATE INDEX idx_notification_templates_type_channel ON notification_templates(alert_type, channel);

CREATE INDEX idx_alert_statistics_date ON alert_statistics(date);
CREATE INDEX idx_alert_statistics_vehicle_id ON alert_statistics(vehicle_id);

-- Updated at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE 'plpgsql';

-- Apply updated_at triggers
CREATE TRIGGER update_alerts_updated_at BEFORE UPDATE ON alerts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_notification_rules_updated_at BEFORE UPDATE ON notification_rules
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_notifications_updated_at BEFORE UPDATE ON notifications
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_notification_templates_updated_at BEFORE UPDATE ON notification_templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_alert_statistics_updated_at BEFORE UPDATE ON alert_statistics
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to auto-acknowledge alerts after timeout
CREATE OR REPLACE FUNCTION auto_resolve_alerts()
RETURNS INTEGER AS $$
DECLARE
    resolved_count INTEGER;
BEGIN
    UPDATE alerts 
    SET 
        status = 'resolved',
        resolved_at = CURRENT_TIMESTAMP,
        resolution_notes = 'Auto-resolved due to timeout'
    WHERE 
        status = 'active' 
        AND auto_resolve = TRUE 
        AND auto_resolve_timeout IS NOT NULL
        AND created_at + (auto_resolve_timeout || ' minutes')::INTERVAL < CURRENT_TIMESTAMP;
    
    GET DIAGNOSTICS resolved_count = ROW_COUNT;
    RETURN resolved_count;
END;
$$ LANGUAGE 'plpgsql';

-- Function to clean old websocket connections
CREATE OR REPLACE FUNCTION cleanup_inactive_connections()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM websocket_connections 
    WHERE 
        is_active = FALSE 
        OR last_activity < CURRENT_TIMESTAMP - INTERVAL '1 hour';
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE 'plpgsql';

-- Function to update alert statistics
CREATE OR REPLACE FUNCTION update_alert_statistics_for_date(target_date DATE)
RETURNS VOID AS $$
BEGIN
    INSERT INTO alert_statistics (
        date, vehicle_id, alert_type, alert_category, severity,
        total_count, resolved_count, 
        average_resolution_time_minutes, escalated_count
    )
    SELECT 
        target_date,
        vehicle_id,
        type,
        category,
        severity,
        COUNT(*) as total_count,
        COUNT(*) FILTER (WHERE status IN ('resolved', 'dismissed')) as resolved_count,
        ROUND(AVG(EXTRACT(EPOCH FROM (resolved_at - created_at))/60))::INTEGER as avg_resolution_minutes,
        COUNT(*) FILTER (WHERE escalation_level > 0) as escalated_count
    FROM alerts
    WHERE DATE(created_at) = target_date
    GROUP BY vehicle_id, type, category, severity
    ON CONFLICT (date, vehicle_id, alert_type, alert_category, severity) 
    DO UPDATE SET
        total_count = EXCLUDED.total_count,
        resolved_count = EXCLUDED.resolved_count,
        average_resolution_time_minutes = EXCLUDED.average_resolution_time_minutes,
        escalated_count = EXCLUDED.escalated_count,
        updated_at = CURRENT_TIMESTAMP;
END;
$$ LANGUAGE 'plpgsql';

-- Insert default notification templates
INSERT INTO notification_templates (name, alert_type, channel, subject_template, message_template, is_default) VALUES
    ('Speed Violation Email', 'speed_violation', 'email', 'Speed Violation Alert - {vehicle_name}', 
     'Vehicle {vehicle_name} exceeded speed limit. Current speed: {current_speed} km/h, Limit: {speed_limit} km/h at {address}', TRUE),
    
    ('Geofence Violation Email', 'geofence_violation', 'email', 'Geofence Alert - {vehicle_name}',
     'Vehicle {vehicle_name} {violation_type} geofence "{geofence_name}" at {address}', TRUE),
     
    ('Device Offline Email', 'device_offline', 'email', 'Vehicle Offline - {vehicle_name}',
     'Vehicle {vehicle_name} has gone offline. Last seen: {last_seen} at {address}', TRUE),
     
    ('Speed Violation WebSocket', 'speed_violation', 'websocket', NULL,
     '{"type": "speed_violation", "vehicle": "{vehicle_name}", "speed": {current_speed}, "limit": {speed_limit}}', TRUE),
     
    ('Geofence Violation WebSocket', 'geofence_violation', 'websocket', NULL,
     '{"type": "geofence_violation", "vehicle": "{vehicle_name}", "geofence": "{geofence_name}", "action": "{violation_type}"}', TRUE);

-- Insert default notification rule for admins
INSERT INTO notification_rules (name, description, alert_types, severity_levels, channels, created_by) VALUES
    ('Admin All Alerts', 'Send all critical alerts to administrators', 
     ARRAY['speed_violation', 'geofence_violation', 'device_offline', 'maintenance_due'], 
     ARRAY['high'::alert_severity, 'critical'::alert_severity], 
     ARRAY['websocket'::notification_channel, 'email'::notification_channel],
     uuid_generate_v4());