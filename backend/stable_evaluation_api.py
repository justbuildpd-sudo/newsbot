#!/usr/bin/env python3
"""
안정적인 정치인 평가 API
API 없이도 작동하는 완전한 평가 지표 제공
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

app = FastAPI(title="안정적인 정치인 평가 API", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class StableEvaluationAPIService:
    def __init__(self, db_path: str = "data/legislative_data_standalone.db"):
        self.db_path = db_path
    
    def get_evaluation_summary(self) -> Dict:
        """평가 요약 조회"""
        try:
            with open("data/stable_evaluation_report.json", 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"평가 요약 조회 실패: {e}")
            return {"error": "평가 요약을 찾을 수 없습니다"}
    
    def get_politician_ranking(self, limit: int = 20, category: str = None) -> List[Dict]:
        """의원 랭킹 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            query = '''
                SELECT 
                    politician_name, total_bills, policy_bills, administrative_bills,
                    technical_bills, bill_cleanup_bills, substantial_bills, passage_rate,
                    avg_policy_impact, avg_legislative_quality, avg_public_interest,
                    avg_innovation, political_intent_score, policy_intent_score,
                    legislative_strategy_score, timing_intent_score, intent_consistency_score,
                    political_agenda_score, bill_diversity_score, committee_activity_score,
                    collaboration_score, total_evaluation_score, ranking, evaluation_category,
                    strengths, weaknesses, recommendations
                FROM stable_politician_evaluation
                WHERE 1=1
            '''
            
            params = []
            if category and category != "all":
                query += ' AND evaluation_category = ?'
                params.append(category)
            
            query += ' ORDER BY total_evaluation_score DESC LIMIT ?'
            params.append(limit)
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            ranking = []
            for row in results:
                strengths = json.loads(row[24]) if row[24] else []
                weaknesses = json.loads(row[25]) if row[25] else []
                recommendations = json.loads(row[26]) if row[26] else []
                
                ranking.append({
                    "rank": row[22],
                    "politician_name": row[0],
                    "total_bills": row[1],
                    "bill_breakdown": {
                        "policy_bills": row[2],
                        "administrative_bills": row[3],
                        "technical_bills": row[4],
                        "bill_cleanup_bills": row[5],
                        "substantial_bills": row[6]
                    },
                    "performance_scores": {
                        "passage_rate": round(row[7], 2),
                        "policy_impact": round(row[8], 2),
                        "legislative_quality": round(row[9], 2),
                        "public_interest": round(row[10], 2),
                        "innovation": round(row[11], 2)
                    },
                    "intent_scores": {
                        "political_intent": round(row[12], 2),
                        "policy_intent": round(row[13], 2),
                        "legislative_strategy": round(row[14], 2),
                        "timing_intent": round(row[15], 2),
                        "consistency": round(row[16], 2),
                        "political_agenda": round(row[17], 2)
                    },
                    "advanced_scores": {
                        "bill_diversity": round(row[18], 2),
                        "committee_activity": round(row[19], 2),
                        "collaboration": round(row[20], 2)
                    },
                    "total_evaluation_score": round(row[21], 2),
                    "evaluation_category": row[23],
                    "strengths": strengths,
                    "weaknesses": weaknesses,
                    "recommendations": recommendations
                })
            
            return ranking
            
        except Exception as e:
            logger.error(f"의원 랭킹 조회 실패: {e}")
            raise HTTPException(status_code=500, detail="의원 랭킹 조회 실패")
        finally:
            conn.close()
    
    def get_politician_detail(self, politician_name: str) -> Dict:
        """특정 의원의 상세 평가 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 기본 평가 정보
            cursor.execute('''
                SELECT 
                    politician_name, total_bills, policy_bills, administrative_bills,
                    technical_bills, bill_cleanup_bills, substantial_bills, passage_rate,
                    avg_policy_impact, avg_legislative_quality, avg_public_interest,
                    avg_innovation, political_intent_score, policy_intent_score,
                    legislative_strategy_score, timing_intent_score, intent_consistency_score,
                    political_agenda_score, bill_diversity_score, committee_activity_score,
                    collaboration_score, total_evaluation_score, ranking, evaluation_category,
                    strengths, weaknesses, recommendations
                FROM stable_politician_evaluation
                WHERE politician_name = ?
            ''', (politician_name,))
            
            result = cursor.fetchone()
            if not result:
                raise HTTPException(status_code=404, detail="의원을 찾을 수 없습니다")
            
            # 의원 프로필 정보
            cursor.execute('''
                SELECT party, district, committee, profile_image_url, birth_year,
                       education, career, major_achievements, political_orientation,
                       constituency_characteristics
                FROM politician_profiles
                WHERE politician_name = ?
            ''', (politician_name,))
            
            profile = cursor.fetchone()
            
            # 해당 의원의 법안 목록
            cursor.execute('''
                SELECT 
                    b.bill_no, b.bill_name, b.proposal_date, b.committee_name, b.bill_status,
                    a.bill_category, a.policy_impact_score, a.legislative_quality_score,
                    a.public_interest_score, a.innovation_score, a.total_analysis_score,
                    i.political_intent_score, i.policy_intent_score, i.legislative_strategy_score,
                    i.timing_intent_score, i.overall_intent_score, i.intent_category
                FROM real_assembly_bills_22nd b
                LEFT JOIN real_bill_analysis_22nd a ON b.bill_id = a.bill_id
                LEFT JOIN bill_intent_analysis i ON b.bill_id = i.bill_id
                WHERE b.proposer_name = ?
                ORDER BY b.proposal_date DESC
            ''', (politician_name,))
            
            bills = []
            for row in cursor.fetchall():
                bills.append({
                    "bill_no": row[0],
                    "bill_name": row[1],
                    "proposal_date": row[2],
                    "committee_name": row[3],
                    "bill_status": row[4],
                    "bill_category": row[5],
                    "analysis_scores": {
                        "policy_impact": round(row[6] or 0, 2),
                        "legislative_quality": round(row[7] or 0, 2),
                        "public_interest": round(row[8] or 0, 2),
                        "innovation": round(row[9] or 0, 2),
                        "total_analysis": round(row[10] or 0, 2)
                    },
                    "intent_scores": {
                        "political_intent": round(row[11] or 0, 2),
                        "policy_intent": round(row[12] or 0, 2),
                        "legislative_strategy": round(row[13] or 0, 2),
                        "timing_intent": round(row[14] or 0, 2),
                        "overall_intent": round(row[15] or 0, 2)
                    },
                    "intent_category": row[16]
                })
            
            strengths = json.loads(result[24]) if result[24] else []
            weaknesses = json.loads(result[25]) if result[25] else []
            recommendations = json.loads(result[26]) if result[26] else []
            
            return {
                "politician_name": result[0],
                "profile": {
                    "party": profile[0] if profile else "미분류",
                    "district": profile[1] if profile else "미분류",
                    "committee": profile[2] if profile else "미분류",
                    "profile_image_url": profile[3] if profile else "",
                    "birth_year": profile[4] if profile else None,
                    "education": profile[5] if profile else "",
                    "career": profile[6] if profile else "",
                    "major_achievements": profile[7] if profile else "",
                    "political_orientation": profile[8] if profile else "미분류",
                    "constituency_characteristics": profile[9] if profile else ""
                },
                "evaluation_summary": {
                    "total_bills": result[1],
                    "total_evaluation_score": round(result[21], 2),
                    "ranking": result[22],
                    "evaluation_category": result[23]
                },
                "bill_breakdown": {
                    "policy_bills": result[2],
                    "administrative_bills": result[3],
                    "technical_bills": result[4],
                    "bill_cleanup_bills": result[5],
                    "substantial_bills": result[6]
                },
                "performance_scores": {
                    "passage_rate": round(result[7], 2),
                    "policy_impact": round(result[8], 2),
                    "legislative_quality": round(result[9], 2),
                    "public_interest": round(result[10], 2),
                    "innovation": round(result[11], 2)
                },
                "intent_scores": {
                    "political_intent": round(result[12], 2),
                    "policy_intent": round(result[13], 2),
                    "legislative_strategy": round(result[14], 2),
                    "timing_intent": round(result[15], 2),
                    "consistency": round(result[16], 2),
                    "political_agenda": round(result[17], 2)
                },
                "advanced_scores": {
                    "bill_diversity": round(result[18], 2),
                    "committee_activity": round(result[19], 2),
                    "collaboration": round(result[20], 2)
                },
                "analysis": {
                    "strengths": strengths,
                    "weaknesses": weaknesses,
                    "recommendations": recommendations
                },
                "bills": bills
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"의원 상세 평가 조회 실패: {e}")
            raise HTTPException(status_code=500, detail="의원 상세 평가 조회 실패")
        finally:
            conn.close()
    
    def get_evaluation_statistics(self) -> Dict:
        """평가 통계 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 기본 통계
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_politicians,
                    AVG(total_evaluation_score) as avg_score,
                    MIN(total_evaluation_score) as min_score,
                    MAX(total_evaluation_score) as max_score,
                    AVG(total_bills) as avg_bills,
                    AVG(passage_rate) as avg_passage_rate
                FROM stable_politician_evaluation
            ''')
            
            basic_stats = cursor.fetchone()
            
            # 카테고리별 분포
            cursor.execute('''
                SELECT evaluation_category, COUNT(*) as count
                FROM stable_politician_evaluation
                GROUP BY evaluation_category
                ORDER BY count DESC
            ''')
            category_distribution = {row[0]: row[1] for row in cursor.fetchall()}
            
            # 점수 구간별 분포
            cursor.execute('''
                SELECT 
                    CASE 
                        WHEN total_evaluation_score >= 80 THEN '80점 이상'
                        WHEN total_evaluation_score >= 60 THEN '60-79점'
                        WHEN total_evaluation_score >= 40 THEN '40-59점'
                        WHEN total_evaluation_score >= 20 THEN '20-39점'
                        ELSE '20점 미만'
                    END as score_range,
                    COUNT(*) as count
                FROM stable_politician_evaluation
                GROUP BY score_range
                ORDER BY MIN(total_evaluation_score) DESC
            ''')
            score_distribution = {row[0]: row[1] for row in cursor.fetchall()}
            
            # 위원회별 평균 점수
            cursor.execute('''
                SELECT p.committee, AVG(e.total_evaluation_score) as avg_score, COUNT(*) as count
                FROM politician_profiles p
                JOIN stable_politician_evaluation e ON p.politician_name = e.politician_name
                WHERE p.committee IS NOT NULL AND p.committee != '미분류'
                GROUP BY p.committee
                ORDER BY avg_score DESC
                LIMIT 10
            ''')
            committee_stats = [{"committee": row[0], "avg_score": round(row[1], 2), "count": row[2]} for row in cursor.fetchall()]
            
            return {
                "basic_statistics": {
                    "total_politicians": basic_stats[0],
                    "average_score": round(basic_stats[1], 2),
                    "min_score": round(basic_stats[2], 2),
                    "max_score": round(basic_stats[3], 2),
                    "average_bills": round(basic_stats[4], 2),
                    "average_passage_rate": round(basic_stats[5], 2)
                },
                "category_distribution": category_distribution,
                "score_distribution": score_distribution,
                "committee_statistics": committee_stats
            }
            
        except Exception as e:
            logger.error(f"평가 통계 조회 실패: {e}")
            raise HTTPException(status_code=500, detail="평가 통계 조회 실패")
        finally:
            conn.close()
    
    def get_bill_evaluation(self, bill_no: str = None, limit: int = 50) -> List[Dict]:
        """법안별 상세 평가 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            query = '''
                SELECT 
                    b.bill_no, b.bill_name, b.proposer_name, b.proposal_date,
                    b.committee_name, b.bill_status, a.bill_category,
                    a.policy_impact_score, a.legislative_quality_score,
                    a.public_interest_score, a.innovation_score, a.total_analysis_score,
                    i.political_intent_score, i.policy_intent_score, i.legislative_strategy_score,
                    i.timing_intent_score, i.overall_intent_score, i.intent_category,
                    i.intent_analysis
                FROM real_assembly_bills_22nd b
                LEFT JOIN real_bill_analysis_22nd a ON b.bill_id = a.bill_id
                LEFT JOIN bill_intent_analysis i ON b.bill_id = i.bill_id
                WHERE 1=1
            '''
            
            params = []
            if bill_no:
                query += ' AND b.bill_no = ?'
                params.append(bill_no)
            
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
                    "analysis_scores": {
                        "policy_impact": round(row[7] or 0, 2),
                        "legislative_quality": round(row[8] or 0, 2),
                        "public_interest": round(row[9] or 0, 2),
                        "innovation": round(row[10] or 0, 2),
                        "total_analysis": round(row[11] or 0, 2)
                    },
                    "intent_scores": {
                        "political_intent": round(row[12] or 0, 2),
                        "policy_intent": round(row[13] or 0, 2),
                        "legislative_strategy": round(row[14] or 0, 2),
                        "timing_intent": round(row[15] or 0, 2),
                        "overall_intent": round(row[16] or 0, 2)
                    },
                    "intent_category": row[17],
                    "intent_analysis": row[18]
                })
            
            return bills
            
        except Exception as e:
            logger.error(f"법안 평가 조회 실패: {e}")
            raise HTTPException(status_code=500, detail="법안 평가 조회 실패")
        finally:
            conn.close()

# API 서비스 인스턴스
api_service = StableEvaluationAPIService()

@app.get("/api/stable/health")
async def health_check():
    """헬스 체크"""
    return {"status": "healthy", "message": "안정적인 정치인 평가 API가 정상 작동 중입니다"}

@app.get("/api/stable/summary")
async def get_evaluation_summary():
    """평가 요약 조회"""
    return api_service.get_evaluation_summary()

@app.get("/api/stable/ranking")
async def get_politician_ranking(
    limit: int = Query(20, description="조회할 의원 수"),
    category: str = Query(None, description="평가 카테고리 필터")
):
    """의원 랭킹 조회"""
    return api_service.get_politician_ranking(limit, category)

@app.get("/api/stable/politician/{politician_name}")
async def get_politician_detail(politician_name: str):
    """특정 의원의 상세 평가 조회"""
    return api_service.get_politician_detail(politician_name)

@app.get("/api/stable/statistics")
async def get_evaluation_statistics():
    """평가 통계 조회"""
    return api_service.get_evaluation_statistics()

@app.get("/api/stable/bills")
async def get_bill_evaluation(
    bill_no: str = Query(None, description="법안번호"),
    limit: int = Query(50, description="조회할 법안 수")
):
    """법안별 상세 평가 조회"""
    return api_service.get_bill_evaluation(bill_no, limit)

if __name__ == "__main__":
    import uvicorn
    print("🚀 안정적인 정치인 평가 API 서버 시작 중...")
    print("🌐 서버 주소: http://localhost:8008")
    print("📖 API 문서: http://localhost:8008/docs")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8008)

