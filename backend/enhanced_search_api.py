#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
향상된 검색 API
22대 출마자와 현직 국회의원을 통합하여 검색할 수 있는 API를 제공합니다.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import logging
from typing import List, Dict, Optional
import difflib
import uvicorn
import os

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="NewsBot Enhanced Search API", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 전역 데이터
search_data = {}
popup_data = {}
politicians_by_category = {
    'current_member': [],
    'election_candidate': []
}

class SearchRequest(BaseModel):
    query: str
    category: Optional[str] = None  # 'current_member', 'election_candidate', or None for all
    limit: Optional[int] = 10

class PoliticianRequest(BaseModel):
    name: str

def load_data():
    """통합된 정치인 데이터를 로드합니다."""
    global search_data, popup_data, politicians_by_category
    
    try:
        # 검색 데이터 로드
        if os.path.exists("newsbot_search_data.json"):
            with open("newsbot_search_data.json", 'r', encoding='utf-8') as f:
                search_data = json.load(f)
            logger.info(f"✅ 검색 데이터 로드 완료: {len(search_data.get('politicians', []))}명")
        
        # 팝업 데이터 로드
        if os.path.exists("newsbot_popup_data.json"):
            with open("newsbot_popup_data.json", 'r', encoding='utf-8') as f:
                popup_data = json.load(f)
            logger.info(f"✅ 팝업 데이터 로드 완료: {len(popup_data)}명")
        
        # 카테고리별 분류
        for politician in search_data.get('politicians', []):
            category = politician.get('category', 'election_candidate')
            politicians_by_category[category].append(politician)
        
        logger.info(f"✅ 현직 의원: {len(politicians_by_category['current_member'])}명")
        logger.info(f"✅ 22대 출마자: {len(politicians_by_category['election_candidate'])}명")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 데이터 로드 실패: {str(e)}")
        return False

@app.on_event("startup")
async def startup_event():
    """앱 시작시 데이터 로드"""
    if not load_data():
        logger.error("❌ 데이터 로드 실패 - 기본 데이터로 시작")

@app.get("/")
async def root():
    """API 정보"""
    return {
        "message": "NewsBot Enhanced Search API",
        "version": "1.0.0",
        "endpoints": {
            "search": "/api/search/politicians",
            "politician_detail": "/api/politicians/candidate",
            "categories": "/api/categories",
            "statistics": "/api/statistics"
        }
    }

