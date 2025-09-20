#!/usr/bin/env python3
"""
향상된 지역별 민생토픽 API 서버
207개 시군구 상세 분석 결과를 프론트엔드에 제공
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

class EnhancedRegionalMinsaengTopicsAPI:
    """향상된 지역별 민생토픽 API 서버"""
    
    def __init__(self):
        self.app = FastAPI(
            title="Enhanced Regional Minsaeng Topics API",
            description="207개 시군구 상세 분석 결과를 제공하는 민생토픽 API",
            version="2.0.0"
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
        self.detailed_analysis_dir = os.path.join(self.backend_dir, "detailed_local_government_analysis")
        
        # 데이터 캐시
        self.detailed_analysis_data = None
        self.comprehensive_analysis_data = None
        self.last_loaded = None
        
        # API 라우트 설정
        self.setup_routes()
        
        # 데이터 로드
        self.load_enhanced_data()
    
    def setup_routes(self):
        """API 라우트 설정"""
        
        @self.app.get("/")
        async def root():
            """API 서버 상태"""
            return {
                "message": "Enhanced Regional Minsaeng Topics API Server",
                "status": "running",
                "version": "2.0.0",
                "features": [
                    "207개 시군구 상세 분석",
                    "2,612개 정책 공약",
                    "8개 토픽 카테고리",
                    "지역별 검색 기능"
                ],
                "data_status": {
                    "detailed_analysis_loaded": self.detailed_analysis_data is not None,
                    "comprehensive_analysis_loaded": self.comprehensive_analysis_data is not None,
                    "last_updated": self.last_loaded
                }
            }
        
        @self.app.get("/api/regional-minsaeng-topics")
        async def get_regional_minsaeng_topics(
            level: str = Query("all", description="지역 레벨 (all/sido/sigungu/dong)"),
            topic: str = Query("all", description="토픽 필터"),
            search: str = Query("", description="지역명 검색"),
            limit: int = Query(50, description="결과 수 제한")
        ):
            """지역별 민생토픽 데이터 조회"""
            try:
                if not self.detailed_analysis_data:
                    raise HTTPException(status_code=503, detail="상세 분석 데이터가 로드되지 않았습니다")
                
                # 데이터 필터링
                filtered_data = self._filter_regional_data(level, topic, search, limit)
                
                return {
                    "success": True,
                    "data": filtered_data,
                    "metadata": {
                        "total_regions": len(filtered_data),
                        "level_filter": level,
                        "topic_filter": topic,
                        "search_term": search,
                        "limit": limit
                    }
                }
                
            except Exception as e:
                logger.error(f"지역별 민생토픽 조회 오류: {e}")
                raise HTTPException(status_code=500, detail=f"데이터 조회 실패: {str(e)}")
        
        @self.app.get("/api/regional-minsaeng-topics/{region_name}")
        async def get_region_detail(region_name: str):
            """특정 지역 상세 정보 조회"""
            try:
                if not self.detailed_analysis_data:
                    raise HTTPException(status_code=503, detail="상세 분석 데이터가 로드되지 않았습니다")
                
                # 지역 검색
                region_data = None
                for sigungu_name, sigungu_data in self.detailed_analysis_data.get("local_government_analysis", {}).items():
                    if region_name in sigungu_name or sigungu_name in region_name:
                        region_data = sigungu_data
                        break
                
                if not region_data:
                    raise HTTPException(status_code=404, detail=f"지역을 찾을 수 없습니다: {region_name}")
                
                return {
                    "success": True,
                    "data": region_data
                }
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"지역 상세 정보 조회 오류: {e}")
                raise HTTPException(status_code=500, detail=f"데이터 조회 실패: {str(e)}")
        
        @self.app.get("/api/regional-minsaeng-topics/search")
        async def search_regions(
            q: str = Query(..., description="검색어"),
            topic: str = Query("all", description="토픽 필터"),
            limit: int = Query(20, description="결과 수 제한")
        ):
            """지역 검색"""
            try:
                if not self.detailed_analysis_data:
                    raise HTTPException(status_code=503, detail="상세 분석 데이터가 로드되지 않았습니다")
                
                search_results = self._search_regions(q, topic, limit)
                
                return {
                    "success": True,
                    "results": search_results,
                    "metadata": {
                        "query": q,
                        "topic_filter": topic,
                        "total_results": len(search_results),
                        "limit": limit
                    }
                }
                
            except Exception as e:
                logger.error(f"지역 검색 오류: {e}")
                raise HTTPException(status_code=500, detail=f"검색 실패: {str(e)}")
        
        @self.app.get("/api/regional-minsaeng-topics/statistics")
        async def get_statistics():
            """전체 통계 정보 조회"""
            try:
                if not self.detailed_analysis_data:
                    raise HTTPException(status_code=503, detail="상세 분석 데이터가 로드되지 않았습니다")
                
                stats = self.detailed_analysis_data.get("overall_statistics", {})
                
                return {
                    "success": True,
                    "statistics": stats
                }
                
            except Exception as e:
                logger.error(f"통계 정보 조회 오류: {e}")
                raise HTTPException(status_code=500, detail=f"통계 조회 실패: {str(e)}")
        
        @self.app.get("/api/regional-minsaeng-topics/topics")
        async def get_topic_categories():
            """토픽 카테고리 조회"""
            try:
                if not self.detailed_analysis_data:
                    raise HTTPException(status_code=503, detail="상세 분석 데이터가 로드되지 않았습니다")
                
                topics = self.detailed_analysis_data.get("enhanced_topic_keywords", {})
                
                return {
                    "success": True,
                    "topics": topics
                }
                
            except Exception as e:
                logger.error(f"토픽 카테고리 조회 오류: {e}")
                raise HTTPException(status_code=500, detail=f"토픽 조회 실패: {str(e)}")
    
    def load_enhanced_data(self):
        """향상된 데이터 로드"""
        try:
            print("📊 향상된 민생토픽 데이터 로드 중...")
            
            # 상세 분석 데이터 로드
            detailed_files = [f for f in os.listdir(self.detailed_analysis_dir) if f.startswith("detailed_local_government_analysis_")]
            if detailed_files:
                latest_detailed_file = max(detailed_files)
                detailed_file_path = os.path.join(self.detailed_analysis_dir, latest_detailed_file)
                
                with open(detailed_file_path, 'r', encoding='utf-8') as f:
                    self.detailed_analysis_data = json.load(f)
                
                print(f"✅ 상세 분석 데이터 로드 완료: {latest_detailed_file}")
            
            # 종합 분석 데이터 로드 (기존)
            comprehensive_analysis_dir = os.path.join(self.backend_dir, "comprehensive_policy_analysis")
            if os.path.exists(comprehensive_analysis_dir):
                comprehensive_files = [f for f in os.listdir(comprehensive_analysis_dir) if f.startswith("comprehensive_regional_topics_frontend_")]
                if comprehensive_files:
                    latest_comprehensive_file = max(comprehensive_files)
                    comprehensive_file_path = os.path.join(comprehensive_analysis_dir, latest_comprehensive_file)
                    
                    with open(comprehensive_file_path, 'r', encoding='utf-8') as f:
                        self.comprehensive_analysis_data = json.load(f)
                    
                    print(f"✅ 종합 분석 데이터 로드 완료: {latest_comprehensive_file}")
            
            self.last_loaded = datetime.now().isoformat()
            
            # 로드된 데이터 요약
            if self.detailed_analysis_data:
                local_gov_count = len(self.detailed_analysis_data.get("local_government_analysis", {}))
                total_promises = sum(
                    len(gov.get("promises", [])) 
                    for gov in self.detailed_analysis_data.get("local_government_analysis", {}).values()
                )
                print(f"📊 데이터 요약:")
                print(f"  • 분석된 시군구: {local_gov_count}개")
                print(f"  • 총 정책 공약: {total_promises}개")
            
        except Exception as e:
            logger.error(f"향상된 데이터 로드 실패: {e}")
            print(f"❌ 데이터 로드 실패: {e}")
    
    def _filter_regional_data(self, level: str, topic: str, search: str, limit: int) -> Dict[str, Any]:
        """지역 데이터 필터링"""
        if not self.detailed_analysis_data:
            return {}
        
        local_gov_analysis = self.detailed_analysis_data.get("local_government_analysis", {})
        filtered_data = {}
        
        for sigungu_name, sigungu_data in local_gov_analysis.items():
            # 레벨 필터
            if level != "all" and sigungu_data.get("level") != level:
                continue
            
            # 토픽 필터
            if topic != "all" and topic not in sigungu_data.get("dominant_topics", []):
                continue
            
            # 검색 필터
            if search and search not in sigungu_name:
                continue
            
            filtered_data[sigungu_name] = sigungu_data
            
            # 제한 수 확인
            if len(filtered_data) >= limit:
                break
        
        return filtered_data
    
    def _search_regions(self, query: str, topic: str, limit: int) -> List[Dict[str, Any]]:
        """지역 검색"""
        if not self.detailed_analysis_data:
            return []
        
        local_gov_analysis = self.detailed_analysis_data.get("local_government_analysis", {})
        search_results = []
        
        for sigungu_name, sigungu_data in local_gov_analysis.items():
            # 지역명 검색
            if query.lower() in sigungu_name.lower():
                # 토픽 필터
                if topic != "all" and topic not in sigungu_data.get("dominant_topics", []):
                    continue
                
                search_results.append({
                    "region_name": sigungu_name,
                    "parent_government": sigungu_data.get("parent_government"),
                    "dominant_topics": sigungu_data.get("dominant_topics", []),
                    "mention_count": sigungu_data.get("mention_count", 0),
                    "confidence_score": sigungu_data.get("confidence_score", 0)
                })
                
                if len(search_results) >= limit:
                    break
        
        return search_results
    
    def run_server(self, host: str = "0.0.0.0", port: int = 8001):
        """서버 실행"""
        print(f"🚀 향상된 지역별 민생토픽 API 서버 시작")
        print(f"📍 주소: http://{host}:{port}")
        print(f"📊 기능: 207개 시군구 상세 분석 API")
        
        uvicorn.run(self.app, host=host, port=port)

def main():
    """메인 실행 함수"""
    api = EnhancedRegionalMinsaengTopicsAPI()
    api.run_server()

if __name__ == "__main__":
    main()
