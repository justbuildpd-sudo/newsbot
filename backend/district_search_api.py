#!/usr/bin/env python3
"""
선거구 검색 및 매칭 API
행정구역과 선거구를 연결하고 정치인 데이터를 제공하는 FastAPI 서비스
"""

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Optional
import json
import re
import logging
from pathlib import Path

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="선거구 검색 API", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DistrictSearchService:
    def __init__(self):
        self.politicians_data = {}
        self.district_mapping = {}
        self.search_index = {}
        self.load_data()
        
    def load_data(self):
        """정치인 및 선거구 데이터 로드"""
        try:
            # 정치인 데이터 로드 (기존 데이터 활용)
            data_files = [
                "web_service/politicians_lightweight.json",
                "backend/data/politicians.json"
            ]
            
            for file_path in data_files:
                if Path(file_path).exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            for politician in data:
                                name = politician.get('name', '')
                                if name:
                                    self.politicians_data[name] = politician
                        elif isinstance(data, dict):
                            self.politicians_data.update(data)
                    logger.info(f"✅ 데이터 로드: {file_path}")
                    break
            
            # 선거구 매핑 데이터 생성
            self._create_district_mapping()
            
            # 검색 인덱스 생성
            self._create_search_index()
            
            logger.info(f"🗺️ 선거구 검색 서비스 초기화 완료: {len(self.politicians_data)}명의 정치인")
            
        except Exception as e:
            logger.error(f"❌ 데이터 로드 실패: {e}")
            self._load_sample_data()
    
    def _load_sample_data(self):
        """샘플 데이터 로드"""
        sample_politicians = [
            {
                "name": "김철수",
                "party": "더불어민주당",
                "district": "서울특별시 강남구갑",
                "region": "서울특별시",
                "phone": "02-123-4567",
                "email": "kim@assembly.go.kr",
                "office": "국회의사당 본관 123호"
            },
            {
                "name": "이영희", 
                "party": "국민의힘",
                "district": "부산광역시 해운대구을",
                "region": "부산광역시",
                "phone": "051-234-5678",
                "email": "lee@assembly.go.kr",
                "office": "국회의사당 본관 456호"
            },
            {
                "name": "박민수",
                "party": "정의당",
                "district": "경기도 수원시갑",
                "region": "경기도",
                "phone": "031-345-6789",
                "email": "park@assembly.go.kr",
                "office": "국회의사당 본관 789호"
            }
        ]
        
        for politician in sample_politicians:
            self.politicians_data[politician['name']] = politician
        
        self._create_district_mapping()
        self._create_search_index()
        
        logger.info("📝 샘플 데이터 로드 완료")
    
    def _create_district_mapping(self):
        """행정구역-선거구 매핑 생성"""
        for name, politician in self.politicians_data.items():
            district = politician.get('district', '')
            region = politician.get('region', '')
            
            if district:
                # 선거구 키 생성
                district_key = self._normalize_district_name(district)
                
                if district_key not in self.district_mapping:
                    self.district_mapping[district_key] = {
                        'district_name': district,
                        'region': region,
                        'members': [],
                        'coordinates': self._get_district_coordinates(district)
                    }
                
                self.district_mapping[district_key]['members'].append({
                    'name': name,
                    'party': politician.get('party', ''),
                    'phone': politician.get('phone', ''),
                    'email': politician.get('email', ''),
                    'office': politician.get('office', ''),
                    'profile': politician
                })
    
    def _create_search_index(self):
        """검색 인덱스 생성"""
        for name, politician in self.politicians_data.items():
            # 이름으로 검색
            self._add_to_search_index(name, 'politician', politician)
            
            # 정당으로 검색
            party = politician.get('party', '')
            if party:
                self._add_to_search_index(party, 'party', politician)
            
            # 선거구로 검색
            district = politician.get('district', '')
            if district:
                self._add_to_search_index(district, 'district', politician)
                
                # 지역명으로도 검색 가능하게
                region_parts = district.split()
                for part in region_parts:
                    if len(part) > 1:  # 한 글자는 제외
                        self._add_to_search_index(part, 'region', politician)
    
    def _add_to_search_index(self, term: str, term_type: str, politician: Dict):
        """검색 인덱스에 항목 추가"""
        term_lower = term.lower()
        if term_lower not in self.search_index:
            self.search_index[term_lower] = []
        
        self.search_index[term_lower].append({
            'type': term_type,
            'politician': politician,
            'match_term': term
        })
    
    def _normalize_district_name(self, district: str) -> str:
        """선거구명 정규화"""
        # 공백 제거 및 소문자 변환
        normalized = re.sub(r'\s+', '_', district.strip()).lower()
        return normalized
    
    def _get_district_coordinates(self, district: str) -> Dict[str, float]:
        """선거구 좌표 정보 (실제로는 GIS 데이터베이스에서 가져와야 함)"""
        # 샘플 좌표 (실제로는 지역별 중심 좌표)
        coordinate_map = {
            '서울특별시': {'lat': 37.5665, 'lng': 126.9780},
            '부산광역시': {'lat': 35.1796, 'lng': 129.0756},
            '경기도': {'lat': 37.4138, 'lng': 127.5183},
            '인천광역시': {'lat': 37.4563, 'lng': 126.7052},
            '대구광역시': {'lat': 35.8714, 'lng': 128.6014}
        }
        
        for region, coords in coordinate_map.items():
            if region in district:
                return coords
        
        return {'lat': 37.5665, 'lng': 126.9780}  # 기본값 (서울)
    
    def search_politicians(self, query: str, limit: int = 10) -> List[Dict]:
        """정치인 검색"""
        query_lower = query.lower()
        results = []
        seen_politicians = set()
        
        # 완전 일치 검색
        if query_lower in self.search_index:
            for item in self.search_index[query_lower]:
                politician = item['politician']
                politician_name = politician.get('name', '')
                if politician_name not in seen_politicians:
                    results.append({
                        'politician': politician,
                        'match_type': item['type'],
                        'match_term': item['match_term'],
                        'relevance': 100
                    })
                    seen_politicians.add(politician_name)
        
        # 부분 일치 검색
        for term, items in self.search_index.items():
            if query_lower in term and query_lower != term:
                for item in items:
                    politician = item['politician']
                    politician_name = politician.get('name', '')
                    if politician_name not in seen_politicians:
                        relevance = int((len(query_lower) / len(term)) * 80)
                        results.append({
                            'politician': politician,
                            'match_type': item['type'],
                            'match_term': item['match_term'],
                            'relevance': relevance
                        })
                        seen_politicians.add(politician_name)
        
        # 관련성 순으로 정렬
        results.sort(key=lambda x: x['relevance'], reverse=True)
        
        return results[:limit]
    
    def get_district_info(self, district_key: str) -> Optional[Dict]:
        """선거구 정보 조회"""
        return self.district_mapping.get(district_key)
    
    def get_all_districts(self) -> List[Dict]:
        """모든 선거구 목록"""
        return [
            {
                'key': key,
                'name': info['district_name'],
                'region': info['region'],
                'member_count': len(info['members']),
                'coordinates': info['coordinates']
            }
            for key, info in self.district_mapping.items()
        ]

