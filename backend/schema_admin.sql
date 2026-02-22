-- ==========================================
-- VISTARA ADMIN PANEL DATABASE SCHEMA
-- ==========================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==========================================
-- NEWS ARTICLES TABLE
-- ==========================================
CREATE TABLE IF NOT EXISTS news_articles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category VARCHAR(100) NOT NULL,
    title TEXT NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    excerpt TEXT NOT NULL,
    content TEXT NOT NULL,
    image_url TEXT,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    featured BOOLEAN DEFAULT FALSE,
    published BOOLEAN DEFAULT FALSE,
    student_name VARCHAR(255),  -- For impact stories
    location VARCHAR(255),       -- For impact stories
    program VARCHAR(255),        -- For impact stories
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_news_slug ON news_articles(slug);
CREATE INDEX idx_news_category ON news_articles(category);
CREATE INDEX idx_news_published ON news_articles(published);
CREATE INDEX idx_news_featured ON news_articles(featured);

-- ==========================================
-- TEAM MEMBERS TABLE
-- ==========================================
CREATE TABLE IF NOT EXISTS team_members (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    role VARCHAR(255) NOT NULL,
    bio TEXT,
    image_url TEXT,
    email VARCHAR(255),
    phone VARCHAR(50),
    linkedin_url TEXT,
    twitter_url TEXT,
    order_index INTEGER DEFAULT 0,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_team_active ON team_members(active);
CREATE INDEX idx_team_order ON team_members(order_index);

-- ==========================================
-- PARTNERS TABLE
-- ==========================================
CREATE TABLE IF NOT EXISTS partners (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(100) NOT NULL,  -- Government, Corporate, NGO, University, International
    logo_url TEXT,
    website_url TEXT,
    description TEXT,
    since VARCHAR(50),  -- Partnership start year
    featured BOOLEAN DEFAULT FALSE,
    active BOOLEAN DEFAULT TRUE,
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_partners_type ON partners(type);
CREATE INDEX idx_partners_featured ON partners(featured);
CREATE INDEX idx_partners_active ON partners(active);

-- ==========================================
-- JOB POSTINGS TABLE (Careers)
-- ==========================================
CREATE TABLE IF NOT EXISTS job_postings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    department VARCHAR(100) NOT NULL,
    location VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,  -- Full-time, Part-time, Contract, Internship
    experience VARCHAR(100),
    description TEXT NOT NULL,
    responsibilities JSONB,  -- Array of strings
    requirements JSONB,      -- Array of strings
    benefits JSONB,          -- Array of strings
    salary VARCHAR(100),
    posted_date DATE NOT NULL DEFAULT CURRENT_DATE,
    closing_date DATE,
    active BOOLEAN DEFAULT TRUE,
    featured BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_jobs_active ON job_postings(active);
CREATE INDEX idx_jobs_type ON job_postings(type);
CREATE INDEX idx_jobs_department ON job_postings(department);
CREATE INDEX idx_jobs_closing_date ON job_postings(closing_date);

-- ==========================================
-- UPLOADED FILES TABLE (for tracking)
-- ==========================================
CREATE TABLE IF NOT EXISTS uploaded_files (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    original_filename VARCHAR(255) NOT NULL,
    stored_filename VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_size BIGINT,
    mime_type VARCHAR(100),
    storage_type VARCHAR(50) DEFAULT 'local',  -- local or s3
    s3_url TEXT,
    uploaded_by VARCHAR(255),
    entity_type VARCHAR(100),  -- news, team, partner, program, event
    entity_id UUID,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_files_entity ON uploaded_files(entity_type, entity_id);
CREATE INDEX idx_files_storage ON uploaded_files(storage_type);

-- ==========================================
-- IMPACT METRICS TABLE (for dashboard)
-- ==========================================
CREATE TABLE IF NOT EXISTS impact_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_name VARCHAR(255) NOT NULL,
    metric_value DECIMAL(15,2) NOT NULL,
    metric_unit VARCHAR(50),
    category VARCHAR(100),  -- students, schools, villages, programs
    description TEXT,
    display_order INTEGER DEFAULT 0,
    active BOOLEAN DEFAULT TRUE,
    recorded_at DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_metrics_category ON impact_metrics(category);
CREATE INDEX idx_metrics_active ON impact_metrics(active);

-- ==========================================
-- UPDATE TIMESTAMP TRIGGER FUNCTION
-- ==========================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to all tables
CREATE TRIGGER update_news_updated_at BEFORE UPDATE ON news_articles 
    FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER update_team_updated_at BEFORE UPDATE ON team_members 
    FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER update_partners_updated_at BEFORE UPDATE ON partners 
    FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER update_jobs_updated_at BEFORE UPDATE ON job_postings 
    FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER update_metrics_updated_at BEFORE UPDATE ON impact_metrics 
    FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
