-- Fleet Tracker Database Initialization
-- Enable required PostgreSQL extensions

-- Enable PostGIS extension for spatial data
CREATE EXTENSION IF NOT EXISTS postgis;

-- Enable UUID extension for generating UUIDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable hstore extension for key-value storage
CREATE EXTENSION IF NOT EXISTS hstore;

-- Enable pg_stat_statements for query performance monitoring
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Verify extensions
SELECT 
    extname AS "Extension",
    extversion AS "Version"
FROM pg_extension 
WHERE extname IN ('postgis', 'uuid-ossp', 'hstore', 'pg_stat_statements');
