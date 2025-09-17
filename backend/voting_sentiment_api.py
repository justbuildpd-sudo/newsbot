#!/usr/bin/env python3
"""
표심 분석 API 서버
정치인의 표심, 언론 노출, 입법 성과, 소통 활동, 정치적 일관성을 제공하는 API
"""

import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sqlite3
import logging
from typing import List, Dict, Optional

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title="표심 분석 API",
    description="정치인 표심 분석 및 평가 시스템",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VotingSentimentAPIService:
    def __init__(self, db_path: str = "newsbot_stable.db"):
        self.db_path = db_path
    
    def get_politician_ranking(self, limit: int = 20) -> List[Dict]:
        """정치인 표심 점수 랭킹"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                p.name, p.party_name, p.district,
                v.voting_sentiment_index, v.media_exposure_index,
                v.legislative_performance_index, v.communication_activity_index,
                v.political_consistency_index, v.total_voting_score
            FROM voting_sentiment_scores v
            JOIN politicians p ON v.politician_name = p.name
            ORDER BY v.total_voting_score DESC
            LIMIT ?
        ''', (limit,))
        
        ranking = []
        for i, row in enumerate(cursor.fetchall()):
            ranking.append({
                "rank": i + 1,
                "name": row[0],
                "party": row[1] if row[1] else "정당정보없음",
                "district": row[2] if row[2] else "정보없음",
                "scores": {
                    "voting_sentiment": round(row[3], 2),
                    "media_exposure": round(row[4], 2),
                    "legislative_performance": round(row[5], 2),
                    "communication_activity": round(row[6], 2),
                    "political_consistency": round(row[7], 2),
                    "total": round(row[8], 2)
                }
            })
        
        conn.close()
        return ranking
    
    def get_politician_detail(self, politician_name: str) -> Dict:
        """개별 정치인 상세 표심 분석"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                p.name, p.party_name, p.district, p.committee,
                v.voting_sentiment_index, v.media_exposure_index,
                v.legislative_performance_index, v.communication_activity_index,
                v.political_consistency_index, v.total_voting_score,
                v.last_updated
            FROM voting_sentiment_scores v
            JOIN politicians p ON v.politician_name = p.name
            WHERE p.name = ?
        ''', (politician_name,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return {
            "name": row[0],
            "party": row[1] if row[1] else "정당정보없음",
            "district": row[2] if row[2] else "정보없음",
            "committee": row[3] if row[3] else "정보없음",
            "scores": {
                "voting_sentiment": {
                    "value": round(row[4], 2),
                    "description": "표심 지수 - 선거구민의 지지도와 정치적 신뢰도"
                },
                "media_exposure": {
                    "value": round(row[5], 2),
                    "description": "언론 노출 지수 - 언론에 노출된 빈도와 질"
                },
                "legislative_performance": {
                    "value": round(row[6], 2),
                    "description": "입법 성과 지수 - 입법 활동의 양과 질"
                },
                "communication_activity": {
                    "value": round(row[7], 2),
                    "description": "소통 활동 지수 - 시민과의 소통 활동"
                },
                "political_consistency": {
                    "value": round(row[8], 2),
                    "description": "정치적 일관성 지수 - 주요 이슈에 대한 입장 일관성"
                },
                "total": {
                    "value": round(row[9], 2),
                    "description": "종합 표심 점수"
                }
            },
            "last_updated": row[10]
        }
    
    def get_party_statistics(self) -> List[Dict]:
        """정당별 표심 통계"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                p.party_name,
                COUNT(p.name) as member_count,
                AVG(v.total_voting_score) as avg_score,
                MAX(v.total_voting_score) as max_score,
                MIN(v.total_voting_score) as min_score,
                AVG(v.voting_sentiment_index) as avg_voting_sentiment,
                AVG(v.media_exposure_index) as avg_media_exposure,
                AVG(v.legislative_performance_index) as avg_legislative_performance,
                AVG(v.communication_activity_index) as avg_communication_activity,
                AVG(v.political_consistency_index) as avg_political_consistency
            FROM voting_sentiment_scores v
            JOIN politicians p ON v.politician_name = p.name
            GROUP BY p.party_name
            ORDER BY AVG(v.total_voting_score) DESC
        ''')
        
        party_stats = []
        for row in cursor.fetchall():
            party_stats.append({
                "party": row[0] if row[0] else "정당정보없음",
                "member_count": row[1],
                "scores": {
                    "total": {
                        "average": round(row[2], 2),
                        "max": round(row[3], 2),
                        "min": round(row[4], 2)
                    },
                    "voting_sentiment": round(row[5], 2),
                    "media_exposure": round(row[6], 2),
                    "legislative_performance": round(row[7], 2),
                    "communication_activity": round(row[8], 2),
                    "political_consistency": round(row[9], 2)
                }
            })
        
        conn.close()
        return party_stats
    
    def get_score_distribution(self) -> Dict:
        """표심 점수 분포"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT total_voting_score FROM voting_sentiment_scores')
        scores = [row[0] for row in cursor.fetchall()]
        
        # 점수 분포 계산
        distribution = {}
        for score in scores:
            if score >= 55: distribution["55-60"] = distribution.get("55-60", 0) + 1
            elif score >= 50: distribution["50-55"] = distribution.get("50-55", 0) + 1
            elif score >= 45: distribution["45-50"] = distribution.get("45-50", 0) + 1
            elif score >= 40: distribution["40-45"] = distribution.get("40-45", 0) + 1
            else: distribution["40미만"] = distribution.get("40미만", 0) + 1
        
        # 정렬된 범위로 변환
        sorted_distribution = []
        for r in ["55-60", "50-55", "45-50", "40-45", "40미만"]:
            sorted_distribution.append({"range": r, "count": distribution.get(r, 0)})
        
        # 통계 계산
        total_count = len(scores)
        avg_score = sum(scores) / len(scores) if scores else 0
        max_score = max(scores) if scores else 0
        min_score = min(scores) if scores else 0
        
        conn.close()
        
        return {
            "distribution": sorted_distribution,
            "statistics": {
                "total_count": total_count,
                "avg_score": round(avg_score, 2),
                "max_score": round(max_score, 2),
                "min_score": round(min_score, 2)
            }
        }

# 서비스 인스턴스 생성
service = VotingSentimentAPIService()

# ==================== API 엔드포인트 ====================

@app.get("/api/voting-sentiment/health")
async def get_health():
    """서버 상태 확인"""
    conn = sqlite3.connect(service.db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM voting_sentiment_scores")
    politician_count = cursor.fetchone()[0]
    cursor.execute("SELECT AVG(total_voting_score) FROM voting_sentiment_scores")
    avg_score = cursor.fetchone()[0]
    conn.close()
    
    return {
        "status": "healthy",
        "politician_count": politician_count,
        "avg_voting_score": round(avg_score, 2) if avg_score else 0,
        "version": "1.0.0"
    }

@app.get("/api/voting-sentiment/ranking")
async def get_politician_ranking(limit: int = Query(20, ge=1, le=100)):
    """정치인 표심 점수 랭킹"""
    try:
        ranking = service.get_politician_ranking(limit)
        return {
            "success": True,
            "data": {
                "ranking": ranking,
                "total_count": len(ranking)
            }
        }
    except Exception as e:
        logger.error(f"랭킹 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="랭킹 조회에 실패했습니다.")

@app.get("/api/voting-sentiment/politician/{politician_name}")
async def get_politician_detail(politician_name: str):
    """개별 정치인 상세 표심 분석"""
    try:
        detail = service.get_politician_detail(politician_name)
        if not detail:
            raise HTTPException(status_code=404, detail="정치인을 찾을 수 없습니다.")
        
        return {
            "success": True,
            "data": detail
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"정치인 상세 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="정치인 상세 조회에 실패했습니다.")

@app.get("/api/voting-sentiment/party-stats")
async def get_party_statistics():
    """정당별 표심 통계"""
    try:
        party_stats = service.get_party_statistics()
        return {
            "success": True,
            "data": {
                "party_statistics": party_stats
            }
        }
    except Exception as e:
        logger.error(f"정당 통계 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="정당 통계 조회에 실패했습니다.")

@app.get("/api/voting-sentiment/score-distribution")
async def get_score_distribution():
    """표심 점수 분포"""
    try:
        distribution = service.get_score_distribution()
        return {
            "success": True,
            "data": distribution
        }
    except Exception as e:
        logger.error(f"점수 분포 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="점수 분포 조회에 실패했습니다.")

if __name__ == "__main__":
    print("🚀 표심 분석 API 서버 시작 중...")
    print("🌐 서버 주소: http://localhost:8004")
    print("📖 API 문서: http://localhost:8004/docs")
    print("=" * 50)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8004,
        log_level="info",
        access_log=True
    )

