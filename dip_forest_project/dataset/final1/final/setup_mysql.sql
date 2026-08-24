-- StudySphere MySQL Database Setup
-- Run this script in MySQL Workbench to create the database

-- Create the database
CREATE DATABASE IF NOT EXISTS studysphere_db;
USE studysphere_db;

-- Create tables (these will be created automatically by Flask-SQLAlchemy)
-- But you can run this to verify the database is accessible

-- Test query to verify connection
SELECT 'StudySphere database is ready!' as status; 