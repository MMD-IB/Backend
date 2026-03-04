-- Database Schema for MMD Project
-- PostgreSQL Syntax

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id_user SERIAL PRIMARY KEY,
    name VARCHAR(20) NOT NULL,
    surname VARCHAR(30) NOT NULL,
    email VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(10) DEFAULT 'user',
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_at DATE NULL,
    created_at DATE DEFAULT CURRENT_DATE,
    updated_at DATE DEFAULT CURRENT_DATE
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- Documents Table
CREATE TABLE IF NOT EXISTS documents (
    id_document SERIAL PRIMARY KEY,
    id_user INTEGER NOT NULL REFERENCES users(id_user) ON DELETE CASCADE,
    title VARCHAR(30) NOT NULL,
    content TEXT DEFAULT '',
    file_name VARCHAR(30) DEFAULT '',
    file_type VARCHAR(10) DEFAULT '',
    file_size VARCHAR(10) DEFAULT '',
    updated_at DATE DEFAULT CURRENT_DATE,
    version VARCHAR(10) DEFAULT '1.0',
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_at DATE NULL,
    deleted_by INTEGER REFERENCES users(id_user) ON DELETE SET NULL,
    status VARCHAR(10) NOT NULL,
    created_at DATE DEFAULT CURRENT_DATE
);

CREATE INDEX idx_documents_id_user ON documents(id_user);
CREATE INDEX idx_documents_status ON documents(status);
CREATE INDEX idx_documents_is_deleted ON documents(is_deleted);

-- Share Documents Table
CREATE TABLE IF NOT EXISTS share_documents (
    id_share_document SERIAL PRIMARY KEY,
    id_document INTEGER NOT NULL REFERENCES documents(id_document) ON DELETE CASCADE,
    id_user INTEGER NOT NULL REFERENCES users(id_user) ON DELETE CASCADE,
    shared_at DATE DEFAULT CURRENT_DATE,
    shared_by INTEGER NOT NULL REFERENCES users(id_user) ON DELETE CASCADE,
    created_at DATE DEFAULT CURRENT_DATE
);

CREATE INDEX idx_share_docs_doc ON share_documents(id_document);
CREATE INDEX idx_share_docs_user ON share_documents(id_user);

-- Groups Table
CREATE TABLE IF NOT EXISTS groups (
    id_group SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    description VARCHAR(255),
    created_at DATE DEFAULT CURRENT_DATE,
    updated_at DATE DEFAULT CURRENT_DATE,
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_at DATE NULL
);

-- Group Users Table
CREATE TABLE IF NOT EXISTS group_users (
    id_group_user SERIAL PRIMARY KEY,
    id_group INTEGER NOT NULL REFERENCES groups(id_group) ON DELETE CASCADE,
    id_user INTEGER NOT NULL REFERENCES users(id_user) ON DELETE CASCADE,
    created_at DATE DEFAULT CURRENT_DATE,
    updated_at DATE DEFAULT CURRENT_DATE,
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_at DATE NULL
);

CREATE INDEX idx_group_users_group ON group_users(id_group);
CREATE INDEX idx_group_users_user ON group_users(id_user);

-- Saved Searches Table
CREATE TABLE IF NOT EXISTS saved_searches (
    id_saved_search SERIAL PRIMARY KEY,
    id_user INTEGER NOT NULL REFERENCES users(id_user) ON DELETE CASCADE,
    query TEXT NOT NULL,
    search_date DATE DEFAULT CURRENT_DATE,
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_at DATE NULL
);

CREATE INDEX idx_saved_searches_user ON saved_searches(id_user);

-- Notifications Table
CREATE TABLE IF NOT EXISTS notifications (
    id_notification SERIAL PRIMARY KEY,
    id_user INTEGER NOT NULL REFERENCES users(id_user) ON DELETE CASCADE,
    message TEXT NOT NULL,
    notification_date DATE DEFAULT CURRENT_DATE,
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_at DATE NULL
);

CREATE INDEX idx_notifications_user ON notifications(id_user);

-- Action Logs Table
CREATE TABLE IF NOT EXISTS action_logs (
    id_action_log SERIAL PRIMARY KEY,
    id_user INTEGER NOT NULL REFERENCES users(id_user) ON DELETE CASCADE,
    action_type VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id INTEGER NOT NULL,
    old_value TEXT,
    new_value TEXT,
    ip_address VARCHAR(50),
    user_agent TEXT,
    action TEXT NOT NULL,
    action_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_action_logs_user ON action_logs(id_user);
CREATE INDEX idx_action_logs_type ON action_logs(action_type);