# 전역 서비스 인스턴스
district_service = DistrictSearchService()

@app.get("/")
async def root():
    """API 정보"""
    return {
        "service": "선거구 검색 API",
        "version": "1.0.0",
        "endpoints": [
            "/search/politicians",
            "/districts",
            "/districts/{district_key}",
            "/stats"
        ]
    }

@app.get("/search/politicians")
async def search_politicians(
    q: str = Query(..., description="검색어 (정치인명, 정당명, 선거구명)"),
    limit: int = Query(10, ge=1, le=50, description="결과 개수 제한")
):
    """정치인 검색"""
    if not q.strip():
        raise HTTPException(status_code=400, detail="검색어를 입력해주세요")
    
    try:
        results = district_service.search_politicians(q.strip(), limit)
        
        return {
            "success": True,
            "query": q,
            "count": len(results),
            "results": results
        }
    except Exception as e:
        logger.error(f"검색 오류: {e}")
        raise HTTPException(status_code=500, detail="검색 중 오류가 발생했습니다")

@app.get("/districts")
async def get_all_districts():
    """모든 선거구 목록"""
    try:
        districts = district_service.get_all_districts()
        return {
            "success": True,
            "count": len(districts),
            "districts": districts
        }
    except Exception as e:
        logger.error(f"선거구 목록 조회 오류: {e}")
        raise HTTPException(status_code=500, detail="선거구 목록 조회 중 오류가 발생했습니다")

@app.get("/districts/{district_key}")
async def get_district_info(district_key: str):
    """특정 선거구 정보"""
    try:
        district_info = district_service.get_district_info(district_key)
        
        if not district_info:
            raise HTTPException(status_code=404, detail="선거구를 찾을 수 없습니다")
        
        return {
            "success": True,
            "district": district_info
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"선거구 정보 조회 오류: {e}")
        raise HTTPException(status_code=500, detail="선거구 정보 조회 중 오류가 발생했습니다")

@app.get("/stats")
async def get_statistics():
    """통계 정보"""
    try:
        return {
            "success": True,
            "statistics": {
                "total_politicians": len(district_service.politicians_data),
                "total_districts": len(district_service.district_mapping),
                "search_terms": len(district_service.search_index)
            }
        }
    except Exception as e:
        logger.error(f"통계 조회 오류: {e}")
        raise HTTPException(status_code=500, detail="통계 조회 중 오류가 발생했습니다")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
