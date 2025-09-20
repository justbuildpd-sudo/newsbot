#!/usr/bin/env python3
"""
지역별 민생토픽 API 서버
정책선거문화 빅데이터 분석 결과를 프론트엔드에 제공
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from pathlib import Path

logger = logging.getLogger(__name__)

class RegionalMinsaengTopicsAPI:
    """지역별 민생토픽 API 서버"""
    
    def __init__(self):
        self.app = FastAPI(
            title="Regional Minsaeng Topics API",
            description="지역별 민생토픽 분석 결과 제공 API",
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
        self.analysis_dir = os.path.join(self.backend_dir, "enhanced_policy_analysis")
        
        # 데이터 캐시
        self.minsaeng_data = None
        self.last_loaded = None
        
        # API 라우트 설정
        self.setup_routes()
        
        # 데이터 로드
        self.load_minsaeng_data()

    def setup_routes(self):
        """API 라우트 설정"""
        
        @self.app.get("/")
        async def root():
            """API 서버 정보"""
            return {
                "service": "Regional Misaeng Topics API",
                "version": "1.0.0",
                "status": "running",
                "data_loaded": self.misaeng_data is not None,
                "last_updated": self.last_loaded.isoformat() if self.last_loaded else None,
                "total_regions": len(self.misaeng_data.get("regional_data", {})) if self.misaeng_data else 0
            }
        
        @self.app.get("/api/misaeng-topics")
        async def get_misaeng_topics(
            level: Optional[str] = Query(None, description="지역 레벨 필터 (광역시도, 시군구, 읍면동)"),
            topic: Optional[str] = Query(None, description="토픽 필터"),
            search: Optional[str] = Query(None, description="지역명 검색"),
            limit: Optional[int] = Query(50, description="결과 개수 제한")
        ):
            """지역별 미생토픽 데이터 조회"""
            
            if not self.misaeng_data:
                raise HTTPException(status_code=503, detail="미생토픽 데이터가 로드되지 않았습니다")
            
            try:
                # 데이터 필터링
                filtered_data = self._filter_regional_data(
                    level=level,
                    topic=topic,
                    search=search,
                    limit=limit
                )
                
                return {
                    "success": True,
                    "data": filtered_data,
                    "total_count": len(filtered_data),
                    "filters": {
                        "level": level,
                        "topic": topic,
                        "search": search,
                        "limit": limit
                    },
                    "last_updated": self.misaeng_data.get("last_updated"),
                    "request_time": datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"미생토픽 조회 오류: {e}")
                raise HTTPException(status_code=500, detail=f"데이터 조회 실패: {str(e)}")
        
        @self.app.get("/api/misaeng-topics/region/{region_name}")
        async def get_region_details(region_name: str):
            """특정 지역의 상세 미생토픽 정보"""
            
            if not self.misaeng_data:
                raise HTTPException(status_code=503, detail="미생토픽 데이터가 로드되지 않았습니다")
            
            regional_data = self.misaeng_data.get("regional_data", {})
            
            # 지역명으로 검색 (정확한 매칭 + 유사 매칭)
            region_info = None
            region_key = None
            
            # 정확한 매칭
            if region_name in regional_data:
                region_key = region_name
                region_info = regional_data[region_name]
            else:
                # 유사 매칭 (지역명 포함)
                for key, data in regional_data.items():
                    if (region_name.lower() in key.lower() or 
                        region_name.lower() in data.get("region_name", "").lower()):
                        region_key = key
                        region_info = data
                        break
            
            if not region_info:
                raise HTTPException(status_code=404, detail=f"지역 '{region_name}'을 찾을 수 없습니다")
            
            # 관련 지역 추천 (같은 레벨, 유사한 토픽)
            related_regions = self._get_related_regions(region_key, region_info)
            
            return {
                "success": True,
                "region_key": region_key,
                "region_data": region_info,
                "related_regions": related_regions,
                "topic_categories": self.misaeng_data.get("misaeng_topic_categories", {}),
                "request_time": datetime.now().isoformat()
            }
        
        @self.app.get("/api/misaeng-topics/statistics")
        async def get_statistics():
            """미생토픽 통계 정보"""
            
            if not self.misaeng_data:
                raise HTTPException(status_code=503, detail="미생토픽 데이터가 로드되지 않았습니다")
            
            try:
                stats = self._calculate_statistics()
                
                return {
                    "success": True,
                    "statistics": stats,
                    "last_updated": self.misaeng_data.get("last_updated"),
                    "request_time": datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"통계 계산 오류: {e}")
                raise HTTPException(status_code=500, detail=f"통계 계산 실패: {str(e)}")
        
        @self.app.get("/api/misaeng-topics/topics")
        async def get_topic_categories():
            """미생토픽 카테고리 정보"""
            
            if not self.misaeng_data:
                raise HTTPException(status_code=503, detail="미생토픽 데이터가 로드되지 않았습니다")
            
            return {
                "success": True,
                "topic_categories": self.misaeng_data.get("misaeng_topic_categories", {}),
                "total_categories": len(self.misaeng_data.get("misaeng_topic_categories", {})),
                "request_time": datetime.now().isoformat()
            }
        
        @self.app.post("/api/misaeng-topics/reload")
        async def reload_data():
            """데이터 다시 로드"""
            
            try:
                success = self.load_misaeng_data()
                
                return {
                    "success": success,
                    "message": "데이터 로드 완료" if success else "데이터 로드 실패",
                    "total_regions": len(self.misaeng_data.get("regional_data", {})) if self.misaeng_data else 0,
                    "last_updated": self.last_loaded.isoformat() if self.last_loaded else None,
                    "request_time": datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"데이터 로드 오류: {e}")
                raise HTTPException(status_code=500, detail=f"데이터 로드 실패: {str(e)}")

    def load_misaeng_data(self) -> bool:
        """미생토픽 데이터 로드"""
        try:
            # 가장 최신 분석 파일 찾기
            if not os.path.exists(self.analysis_dir):
                logger.error(f"분석 디렉토리가 존재하지 않습니다: {self.analysis_dir}")
                return False
            
            frontend_files = []
            for file in os.listdir(self.analysis_dir):
                if file.startswith("regional_misaeng_topics_frontend_") and file.endswith(".json"):
                    file_path = os.path.join(self.analysis_dir, file)
                    frontend_files.append((file_path, os.path.getmtime(file_path)))
            
            if not frontend_files:
                logger.error("프론트엔드용 미생토픽 데이터 파일을 찾을 수 없습니다")
                return False
            
            # 가장 최신 파일 선택
            latest_file = sorted(frontend_files, key=lambda x: x[1], reverse=True)[0][0]
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                self.misaeng_data = json.load(f)
            
            self.last_loaded = datetime.now()
            
            logger.info(f"✅ 미생토픽 데이터 로드 완료: {latest_file}")
            logger.info(f"   총 지역: {len(self.misaeng_data.get('regional_data', {}))}개")
            logger.info(f"   토픽 카테고리: {len(self.misaeng_data.get('misaeng_topic_categories', {}))}개")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 미생토픽 데이터 로드 실패: {e}")
            return False

    def _filter_regional_data(self, level: str = None, topic: str = None, search: str = None, limit: int = 50) -> List[Dict]:
        """지역 데이터 필터링"""
        
        regional_data = self.misaeng_data.get("regional_data", {})
        filtered_regions = []
        
        for region_key, region_info in regional_data.items():
            # 레벨 필터
            if level and region_info.get("level") != level:
                continue
            
            # 토픽 필터
            if topic and topic not in region_info.get("dominant_topics", []):
                continue
            
            # 검색 필터
            if search:
                search_lower = search.lower()
                if (search_lower not in region_key.lower() and 
                    search_lower not in region_info.get("region_name", "").lower()):
                    continue
            
            # 결과에 추가
            result_item = {
                "region_key": region_key,
                **region_info
            }
            filtered_regions.append(result_item)
        
        # 언급 횟수 순으로 정렬
        filtered_regions.sort(key=lambda x: x.get("mention_count", 0), reverse=True)
        
        # 제한 적용
        return filtered_regions[:limit]

    def _get_related_regions(self, target_region_key: str, target_region_info: Dict) -> List[Dict]:
        """관련 지역 추천"""
        
        regional_data = self.misaeng_data.get("regional_data", {})
        related_regions = []
        
        target_level = target_region_info.get("level")
        target_topics = set(target_region_info.get("dominant_topics", []))
        
        for region_key, region_info in regional_data.items():
            if region_key == target_region_key:
                continue
            
            # 같은 레벨 우선
            if region_info.get("level") != target_level:
                continue
            
            # 공통 토픽 계산
            region_topics = set(region_info.get("dominant_topics", []))
            common_topics = target_topics & region_topics
            
            if common_topics:
                similarity_score = len(common_topics) / len(target_topics | region_topics)
                
                related_regions.append({
                    "region_key": region_key,
                    "region_name": region_info.get("region_name"),
                    "level": region_info.get("level"),
                    "common_topics": list(common_topics),
                    "similarity_score": similarity_score,
                    "mention_count": region_info.get("mention_count", 0)
                })
        
        # 유사도 순으로 정렬하고 상위 5개만 반환
        related_regions.sort(key=lambda x: x["similarity_score"], reverse=True)
        return related_regions[:5]

    def _calculate_statistics(self) -> Dict[str, Any]:
        """통계 정보 계산"""
        
        regional_data = self.misaeng_data.get("regional_data", {})
        topic_categories = self.misaeng_data.get("misaeng_topic_categories", {})
        
        # 기본 통계
        total_regions = len(regional_data)
        total_mentions = sum(region.get("mention_count", 0) for region in regional_data.values())
        total_promises = sum(len(region.get("promises", [])) for region in regional_data.values())
        
        # 레벨별 통계
        level_stats = {}
        for region in regional_data.values():
            level = region.get("level", "기타")
            if level not in level_stats:
                level_stats[level] = {"count": 0, "total_mentions": 0}
            level_stats[level]["count"] += 1
            level_stats[level]["total_mentions"] += region.get("mention_count", 0)
        
        # 토픽별 통계
        topic_stats = {}
        for topic in topic_categories.keys():
            topic_stats[topic] = {"regions": 0, "total_score": 0, "avg_score": 0}
        
        for region in regional_data.values():
            for topic in region.get("dominant_topics", []):
                if topic in topic_stats:
                    topic_stats[topic]["regions"] += 1
                    topic_stats[topic]["total_score"] += region.get("topic_scores", {}).get(topic, 0)
        
        # 평균 점수 계산
        for topic, stats in topic_stats.items():
            if stats["regions"] > 0:
                stats["avg_score"] = round(stats["total_score"] / stats["regions"], 2)
        
        # 상위 지역 (언급 횟수 기준)
        top_regions = sorted(
            [(key, region.get("mention_count", 0), region.get("region_name", key)) 
             for key, region in regional_data.items()],
            key=lambda x: x[1], reverse=True
        )[:10]
        
        return {
            "overview": {
                "total_regions": total_regions,
                "total_mentions": total_mentions,
                "total_promises": total_promises,
                "avg_mentions_per_region": round(total_mentions / total_regions, 2) if total_regions > 0 else 0
            },
            "level_distribution": level_stats,
            "topic_statistics": topic_stats,
            "top_regions": [
                {
                    "region_key": key,
                    "region_name": name,
                    "mention_count": count
                }
                for key, count, name in top_regions
            ],
            "calculation_time": datetime.now().isoformat()
        }

def create_app():
    """FastAPI 앱 생성"""
    api_server = RegionalMisaengTopicsAPI()
    return api_server.app

# 개발용 서버 실행
if __name__ == "__main__":
    print("🚀 지역별 미생토픽 API 서버 시작")
    print("=" * 50)
    
    api_server = RegionalMisaengTopicsAPI()
    
    if api_server.misaeng_data:
        print(f"✅ 데이터 로드 성공:")
        print(f"   📊 총 지역: {len(api_server.misaeng_data.get('regional_data', {}))}개")
        print(f"   🏷️ 토픽 카테고리: {len(api_server.misaeng_data.get('misaeng_topic_categories', {}))}개")
        print(f"   🕐 마지막 업데이트: {api_server.misaeng_data.get('last_updated')}")
    else:
        print("❌ 데이터 로드 실패")
    
    print("\n🌐 API 서버 정보:")
    print("   📍 URL: http://localhost:8001")
    print("   📚 문서: http://localhost:8001/docs")
    print("   🔍 API 테스트: http://localhost:8001/api/misaeng-topics")
    
    uvicorn.run(
        api_server.app,
        host="0.0.0.0",
        port=8001,
        reload=True
    )
