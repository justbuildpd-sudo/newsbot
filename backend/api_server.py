#!/usr/bin/env python3
"""
NewsBot 경량 API 서버 - Render 배포 전용
국회의원 데이터와 기본 평가만 제공하는 최소한의 서버
"""

import os
import json
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from datetime import datetime, timedelta

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title="NewsBot 경량 API",
    description="국회의원 데이터 및 기본 평가 시스템",
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

# 개별 API 서비스 임포트
from assembly_member_api import assembly_api
from bills_info_api import bills_api  
from naver_api_service import naver_api

# 전역 데이터 저장 (개별 API에서 관리)
politicians_data = []
bills_data = {}
news_data = {}
trend_data = {}

def load_bills_data():
    """발의안 데이터 로드"""
    global bills_data
    
    # 발의안 데이터 파일 찾기 (개선된 데이터 우선)
    possible_paths = [
        'enhanced_bills_data_22nd.json',
        'bills_data_22nd.json',
        '../enhanced_bills_data_22nd.json',
        '../bills_data_22nd.json',
        './backend/enhanced_bills_data_22nd.json',
        './backend/bills_data_22nd.json'
    ]
    
    for path in possible_paths:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                bills_data = json.load(f)
            logger.info(f"발의안 데이터 로드 성공: {len(bills_data)}명 ({path})")
            return
        except FileNotFoundError:
            continue
    
    logger.warning("발의안 데이터 파일을 찾을 수 없음")

def load_news_data():
    """뉴스 데이터 로드"""
    global news_data
    
    # 뉴스 데이터 파일 찾기
    possible_paths = [
        'naver_news_collected.json',
        '../naver_news_collected.json'
    ]
    
    for path in possible_paths:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                news_data = json.load(f)
            total_news = sum(len(news) for news in news_data.values())
            logger.info(f"뉴스 데이터 로드 성공: {len(news_data)}명, {total_news}건 ({path})")
            return
        except FileNotFoundError:
            continue
    
    logger.warning("뉴스 데이터 파일을 찾을 수 없음")

def load_trend_data():
    """트렌드 분석 데이터 로드"""
    global trend_data
    
    # 트렌드 데이터 파일 찾기 (확장된 데이터 우선)
    possible_paths = [
        'extended_trend_data.json',
        'naver_integrated_data.json',
        'trend_analysis_result.json',
        '../extended_trend_data.json',
        '../naver_integrated_data.json',
        '../trend_analysis_result.json'
    ]
    
    for path in possible_paths:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                trend_data = json.load(f)
            logger.info(f"트렌드 데이터 로드 성공: {len(trend_data.get('trends', {}))}명 ({path})")
            return
        except FileNotFoundError:
            continue
    
    logger.warning("트렌드 데이터 파일을 찾을 수 없음")

