#!/usr/bin/env python3
"""
연결성 시각화 API
3단계(위젯)와 5단계(보고서) 연결성 시각화 제공
"""

import sqlite3
import json
import logging
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Optional
from connectivity_visualizer import ConnectivityVisualizer

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="연결성 시각화 API", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectivityAPIService:
    def __init__(self, db_path: str = "data/legislative_data_standalone.db"):
        self.db_path = db_path
        self.visualizer = ConnectivityVisualizer(db_path)
    
    def get_connectivity_ranking(self, limit: int = 20) -> List[Dict]:
        """연결성 랭킹 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT politician_name, connectivity_score, total_connections,
                       legislative_connections, committee_connections, political_connections
                FROM basic_connectivity_analysis
                ORDER BY connectivity_score DESC
                LIMIT ?
            ''', (limit,))
            
            results = cursor.fetchall()
            
            ranking = []
            for i, row in enumerate(results):
                ranking.append({
                    "rank": i + 1,
                    "politician_name": row[0],
                    "connectivity_score": round(row[1], 2),
                    "total_connections": row[2],
                    "connection_breakdown": {
                        "legislative": row[3],
                        "committee": row[4],
                        "political": row[5]
                    }
                })
            
            return ranking
            
        except Exception as e:
            logger.error(f"연결성 랭킹 조회 실패: {e}")
            raise HTTPException(status_code=500, detail="연결성 랭킹 조회 실패")
        finally:
            conn.close()
    
    def get_politician_connectivity(self, politician_name: str) -> Dict:
        """특정 정치인의 연결성 정보 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT politician_name, connectivity_score, total_connections,
                       legislative_connections, committee_connections, political_connections,
                       main_connections
                FROM basic_connectivity_analysis
                WHERE politician_name = ?
            ''', (politician_name,))
            
            result = cursor.fetchone()
            if not result:
                raise HTTPException(status_code=404, detail="정치인을 찾을 수 없습니다")
            
            main_connections = json.loads(result[6]) if result[6] else []
            
            return {
                "politician_name": result[0],
                "connectivity_score": round(result[1], 2),
                "total_connections": result[2],
                "connection_breakdown": {
                    "legislative": result[3],
                    "committee": result[4],
                    "political": result[5]
                },
                "main_connections": main_connections
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"정치인 연결성 조회 실패: {e}")
            raise HTTPException(status_code=500, detail="정치인 연결성 조회 실패")
        finally:
            conn.close()
    
    def get_widget_visualization(self, politician_name: str) -> Dict:
        """위젯용 3단계 연결성 시각화"""
        try:
            result = self.visualizer.create_widget_visualization(politician_name, 3)
            return result
        except Exception as e:
            logger.error(f"위젯 시각화 생성 실패: {e}")
            raise HTTPException(status_code=500, detail="위젯 시각화 생성 실패")
    
    def get_report_visualization(self, politician_name: str) -> Dict:
        """보고서용 5단계 연결성 시각화"""
        try:
            result = self.visualizer.create_report_visualization(politician_name, 5)
            return result
        except Exception as e:
            logger.error(f"보고서 시각화 생성 실패: {e}")
            raise HTTPException(status_code=500, detail="보고서 시각화 생성 실패")
    
    def get_connectivity_statistics(self) -> Dict:
        """연결성 통계 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 전체 통계
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_politicians,
                    AVG(connectivity_score) as avg_connectivity,
                    MAX(connectivity_score) as max_connectivity,
                    MIN(connectivity_score) as min_connectivity,
                    AVG(total_connections) as avg_connections,
                    AVG(legislative_connections) as avg_legislative,
                    AVG(committee_connections) as avg_committee,
                    AVG(political_connections) as avg_political
                FROM basic_connectivity_analysis
            ''')
            
            stats = cursor.fetchone()
            
            # 연결성 점수 구간별 분포
            cursor.execute('''
                SELECT 
                    CASE 
                        WHEN connectivity_score >= 80 THEN '80점 이상'
                        WHEN connectivity_score >= 60 THEN '60-79점'
                        WHEN connectivity_score >= 40 THEN '40-59점'
                        WHEN connectivity_score >= 20 THEN '20-39점'
                        ELSE '20점 미만'
                    END as score_range,
                    COUNT(*) as count
                FROM basic_connectivity_analysis
                GROUP BY score_range
                ORDER BY MIN(connectivity_score) DESC
            ''')
            
            score_distribution = {row[0]: row[1] for row in cursor.fetchall()}
            
            # 연결 유형별 평균
            cursor.execute('''
                SELECT 
                    AVG(legislative_connections) as avg_legislative,
                    AVG(committee_connections) as avg_committee,
                    AVG(political_connections) as avg_political
                FROM basic_connectivity_analysis
            ''')
            
            connection_type_stats = cursor.fetchone()
            
            return {
                "total_politicians": stats[0],
                "average_scores": {
                    "connectivity": round(stats[1], 2),
                    "max_connectivity": round(stats[2], 2),
                    "min_connectivity": round(stats[3], 2)
                },
                "average_connections": {
                    "total": round(stats[4], 2),
                    "legislative": round(stats[5], 2),
                    "committee": round(stats[6], 2),
                    "political": round(stats[7], 2)
                },
                "score_distribution": score_distribution,
                "connection_type_averages": {
                    "legislative": round(connection_type_stats[0], 2),
                    "committee": round(connection_type_stats[1], 2),
                    "political": round(connection_type_stats[2], 2)
                }
            }
            
        except Exception as e:
            logger.error(f"연결성 통계 조회 실패: {e}")
            raise HTTPException(status_code=500, detail="연결성 통계 조회 실패")
        finally:
            conn.close()

# API 서비스 인스턴스
api_service = ConnectivityAPIService()

@app.get("/api/connectivity/health")
async def health_check():
    """헬스 체크"""
    return {"status": "healthy", "message": "연결성 시각화 API가 정상 작동 중입니다"}

@app.get("/api/connectivity/ranking")
async def get_connectivity_ranking(
    limit: int = Query(20, description="조회할 정치인 수")
):
    """연결성 랭킹 조회"""
    return api_service.get_connectivity_ranking(limit)

@app.get("/api/connectivity/politician/{politician_name}")
async def get_politician_connectivity(politician_name: str):
    """특정 정치인의 연결성 정보 조회"""
    return api_service.get_politician_connectivity(politician_name)

@app.get("/api/connectivity/widget/{politician_name}")
async def get_widget_visualization(politician_name: str):
    """위젯용 3단계 연결성 시각화"""
    return api_service.get_widget_visualization(politician_name)

@app.get("/api/connectivity/report/{politician_name}")
async def get_report_visualization(politician_name: str):
    """보고서용 5단계 연결성 시각화"""
    return api_service.get_report_visualization(politician_name)

@app.get("/api/connectivity/statistics")
async def get_connectivity_statistics():
    """연결성 통계 조회"""
    return api_service.get_connectivity_statistics()

if __name__ == "__main__":
    import uvicorn
    print("🚀 연결성 시각화 API 서버 시작 중...")
    print("🌐 서버 주소: http://localhost:8009")
    print("📖 API 문서: http://localhost:8009/docs")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8009)