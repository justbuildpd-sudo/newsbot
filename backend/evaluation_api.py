#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
정치인 평가 API 서비스
종합적인 정치인 평가 결과를 제공하는 API
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sqlite3
import json
from typing import Dict, List, Optional
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Politician Evaluation API",
    version="1.0.0",
    description="종합적인 정치인 평가 및 랭킹 API"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 데이터베이스 경로
DB_PATH = "practical_evaluation.db"

def get_db_connection():
    """데이터베이스 연결"""
    return sqlite3.connect(DB_PATH)

@app.get("/")
async def root():
    return {"message": "Politician Evaluation API", "status": "running"}

@app.get("/api/evaluation/ranking")
async def get_politician_ranking(limit: int = 50, party: Optional[str] = None):
    """정치인 랭킹 조회"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT politician_name, party, district, committee, total_score, rank,
                   news_mention_score, news_sentiment_score, news_trend_score,
                   bill_sponsor_score, bill_co_sponsor_score, bill_success_rate,
                   bill_pass_rate, bill_impact_score, bill_quality_score,
                   connectivity_score, influence_score, collaboration_score
            FROM politician_evaluation
        '''
        
        params = []
        if party:
            query += " WHERE party = ?"
            params.append(party)
        
        query += " ORDER BY total_score DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        politicians = []
        for row in results:
            politicians.append({
                "rank": row[5],
                "name": row[0],
                "party": row[1],
                "district": row[2],
                "committee": row[3],
                "total_score": row[4],
                "scores": {
                    "news": {
                        "mention": row[6],
                        "sentiment": row[7],
                        "trend": row[8]
                    },
                    "bill_sponsor": {
                        "main": row[9],
                        "co": row[10],
                        "success_rate": row[11]
                    },
                    "bill_result": {
                        "pass_rate": row[12],
                        "impact": row[13],
                        "quality": row[14]
                    },
                    "connectivity": {
                        "total": row[15],
                        "influence": row[16],
                        "collaboration": row[17]
                    }
                }
            })
        
        conn.close()
        
        return {
            "success": True,
            "data": {
                "politicians": politicians,
                "total_count": len(politicians),
                "filter": {"party": party, "limit": limit}
            }
        }
        
    except Exception as e:
        logger.error(f"랭킹 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/evaluation/politician/{politician_name}")
async def get_politician_detail(politician_name: str):
    """특정 정치인 상세 정보 조회"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM politician_evaluation
            WHERE politician_name = ?
        ''', (politician_name,))
        
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="정치인을 찾을 수 없습니다")
        
        conn.close()
        
        return {
            "success": True,
            "data": {
                "name": result[1],
                "party": result[2],
                "district": result[3],
                "committee": result[4],
                "rank": result[18],
                "total_score": result[17],
                "scores": {
                    "news": {
                        "mention": result[5],
                        "sentiment": result[6],
                        "trend": result[7]
                    },
                    "bill_sponsor": {
                        "main": result[8],
                        "co": result[9],
                        "success_rate": result[10]
                    },
                    "bill_result": {
                        "pass_rate": result[11],
                        "impact": result[12],
                        "quality": result[13]
                    },
                    "connectivity": {
                        "total": result[14],
                        "influence": result[15],
                        "collaboration": result[16]
                    }
                }
            }
        }
        
    except Exception as e:
        logger.error(f"정치인 상세 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/evaluation/party-stats")
async def get_party_statistics():
    """정당별 통계 조회"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 정당별 평균 점수
        cursor.execute('''
            SELECT party, COUNT(*) as count, AVG(total_score) as avg_score,
                   MAX(total_score) as max_score, MIN(total_score) as min_score
            FROM politician_evaluation
            GROUP BY party
            ORDER BY avg_score DESC
        ''')
        
        party_stats = []
        for row in cursor.fetchall():
            party_stats.append({
                "party": row[0],
                "count": row[1],
                "avg_score": round(row[2], 2),
                "max_score": round(row[3], 2),
                "min_score": round(row[4], 2)
            })
        
        # 정당별 상위 3명
        cursor.execute('''
            SELECT party, politician_name, total_score, rank
            FROM politician_evaluation
            WHERE rank IN (
                SELECT MIN(rank) FROM politician_evaluation GROUP BY party
                UNION
                SELECT MIN(rank) FROM politician_evaluation 
                WHERE rank NOT IN (SELECT MIN(rank) FROM politician_evaluation GROUP BY party)
                GROUP BY party
                UNION
                SELECT MIN(rank) FROM politician_evaluation 
                WHERE rank NOT IN (
                    SELECT MIN(rank) FROM politician_evaluation GROUP BY party
                    UNION
                    SELECT MIN(rank) FROM politician_evaluation 
                    WHERE rank NOT IN (SELECT MIN(rank) FROM politician_evaluation GROUP BY party)
                    GROUP BY party
                )
                GROUP BY party
            )
            ORDER BY party, rank
        ''')
        
        party_leaders = {}
        for row in cursor.fetchall():
            party = row[0]
            if party not in party_leaders:
                party_leaders[party] = []
            party_leaders[party].append({
                "name": row[1],
                "score": round(row[2], 2),
                "rank": row[3]
            })
        
        conn.close()
        
        return {
            "success": True,
            "data": {
                "party_statistics": party_stats,
                "party_leaders": party_leaders
            }
        }
        
    except Exception as e:
        logger.error(f"정당 통계 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/evaluation/committee-stats")
async def get_committee_statistics():
    """위원회별 통계 조회"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 위원회별 평균 점수
        cursor.execute('''
            SELECT committee, COUNT(*) as count, AVG(total_score) as avg_score
            FROM politician_evaluation
            WHERE committee IS NOT NULL AND committee != ''
            GROUP BY committee
            ORDER BY avg_score DESC
        ''')
        
        committee_stats = []
        for row in cursor.fetchall():
            committee_stats.append({
                "committee": row[0],
                "count": row[1],
                "avg_score": round(row[2], 2)
            })
        
        conn.close()
        
        return {
            "success": True,
            "data": {
                "committee_statistics": committee_stats
            }
        }
        
    except Exception as e:
        logger.error(f"위원회 통계 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/evaluation/score-distribution")
async def get_score_distribution():
    """점수 분포 조회"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 점수 구간별 분포
        cursor.execute('''
            SELECT 
                CASE 
                    WHEN total_score >= 8 THEN '8-10점'
                    WHEN total_score >= 6 THEN '6-8점'
                    WHEN total_score >= 4 THEN '4-6점'
                    WHEN total_score >= 2 THEN '2-4점'
                    ELSE '0-2점'
                END as score_range,
                COUNT(*) as count
            FROM politician_evaluation
            GROUP BY 
                CASE 
                    WHEN total_score >= 8 THEN '8-10점'
                    WHEN total_score >= 6 THEN '6-8점'
                    WHEN total_score >= 4 THEN '4-6점'
                    WHEN total_score >= 2 THEN '2-4점'
                    ELSE '0-2점'
                END
            ORDER BY MIN(total_score) DESC
        ''')
        
        distribution = []
        for row in cursor.fetchall():
            distribution.append({
                "range": row[0],
                "count": row[1]
            })
        
        # 전체 통계
        cursor.execute('''
            SELECT 
                COUNT(*) as total_count,
                AVG(total_score) as avg_score,
                MAX(total_score) as max_score,
                MIN(total_score) as min_score
            FROM politician_evaluation
        ''')
        
        stats = cursor.fetchone()
        
        # 표준편차 수동 계산
        cursor.execute('SELECT total_score FROM politician_evaluation')
        scores = [row[0] for row in cursor.fetchall()]
        
        if len(scores) > 1:
            mean = sum(scores) / len(scores)
            variance = sum((x - mean) ** 2 for x in scores) / (len(scores) - 1)
            std_score = variance ** 0.5
        else:
            std_score = 0.0
        
        conn.close()
        
        return {
            "success": True,
            "data": {
                "distribution": distribution,
                "statistics": {
                    "total_count": stats[0],
                    "avg_score": round(stats[1], 2),
                    "max_score": round(stats[2], 2),
                    "min_score": round(stats[3], 2),
                    "std_score": round(std_score, 2)
                }
            }
        }
        
    except Exception as e:
        logger.error(f"점수 분포 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/evaluation/health")
async def health_check():
    """헬스 체크"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM politician_evaluation')
        politician_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT AVG(total_score) FROM politician_evaluation')
        avg_score = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "status": "healthy",
            "politician_count": politician_count,
            "avg_score": round(avg_score, 2) if avg_score else 0,
            "database": "connected"
        }
        
    except Exception as e:
        logger.error(f"헬스 체크 실패: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
