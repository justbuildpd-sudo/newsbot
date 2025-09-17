#!/usr/bin/env python3
"""
입법 의도 분석 API
고도화된 의도 분석 결과를 제공
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

app = FastAPI(title="입법 의도 분석 API", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class IntentAnalysisAPIService:
    def __init__(self, db_path: str = "data/legislative_data_standalone.db"):
        self.db_path = db_path
    
    def get_intent_analysis_summary(self) -> Dict:
        """의도 분석 요약 조회"""
        try:
            with open("data/intent_analysis_summary.json", 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"의도 분석 요약 조회 실패: {e}")
            return {"error": "의도 분석 요약을 찾을 수 없습니다"}
    
    def get_bill_intent_analysis(self, bill_no: str = None, limit: int = 50) -> List[Dict]:
        """법안별 의도 분석 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            query = '''
                SELECT 
                    b.bill_no, b.bill_name, b.proposer_name, b.proposal_date,
                    b.committee_name, b.bill_status,
                    i.political_intent_score, i.policy_intent_score,
                    i.legislative_strategy_score, i.timing_intent_score,
                    i.overall_intent_score, i.intent_category,
                    i.intent_keywords, i.intent_analysis
                FROM real_assembly_bills_22nd b
                JOIN bill_intent_analysis i ON b.bill_id = i.bill_id
                WHERE 1=1
            '''
            
            params = []
            if bill_no:
                query += ' AND b.bill_no = ?'
                params.append(bill_no)
            
            query += ' ORDER BY i.overall_intent_score DESC LIMIT ?'
            params.append(limit)
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            bills = []
            for row in results:
                intent_keywords = json.loads(row[12]) if row[12] else {}
                
                bills.append({
                    "bill_no": row[0],
                    "bill_name": row[1],
                    "proposer_name": row[2],
                    "proposal_date": row[3],
                    "committee_name": row[4],
                    "bill_status": row[5],
                    "intent_scores": {
                        "political": round(row[6], 2),
                        "policy": round(row[7], 2),
                        "legislative_strategy": round(row[8], 2),
                        "timing": round(row[9], 2),
                        "overall": round(row[10], 2)
                    },
                    "intent_category": row[11],
                    "intent_keywords": intent_keywords,
                    "intent_analysis": row[13]
                })
            
            return bills
            
        except Exception as e:
            logger.error(f"법안 의도 분석 조회 실패: {e}")
            raise HTTPException(status_code=500, detail="법안 의도 분석 조회 실패")
        finally:
            conn.close()
    
    def get_politician_intent_patterns(self, limit: int = 20) -> List[Dict]:
        """의원별 의도 패턴 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            query = '''
                SELECT 
                    politician_name, total_bills, political_intent_avg,
                    policy_intent_avg, legislative_strategy_avg,
                    timing_intent_avg, overall_intent_avg,
                    dominant_intent_category, intent_consistency_score,
                    political_agenda_score
                FROM politician_intent_patterns
                ORDER BY political_agenda_score DESC
                LIMIT ?
            '''
            
            cursor.execute(query, (limit,))
            results = cursor.fetchall()
            
            politicians = []
            for i, row in enumerate(results):
                politicians.append({
                    "rank": i + 1,
                    "politician_name": row[0],
                    "total_bills": row[1],
                    "intent_scores": {
                        "political": round(row[2], 2),
                        "policy": round(row[3], 2),
                        "legislative_strategy": round(row[4], 2),
                        "timing": round(row[5], 2),
                        "overall": round(row[6], 2)
                    },
                    "dominant_intent_category": row[7],
                    "intent_consistency_score": round(row[8], 2),
                    "political_agenda_score": round(row[9], 2)
                })
            
            return politicians
            
        except Exception as e:
            logger.error(f"의원 의도 패턴 조회 실패: {e}")
            raise HTTPException(status_code=500, detail="의원 의도 패턴 조회 실패")
        finally:
            conn.close()
    
    def get_politician_intent_detail(self, politician_name: str) -> Dict:
        """특정 의원의 상세 의도 분석"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 의원 기본 의도 패턴 정보
            cursor.execute('''
                SELECT 
                    politician_name, total_bills, political_intent_avg,
                    policy_intent_avg, legislative_strategy_avg,
                    timing_intent_avg, overall_intent_avg,
                    dominant_intent_category, intent_consistency_score,
                    political_agenda_score
                FROM politician_intent_patterns
                WHERE politician_name = ?
            ''', (politician_name,))
            
            result = cursor.fetchone()
            if not result:
                raise HTTPException(status_code=404, detail="의원을 찾을 수 없습니다")
            
            # 해당 의원의 법안별 의도 분석
            cursor.execute('''
                SELECT 
                    b.bill_no, b.bill_name, b.proposal_date, b.committee_name,
                    i.political_intent_score, i.policy_intent_score,
                    i.legislative_strategy_score, i.timing_intent_score,
                    i.overall_intent_score, i.intent_category,
                    i.intent_keywords, i.intent_analysis
                FROM real_assembly_bills_22nd b
                JOIN bill_intent_analysis i ON b.bill_id = i.bill_id
                WHERE b.proposer_name = ?
                ORDER BY i.overall_intent_score DESC
            ''', (politician_name,))
            
            bills = []
            for row in cursor.fetchall():
                intent_keywords = json.loads(row[10]) if row[10] else {}
                
                bills.append({
                    "bill_no": row[0],
                    "bill_name": row[1],
                    "proposal_date": row[2],
                    "committee_name": row[3],
                    "intent_scores": {
                        "political": round(row[4], 2),
                        "policy": round(row[5], 2),
                        "legislative_strategy": round(row[6], 2),
                        "timing": round(row[7], 2),
                        "overall": round(row[8], 2)
                    },
                    "intent_category": row[9],
                    "intent_keywords": intent_keywords,
                    "intent_analysis": row[11]
                })
            
            return {
                "politician_name": result[0],
                "total_bills": result[1],
                "intent_scores": {
                    "political": round(result[2], 2),
                    "policy": round(result[3], 2),
                    "legislative_strategy": round(result[4], 2),
                    "timing": round(result[5], 2),
                    "overall": round(result[6], 2)
                },
                "dominant_intent_category": result[7],
                "intent_consistency_score": round(result[8], 2),
                "political_agenda_score": round(result[9], 2),
                "bills": bills
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"의원 상세 의도 분석 조회 실패: {e}")
            raise HTTPException(status_code=500, detail="의원 상세 의도 분석 조회 실패")
        finally:
            conn.close()
    
    def get_bill_relationships(self, bill_no: str = None, limit: int = 50) -> List[Dict]:
        """법안 간 연관성 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            query = '''
                SELECT 
                    r.bill_id_1, r.bill_id_2, r.similarity_score,
                    r.relationship_type, r.common_keywords,
                    r.proposer_overlap, r.committee_overlap, r.timing_proximity,
                    b1.bill_no as bill1_no, b1.bill_name as bill1_name, b1.proposer_name as bill1_proposer,
                    b2.bill_no as bill2_no, b2.bill_name as bill2_name, b2.proposer_name as bill2_proposer
                FROM bill_relationships r
                JOIN real_assembly_bills_22nd b1 ON r.bill_id_1 = b1.bill_id
                JOIN real_assembly_bills_22nd b2 ON r.bill_id_2 = b2.bill_id
                WHERE 1=1
            '''
            
            params = []
            if bill_no:
                query += ' AND (b1.bill_no = ? OR b2.bill_no = ?)'
                params.extend([bill_no, bill_no])
            
            query += ' ORDER BY r.similarity_score DESC LIMIT ?'
            params.append(limit)
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            relationships = []
            for row in results:
                common_keywords = json.loads(row[4]) if row[4] else []
                
                relationships.append({
                    "bill1": {
                        "bill_no": row[8],
                        "bill_name": row[9],
                        "proposer_name": row[10]
                    },
                    "bill2": {
                        "bill_no": row[11],
                        "bill_name": row[12],
                        "proposer_name": row[13]
                    },
                    "similarity_score": round(row[2], 3),
                    "relationship_type": row[3],
                    "common_keywords": common_keywords,
                    "proposer_overlap": bool(row[5]),
                    "committee_overlap": bool(row[6]),
                    "timing_proximity_days": row[7]
                })
            
            return relationships
            
        except Exception as e:
            logger.error(f"법안 연관성 조회 실패: {e}")
            raise HTTPException(status_code=500, detail="법안 연관성 조회 실패")
        finally:
            conn.close()
    
    def get_intent_insights(self) -> Dict:
        """의도 분석 인사이트 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 의도 카테고리별 통계
            cursor.execute('''
                SELECT intent_category, COUNT(*) as count, AVG(overall_intent_score) as avg_score
                FROM bill_intent_analysis
                GROUP BY intent_category
                ORDER BY count DESC
            ''')
            intent_stats = {row[0]: {"count": row[1], "avg_score": round(row[2], 2)} for row in cursor.fetchall()}
            
            # 정치적 아젠다 상위 의원들
            cursor.execute('''
                SELECT politician_name, political_agenda_score, total_bills
                FROM politician_intent_patterns
                WHERE political_agenda_score > 0.5
                ORDER BY political_agenda_score DESC
                LIMIT 10
            ''')
            high_agenda_politicians = [{"name": row[0], "score": round(row[1], 2), "bills": row[2]} for row in cursor.fetchall()]
            
            # 의도 일관성 상위 의원들
            cursor.execute('''
                SELECT politician_name, intent_consistency_score, total_bills
                FROM politician_intent_patterns
                WHERE intent_consistency_score > 50
                ORDER BY intent_consistency_score DESC
                LIMIT 10
            ''')
            high_consistency_politicians = [{"name": row[0], "score": round(row[1], 2), "bills": row[2]} for row in cursor.fetchall()]
            
            # 가장 연관성이 높은 법안 쌍들
            cursor.execute('''
                SELECT 
                    b1.bill_name as bill1_name, b2.bill_name as bill2_name,
                    r.similarity_score, r.relationship_type
                FROM bill_relationships r
                JOIN real_assembly_bills_22nd b1 ON r.bill_id_1 = b1.bill_id
                JOIN real_assembly_bills_22nd b2 ON r.bill_id_2 = b2.bill_id
                ORDER BY r.similarity_score DESC
                LIMIT 10
            ''')
            top_relationships = [{"bill1": row[0], "bill2": row[1], "score": round(row[2], 3), "type": row[3]} for row in cursor.fetchall()]
            
            return {
                "intent_category_stats": intent_stats,
                "high_agenda_politicians": high_agenda_politicians,
                "high_consistency_politicians": high_consistency_politicians,
                "top_relationships": top_relationships
            }
            
        except Exception as e:
            logger.error(f"의도 분석 인사이트 조회 실패: {e}")
            raise HTTPException(status_code=500, detail="의도 분석 인사이트 조회 실패")
        finally:
            conn.close()

