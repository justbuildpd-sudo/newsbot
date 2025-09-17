#!/usr/bin/env python3
"""
NewsBot 통합 서버 - 맥 환경 최적화
모든 API 기능을 하나의 서버에서 제공합니다.
"""

import os
import sys
import sqlite3
import json
import logging
import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from typing import Dict, List, Optional
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from collections import defaultdict
import math

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title="NewsBot 통합 API",
    description="정치인 뉴스 분석 및 평가 시스템",
    version="2.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 서빙
app.mount("/static", StaticFiles(directory="../"), name="static")

class NewsBotUnifiedService:
    def __init__(self):
        self.politicians_data = {}
        self.db_path = "newsbot_unified.db"
        self.init_database()
        self.load_politicians()
        self.generate_evaluation_data()
        self.generate_connectivity_data()
        
    def init_database(self):
        """통합 데이터베이스 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 정치인 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS politicians (
                name TEXT PRIMARY KEY,
                party_name TEXT,
                district TEXT,
                committee TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 평가 점수 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS evaluation_scores (
                politician_name TEXT PRIMARY KEY,
                total_score REAL DEFAULT 0.0,
                news_mention_score REAL DEFAULT 0.0,
                news_sentiment_score REAL DEFAULT 0.0,
                news_trend_score REAL DEFAULT 0.0,
                bill_main_sponsor_score REAL DEFAULT 0.0,
                bill_co_sponsor_score REAL DEFAULT 0.0,
                bill_success_rate_score REAL DEFAULT 0.0,
                bill_pass_rate_score REAL DEFAULT 0.0,
                bill_impact_score REAL DEFAULT 0.0,
                bill_quality_score REAL DEFAULT 0.0,
                connectivity_total_score REAL DEFAULT 0.0,
                connectivity_influence_score REAL DEFAULT 0.0,
                connectivity_collaboration_score REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (politician_name) REFERENCES politicians (name)
            )
        ''')
        
        # 연결성 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS connectivity_relations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                politician_a TEXT,
                politician_b TEXT,
                connection_type TEXT,
                strength REAL DEFAULT 1.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (politician_a) REFERENCES politicians (name),
                FOREIGN KEY (politician_b) REFERENCES politicians (name)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("통합 데이터베이스 초기화 완료")
    
    def load_politicians(self):
        """정치인 데이터 로드"""
        try:
            with open('data/politicians.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.politicians_data = {p.get('name'): p for p in data if p.get('name')}
            
            # 데이터베이스에 저장
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for name, politician in self.politicians_data.items():
                cursor.execute('''
                    INSERT OR REPLACE INTO politicians (name, party_name, district, committee)
                    VALUES (?, ?, ?, ?)
                ''', (
                    name,
                    politician.get('party_name', ''),
                    politician.get('district', ''),
                    politician.get('committee', '')
                ))
            
            conn.commit()
            conn.close()
            logger.info(f"정치인 데이터 로드 완료: {len(self.politicians_data)}명")
            
        except Exception as e:
            logger.error(f"정치인 데이터 로드 실패: {e}")
            self.politicians_data = {}
    
    def generate_evaluation_data(self):
        """평가 데이터 생성"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 기존 평가 데이터 삭제
        cursor.execute('DELETE FROM evaluation_scores')
        
        for name, politician in self.politicians_data.items():
            # 뉴스 점수 (가상 데이터)
            news_mention = min(10.0, len(name) * 0.5 + hash(name) % 5)
            news_sentiment = min(10.0, 5.0 + (hash(name) % 10) * 0.3)
            news_trend = min(10.0, 3.0 + (hash(name) % 7) * 0.4)
            
            # 의안 점수 (가상 데이터)
            bill_main = min(10.0, (hash(name) % 8) * 1.2)
            bill_co = min(10.0, (hash(name) % 12) * 0.8)
            bill_success = min(10.0, 4.0 + (hash(name) % 6) * 0.6)
            bill_pass = min(10.0, 3.0 + (hash(name) % 7) * 0.7)
            bill_impact = min(10.0, 2.0 + (hash(name) % 8) * 0.8)
            bill_quality = min(10.0, 3.0 + (hash(name) % 6) * 0.9)
            
            # 연결성 점수 (가상 데이터)
            connectivity_total = min(10.0, (hash(name) % 15) * 0.6)
            connectivity_influence = min(10.0, (hash(name) % 12) * 0.7)
            connectivity_collaboration = min(10.0, (hash(name) % 10) * 0.8)
            
            # 총점 계산 (가중치 적용)
            total_score = (
                news_mention * 0.2 + news_sentiment * 0.1 + news_trend * 0.1 +
                bill_main * 0.15 + bill_co * 0.1 + bill_success * 0.1 +
                bill_pass * 0.1 + bill_impact * 0.05 + bill_quality * 0.05 +
                connectivity_total * 0.05
            )
            
            cursor.execute('''
                INSERT INTO evaluation_scores (
                    politician_name, total_score,
                    news_mention_score, news_sentiment_score, news_trend_score,
                    bill_main_sponsor_score, bill_co_sponsor_score, bill_success_rate_score,
                    bill_pass_rate_score, bill_impact_score, bill_quality_score,
                    connectivity_total_score, connectivity_influence_score, connectivity_collaboration_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                name, total_score,
                news_mention, news_sentiment, news_trend,
                bill_main, bill_co, bill_success,
                bill_pass, bill_impact, bill_quality,
                connectivity_total, connectivity_influence, connectivity_collaboration
            ))
        
        conn.commit()
        conn.close()
        logger.info("평가 데이터 생성 완료")
    
    def generate_connectivity_data(self):
        """연결성 데이터 생성"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 기존 연결성 데이터 삭제
        cursor.execute('DELETE FROM connectivity_relations')
        
        politicians = list(self.politicians_data.keys())
        connection_count = 0
        
        for i, pol_a in enumerate(politicians):
            for j, pol_b in enumerate(politicians[i+1:], i+1):
                # 같은 정당인 경우 높은 연결성
                if (self.politicians_data[pol_a].get('party_name') == 
                    self.politicians_data[pol_b].get('party_name')):
                    strength = 0.8 + (hash(pol_a + pol_b) % 20) * 0.01
                    cursor.execute('''
                        INSERT INTO connectivity_relations (politician_a, politician_b, connection_type, strength)
                        VALUES (?, ?, ?, ?)
                    ''', (pol_a, pol_b, 'party', strength))
                    connection_count += 1
                
                # 같은 지역구인 경우 중간 연결성
                elif (self.politicians_data[pol_a].get('district') == 
                      self.politicians_data[pol_b].get('district')):
                    strength = 0.5 + (hash(pol_a + pol_b) % 30) * 0.01
                    cursor.execute('''
                        INSERT INTO connectivity_relations (politician_a, politician_b, connection_type, strength)
                        VALUES (?, ?, ?, ?)
                    ''', (pol_a, pol_b, 'district', strength))
                    connection_count += 1
                
                # 같은 위원회인 경우 낮은 연결성
                elif (self.politicians_data[pol_a].get('committee') == 
                      self.politicians_data[pol_b].get('committee')):
                    strength = 0.3 + (hash(pol_a + pol_b) % 40) * 0.01
                    cursor.execute('''
                        INSERT INTO connectivity_relations (politician_a, politician_b, connection_type, strength)
                        VALUES (?, ?, ?, ?)
                    ''', (pol_a, pol_b, 'committee', strength))
                    connection_count += 1
        
        conn.commit()
        conn.close()
        logger.info(f"연결성 데이터 생성 완료: {connection_count}개 연결")
    
    def calculate_std_dev(self, values):
        """표준편차 계산"""
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return math.sqrt(variance)

# 서비스 인스턴스 생성
service = NewsBotUnifiedService()

# ==================== API 엔드포인트 ====================

@app.get("/")
async def root():
    """메인 페이지"""
    return FileResponse("../index.html")

@app.get("/api/health")
async def get_health():
    """서버 상태 확인"""
    conn = sqlite3.connect(service.db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM politicians")
    politician_count = cursor.fetchone()[0]
    cursor.execute("SELECT AVG(total_score) FROM evaluation_scores")
    avg_score = cursor.fetchone()[0]
    conn.close()
    
    return {
        "status": "healthy",
        "politician_count": politician_count,
        "avg_score": round(avg_score, 2) if avg_score else 0,
        "database": "connected",
        "version": "2.0.0"
    }

# ==================== 정치인 데이터 API ====================

@app.get("/api/politicians")
async def get_politicians(limit: int = Query(50, ge=1, le=500)):
    """정치인 목록 조회"""
    conn = sqlite3.connect(service.db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT name, party_name, district, committee
        FROM politicians
        ORDER BY name
        LIMIT ?
    ''', (limit,))
    
    politicians = []
    for row in cursor.fetchall():
        politicians.append({
            "name": row[0],
            "party": row[1] if row[1] else "정당정보없음",
            "district": row[2] if row[2] else "정보없음",
            "committee": row[3] if row[3] else "정보없음"
        })
    
    conn.close()
    return {"success": True, "data": politicians, "count": len(politicians)}

