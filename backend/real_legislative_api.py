#!/usr/bin/env python3
"""
실제 22대 국회 입법 데이터 API
수집된 실제 데이터를 기반으로 정교한 분석 제공
"""

import sqlite3
import json
import logging
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Optional
import statistics

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="실제 22대 국회 입법 데이터 API", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RealLegislativeAPIService:
    def __init__(self, db_path: str = "newsbot_stable.db"):
        self.db_path = db_path
    
    def get_legislative_stats(self) -> Dict:
        """전체 입법 통계 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 전체 법안 수
            cursor.execute('SELECT COUNT(*) FROM real_assembly_bills_22nd')
            total_bills = cursor.fetchone()[0]
            
            # 의원 수
            cursor.execute('SELECT COUNT(*) FROM real_politician_legislative_stats_22nd')
            total_politicians = cursor.fetchone()[0]
            
            # 카테고리별 법안 수
            cursor.execute('''
                SELECT a.bill_category, COUNT(*) as count
                FROM real_bill_analysis_22nd a
                JOIN real_assembly_bills_22nd b ON a.bill_id = b.bill_id
                GROUP BY a.bill_category
                ORDER BY count DESC
            ''')
            category_stats = {row[0]: row[1] for row in cursor.fetchall()}
            
            # 통과율 통계
            cursor.execute('''
                SELECT 
                    AVG(passage_rate) as avg_passage_rate,
                    MIN(passage_rate) as min_passage_rate,
                    MAX(passage_rate) as max_passage_rate
                FROM real_politician_legislative_stats_22nd
                WHERE passage_rate > 0
            ''')
            passage_stats = cursor.fetchone()
            
            return {
                "total_bills": total_bills,
                "total_politicians": total_politicians,
                "category_distribution": category_stats,
                "passage_rate_stats": {
                    "average": round(passage_stats[0], 2) if passage_stats[0] else 0,
                    "minimum": round(passage_stats[1], 2) if passage_stats[1] else 0,
                    "maximum": round(passage_stats[2], 2) if passage_stats[2] else 0
                }
            }
            
        except Exception as e:
            logger.error(f"입법 통계 조회 실패: {e}")
            raise HTTPException(status_code=500, detail="입법 통계 조회 실패")
        finally:
            conn.close()
    
    def get_politician_ranking(self, limit: int = 20, party: str = None) -> List[Dict]:
        """의원별 입법성과 랭킹 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            query = '''
                SELECT 
                    p.politician_name,
                    p.total_bills,
                    p.policy_bills,
                    p.administrative_bills,
                    p.technical_bills,
                    p.bill_cleanup_bills,
                    p.substantial_bills,
                    p.passage_rate,
                    p.avg_policy_impact,
                    p.avg_legislative_quality,
                    p.avg_public_interest,
                    p.avg_innovation,
                    p.total_performance_score,
                    p.ranking
                FROM real_politician_legislative_stats_22nd p
            '''
            
            params = []
            if party:
                # 정당 정보가 있다면 추가 (현재는 기본 데이터만)
                pass
            
            query += ' ORDER BY p.total_performance_score DESC LIMIT ?'
            params.append(limit)
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            ranking = []
            for i, row in enumerate(results):
                ranking.append({
                    "rank": i + 1,
                    "politician_name": row[0],
                    "total_bills": row[1],
                    "policy_bills": row[2],
                    "administrative_bills": row[3],
                    "technical_bills": row[4],
                    "bill_cleanup_bills": row[5],
                    "substantial_bills": row[6],
                    "passage_rate": round(row[7], 2),
                    "avg_policy_impact": round(row[8], 2),
                    "avg_legislative_quality": round(row[9], 2),
                    "avg_public_interest": round(row[10], 2),
                    "avg_innovation": round(row[11], 2),
                    "total_performance_score": round(row[12], 2),
                    "original_ranking": row[13]
                })
            
            return ranking
            
        except Exception as e:
            logger.error(f"의원 랭킹 조회 실패: {e}")
            raise HTTPException(status_code=500, detail="의원 랭킹 조회 실패")
        finally:
            conn.close()
    
    def get_politician_detail(self, politician_name: str) -> Dict:
        """특정 의원의 상세 입법성과 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 의원 기본 정보
            cursor.execute('''
                SELECT 
                    politician_name, total_bills, policy_bills, administrative_bills,
                    technical_bills, bill_cleanup_bills, substantial_bills,
                    passage_rate, avg_policy_impact, avg_legislative_quality,
                    avg_public_interest, avg_innovation, total_performance_score, ranking
                FROM real_politician_legislative_stats_22nd
                WHERE politician_name = ?
            ''', (politician_name,))
            
            result = cursor.fetchone()
            if not result:
                raise HTTPException(status_code=404, detail="의원을 찾을 수 없습니다")
            
            # 해당 의원의 법안 목록
            cursor.execute('''
                SELECT 
                    b.bill_no, b.bill_name, b.bill_type, b.proposal_date,
                    b.committee_name, b.bill_status, a.bill_category,
                    a.policy_impact_score, a.legislative_quality_score,
                    a.public_interest_score, a.innovation_score,
                    a.total_analysis_score
                FROM real_assembly_bills_22nd b
                JOIN real_bill_analysis_22nd a ON b.bill_id = a.bill_id
                WHERE b.proposer_name = ?
                ORDER BY b.proposal_date DESC
            ''', (politician_name,))
            
            bills = []
            for row in cursor.fetchall():
                bills.append({
                    "bill_no": row[0],
                    "bill_name": row[1],
                    "bill_type": row[2],
                    "proposal_date": row[3],
                    "committee_name": row[4],
                    "bill_status": row[5],
                    "bill_category": row[6],
                    "policy_impact_score": round(row[7], 2),
                    "legislative_quality_score": round(row[8], 2),
                    "public_interest_score": round(row[9], 2),
                    "innovation_score": round(row[10], 2),
                    "total_analysis_score": round(row[11], 2)
                })
            
            return {
                "politician_name": result[0],
                "total_bills": result[1],
                "policy_bills": result[2],
                "administrative_bills": result[3],
                "technical_bills": result[4],
                "bill_cleanup_bills": result[5],
                "substantial_bills": result[6],
                "passage_rate": round(result[7], 2),
                "avg_policy_impact": round(result[8], 2),
                "avg_legislative_quality": round(result[9], 2),
                "avg_public_interest": round(result[10], 2),
                "avg_innovation": round(result[11], 2),
                "total_performance_score": round(result[12], 2),
                "ranking": result[13],
                "bills": bills
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"의원 상세 정보 조회 실패: {e}")
            raise HTTPException(status_code=500, detail="의원 상세 정보 조회 실패")
        finally:
            conn.close()
    
    def get_bill_analysis(self, bill_no: str = None, category: str = None, limit: int = 50) -> List[Dict]:
        """법안 분석 결과 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            query = '''
                SELECT 
                    b.bill_no, b.bill_name, b.proposer_name, b.proposal_date,
                    b.committee_name, b.bill_status, a.bill_category,
                    a.policy_impact_score, a.legislative_quality_score,
                    a.public_interest_score, a.innovation_score,
                    a.complexity_score, a.urgency_score, a.total_analysis_score
                FROM real_assembly_bills_22nd b
                JOIN real_bill_analysis_22nd a ON b.bill_id = a.bill_id
                WHERE 1=1
            '''
            
            params = []
            if bill_no:
                query += ' AND b.bill_no = ?'
                params.append(bill_no)
            
            if category:
                query += ' AND a.bill_category = ?'
                params.append(category)
            
            query += ' ORDER BY a.total_analysis_score DESC LIMIT ?'
            params.append(limit)
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            bills = []
            for row in results:
                bills.append({
                    "bill_no": row[0],
                    "bill_name": row[1],
                    "proposer_name": row[2],
                    "proposal_date": row[3],
                    "committee_name": row[4],
                    "bill_status": row[5],
                    "bill_category": row[6],
                    "policy_impact_score": round(row[7], 2),
                    "legislative_quality_score": round(row[8], 2),
                    "public_interest_score": round(row[9], 2),
                    "innovation_score": round(row[10], 2),
                    "complexity_score": round(row[11], 2),
                    "urgency_score": round(row[12], 2),
                    "total_analysis_score": round(row[13], 2)
                })
            
            return bills
            
        except Exception as e:
            logger.error(f"법안 분석 조회 실패: {e}")
            raise HTTPException(status_code=500, detail="법안 분석 조회 실패")
        finally:
            conn.close()