@app.post("/api/search/politicians")
async def search_politicians(request: SearchRequest):
    """정치인 검색 API"""
    try:
        query = request.query.strip().lower()
        category = request.category
        limit = request.limit or 10
        
        if not query:
            raise HTTPException(status_code=400, detail="검색어를 입력해주세요")
        
        results = []
        search_pool = []
        
        # 검색 대상 결정
        if category:
            search_pool = politicians_by_category.get(category, [])
        else:
            search_pool = search_data.get('politicians', [])
        
        # 정확한 이름 매칭 우선
        for politician in search_pool:
            name = politician.get('name', '').lower()
            if query in name or name in query:
                results.append({
                    **politician,
                    'match_score': 1.0,
                    'match_type': 'exact'
                })
        
        # 퍼지 매칭 (정확한 매칭이 부족한 경우)
        if len(results) < limit:
            fuzzy_results = []
            for politician in search_pool:
                if politician in [r for r in results]:  # 이미 추가된 경우 스킵
                    continue
                
                name = politician.get('name', '').lower()
                party = politician.get('party', '').lower()
                district = politician.get('district', '').lower()
                
                # 유사도 계산
                name_similarity = difflib.SequenceMatcher(None, query, name).ratio()
                party_similarity = difflib.SequenceMatcher(None, query, party).ratio()
                district_similarity = difflib.SequenceMatcher(None, query, district).ratio()
                
                max_similarity = max(name_similarity, party_similarity, district_similarity)
                
                if max_similarity > 0.6:  # 60% 이상 유사도
                    fuzzy_results.append({
                        **politician,
                        'match_score': max_similarity,
                        'match_type': 'fuzzy'
                    })
            
            # 유사도 순으로 정렬
            fuzzy_results.sort(key=lambda x: x['match_score'], reverse=True)
            results.extend(fuzzy_results[:limit - len(results)])
        
        # 결과 제한
        results = results[:limit]
        
        return {
            'success': True,
            'query': request.query,
            'category': category,
            'total_results': len(results),
            'results': results
        }
        
    except Exception as e:
        logger.error(f"검색 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"검색 중 오류가 발생했습니다: {str(e)}")

@app.post("/api/politicians/candidate")
async def get_politician_detail(request: PoliticianRequest):
    """정치인 상세 정보 API"""
    try:
        politician_name = request.name.strip()
        
        if not politician_name:
            raise HTTPException(status_code=400, detail="정치인 이름을 입력해주세요")
        
        # 팝업 데이터에서 검색
        for politician_id, data in popup_data.items():
            if data.get('basic_info', {}).get('name') == politician_name:
                return {
                    'success': True,
                    'politician_id': politician_id,
                    **data
                }
        
        # 검색 데이터에서 대안 검색
        for politician in search_data.get('politicians', []):
            if politician.get('name') == politician_name:
                # 기본 팝업 데이터 생성
                basic_popup_data = {
                    'basic_info': {
                        'name': politician.get('name'),
                        'category': politician.get('category'),
                        'party': politician.get('party'),
                        'district': politician.get('district'),
                        'age': None,
                        'gender': None,
                        'education': None,
                        'career': None
                    },
                    'election_info': {
                        'vote_count': None,
                        'vote_rate': None,
                        'is_elected': False,
                        'election_symbol': None,
                        'vote_grade': None
                    } if politician.get('category') == 'election_candidate' else None,
                    'news_section': {
                        'articles': [],
                        'count': 0,
                        'placeholder_message': f"{politician_name} 관련 최신 기사를 불러오는 중..."
                    }
                }
                
                return {
                    'success': True,
                    'politician_id': f"fallback_{politician_name}",
                    **basic_popup_data
                }
        
        raise HTTPException(status_code=404, detail=f"'{politician_name}' 정치인을 찾을 수 없습니다")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"정치인 상세 정보 조회 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"정치인 정보 조회 중 오류가 발생했습니다: {str(e)}")

@app.get("/api/categories")
async def get_categories():
    """카테고리 정보 API"""
    return {
        'success': True,
        'categories': {
            'current_member': {
                'name': '현직 국회의원',
                'count': len(politicians_by_category['current_member']),
                'description': '현직 22대 국회의원'
            },
            'election_candidate': {
                'name': '22대 출마자',
                'count': len(politicians_by_category['election_candidate']),
                'description': '22대 국회의원선거 출마자'
            }
        }
    }

@app.get("/api/statistics")
async def get_statistics():
    """통계 정보 API"""
    try:
        current_members = politicians_by_category['current_member']
        candidates = politicians_by_category['election_candidate']
        
        # 정당별 통계
        party_stats = {}
        for politician in current_members + candidates:
            party = politician.get('party', '미상')
            if party not in party_stats:
                party_stats[party] = {'current': 0, 'candidate': 0}
            
            if politician.get('category') == 'current_member':
                party_stats[party]['current'] += 1
            else:
                party_stats[party]['candidate'] += 1
        
        return {
            'success': True,
            'statistics': {
                'total_politicians': len(current_members) + len(candidates),
                'current_members': len(current_members),
                'election_candidates': len(candidates),
                'parties': len(party_stats),
                'party_breakdown': party_stats
            }
        }
        
    except Exception as e:
        logger.error(f"통계 조회 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"통계 조회 중 오류가 발생했습니다: {str(e)}")

@app.get("/api/reload")
async def reload_data():
    """데이터 다시 로드"""
    if load_data():
        return {
            'success': True,
            'message': '데이터 다시 로드 완료',
            'statistics': {
                'current_members': len(politicians_by_category['current_member']),
                'election_candidates': len(politicians_by_category['election_candidate'])
            }
        }
    else:
        raise HTTPException(status_code=500, detail="데이터 로드 실패")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8002))
    uvicorn.run(app, host="0.0.0.0", port=port)