@app.get("/api/politicians/stats")
async def get_politician_stats():
    """정치인 통계"""
    conn = sqlite3.connect(service.db_path)
    cursor = conn.cursor()
    
    # 정당별 분포
    cursor.execute('''
        SELECT party_name, COUNT(*) as count
        FROM politicians
        GROUP BY party_name
        ORDER BY count DESC
    ''')
    
    party_distribution = {}
    for row in cursor.fetchall():
        party_distribution[row[0] if row[0] else "정당정보없음"] = row[1]
    
    # 지역별 분포
    cursor.execute('''
        SELECT district, COUNT(*) as count
        FROM politicians
        WHERE district IS NOT NULL AND district != ''
        GROUP BY district
        ORDER BY count DESC
        LIMIT 10
    ''')
    
    district_distribution = {}
    for row in cursor.fetchall():
        district_distribution[row[0]] = row[1]
    
    conn.close()
    
    return {
        "success": True,
        "data": {
            "total_politicians": len(service.politicians_data),
            "party_distribution": party_distribution,
            "district_distribution": district_distribution
        }
    }

# ==================== 평가 API ====================

@app.get("/api/evaluation/ranking")
async def get_politician_ranking(limit: int = Query(10, ge=1, le=100), party: str = Query(None)):
    """정치인 랭킹"""
    conn = sqlite3.connect(service.db_path)
    cursor = conn.cursor()
    
    query = '''
        SELECT p.name, p.party_name, p.district, es.total_score,
               es.news_mention_score, es.news_sentiment_score, es.news_trend_score,
               es.bill_main_sponsor_score, es.bill_co_sponsor_score, es.bill_success_rate_score,
               es.bill_pass_rate_score, es.bill_impact_score, es.bill_quality_score,
               es.connectivity_total_score, es.connectivity_influence_score, es.connectivity_collaboration_score
        FROM evaluation_scores es
        JOIN politicians p ON es.politician_name = p.name
    '''
    params = []
    
    if party and party != "all":
        query += " WHERE p.party_name = ?"
        params.append(party)
    
    query += " ORDER BY es.total_score DESC LIMIT ?"
    params.append(limit)
    
    cursor.execute(query, params)
    
    politicians = []
    for i, row in enumerate(cursor.fetchall()):
        politicians.append({
            "rank": i + 1,
            "name": row[0],
            "party": row[1] if row[1] else "정당정보없음",
            "district": row[2] if row[2] else "정보없음",
            "total_score": round(row[3], 2),
            "scores": {
                "news": {
                    "mention": round(row[4], 2),
                    "sentiment": round(row[5], 2),
                    "trend": round(row[6], 2)
                },
                "bill_sponsor": {
                    "main": round(row[7], 2),
                    "co": round(row[8], 2),
                    "success_rate": round(row[9], 2)
                },
                "bill_result": {
                    "pass_rate": round(row[10], 2),
                    "impact": round(row[11], 2),
                    "quality": round(row[12], 2)
                },
                "connectivity": {
                    "total": round(row[13], 2),
                    "influence": round(row[14], 2),
                    "collaboration": round(row[15], 2)
                }
            }
        })
    
    conn.close()
    return {"success": True, "data": {"politicians": politicians, "total_count": len(politicians), "filter": {"party": party, "limit": limit}}}