def load_politicians_data():
    """정치인 데이터 로드"""
    global politicians_data
    
    # 여러 경로에서 데이터 파일 찾기 (인증된 충돌 없는 데이터 우선)
    possible_paths = [
        'authentic_assembly_members.json',  # 지역구 충돌 해결된 인증 데이터
        'verified_real_assembly_members.json',  # 가짜 인물 제거된 검증된 데이터
        'processed_full_assembly_members.json',  # 처리된 전체 데이터 (원본)
        '22nd_assembly_members_300.json',  # 백엔드 폴더 내
        '../22nd_assembly_members_300.json',  # 상위 폴더
        'politicians_data_with_party.json',
        'data/politicians.json',
        '../politicians_data_with_party.json'
    ]
    
    for path in possible_paths:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                politicians_data = json.load(f)
            logger.info(f"정치인 데이터 로드 성공: {len(politicians_data)}명 ({path})")
            return
        except FileNotFoundError:
            continue
    
    # 데이터 파일이 없으면 실제 정당 데이터로 샘플 생성
    politicians_data = [
        {
            "name": "이재명",
            "party": "더불어민주당", 
            "district": "경기 성남시분당구을",
            "committee": "기획재정위원회",
            "id": "sample1",
            "photo_url": "https://www.assembly.go.kr/static/portal/img/openassm/new/sample1.jpg"
        },
        {
            "name": "한동훈", 
            "party": "국민의힘",
            "district": "서울 동작구갑",
            "committee": "법제사법위원회", 
            "id": "sample2",
            "photo_url": "https://www.assembly.go.kr/static/portal/img/openassm/new/sample2.jpg"
        },
        {
            "name": "조국", 
            "party": "조국혁신당",
            "district": "서울 종로구",
            "committee": "법제사법위원회", 
            "id": "sample3",
            "photo_url": "https://www.assembly.go.kr/static/portal/img/openassm/new/sample3.jpg"
        },
        {
            "name": "정청래",
            "party": "더불어민주당", 
            "district": "서울 마포구을",
            "committee": "기획재정위원회",
            "id": "sample4",
            "photo_url": "https://www.assembly.go.kr/static/portal/img/openassm/new/sample4.jpg"
        },
        {
            "name": "김기현", 
            "party": "국민의힘",
            "district": "울산 북구",
            "committee": "정무위원회", 
            "id": "sample5",
            "photo_url": "https://www.assembly.go.kr/static/portal/img/openassm/new/sample5.jpg"
        }
    ]
    logger.warning("데이터 파일을 찾을 수 없어 샘플 데이터 사용")

# 성능 최적화 시스템 초기화
try:
    from performance_optimizer import PerformanceOptimizer
    performance_optimizer = PerformanceOptimizer()
    logger.info("성능 최적화 시스템 초기화 완료")
except Exception as e:
    logger.error(f"성능 최적화 시스템 초기화 실패: {e}")
    performance_optimizer = None

# 서버 시작 시 데이터 로드
load_politicians_data()
load_bills_data()
load_news_data()
load_trend_data()

@app.get("/")
async def root():
    """루트 페이지"""
    return {
        "message": "NewsBot 경량 API 서버",
        "status": "running",
        "politicians_count": len(politicians_data),
        "version": "1.0.0"
    }

@app.get("/api/health")
async def health_check():
    """서버 상태 확인"""
    return {
        "status": "healthy",
        "politicians_count": len(politicians_data),
        "data_loaded": len(politicians_data) > 0,
        "version": "1.0.0"
    }

@app.post("/api/reload")
async def reload_data():
    """데이터 강제 재로드"""
    try:
        load_politicians_data()
        load_bills_data()
        load_news_data()
        load_trend_data()
        
        # 샘플 정당 확인
        sample_parties = []
        for member in politicians_data[:5]:
            party = member.get('party', '무소속')
            sample_parties.append(party)
        
        return {
            "success": True,
            "message": "데이터 재로드 완료",
            "politicians_count": len(politicians_data),
            "sample_parties": sample_parties,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"데이터 재로드 실패: {e}")
        raise HTTPException(status_code=500, detail="데이터 재로드 실패")

@app.get("/api/assembly/members")
async def get_assembly_members():
    """국회의원 목록 조회 (최적화)"""
    try:
        # 성능 최적화된 데이터 사용
        if performance_optimizer:
            optimized_data = performance_optimizer.get_politicians_fast()
            if optimized_data:
                return {
                    "success": True,
                    "data": optimized_data,
                    "total_count": len(optimized_data),
                    "source": "NewsBot 경량 API (캐시 최적화)",
                    "cached": True
                }
        
        # 폴백: 기존 데이터
        return {
            "success": True,
            "data": politicians_data,
            "total_count": len(politicians_data),
            "source": "NewsBot 경량 API",
            "cached": False
        }
    except Exception as e:
        logger.error(f"국회의원 조회 오류: {e}")
        raise HTTPException(status_code=500, detail="국회의원 데이터 조회 실패")

