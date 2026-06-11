-- Create the application database
-- (Docker Compose handles this via POSTGRES_DB env var, but this ensures it exists)

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS career;

-- Set search path
SET search_path TO career, public;
