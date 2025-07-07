-- Desabilita temporariamente a verificação de chaves estrangeiras
DO $$
DECLARE
    r RECORD;
BEGIN
    -- Remove constraints
    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
        EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
    END LOOP;
END
$$;

-- Ative a extensão TimescaleDB
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Tabela de dispositivos
CREATE TABLE devices (
    id SERIAL PRIMARY KEY,
    ip VARCHAR(15) NOT NULL CHECK (ip ~ '^\d{1,3}(\.\d{1,3}){3}$'),
    hostname VARCHAR(50) NOT NULL CHECK (hostname ~ '^[A-Z0-9_]+$'),
    type VARCHAR(30) NOT NULL CHECK (type ~ '^[A-Z0-9_]+$'),
    site VARCHAR(20) NOT NULL CHECK (site ~ '^[A-Z0-9_]+$'),
    monitoring_interval_seconds INTEGER NOT NULL DEFAULT 60 CHECK (monitoring_interval_seconds IN (30, 60, 90, 120, 150, 180, 210, 240, 270, 300)),
    ping_timeout_milliseconds INTEGER NOT NULL DEFAULT 1000 CHECK (ping_timeout_milliseconds BETWEEN 100 AND 5000),
    ping_count INTEGER NOT NULL DEFAULT 1 CHECK (ping_count BETWEEN 1 AND 10),
    monitoring_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    status INTEGER NOT NULL,
    last_status_change TIMESTAMPTZ NOT NULL
);

-- Tabela de histórico de status
CREATE TABLE devices_status_history (
    device_id INTEGER REFERENCES devices(id) ON DELETE CASCADE,
    last_status_change TIMESTAMPTZ NOT NULL,
    count INTEGER NOT NULL DEFAULT 1
);

-- Tabela de resultados de monitoramento
CREATE TABLE monitoring_data (
    timestamp TIMESTAMPTZ NOT NULL,
    device_id INTEGER NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
    status INTEGER NOT NULL,
    pack_sent INTEGER NOT NULL,
    pack_recv INTEGER NOT NULL,
    rtt_min INTEGER,
    rtt_max INTEGER,
    rtt_avg INTEGER
);

-- Converter para hypertable
SELECT create_hypertable('monitoring_data', 'timestamp');

-- Índice para performance
CREATE INDEX ON monitoring_data (device_id, timestamp DESC);