@app.get("/api/assembly/members/{member_id}")
async def get_assembly_member(member_id: str):
    """특정 국회의원 조회 (국회의원통합API 사용)"""
    try:
        # 1. 국회의원통합API 사용
        member = assembly_api.get_member_by_name(member_id)
        
        if member:
            return {
                "success": True,
                "data": member,
                "source": "국회의원통합API"
            }
        else:
            return {
                "success": False,
                "error": f"국회의원 '{member_id}'를 찾을 수 없습니다"
            }
            
    except Exception as e:
        logger.error(f"국회의원 상세 조회 오류: {e}")
        return {
            "success": False,
            "error": f"국회의원 상세 조회 실패: {str(e)}"
        }

@app.get("/api/assembly/stats")
async def get_assembly_stats():
    """국회의원 통계"""
    try:
        # 정당별 분포 계산
        party_stats = {}
        for politician in politicians_data:
            party = politician.get('party', '정당정보없음')
            party_stats[party] = party_stats.get(party, 0) + 1
        
        return {
            "success": True,
            "data": {
                "total_politicians": len(politicians_data),
                "party_distribution": party_stats
            },
            "source": "NewsBot 경량 API"
        }
    except Exception as e:
        logger.error(f"통계 조회 오류: {e}")
        raise HTTPException(status_code=500, detail="통계 조회 실패")

@app.get("/api/politicians")
async def get_politicians():
    """정치인 목록 (호환성)"""
    return await get_assembly_members()

@app.get("/api/politicians/featured")
async def get_featured_politicians():
    """주요 정치인 목록"""
    try:
        # 상위 6명만 반환
        featured = politicians_data[:6]
        return {
            "success": True,
            "data": featured,
            "count": len(featured),
            "source": "NewsBot 경량 API"
        }
    except Exception as e:
        logger.error(f"주요 정치인 조회 오류: {e}")
        raise HTTPException(status_code=500, detail="주요 정치인 조회 실패")

@app.get("/api/bills/scores")
async def get_bill_scores():
    """발의안 점수 (최적화)"""
    try:
        # 성능 최적화된 데이터 사용
        if performance_optimizer:
            cached_scores = performance_optimizer.get_bill_scores_fast()
            if cached_scores:
                return {
                    "success": True,
                    "data": cached_scores,
                    "count": len(cached_scores),
                    "source": "NewsBot 경량 API (캐시 최적화)",
                    "last_updated": datetime.now().isoformat(),
                    "cached": True
                }
        
        # 폴백: 기존 계산
        bill_scores = {}
        for name, bills in bills_data.items():
            if bills:
                main_proposals = sum(1 for bill in bills if len(bill.get('co_proposers', [])) > 0)
                co_proposals = len(bills) - main_proposals
                total_bills = len(bills)
                
                passed_bills = sum(1 for bill in bills 
                                 if bill.get('status') in ['본회의 통과', '정부이송', '공포'])
                success_rate = round(passed_bills / total_bills, 2) if total_bills > 0 else 0
                
                recent_bills = sum(1 for bill in bills 
                                 if is_recent_bill(bill.get('propose_date', '')))
                
                bill_scores[name] = {
                    "main_proposals": main_proposals,
                    "co_proposals": co_proposals,
                    "total_bills": total_bills,
                    "success_rate": success_rate,
                    "recent_activity": recent_bills
                }
        
        return {
            "success": True,
            "data": bill_scores,
            "count": len(bill_scores),
            "source": "NewsBot 경량 API (실시간 계산)",
            "last_updated": datetime.now().isoformat(),
            "cached": False
        }
    except Exception as e:
        logger.error(f"발의안 점수 조회 오류: {e}")
        raise HTTPException(status_code=500, detail="발의안 점수 조회 실패")

def is_recent_bill(propose_date):
    """최근 3개월 내 발의안인지 확인"""
    try:
        if not propose_date:
            return False
        bill_date = datetime.strptime(propose_date, '%Y-%m-%d')
        three_months_ago = datetime.now() - timedelta(days=90)
        return bill_date >= three_months_ago
    except:
        return False

