#!/usr/bin/env python3
"""
통합 매니페스토 분석 API
지역 민생토픽 분석 + 출마자 공약 검증을 통합한 종합 서비스
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

logger = logging.getLogger(__name__)

class IntegratedManifestoAnalysisAPI:
    """통합 매니페스토 분석 API"""
    
    def __init__(self):
        self.app = FastAPI(
            title="Integrated Manifesto Analysis API",
            description="지역 민생토픽 + 출마자 공약 검증 통합 API",
            version="1.0.0"
        )
        
        # CORS 설정
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        self.base_dir = "/Users/hopidaay/newsbot-kr"
        self.backend_dir = "/Users/hopidaay/newsbot-kr/backend"
        
        # 데이터 로드
        self.regional_data = None
        self.candidates_data = None
        self.verification_results = None
        self.analysis_results = None
        
        # API 라우트 설정
        self.setup_routes()
        
        # 데이터 초기화
        self.load_all_data()
    
    def setup_routes(self):
        """API 라우트 설정"""
        
        @self.app.get("/")
        async def root():
            """API 서버 상태"""
            return {
                "message": "Integrated Manifesto Analysis API Server",
                "status": "running",
                "version": "1.0.0",
                "features": [
                    "지역 민생토픽 분석 (207개 시군구)",
                    "출마자 공약 검증 (8회 지방선거)",
                    "텍스트마이닝 기반 분석",
                    "매니페스토 신뢰도 평가"
                ],
                "data_status": {
                    "regional_data_loaded": self.regional_data is not None,
                    "candidates_data_loaded": self.candidates_data is not None,
                    "verification_results_loaded": self.verification_results is not None,
                    "analysis_results_loaded": self.analysis_results is not None
                }
            }
        
        @self.app.get("/api/region/{region_name}/analysis")
        async def get_regional_analysis(region_name: str):
            """지역별 민생토픽 분석 조회"""
            try:
                if not self.regional_data:
                    raise HTTPException(status_code=503, detail="지역 데이터가 로드되지 않았습니다")
                
                # 지역 데이터 검색
                region_analysis = None
                for region_key, region_info in self.regional_data.get("local_government_analysis", {}).items():
                    if region_name in region_key or region_key in region_name:
                        region_analysis = region_info
                        break
                
                if not region_analysis:
                    raise HTTPException(status_code=404, detail=f"지역을 찾을 수 없습니다: {region_name}")
                
                return {
                    "success": True,
                    "region_name": region_name,
                    "analysis": region_analysis
                }
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"지역 분석 조회 오류: {e}")
                raise HTTPException(status_code=500, detail=f"분석 조회 실패: {str(e)}")
        
        @self.app.get("/api/candidate/{candidate_name}/verification")
        async def get_candidate_verification(candidate_name: str):
            """후보자별 공약 검증 결과 조회"""
            try:
                if not self.verification_results:
                    raise HTTPException(status_code=503, detail="검증 데이터가 로드되지 않았습니다")
                
                # 후보자 검증 결과 검색
                candidate_verification = None
                for verification in self.verification_results:
                    if verification["candidate_name"] == candidate_name:
                        candidate_verification = verification
                        break
                
                if not candidate_verification:
                    raise HTTPException(status_code=404, detail=f"후보자를 찾을 수 없습니다: {candidate_name}")
                
                return {
                    "success": True,
                    "candidate_name": candidate_name,
                    "verification": candidate_verification
                }
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"후보자 검증 조회 오류: {e}")
                raise HTTPException(status_code=500, detail=f"검증 조회 실패: {str(e)}")
        
        @self.app.get("/api/integrated/analysis")
        async def get_integrated_analysis(
            region: str = Query(..., description="지역명"),
            include_candidates: bool = Query(True, description="후보자 정보 포함 여부")
        ):
            """통합 분석 - 지역 요구사항 + 후보자 공약 매칭"""
            try:
                # 지역 분석 데이터 가져오기
                region_analysis = await self.get_regional_analysis_data(region)
                
                result = {
                    "success": True,
                    "region": region,
                    "analysis_date": datetime.now().isoformat(),
                    "regional_analysis": region_analysis
                }
                
                if include_candidates:
                    # 해당 지역 후보자들 찾기
                    region_candidates = self.find_candidates_by_region(region)
                    candidate_verifications = []
                    
                    for candidate in region_candidates:
                        verification = self.get_candidate_verification_data(candidate["name"])
                        if verification:
                            candidate_verifications.append(verification)
                    
                    result["candidates_verification"] = candidate_verifications
                    
                    # 매칭 분석
                    if region_analysis and candidate_verifications:
                        matching_analysis = self.analyze_region_candidate_matching(
                            region_analysis, candidate_verifications
                        )
                        result["matching_analysis"] = matching_analysis
                
                return result
                
            except Exception as e:
                logger.error(f"통합 분석 오류: {e}")
                raise HTTPException(status_code=500, detail=f"통합 분석 실패: {str(e)}")
        
        @self.app.get("/api/verification/summary")
        async def get_verification_summary():
            """전체 검증 결과 요약"""
            try:
                if not self.verification_results:
                    raise HTTPException(status_code=503, detail="검증 데이터가 로드되지 않았습니다")
                
                # 요약 통계 계산
                total_candidates = len(self.verification_results)
                total_pledges = sum(v["total_pledges"] for v in self.verification_results)
                avg_credibility = sum(v["credibility_score"] for v in self.verification_results) / total_candidates
                
                # 등급별 분포
                grade_distribution = {}
                for verification in self.verification_results:
                    grade = verification["overall_grade"]
                    grade_distribution[grade] = grade_distribution.get(grade, 0) + 1
                
                # 당별 분석
                party_analysis = {}
                for verification in self.verification_results:
                    party = verification["party"]
                    if party not in party_analysis:
                        party_analysis[party] = {
                            "candidates": 0,
                            "avg_credibility": 0,
                            "credibility_scores": []
                        }
                    
                    party_analysis[party]["candidates"] += 1
                    party_analysis[party]["credibility_scores"].append(verification["credibility_score"])
                
                # 당별 평균 계산
                for party, data in party_analysis.items():
                    data["avg_credibility"] = sum(data["credibility_scores"]) / len(data["credibility_scores"])
                    del data["credibility_scores"]  # 불필요한 데이터 제거
                
                return {
                    "success": True,
                    "summary": {
                        "total_candidates": total_candidates,
                        "total_pledges": total_pledges,
                        "avg_credibility_score": avg_credibility,
                        "grade_distribution": grade_distribution,
                        "party_analysis": party_analysis
                    }
                }
                
            except Exception as e:
                logger.error(f"검증 요약 조회 오류: {e}")
                raise HTTPException(status_code=500, detail=f"요약 조회 실패: {str(e)}")
    
    def load_all_data(self):
        """모든 필요한 데이터 로드"""
        try:
            print("📂 통합 데이터 로드 중...")
            
            # 1. 지역 민생토픽 데이터
            regional_files = [
                f for f in os.listdir(os.path.join(self.backend_dir, "detailed_local_government_analysis"))
                if f.startswith("detailed_local_government_analysis_")
            ]
            if regional_files:
                latest_regional = max(regional_files)
                regional_path = os.path.join(self.backend_dir, "detailed_local_government_analysis", latest_regional)
                with open(regional_path, 'r', encoding='utf-8') as f:
                    self.regional_data = json.load(f)
                print(f"✅ 지역 데이터 로드: {latest_regional}")
            
            # 2. 출마자 데이터
            candidates_files = [
                f for f in os.listdir(os.path.join(self.backend_dir, "election_data"))
                if f.startswith("comprehensive_8th_election_candidates_")
            ]
            if candidates_files:
                latest_candidates = max(candidates_files)
                candidates_path = os.path.join(self.backend_dir, "election_data", latest_candidates)
                with open(candidates_path, 'r', encoding='utf-8') as f:
                    self.candidates_data = json.load(f)
                print(f"✅ 출마자 데이터 로드: {latest_candidates}")
            
            # 3. 검증 결과 데이터
            verification_files = [
                f for f in os.listdir(os.path.join(self.backend_dir, "manifesto_verification"))
                if f.startswith("manifesto_verifications_")
            ]
            if verification_files:
                latest_verification = max(verification_files)
                verification_path = os.path.join(self.backend_dir, "manifesto_verification", latest_verification)
                with open(verification_path, 'r', encoding='utf-8') as f:
                    self.verification_results = json.load(f)
                print(f"✅ 검증 결과 로드: {latest_verification}")
            
            # 4. 분석 결과 데이터
            analysis_files = [
                f for f in os.listdir(os.path.join(self.backend_dir, "manifesto_analysis"))
                if f.startswith("manifesto_analyses_")
            ]
            if analysis_files:
                latest_analysis = max(analysis_files)
                analysis_path = os.path.join(self.backend_dir, "manifesto_analysis", latest_analysis)
                with open(analysis_path, 'r', encoding='utf-8') as f:
                    self.analysis_results = json.load(f)
                print(f"✅ 분석 결과 로드: {latest_analysis}")
            
            print("🎉 모든 데이터 로드 완료!")
            
        except Exception as e:
            logger.error(f"데이터 로드 실패: {e}")
            print(f"❌ 데이터 로드 실패: {e}")
    
    async def get_regional_analysis_data(self, region_name: str) -> Optional[Dict[str, Any]]:
        """지역 분석 데이터 조회"""
        if not self.regional_data:
            return None
        
        for region_key, region_info in self.regional_data.get("local_government_analysis", {}).items():
            if region_name in region_key or region_key in region_name:
                return region_info
        
        return None
    
    def find_candidates_by_region(self, region_name: str) -> List[Dict[str, Any]]:
        """지역별 후보자 검색"""
        if not self.candidates_data:
            return []
        
        candidates = []
        for district_id, district_info in self.candidates_data.get("districts", {}).items():
            if region_name in district_info.get("district_name", ""):
                for candidate_id, candidate_info in district_info.get("candidates", {}).items():
                    candidates.append(candidate_info)
        
        return candidates
    
    def get_candidate_verification_data(self, candidate_name: str) -> Optional[Dict[str, Any]]:
        """후보자 검증 데이터 조회"""
        if not self.verification_results:
            return None
        
        for verification in self.verification_results:
            if verification["candidate_name"] == candidate_name:
                return verification
        
        return None
    
    def analyze_region_candidate_matching(self, regional_analysis: Dict[str, Any], candidate_verifications: List[Dict[str, Any]]) -> Dict[str, Any]:
        """지역 요구사항과 후보자 공약 매칭 분석"""
        
        # 지역 주요 토픽
        regional_topics = regional_analysis.get("dominant_topics", [])
        regional_scores = regional_analysis.get("topic_scores", {})
        
        matching_results = []
        
        for verification in candidate_verifications:
            candidate_name = verification["candidate_name"]
            
            # 후보자의 공약 카테고리 분석
            candidate_categories = {}
            for pledge_verification in verification.get("pledge_verifications", []):
                category = pledge_verification.get("category", "기타")
                if category not in candidate_categories:
                    candidate_categories[category] = {
                        "count": 0,
                        "avg_specificity": 0,
                        "specificity_scores": []
                    }
                
                candidate_categories[category]["count"] += 1
                candidate_categories[category]["specificity_scores"].append(
                    pledge_verification.get("specificity_score", 0)
                )
            
            # 카테고리별 평균 계산
            for category, data in candidate_categories.items():
                scores = data["specificity_scores"]
                data["avg_specificity"] = sum(scores) / len(scores) if scores else 0
                del data["specificity_scores"]
            
            # 매칭 점수 계산
            matching_score = 0
            covered_topics = []
            uncovered_topics = []
            
            for topic in regional_topics:
                regional_score = regional_scores.get(topic, 0)
                
                # 토픽을 카테고리로 매핑
                topic_mapping = {
                    "경제정책": "경제정책",
                    "주거정책": "주거정책", 
                    "교육정책": "교육정책",
                    "복지정책": "복지정책",
                    "환경정책": "환경정책",
                    "교통정책": "교통정책",
                    "문화정책": "문화정책",
                    "안전정책": "안전정책"
                }
                
                mapped_category = topic_mapping.get(topic, topic)
                
                if mapped_category in candidate_categories:
                    # 대응 공약 있음
                    candidate_specificity = candidate_categories[mapped_category]["avg_specificity"]
                    topic_match_score = (regional_score / 100) * (candidate_specificity / 100) * 100
                    matching_score += topic_match_score
                    covered_topics.append({
                        "topic": topic,
                        "regional_score": regional_score,
                        "candidate_specificity": candidate_specificity,
                        "match_score": topic_match_score
                    })
                else:
                    # 대응 공약 없음
                    uncovered_topics.append({
                        "topic": topic,
                        "regional_score": regional_score
                    })
            
            # 전체 매칭 점수 정규화
            final_matching_score = matching_score / len(regional_topics) if regional_topics else 0
            
            matching_results.append({
                "candidate_name": candidate_name,
                "party": verification.get("party", ""),
                "matching_score": final_matching_score,
                "covered_topics": covered_topics,
                "uncovered_topics": uncovered_topics,
                "candidate_categories": candidate_categories,
                "overall_grade": verification.get("overall_grade", ""),
                "credibility_score": verification.get("credibility_score", 0)
            })
        
        # 매칭 점수 순으로 정렬
        matching_results.sort(key=lambda x: x["matching_score"], reverse=True)
        
        return {
            "regional_priorities": [
                {"topic": topic, "score": regional_scores.get(topic, 0)}
                for topic in regional_topics
            ],
            "candidate_matching": matching_results,
            "best_match": matching_results[0] if matching_results else None,
            "analysis_summary": {
                "total_candidates": len(matching_results),
                "avg_matching_score": sum(r["matching_score"] for r in matching_results) / len(matching_results) if matching_results else 0,
                "full_coverage_candidates": len([r for r in matching_results if not r["uncovered_topics"]])
            }
        }
    
    def run_server(self, host: str = "0.0.0.0", port: int = 8002):
        """서버 실행"""
        print(f"🚀 통합 매니페스토 분석 API 서버 시작")
        print(f"📍 주소: http://{host}:{port}")
        print(f"📊 기능: 지역 분석 + 공약 검증 통합")
        
        uvicorn.run(self.app, host=host, port=port)

def main():
    """메인 실행 함수"""
    api = IntegratedManifestoAnalysisAPI()
    api.run_server()

if __name__ == "__main__":
    main()
