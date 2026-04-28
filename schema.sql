PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS keywords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword TEXT NOT NULL,
    category TEXT,
    priority INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
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

-- Helpful indexes for v2 workloads.
CREATE INDEX IF NOT EXISTS idx_keywords_active ON keywords(is_active);
CREATE INDEX IF NOT EXISTS idx_keywords_category ON keywords(category);
CREATE INDEX IF NOT EXISTS idx_scraped_keyword ON scraped_content(keyword_id);
CREATE INDEX IF NOT EXISTS idx_scraped_type ON scraped_content(content_type);
CREATE INDEX IF NOT EXISTS idx_scraped_date ON scraped_content(published_date);
CREATE INDEX IF NOT EXISTS idx_ideas_content ON generated_ideas(content_id);
CREATE INDEX IF NOT EXISTS idx_ideas_type ON generated_ideas(idea_type);