# API 서비스 인스턴스
api_service = RealLegislativeAPIService()

@app.get("/api/real-legislative/health")
async def health_check():
    """헬스 체크"""
    return {"status": "healthy", "message": "실제 22대 국회 입법 데이터 API가 정상 작동 중입니다"}

@app.get("/api/real-legislative/stats")
async def get_legislative_stats():
    """전체 입법 통계 조회"""
    return api_service.get_legislative_stats()

@app.get("/api/real-legislative/ranking")
async def get_politician_ranking(
    limit: int = Query(20, description="조회할 의원 수"),
    party: str = Query(None, description="정당 필터")
):
    """의원별 입법성과 랭킹 조회"""
    return api_service.get_politician_ranking(limit, party)

@app.get("/api/real-legislative/politician/{politician_name}")
async def get_politician_detail(politician_name: str):
    """특정 의원의 상세 입법성과 조회"""
    return api_service.get_politician_detail(politician_name)

@app.get("/api/real-legislative/bills")
async def get_bill_analysis(
    bill_no: str = Query(None, description="법안번호"),
    category: str = Query(None, description="법안 카테고리"),
    limit: int = Query(50, description="조회할 법안 수")
):
    """법안 분석 결과 조회"""
    return api_service.get_bill_analysis(bill_no, category, limit)

if __name__ == "__main__":
    import uvicorn
    print("🚀 실제 22대 국회 입법 데이터 API 서버 시작 중...")
    print("🌐 서버 주소: http://localhost:8005")
    print("📖 API 문서: http://localhost:8005/docs")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8005)