@app.get("/api/bills/politician/{politician_name}")
async def get_politician_bills(politician_name: str):
    """특정 정치인의 발의안 목록 (개선된 데이터)"""
    try:
        # 발의안 데이터에서 해당 정치인 찾기
        if politician_name not in bills_data:
            raise HTTPException(status_code=404, detail="해당 정치인의 발의안을 찾을 수 없습니다")
        
        bills = bills_data[politician_name]
        
        # 발의안을 최신순으로 정렬
        sorted_bills = sorted(bills, key=lambda x: x.get('propose_date', ''), reverse=True)
        
        # 통계 계산
        stats = {
            "total_bills": len(bills),
            "main_proposals": sum(1 for bill in bills if len(bill.get('co_proposers', [])) > 0),
            "recent_bills": sum(1 for bill in bills if is_recent_bill(bill.get('propose_date', ''))),
            "passed_bills": sum(1 for bill in bills 
                              if bill.get('status') in ['본회의 통과', '정부이송', '공포']),
            "committees": list(set(bill.get('committee', '') for bill in bills if bill.get('committee')))
        }
        
        return {
            "success": True,
            "data": {
                "politician": politician_name,
                "bills": sorted_bills,
                "statistics": stats,
                "total_count": len(bills)
            },
            "source": "NewsBot 경량 API (개선된 발의안 데이터)",
            "last_updated": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"정치인 발의안 조회 오류: {e}")
        raise HTTPException(status_code=500, detail="발의안 조회 실패")

@app.get("/api/bills/recent")
async def get_recent_bills(limit: int = 25):
    """최근 발의안 목록"""
    try:
        all_bills = []
        
        # 모든 의원의 발의안 수집
        for politician_name, bills in bills_data.items():
            for bill in bills:
                bill_copy = bill.copy()
                bill_copy['politician'] = politician_name
                all_bills.append(bill_copy)
        
        # 최신순으로 정렬
        sorted_bills = sorted(all_bills, 
                            key=lambda x: x.get('propose_date', ''), 
                            reverse=True)[:limit]
        
        return {
            "success": True,
            "data": sorted_bills,
            "total_count": len(sorted_bills),
            "source": "NewsBot 경량 API (개선된 발의안 데이터)"
        }
    except Exception as e:
        logger.error(f"최근 발의안 조회 오류: {e}")
        raise HTTPException(status_code=500, detail="최근 발의안 조회 실패")

@app.get("/api/news/politician/{politician_name}")
async def get_politician_news(politician_name: str):
    """특정 정치인 관련 뉴스"""
    try:
        if politician_name not in news_data:
            raise HTTPException(status_code=404, detail="해당 정치인의 뉴스를 찾을 수 없습니다")
        
        news_list = news_data[politician_name]
        
        # 감정 분석 통계
        sentiments = {'positive': 0, 'negative': 0, 'neutral': 0}
        for news in news_list:
            sentiments[news.get('sentiment', 'neutral')] += 1
        
        return {
            "success": True,
            "data": {
                "politician": politician_name,
                "news": news_list,
                "statistics": {
                    "total_count": len(news_list),
                    "positive": sentiments['positive'],
                    "negative": sentiments['negative'],
                    "neutral": sentiments['neutral'],
                    "sentiment_ratio": sentiments['positive'] / len(news_list) if news_list else 0
                }
            },
            "source": "네이버 뉴스 API"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"정치인 뉴스 조회 오류: {e}")
        raise HTTPException(status_code=500, detail="뉴스 조회 실패")

@app.get("/api/news/trending")
async def get_trending_news(limit: int = 25):
    """트렌딩 뉴스 (모든 정치인)"""
    try:
        all_news = []
        
        # 모든 정치인의 뉴스 수집
        for politician_name, news_list in news_data.items():
            for news in news_list:
                news_copy = news.copy()
                all_news.append(news_copy)
        
        # 최신순으로 정렬 (pub_date 기준)
        all_news.sort(key=lambda x: x.get('pub_date', ''), reverse=True)
        
        return {
            "success": True,
            "data": all_news[:limit],
            "total_count": len(all_news),
            "source": "네이버 뉴스 API"
        }
    except Exception as e:
        logger.error(f"트렌딩 뉴스 조회 오류: {e}")
        raise HTTPException(status_code=500, detail="트렌딩 뉴스 조회 실패")