@app.get("/api/evaluation/party-stats")
async def get_party_statistics():
    """정당별 통계"""
    conn = sqlite3.connect(service.db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT p.party_name, COUNT(p.name), AVG(es.total_score), MAX(es.total_score), MIN(es.total_score)
        FROM evaluation_scores es
        JOIN politicians p ON es.politician_name = p.name
        GROUP BY p.party_name
        ORDER BY AVG(es.total_score) DESC
    ''')
    
    party_stats = []
    for row in cursor.fetchall():
        party_stats.append({
            "party": row[0] if row[0] else "정당정보없음",
            "count": row[1],
            "avg_score": round(row[2], 2),
            "max_score": round(row[3], 2),
            "min_score": round(row[4], 2)
        })
    
    conn.close()
    return {"success": True, "data": {"party_statistics": party_stats}}

@app.get("/api/evaluation/score-distribution")
async def get_score_distribution():
    """점수 분포"""
    conn = sqlite3.connect(service.db_path)
    cursor = conn.cursor()
    
    cursor.execute('SELECT total_score FROM evaluation_scores')
    scores = [row[0] for row in cursor.fetchall()]
    
    # 점수 분포 계산
    distribution = defaultdict(int)
    for score in scores:
        if score >= 9: distribution["9-10"] += 1
        elif score >= 8: distribution["8-9"] += 1
        elif score >= 7: distribution["7-8"] += 1
        elif score >= 6: distribution["6-7"] += 1
        elif score >= 5: distribution["5-6"] += 1
        elif score >= 4: distribution["4-5"] += 1
        elif score >= 3: distribution["3-4"] += 1
        elif score >= 2: distribution["2-3"] += 1
        elif score >= 1: distribution["1-2"] += 1
        else: distribution["0-1"] += 1
    
    # 정렬된 범위로 변환
    sorted_distribution = []
    for r in ["9-10", "8-9", "7-8", "6-7", "5-6", "4-5", "3-4", "2-3", "1-2", "0-1"]:
        sorted_distribution.append({"range": r, "count": distribution[r]})
    
    # 통계 계산
    total_count = len(scores)
    avg_score = sum(scores) / len(scores) if scores else 0
    max_score = max(scores) if scores else 0
    min_score = min(scores) if scores else 0
    std_score = service.calculate_std_dev(scores)
    
    conn.close()
    
    return {
        "success": True,
        "data": {
            "distribution": sorted_distribution,
            "statistics": {
                "total_count": total_count,
                "avg_score": round(avg_score, 2),
                "max_score": round(max_score, 2),
                "min_score": round(min_score, 2),
                "std_score": round(std_score, 2)
            }
        }
    }

@app.get("/api/evaluation/politician/{politician_name}")
async def get_politician_detail_evaluation(politician_name: str):
    """개별 정치인 상세 평가"""
    conn = sqlite3.connect(service.db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT p.name, p.party_name, p.district, p.committee, es.total_score,
               es.news_mention_score, es.news_sentiment_score, es.news_trend_score,
               es.bill_main_sponsor_score, es.bill_co_sponsor_score, es.bill_success_rate_score,
               es.bill_pass_rate_score, es.bill_impact_score, es.bill_quality_score,
               es.connectivity_total_score, es.connectivity_influence_score, es.connectivity_collaboration_score
        FROM evaluation_scores es
        JOIN politicians p ON es.politician_name = p.name
        WHERE p.name = ?
    ''', (politician_name,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "success": True,
            "data": {
                "name": row[0],
                "party": row[1] if row[1] else "정당정보없음",
                "district": row[2] if row[2] else "정보없음",
                "committee": row[3] if row[3] else "정보없음",
                "total_score": round(row[4], 2),
                "scores": {
                    "news": {
                        "mention": round(row[5], 2),
                        "sentiment": round(row[6], 2),
                        "trend": round(row[7], 2)
                    },
                    "bill_sponsor": {
                        "main": round(row[8], 2),
                        "co": round(row[9], 2),
                        "success_rate": round(row[10], 2)
                    },
                    "bill_result": {
                        "pass_rate": round(row[11], 2),
                        "impact": round(row[12], 2),
                        "quality": round(row[13], 2)
                    },
                    "connectivity": {
                        "total": round(row[14], 2),
                        "influence": round(row[15], 2),
                        "collaboration": round(row[16], 2)
                    }
                }
            }
        }
    
    raise HTTPException(status_code=404, detail="Politician not found")

# ==================== 연결성 API ====================

@app.get("/api/connectivity/stats")
async def get_connectivity_stats():
    """연결성 통계"""
    conn = sqlite3.connect(service.db_path)
    cursor = conn.cursor()
    
    # 총 연결 수
    cursor.execute('SELECT COUNT(*) FROM connectivity_relations')
    total_connections = cursor.fetchone()[0]
    
    # 연결 유형별 통계
    cursor.execute('''
        SELECT connection_type, COUNT(*) as count
        FROM connectivity_relations
        GROUP BY connection_type
        ORDER BY count DESC
    ''')
    
    connection_types = []
    for row in cursor.fetchall():
        connection_types.append({
            "type": row[0],
            "count": row[1]
        })
    
    # 상위 연결 정치인
    cursor.execute('''
        SELECT politician_a, COUNT(*) as connections
        FROM connectivity_relations
        GROUP BY politician_a
        ORDER BY connections DESC
        LIMIT 10
    ''')
    
    top_connected = []
    for row in cursor.fetchall():
        top_connected.append({
            "name": row[0],
            "connections": row[1]
        })
    
    # 정당별 연결성
    cursor.execute('''
        SELECT p.party_name, COUNT(cr.id) as connections
        FROM connectivity_relations cr
        JOIN politicians p ON cr.politician_a = p.name
        GROUP BY p.party_name
        ORDER BY connections DESC
    ''')
    
    party_connections = []
    for row in cursor.fetchall():
        party_connections.append({
            "party": row[0] if row[0] else "정당정보없음",
            "connections": row[1]
        })
    
    conn.close()
    
    return {
        "success": True,
        "data": {
            "total_politicians": len(service.politicians_data),
            "total_connections": total_connections,
            "connection_types": connection_types,
            "top_connected": top_connected,
            "party_connections": party_connections
        }
    }

@app.get("/api/connectivity/politician/{politician_name}")
async def get_politician_connectivity(politician_name: str):
    """개별 정치인 연결성 정보"""
    conn = sqlite3.connect(service.db_path)
    cursor = conn.cursor()
    
    # 해당 정치인의 연결 정보
    cursor.execute('''
        SELECT politician_b, connection_type, strength
        FROM connectivity_relations
        WHERE politician_a = ?
        ORDER BY strength DESC
        LIMIT 20
    ''', (politician_name,))
    
    connections = []
    for row in cursor.fetchall():
        connections.append({
            "politician": row[0],
            "type": row[1],
            "strength": round(row[2], 2)
        })
    
    # 연결 통계
    cursor.execute('''
        SELECT connection_type, COUNT(*), AVG(strength)
        FROM connectivity_relations
        WHERE politician_a = ?
        GROUP BY connection_type
    ''', (politician_name,))
    
    stats = {}
    for row in cursor.fetchall():
        stats[row[0]] = {
            "count": row[1],
            "avg_strength": round(row[2], 2)
        }
    
    conn.close()
    
    return {
        "success": True,
        "data": {
            "politician": politician_name,
            "connections": connections,
            "statistics": stats
        }
    }

@app.get("/api/connectivity/family-tree")
async def get_family_tree():
    """패밀리 트리 이미지 생성"""
    try:
        # NetworkX 그래프 생성
        G = nx.Graph()
        
        conn = sqlite3.connect(service.db_path)
        cursor = conn.cursor()
        
        # 연결성 데이터 로드
        cursor.execute('''
            SELECT politician_a, politician_b, connection_type, strength
            FROM connectivity_relations
            WHERE strength > 0.5
            LIMIT 100
        ''')
        
        for row in cursor.fetchall():
            G.add_edge(row[0], row[1], weight=row[3], type=row[2])
        
        conn.close()
        
        if len(G.nodes()) == 0:
            return {"success": False, "error": "No connectivity data available"}
        
        # 그래프 시각화
        plt.figure(figsize=(20, 16))
        
        # 레이아웃 계산
        pos = nx.spring_layout(G, k=3, iterations=50)
        
        # 노드 크기 계산 (연결 수에 비례)
        node_sizes = [G.degree(node) * 50 + 100 for node in G.nodes()]
        
        # 노드 색상 계산 (정당별)
        node_colors = []
        for node in G.nodes():
            if node in service.politicians_data:
                party = service.politicians_data[node].get('party_name', '')
                if '국민의힘' in party:
                    node_colors.append('#ff6b6b')
                elif '더불어민주당' in party:
                    node_colors.append('#4ecdc4')
                elif '정의당' in party:
                    node_colors.append('#45b7d1')
                else:
                    node_colors.append('#96ceb4')
            else:
                node_colors.append('#feca57')
        
        # 그래프 그리기
        nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=node_colors, alpha=0.8)
        nx.draw_networkx_edges(G, pos, alpha=0.3, width=0.5)
        nx.draw_networkx_labels(G, pos, font_size=8, font_family='AppleGothic')
        
        plt.title('정치인 연결성 네트워크', fontsize=20, fontfamily='AppleGothic')
        plt.axis('off')
        
        # 이미지 저장
        image_path = "family_tree.png"
        plt.savefig(image_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return FileResponse(image_path, media_type="image/png")
        
    except Exception as e:
        logger.error(f"패밀리 트리 생성 실패: {e}")
        return {"success": False, "error": str(e)}

# ==================== 뉴스 API (가상 데이터) ====================

@app.get("/api/news")
async def get_news(limit: int = Query(10, ge=1, le=50)):
    """뉴스 목록 (가상 데이터)"""
    news_items = []
    politicians = list(service.politicians_data.keys())[:limit]
    
    for i, politician in enumerate(politicians):
        news_items.append({
            "id": i + 1,
            "title": f"{politician} 의원, 주요 정책 발표",
            "summary": f"{politician} 의원이 최근 주요 정책에 대한 입장을 발표했습니다.",
            "politician": politician,
            "date": "2025-01-16",
            "sentiment": "positive" if i % 3 == 0 else "neutral" if i % 3 == 1 else "negative",
            "source": "뉴스봇"
        })
    
    return {"success": True, "data": news_items}

@app.get("/api/news/trends")
async def get_news_trends():
    """뉴스 트렌드 (가상 데이터)"""
    trends = []
    for i in range(7):
        trends.append({
            "date": f"2025-01-{10 + i}",
            "positive": 15 + (i * 2),
            "negative": 8 + i,
            "neutral": 12 + (i % 3)
        })
    
    return {"success": True, "data": trends}

if __name__ == "__main__":
    print("🚀 NewsBot 통합 서버 시작 중...")
    print("📊 데이터 로드 완료")
    print("🌐 서버 주소: http://localhost:8000")
    print("📖 API 문서: http://localhost:8000/docs")
    print("=" * 50)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=True
    )