# API 서비스 인스턴스
api_service = IntentAnalysisAPIService()

@app.get("/api/intent/health")
async def health_check():
    """헬스 체크"""
    return {"status": "healthy", "message": "입법 의도 분석 API가 정상 작동 중입니다"}

@app.get("/api/intent/summary")
async def get_intent_analysis_summary():
    """의도 분석 요약 조회"""
    return api_service.get_intent_analysis_summary()

@app.get("/api/intent/bills")
async def get_bill_intent_analysis(
    bill_no: str = Query(None, description="법안번호"),
    limit: int = Query(50, description="조회할 법안 수")
):
    """법안별 의도 분석 조회"""
    return api_service.get_bill_intent_analysis(bill_no, limit)

@app.get("/api/intent/politicians")
async def get_politician_intent_patterns(
    limit: int = Query(20, description="조회할 의원 수")
):
    """의원별 의도 패턴 조회"""
    return api_service.get_politician_intent_patterns(limit)

@app.get("/api/intent/politician/{politician_name}")
async def get_politician_intent_detail(politician_name: str):
    """특정 의원의 상세 의도 분석"""
    return api_service.get_politician_intent_detail(politician_name)

@app.get("/api/intent/relationships")
async def get_bill_relationships(
    bill_no: str = Query(None, description="법안번호"),
    limit: int = Query(50, description="조회할 연관성 수")
):
    """법안 간 연관성 조회"""
    return api_service.get_bill_relationships(bill_no, limit)

@app.get("/api/intent/insights")
async def get_intent_insights():
    """의도 분석 인사이트 조회"""
    return api_service.get_intent_insights()

if __name__ == "__main__":
    import uvicorn
    print("🚀 입법 의도 분석 API 서버 시작 중...")
    print("🌐 서버 주소: http://localhost:8007")
    print("📖 API 문서: http://localhost:8007/docs")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8007)
