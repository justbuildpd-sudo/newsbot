#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
데이터베이스 연결 및 설정
Railway PostgreSQL 사용
"""

import os
import psycopg
from psycopg.rows import dict_row
import json
from typing import List, Dict, Optional

class Database:
    def __init__(self):
        self.connection = None
        self.connect()
    
    def connect(self):
        """PostgreSQL 데이터베이스에 연결합니다."""
        try:
            # Railway 환경변수에서 데이터베이스 URL 가져오기
            database_url = os.getenv('DATABASE_URL')
            if not database_url:
                # 로컬 개발용 (Railway 없이 테스트)
                database_url = "postgresql://localhost:5432/newsbot"
            
            self.connection = psycopg.connect(
                database_url,
                row_factory=dict_row
            )
            print("✅ PostgreSQL 데이터베이스 연결 성공")
            
            # 테이블 생성
            self.create_tables()
            
        except Exception as e:
            print(f"❌ 데이터베이스 연결 오류: {e}")
            print("⚠️ 데이터베이스 없이 계속 진행합니다...")
            self.connection = None
    
    def create_tables(self):
        """필요한 테이블들을 생성합니다."""
        if not self.connection:
            return
        
        try:
            cursor = self.connection.cursor()
            
            # 정치인 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS politicians (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    name_hanja VARCHAR(100),
                    district VARCHAR(200),
                    party VARCHAR(100),
                    committee TEXT,
                    terms VARCHAR(100),
                    office VARCHAR(100),
                    phone VARCHAR(50),
                    email VARCHAR(100),
                    website VARCHAR(200),
                    image_url VARCHAR(500),
                    political_orientation VARCHAR(50),
                    key_issues JSONB,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 뉴스 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS news (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    link VARCHAR(500) UNIQUE,
                    pub_date TIMESTAMP,
                    category VARCHAR(50),
                    content TEXT,
                    images JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 정치인 언급 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS politician_mentions (
                    id SERIAL PRIMARY KEY,
                    politician_id INTEGER REFERENCES politicians(id),
                    news_id INTEGER REFERENCES news(id),
                    mention_count INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 인덱스 생성
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_politicians_party ON politicians(party)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_news_pub_date ON news(pub_date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_mentions_politician ON politician_mentions(politician_id)")
            
            self.connection.commit()
            print("✅ 데이터베이스 테이블 생성 완료")
            
        except Exception as e:
            print(f"❌ 테이블 생성 오류: {e}")
            self.connection.rollback()
    
    def insert_politicians(self, politicians: List[Dict]):
        """정치인 데이터를 데이터베이스에 삽입합니다."""
        if not self.connection:
            return False
        
        try:
            cursor = self.connection.cursor()
            
            for politician in politicians:
                cursor.execute("""
                    INSERT INTO politicians (
                        name, name_hanja, district, party, committee, terms,
                        office, phone, email, website, image_url, political_orientation,
                        key_issues, description
                    ) VALUES (
                        %(name)s, %(name_hanja)s, %(district)s, %(party)s, %(committee)s, %(terms)s,
                        %(office)s, %(phone)s, %(email)s, %(website)s, %(image_url)s, %(political_orientation)s,
                        %(key_issues)s, %(description)s
                    ) ON CONFLICT (name, party) DO UPDATE SET
                        name_hanja = EXCLUDED.name_hanja,
                        district = EXCLUDED.district,
                        committee = EXCLUDED.committee,
                        terms = EXCLUDED.terms,
                        office = EXCLUDED.office,
                        phone = EXCLUDED.phone,
                        email = EXCLUDED.email,
                        website = EXCLUDED.website,
                        image_url = EXCLUDED.image_url,
                        political_orientation = EXCLUDED.political_orientation,
                        key_issues = EXCLUDED.key_issues,
                        description = EXCLUDED.description,
                        updated_at = CURRENT_TIMESTAMP
                """, politician)
            
            self.connection.commit()
            print(f"✅ {len(politicians)}명의 정치인 데이터 삽입 완료")
            return True
            
        except Exception as e:
            print(f"❌ 정치인 데이터 삽입 오류: {e}")
            self.connection.rollback()
            return False
    
    def get_politicians(self, limit: int = 100) -> List[Dict]:
        """정치인 목록을 조회합니다."""
        if not self.connection:
            return []
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT * FROM politicians 
                ORDER BY created_at DESC 
                LIMIT %s
            """, (limit,))
            
            politicians = cursor.fetchall()
            return list(politicians)
            
        except Exception as e:
            print(f"❌ 정치인 조회 오류: {e}")
            return []
    
    def get_politician_by_id(self, politician_id: int) -> Optional[Dict]:
        """ID로 특정 정치인을 조회합니다."""
        if not self.connection:
            return None
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM politicians WHERE id = %s", (politician_id,))
            politician = cursor.fetchone()
            return politician if politician else None
            
        except Exception as e:
            print(f"❌ 정치인 조회 오류: {e}")
            return None
    
    def close(self):
        """데이터베이스 연결을 닫습니다."""
        if self.connection:
            self.connection.close()
            print("✅ 데이터베이스 연결 종료")

# 전역 데이터베이스 인스턴스
db = Database()
