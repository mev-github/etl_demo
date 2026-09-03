-- =============================================================
-- MySQL init: dimension tables for hotel supply-chain demo
-- Executed automatically on first container start.
-- =============================================================

CREATE DATABASE IF NOT EXISTS hotel_dims;
USE hotel_dims;

-- ----- dim_hotel -----
CREATE TABLE dim_hotel (
    hotel_id    VARCHAR(10)  PRIMARY KEY,
    name        VARCHAR(120) NOT NULL,
    city        VARCHAR(80)  NOT NULL,
    star_rating TINYINT      NOT NULL CHECK (star_rating BETWEEN 1 AND 5),
    room_count  SMALLINT     NOT NULL
);

INSERT INTO dim_hotel (hotel_id, name, city, star_rating, room_count) VALUES
('HTL-1', 'Grand Palace Hotel',   'Prague',    4, 85),
('HTL-2', 'Riverside Inn',        'Vienna',    3, 42),
('HTL-3', 'Mountain View Lodge',  'Innsbruck', 3, 30);

-- ----- dim_supplier -----
CREATE TABLE dim_supplier (
    supplier_id       VARCHAR(10)  PRIMARY KEY,
    name              VARCHAR(120) NOT NULL,
    supply_category   VARCHAR(40)  NOT NULL,
    reliability_score DECIMAL(3,2) NOT NULL CHECK (reliability_score BETWEEN 0 AND 5),
    contact_email     VARCHAR(120) NOT NULL
);

INSERT INTO dim_supplier (supplier_id, name, supply_category, reliability_score, contact_email) VALUES
('SUP-1', 'EuroLinen GmbH',         'linens',     4.70, 'orders@eurolinen.example.com'),
('SUP-2', 'CleanComfort Supplies',   'toiletries', 4.20, 'sales@cleancomfort.example.com'),
('SUP-3', 'ProHygiene Solutions',    'cleaning',   3.85, 'info@prohygiene.example.com'),
('SUP-4', 'HotelEquip Direct',      'equipment',  4.50, 'support@hotelequip.example.com'),
('SUP-5', 'AlpenFood Distribution', 'food_bev',   4.10, 'orders@alpenfood.example.com');

-- ----- dim_room -----
CREATE TABLE dim_room (
    room_id       VARCHAR(10)  PRIMARY KEY,
    hotel_id      VARCHAR(10)  NOT NULL,
    room_type     VARCHAR(30)  NOT NULL,
    capacity      TINYINT      NOT NULL,
    base_rate_eur DECIMAL(8,2) NOT NULL,
    FOREIGN KEY (hotel_id) REFERENCES dim_hotel(hotel_id)
);

INSERT INTO dim_room (room_id, hotel_id, room_type, capacity, base_rate_eur) VALUES
('RM-101', 'HTL-1', 'standard_double', 2, 110.00),
('RM-102', 'HTL-1', 'deluxe_double',   2, 165.00),
('RM-103', 'HTL-1', 'suite',           4, 290.00),
('RM-201', 'HTL-2', 'standard_single', 1,  72.00),
('RM-202', 'HTL-2', 'standard_double', 2,  95.00),
('RM-203', 'HTL-2', 'deluxe_double',   2, 130.00),
('RM-204', 'HTL-2', 'family',          4, 160.00),
('RM-301', 'HTL-3', 'standard_double', 2,  88.00),
('RM-302', 'HTL-3', 'deluxe_double',   2, 125.00),
('RM-303', 'HTL-3', 'suite',           3, 210.00);

-- Grant read access to the ETL user (created via env vars in docker-compose)
GRANT SELECT ON hotel_dims.* TO 'etl_user'@'%';
FLUSH PRIVILEGES;
