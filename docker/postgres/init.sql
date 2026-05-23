-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'analyst',
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);

-- Scans table
CREATE TABLE IF NOT EXISTS scans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    target VARCHAR(255) NOT NULL,
    target_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
    progress INTEGER DEFAULT 0,
    user_id UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error TEXT
);

-- Entities table
CREATE TABLE IF NOT EXISTS entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type VARCHAR(50) NOT NULL,
    value VARCHAR(500) NOT NULL,
    metadata JSONB,
    threat_level VARCHAR(50),
    first_seen TIMESTAMP DEFAULT NOW(),
    last_seen TIMESTAMP DEFAULT NOW(),
    scan_id UUID REFERENCES scans(id),
    user_id UUID REFERENCES users(id),
    tags TEXT[]
);

-- IOCs table
CREATE TABLE IF NOT EXISTS iocs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type VARCHAR(50) NOT NULL,
    value VARCHAR(500) NOT NULL,
    source VARCHAR(100) NOT NULL,
    confidence INTEGER DEFAULT 0,
    threat_level VARCHAR(50) NOT NULL,
    description TEXT,
    tags TEXT[],
    first_seen TIMESTAMP DEFAULT NOW(),
    last_seen TIMESTAMP DEFAULT NOW(),
    scan_id UUID REFERENCES scans(id),
    metadata JSONB
);

-- Relationships table
CREATE TABLE IF NOT EXISTS relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID REFERENCES entities(id),
    target_id UUID REFERENCES entities(id),
    type VARCHAR(100) NOT NULL,
    properties JSONB,
    confidence INTEGER DEFAULT 100,
    scan_id UUID REFERENCES scans(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Timeline events table
CREATE TABLE IF NOT EXISTS timeline_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMP DEFAULT NOW(),
    type VARCHAR(100) NOT NULL,
    entity_id UUID REFERENCES entities(id),
    description TEXT,
    metadata JSONB,
    scan_id UUID REFERENCES scans(id)
);

-- Audit log table
CREATE TABLE IF NOT EXISTS audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id UUID,
    details JSONB,
    ip_address INET,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_entities_type ON entities(type);
CREATE INDEX idx_entities_value ON entities(value);
CREATE INDEX idx_entities_scan_id ON entities(scan_id);
CREATE INDEX idx_iocs_type ON iocs(type);
CREATE INDEX idx_iocs_value ON iocs(value);
CREATE INDEX idx_iocs_threat_level ON iocs(threat_level);
CREATE INDEX idx_scans_user_id ON scans(user_id);
CREATE INDEX idx_scans_status ON scans(status);
CREATE INDEX idx_relationships_source ON relationships(source_id);
CREATE INDEX idx_relationships_target ON relationships(target_id);
CREATE INDEX idx_timeline_entity ON timeline_events(entity_id);
CREATE INDEX idx_audit_user ON audit_log(user_id);
CREATE INDEX idx_audit_timestamp ON audit_log(timestamp);

-- Insert default admin user (password: admin123)
INSERT INTO users (email, username, password_hash, role)
VALUES ('admin@cyberintel.local', 'admin', '$2b$10$rBV2kHf7gu8qvXqhQfJzKOxKxJxJxJxJxJxJxJxJxJxJxJxJxJxJx', 'admin')
ON CONFLICT DO NOTHING;
