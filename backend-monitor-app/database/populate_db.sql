INSERT INTO devices (hostname, ip, type, site, monitoring_interval_seconds, ping_timeout_milliseconds, ping_count, monitoring_enabled)
VALUES
-- Google
('GOOGLE', '142.250.190.14', 'WEBSITE', 'INT-GOOG', 30, 1000, 4, TRUE),

-- Facebook
('FACEBOOK', '157.240.222.35', 'WEBSITE', 'INT-FB', 60, 1000, 4, TRUE),

-- Cloudflare DNS (serviço de infraestrutura de rede)
('CLOUDFLARE', '1.1.1.1', 'DNS', 'INT-CLOUDFLARE', 90, 1000, 2, TRUE),

-- GitHub
('GITHUB', '140.82.112.4', 'WEBSITE', 'INT-GIT', 30, 1000, 4, TRUE),

-- Wikipedia
('WIKIPEDIA', '208.80.154.224', 'WEBSITE', 'INT-WIKI', 60, 1000, 3, TRUE);
