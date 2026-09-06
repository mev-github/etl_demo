-- =============================================================
-- PostgreSQL init: target warehouse table for ETL output
-- =============================================================

CREATE SCHEMA IF NOT EXISTS dwh;

-- Surrogate PK (row_id) keeps each inserted row uniquely addressable
-- without depending on source keys.  The mandatory metadata columns
-- (batch_id, batch_ts, event_type) come from the Transform stage.

CREATE TABLE dwh.fact_hotel_operations (
    row_id          BIGSERIAL                PRIMARY KEY,

    -- ---- mandatory metadata (same for every student) ----
    batch_id        VARCHAR(64)              NOT NULL,
    batch_ts        TIMESTAMP WITH TIME ZONE NOT NULL,
    event_type      VARCHAR(60)              NOT NULL,

    -- ---- source keys ----
    source_event_id VARCHAR(30),
    hotel_id        VARCHAR(10),
    hotel_name      VARCHAR(120),
    city            VARCHAR(80),

    -- ---- supply order fields ----
    supplier_id     VARCHAR(10),
    supplier_name   VARCHAR(120),
    item_category   VARCHAR(40),
    item_description VARCHAR(200),
    quantity        INTEGER,
    unit_price      NUMERIC(12,2),
    discount_pct    NUMERIC(5,2),
    final_price     NUMERIC(12,2),

    -- ---- housekeeping fields ----
    room_id         VARCHAR(10),
    room_type       VARCHAR(30),
    hk_status       VARCHAR(20),
    duration_minutes INTEGER,
    hk_notes        TEXT
);

-- Index on batch columns for easy per-run queries
CREATE INDEX idx_fact_batch ON dwh.fact_hotel_operations (batch_id, batch_ts);

-- Index on event_type for analytic filters
CREATE INDEX idx_fact_event_type ON dwh.fact_hotel_operations (event_type);
