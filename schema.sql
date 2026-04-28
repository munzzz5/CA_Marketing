PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS keywords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword TEXT NOT NULL,
    category TEXT,
    priority INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS keyword_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS keyword_group_members (
    group_id INTEGER NOT NULL,
    keyword_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (group_id, keyword_id),
    FOREIGN KEY(group_id) REFERENCES keyword_groups(id) ON DELETE CASCADE,
    FOREIGN KEY(keyword_id) REFERENCES keywords(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS scraped_content (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword_id INTEGER,
    title TEXT,
    description TEXT,
    source TEXT,
    source_url TEXT,
    content_type TEXT,
    relevance_score INTEGER,
    published_date DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(keyword_id) REFERENCES keywords(id)
);

CREATE TABLE IF NOT EXISTS generated_ideas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_id INTEGER,
    idea_type TEXT,
    title TEXT,
    description TEXT,
    execution_notes TEXT,
    difficulty TEXT,
    expected_impact TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(content_id) REFERENCES scraped_content(id)
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_scraped_keyword_source ON scraped_content(keyword_id, source_url);
CREATE INDEX IF NOT EXISTS idx_keywords_active ON keywords(is_active);
CREATE INDEX IF NOT EXISTS idx_keywords_category ON keywords(category);
CREATE INDEX IF NOT EXISTS idx_group_member_keyword ON keyword_group_members(keyword_id);
CREATE INDEX IF NOT EXISTS idx_scraped_keyword ON scraped_content(keyword_id);
CREATE INDEX IF NOT EXISTS idx_scraped_type ON scraped_content(content_type);
CREATE INDEX IF NOT EXISTS idx_scraped_date ON scraped_content(published_date);
CREATE INDEX IF NOT EXISTS idx_scraped_score ON scraped_content(relevance_score);
CREATE INDEX IF NOT EXISTS idx_ideas_content ON generated_ideas(content_id);
CREATE INDEX IF NOT EXISTS idx_ideas_type ON generated_ideas(idea_type);