@app.get("/api/news/stats")
async def get_news_stats():
    """뉴스 통계"""
    try:
        stats = {
            "politicians_count": len(news_data),
            "total_news": sum(len(news) for news in news_data.values()),
            "sentiment_distribution": {'positive': 0, 'negative': 0, 'neutral': 0},
            "politicians_ranking": []
        }
        
        # 감정 분석 통계
        for politician_name, news_list in news_data.items():
            politician_sentiments = {'positive': 0, 'negative': 0, 'neutral': 0}
            for news in news_list:
                sentiment = news.get('sentiment', 'neutral')
                stats["sentiment_distribution"][sentiment] += 1
                politician_sentiments[sentiment] += 1
            
            stats["politicians_ranking"].append({
                "politician": politician_name,
                "news_count": len(news_list),
                "positive": politician_sentiments['positive'],
                "negative": politician_sentiments['negative'],
                "neutral": politician_sentiments['neutral']
            })
        
        # 뉴스 수 기준 정렬
        stats["politicians_ranking"].sort(key=lambda x: x['news_count'], reverse=True)
        
        return {
            "success": True,
            "data": stats,
            "source": "네이버 뉴스 API"
        }
    except Exception as e:
        logger.error(f"뉴스 통계 조회 오류: {e}")
        raise HTTPException(status_code=500, detail="뉴스 통계 조회 실패")

# 정치인 전용 검색 서비스 초기화
try:
    from politician_search_service import PoliticianSearchService
    search_service = PoliticianSearchService()
    logger.info("정치인 검색 서비스 초기화 완료")
except Exception as e:
    logger.error(f"검색 서비스 초기화 실패: {e}")
    search_service = None

@app.get("/api/search/politicians")
async def search_politicians(q: str, limit: int = 10):
    """정치인 검색 (정치인만 검색 가능)"""
    try:
        if not search_service:
            raise HTTPException(status_code=503, detail="검색 서비스를 사용할 수 없습니다")
        
        # 검색어 유효성 검사
        validation = search_service.validate_search_query(q)
        if not validation['valid']:
            return {
                "success": False,
                "error": validation['error'],
                "error_code": validation['error_code'],
                "suggestions": validation.get('suggestions', [])
            }
        
        # 정치인 검색 실행
        search_results = search_service.search_politicians(q, max_results=limit)
        
        return {
            "success": search_results['success'],
            "query": q,
            "results": search_results['results'],
            "total_found": search_results['total_found'],
            "search_type": "politician_only"
        }
        
    except Exception as e:
        logger.error(f"정치인 검색 오류: {e}")
        raise HTTPException(status_code=500, detail="검색 서비스 오류")

@app.get("/api/trends/chart")
async def get_trend_chart():
    """트렌드 차트 데이터"""
    try:
        if not trend_data:
            raise HTTPException(status_code=404, detail="트렌드 데이터를 찾을 수 없습니다")
        
        chart_data = trend_data.get('chart_data', {})
        if not chart_data:
            raise HTTPException(status_code=404, detail="차트 데이터가 없습니다")
        
        return {
            "success": True,
            "data": chart_data,
            "source": "네이버 데이터랩 + 뉴스 API"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"트렌드 차트 조회 오류: {e}")
        raise HTTPException(status_code=500, detail="트렌드 차트 조회 실패")

@app.get("/api/trends/ranking")
async def get_trend_ranking():
    """트렌드 랭킹"""
    try:
        if not trend_data:
            raise HTTPException(status_code=404, detail="트렌드 데이터를 찾을 수 없습니다")
        
        ranking = trend_data.get('ranking', [])
        summary = trend_data.get('summary', {})
        
        return {
            "success": True,
            "data": {
                "ranking": ranking,
                "summary": summary,
                "generated_at": trend_data.get('generated_at', '')
            },
            "source": "네이버 데이터랩 + 뉴스 API"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"트렌드 랭킹 조회 오류: {e}")
        raise HTTPException(status_code=500, detail="트렌드 랭킹 조회 실패")

