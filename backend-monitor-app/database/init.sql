-- Exlui tabelas se existirem
DROP TABLE IF EXISTS MONITORING_DATA CASCADE;
DROP TABLE IF EXISTS DEVICES_STATUS_HISTORY CASCADE;
DROP TABLE IF EXISTS DEVICES CASCADE;


-- Ative a extensão TimescaleDB
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Tabela de histórico de status
CREATE TABLE devices_status_history (
    id SERIAL PRIMARY KEY,
    device_id INTEGER NOT NULL, -- FK adicionada depois
    status INTEGER NOT NULL,
    last_status_change TIMESTAMPTZ NOT NULL,
    count INTEGER NOT NULL
);

-- Tabela de dispositivos
CREATE TABLE devices (
    id SERIAL PRIMARY KEY,
    ip_address VARCHAR(15) NOT NULL CHECK (ip_address ~ '^[0-9]{1,3}(\.[0-9]{1,3}){3}$'),
    hostname VARCHAR(50) NOT NULL CHECK (hostname ~ '^[A-Z0-9_]+$'),
    site VARCHAR(20) NOT NULL CHECK (site ~ '^[A-Z0-9_]+$'),
    type VARCHAR(30) CHECK (type ~ '^[A-Z0-9_]+$'),
    monitoring_interval_seconds INTEGER NOT NULL DEFAULT 60 CHECK (monitoring_interval_seconds IN (30, 60, 90, 120, 150, 180, 210, 240, 270, 300)),
    ping_timeout_milliseconds INTEGER NOT NULL DEFAULT 1000 CHECK (ping_timeout_milliseconds BETWEEN 100 AND 5000),
    ping_count INTEGER NOT NULL DEFAULT 1 CHECK (ping_count BETWEEN 1 AND 10),
    monitoring_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    current_status INTEGER DEFAULT 99,
    last_status_change TIMESTAMPTZ DEFAULT now(),
    current_history_id INTEGER
);

-- Adicionar FK após para evitar referência circular
ALTER TABLE DEVICES_STATUS_HISTORY
ADD CONSTRAINT fk_device_id FOREIGN KEY (DEVICE_ID) REFERENCES DEVICES(ID);

ALTER TABLE DEVICES
ADD CONSTRAINT fk_current_history FOREIGN KEY (CURRENT_HISTORY_ID) REFERENCES DEVICES_STATUS_HISTORY(ID);


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
SELECT create_hypertable('monitoring_data', 'timestamp', if_not_exists => TRUE);

-- Índice para performance
CREATE INDEX ON monitoring_data (device_id, timestamp DESC);

-- Trigger para criar entrada de histórico automaticamente
CREATE OR REPLACE FUNCTION insert_device_history()
RETURNS TRIGGER AS $$
DECLARE
    new_history_id INTEGER;
BEGIN
    INSERT INTO DEVICES_STATUS_HISTORY (DEVICE_ID, STATUS, LAST_STATUS_CHANGE, COUNT)
    VALUES (NEW.ID, NEW.CURRENT_STATUS, NEW.LAST_STATUS_CHANGE, 1)
    RETURNING ID INTO new_history_id;

    -- Atualiza o campo CURRENT_HISTORY_ID com o ID recém-inserido
    UPDATE DEVICES SET CURRENT_HISTORY_ID = new_history_id WHERE ID = NEW.ID;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger
CREATE TRIGGER trg_insert_device_history
AFTER INSERT ON DEVICES
FOR EACH ROW
EXECUTE FUNCTION insert_device_history();
