-- init_db.sql
CREATE DATABASE IF NOT EXISTS etl_demo_mysql;
USE etl_demo_mysql;

CREATE TABLE IF NOT EXISTS result_table (
    guid VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    action_type VARCHAR(100) NOT NULL,
    action_count INT NOT NULL,
    PRIMARY KEY (guid)
);