@app.get("/api/trends/politician/{politician_name}")
async def get_politician_trend(politician_name: str):
    """특정 정치인 트렌드"""
    try:
        if not trend_data or 'trends' not in trend_data:
            raise HTTPException(status_code=404, detail="트렌드 데이터를 찾을 수 없습니다")
        
        politician_trend = trend_data['trends'].get(politician_name)
        if not politician_trend:
            raise HTTPException(status_code=404, detail="해당 정치인의 트렌드 데이터를 찾을 수 없습니다")
        
        return {
            "success": True,
            "data": politician_trend,
            "source": "네이버 데이터랩 + 뉴스 API"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"정치인 트렌드 조회 오류: {e}")
        raise HTTPException(status_code=500, detail="정치인 트렌드 조회 실패")

@app.get("/api/connectivity/{politician_name}")
async def get_politician_connectivity(politician_name: str):
    """정치인 연결성 분석"""
    try:
        # 해당 정치인 정보 찾기
        target_politician = None
        for politician in politicians_data:
            if politician.get('name') == politician_name:
                target_politician = politician
                break
        
        if not target_politician:
            return {
                "success": False,
                "error": "정치인을 찾을 수 없습니다"
            }
        
        # 연결성 분석
        connectivity_data = analyze_connectivity(target_politician, politicians_data)
        
        return {
            "success": True,
            "data": connectivity_data,
            "politician": politician_name,
            "source": "연결성 분석 시스템"
        }
        
    except Exception as e:
        logger.error(f"연결성 분석 오류: {e}")
        raise HTTPException(status_code=500, detail="연결성 분석 실패")

def analyze_connectivity(target_politician, all_politicians):
    """정치인 연결성 분석 함수"""
    try:
        connections = []
        target_committee = target_politician.get('committee', '')
        target_party = target_politician.get('party', '')
        
        if not target_committee:
            return []
        
        # 같은 상임위원회 의원들 찾기
        for politician in all_politicians:
            if (politician.get('name') != target_politician.get('name') and 
                politician.get('committee') == target_committee):
                
                # 연결성 점수 계산
                score = calculate_connectivity_score(target_politician, politician)
                
                connections.append({
                    'name': politician.get('name'),
                    'party': politician.get('party'),
                    'district': politician.get('district'),
                    'committee': politician.get('committee'),
                    'connectivity_score': score,
                    'is_same_party': politician.get('party') == target_party,
                    'connection_type': 'committee',
                    'connection_reason': f"{target_committee} 동료"
                })
        
        # 점수순으로 정렬하고 상위 8명 반환
        connections.sort(key=lambda x: x['connectivity_score'], reverse=True)
        return connections[:8]
        
    except Exception as e:
        logger.error(f"연결성 분석 계산 오류: {e}")
        return []

def calculate_connectivity_score(politician1, politician2):
    """두 정치인 간의 연결성 점수 계산"""
    try:
        score = 70  # 기본 위원회 연결 점수
        
        # 같은 정당 보너스
        if politician1.get('party') == politician2.get('party'):
            score += 20
        else:
            score += 10  # 다른 정당이어도 협력 가능성
        
        # 지역 유사성 보너스
        district1 = politician1.get('district', '')
        district2 = politician2.get('district', '')
        
        if district1 and district2:
            # 같은 시/도인지 확인
            region1 = district1.split(' ')[0] if ' ' in district1 else district1
            region2 = district2.split(' ')[0] if ' ' in district2 else district2
            
            if region1 == region2:
                score += 10
        
        return min(100, score)
        
    except Exception as e:
        logger.error(f"연결성 점수 계산 오류: {e}")
        return 70

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    
    print("🚀 NewsBot 경량 API 서버 시작")
    print(f"📊 정치인 데이터: {len(politicians_data)}명")
    print(f"🌐 서버 주소: http://0.0.0.0:{port}")
    print(f"📖 API 문서: http://0.0.0.0:{port}/docs")
    print("=" * 50)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
