-- Creazione del database
CREATE DATABASE "ABNSCraper";

\connect "ABNSCraper";

-- Creazione della tabella
CREATE TABLE abnscraper (
    pkey SERIAL PRIMARY KEY,
    id VARCHAR,
    name VARCHAR,
    location JSON,
    price NUMERIC,
    priceCleaning NUMERIC,
    checkin DATE,
    checkout DATE,
    rented BOOLEAN,
    created_ts TIMESTAMP,
    updating_logs JSON,
    CONSTRAINT abnscraper_unique_constraint UNIQUE (id, checkin, checkout)
);

-- Esempio di definizione per il campo updating_logs JSON:
-- [
--     {
--         "id": "UUID",
--         "updated_at": "TIMESTAMP",
--         "updated_fields": [
--             {
--                 "field_updated": "string",
--                 "old_value": "string",
--                 "new_value": "string"
--             }
--         ]
--     }
-- ]
