-- newsbot.kr 데이터베이스 스키마
-- 뉴스 분석 플랫폼을 위한 테이블 구조

-- 뉴스 테이블
CREATE TABLE IF NOT EXISTS news (
    id SERIAL PRIMARY KEY,
    news_id VARCHAR(255) UNIQUE NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    link VARCHAR(500) NOT NULL,
    pub_date TIMESTAMP NOT NULL,
    keyword VARCHAR(100),
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 뉴스 분석 결과 테이블
CREATE TABLE IF NOT EXISTS news_analysis (
    id SERIAL PRIMARY KEY,
    news_id INTEGER REFERENCES news(id) ON DELETE CASCADE,
    sentiment_score FLOAT,
    sentiment_label VARCHAR(50),
    keywords TEXT[],
    topics TEXT[],
    entities TEXT[],
    summary TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 정치인 테이블
CREATE TABLE IF NOT EXISTS politicians (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    party VARCHAR(100),
    position VARCHAR(100),
    constituency VARCHAR(100),
    profile_image_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 정치인 언급 테이블
CREATE TABLE IF NOT EXISTS politician_mentions (
    id SERIAL PRIMARY KEY,
    news_id INTEGER REFERENCES news(id) ON DELETE CASCADE,
    politician_id INTEGER REFERENCES politicians(id) ON DELETE CASCADE,
    mention_count INTEGER DEFAULT 1,
    context TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 키워드 테이블
CREATE TABLE IF NOT EXISTS keywords (
    id SERIAL PRIMARY KEY,
    keyword VARCHAR(100) UNIQUE NOT NULL,
    frequency INTEGER DEFAULT 1,
    category VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 연결성 분석 테이블
CREATE TABLE IF NOT EXISTS connections (
    id SERIAL PRIMARY KEY,
    source_type VARCHAR(50) NOT NULL, -- 'news', 'politician', 'keyword'
    source_id INTEGER NOT NULL,
    target_type VARCHAR(50) NOT NULL,
    target_id INTEGER NOT NULL,
    connection_strength FLOAT DEFAULT 0.0,
    connection_type VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_news_pub_date ON news(pub_date);
CREATE INDEX IF NOT EXISTS idx_news_keyword ON news(keyword);
CREATE INDEX IF NOT EXISTS idx_news_analysis_news_id ON news_analysis(news_id);
CREATE INDEX IF NOT EXISTS idx_politician_mentions_news_id ON politician_mentions(news_id);
CREATE INDEX IF NOT EXISTS idx_politician_mentions_politician_id ON politician_mentions(politician_id);
CREATE INDEX IF NOT EXISTS idx_connections_source ON connections(source_type, source_id);
CREATE INDEX IF NOT EXISTS idx_connections_target ON connections(target_type, target_id);

-- 뷰 생성: 뉴스 통계
CREATE OR REPLACE VIEW news_stats AS
SELECT 
    DATE(pub_date) as date,
    COUNT(*) as total_news,
    COUNT(DISTINCT keyword) as unique_keywords,
    AVG(sentiment_score) as avg_sentiment
FROM news n
LEFT JOIN news_analysis na ON n.id = na.news_id
GROUP BY DATE(pub_date)
ORDER BY date DESC;

-- 뷰 생성: 정치인 언급 통계
CREATE OR REPLACE VIEW politician_mention_stats AS
SELECT 
    p.name,
    p.party,
    COUNT(pm.id) as mention_count,
    COUNT(DISTINCT pm.news_id) as news_count,
    AVG(na.sentiment_score) as avg_sentiment
FROM politicians p
LEFT JOIN politician_mentions pm ON p.id = pm.politician_id
LEFT JOIN news n ON pm.news_id = n.id
LEFT JOIN news_analysis na ON n.id = na.news_id
GROUP BY p.id, p.name, p.party
ORDER BY mention_count DESC;
