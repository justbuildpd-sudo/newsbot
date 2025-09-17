from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.responses import Response
import uvicorn
from news_service import NewsService
from stable_news_service import stable_news_service
from politician_service import politician_service
from politician_analyzer import politician_analyzer
from rate_limiter import rate_limiter
from monitoring import system_monitor
from database import db
from assembly_api_service import assembly_api
from processed_assembly_service import processed_assembly_service
from processed_full_assembly_service import processed_full_assembly_service
from meeting_processor import MeetingProcessor
import json
import time
from datetime import datetime

app = FastAPI(title="NewsBot API", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 뉴스 서비스 인스턴스
news_service = NewsService()

# 상임위원회 발화록 처리기
meeting_processor = MeetingProcessor("/Users/hopidaay/InsightForge/qa_service/data/processed_meetings")

# Rate Limiting 및 모니터링 미들웨어
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    start_time = time.time()
    
    # 클라이언트 IP 추출
    client_ip = request.client.host
    if request.headers.get("x-forwarded-for"):
        client_ip = request.headers.get("x-forwarded-for").split(",")[0].strip()
    
    # Rate Limiting 확인
    is_allowed, message = rate_limiter.is_allowed(client_ip)
    
    if not is_allowed:
        # 보안 이벤트 로깅
        system_monitor.log_security_event("rate_limit_exceeded", {
            "ip": client_ip,
            "path": request.url.path,
            "user_agent": request.headers.get("user-agent", "")
        })
        
        return JSONResponse(
            status_code=429,
            content={
                "success": False,
                "error": "Rate limit exceeded",
                "message": message,
                "retry_after": 60
            }
        )
    
    # 요청 처리
    response = await call_next(request)
    
    # 응답 시간 기록
    response_time = time.time() - start_time
    system_monitor.record_request(response_time, response.status_code)
    
    return response

@app.get("/")
async def root():
    return {"message": "NewsBot API Server", "status": "running"}

@app.get("/api/news")
async def get_news():
    """정치 관련 뉴스 가져오기 (안정적 버전)"""
    try:
        # 안정적인 뉴스 서비스 사용
        news = stable_news_service.get_cached_news()
        return {
            "success": True,
            "data": news,
            "count": len(news),
            "timestamp": datetime.now().isoformat(),
            "source": "안정적 뉴스 서비스"
        }
    except Exception as e:
        # 백업으로 기존 서비스 사용
        try:
            news = news_service.get_cached_news()
            return {
                "success": True,
                "data": news,
                "count": len(news),
                "timestamp": datetime.now().isoformat(),
                "source": "백업 뉴스 서비스"
            }
        except Exception as backup_error:
            raise HTTPException(status_code=500, detail=f"뉴스 가져오기 실패: {str(e)}")

@app.get("/api/news/refresh")
async def refresh_news():
    """뉴스 새로고침"""
    try:
        # 캐시 초기화하고 새로운 뉴스 가져오기
        news_service.news_cache = {}
        news = news_service.get_political_news()
        
        # 캐시에 저장
        for article in news:
            news_id = hashlib.md5(article['title'].encode()).hexdigest()
            news_service.news_cache[news_id] = article
        
        return {
            "success": True,
            "data": news,
            "count": len(news),
            "message": "뉴스가 새로고침되었습니다",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"뉴스 새로고침 실패: {str(e)}")


@app.get("/api/news/stats")
async def get_news_stats():
    """뉴스 통계 정보"""
    try:
        news = news_service.get_cached_news()
        
        # 키워드별 통계
        keyword_stats = {}
        for article in news:
            for keyword in news_service.political_keywords:
                if keyword in article['title'].lower():
                    keyword_stats[keyword] = keyword_stats.get(keyword, 0) + 1
        
        return {
            "success": True,
            "stats": {
                "total_news": len(news),
                "keyword_stats": keyword_stats,
                "last_cleanup": news_service.last_cleanup.isoformat(),
                "next_cleanup": (news_service.last_cleanup + news_service.cleanup_interval).isoformat()
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"통계 가져오기 실패: {str(e)}")

@app.get("/api/news/content")
async def get_news_content(url: str):
    """뉴스 기사 전문 가져오기"""
    try:
        content = news_service.get_news_content(url)
        return {
            "success": True,
            "data": content,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"뉴스 내용 가져오기 실패: {str(e)}")

@app.get("/api/news/with-politicians")
async def get_news_with_politicians():
    """뉴스별 언급된 정치인 정보 포함하여 반환"""
    try:
        news_data = news_service.get_cached_news()
        news_with_politicians = politician_analyzer.get_news_with_politicians(news_data)
        
        response_data = {
            "success": True,
            "data": news_with_politicians,
            "total_count": len(news_with_politicians),
            "timestamp": datetime.now().isoformat()
        }
        
        # 캐시 제어 헤더 추가
        response = JSONResponse(content=response_data)
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"뉴스-정치인 매칭 실패: {str(e)}")

@app.get("/api/news/politician-mentions")
async def get_politician_mentions():
    """정치인별 뉴스 언급 통계"""
    try:
        news_data = news_service.get_cached_news()
        mentioned_politicians = politician_analyzer.analyze_news_mentions(news_data)
        
        response_data = {
            "success": True,
            "data": mentioned_politicians,
            "total_politicians": len(mentioned_politicians),
            "timestamp": datetime.now().isoformat()
        }
        
        # 캐시 제어 헤더 추가
        response = JSONResponse(content=response_data)
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"정치인 언급 분석 실패: {str(e)}")

@app.get("/api/health")
async def health_check():
    """서버 상태 확인 (최적화)"""
    try:
        # 기본 상태 정보
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "uptime": "running"
        }
        
        # 뉴스 서비스 상태
        try:
            news_count = len(news_service.news_cache)
            health_status["news_service"] = {
                "status": "healthy",
                "cached_news": news_count,
                "last_fetch": news_service.last_news_fetch.isoformat() if news_service.last_news_fetch else None
            }
        except Exception as e:
            health_status["news_service"] = {"status": "error", "error": str(e)}
        
        # 정치인 분석기 상태
        try:
            if hasattr(politician_analyzer, '_initialized') and politician_analyzer._initialized:
                health_status["politician_analyzer"] = {
                    "status": "healthy",
                    "politicians_count": len(politician_analyzer.politicians),
                    "mapping_count": len(politician_analyzer.name_mapping)
                }
            else:
                health_status["politician_analyzer"] = {"status": "not_initialized"}
        except Exception as e:
            health_status["politician_analyzer"] = {"status": "error", "error": str(e)}
        
        # 시스템 모니터링 (간소화)
        try:
            stats = system_monitor.get_system_stats()
            health_status["system"] = {
                "memory_usage": stats.get("memory_usage", "unknown"),
                "cpu_usage": stats.get("cpu_usage", "unknown")
            }
        except:
            health_status["system"] = {"status": "monitoring_unavailable"}
        
        return health_status
        
    except Exception as e:
        return {
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

@app.get("/api/monitoring/stats")
async def get_monitoring_stats():
    """모니터링 통계 확인"""
    stats = system_monitor.get_system_stats()
    alerts = system_monitor.check_alerts()
    recent_errors = system_monitor.get_recent_errors()
    
    return {
        "success": True,
        "data": {
            "system_stats": stats,
            "alerts": alerts,
            "recent_errors": recent_errors
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/rate-limit/stats")
async def get_rate_limit_stats():
    """Rate Limiting 통계 확인"""
    stats = rate_limiter.get_stats()
    return {
        "success": True,
        "data": stats,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/rate-limit/reset")
async def reset_rate_limits():
    """Rate Limiting 초기화 (관리자용)"""
    # 실제 운영에서는 인증이 필요
    rate_limiter.blocked_ips.clear()
    rate_limiter.ip_requests.clear()
    return {
        "success": True,
        "message": "Rate limits have been reset",
        "timestamp": datetime.now().isoformat()
    }

# 정치인 관련 API 엔드포인트
@app.get("/api/politicians")
async def get_politicians():
    """모든 정치인 목록을 반환합니다. (전체 309명)"""
    try:
        # 전체 국회의원 데이터 사용
        politicians = processed_full_assembly_service.get_all_members()
        
        return {
            "success": True,
            "data": politicians,
            "total_count": len(politicians),
            "source": "22대 국회의원 전체 데이터 (309명)"
        }
    except Exception as e:
        # 오류 발생 시 빈 배열 반환 (서비스 중단 방지)
        return {
            "success": False,
            "data": [],
            "total_count": 0,
            "error": f"정치인 목록 조회 오류: {str(e)}",
            "message": "일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
        }

@app.get("/api/politicians/featured")
async def get_featured_politicians(limit: int = 6):
    """주요 정치인 목록을 반환합니다. (정당별 대표)"""
    try:
        # 전체 국회의원 데이터에서 정당별 대표 의원들 선택
        politicians = processed_full_assembly_service.get_top_members(limit)
        return {
            "success": True,
            "data": politicians,
            "count": len(politicians),
            "source": "22대 국회의원 전체 데이터 (정당별 대표)"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"주요 정치인 조회 오류: {str(e)}")

@app.get("/api/politicians/{politician_id}")
async def get_politician_by_id(politician_id: int):
    """특정 정치인 정보를 반환합니다."""
    try:
        politician = politician_service.get_politician_by_id(politician_id)
        if not politician:
            raise HTTPException(status_code=404, detail="정치인을 찾을 수 없습니다")
        
        return {
            "success": True,
            "data": politician
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"정치인 조회 오류: {str(e)}")

@app.get("/api/politicians/search")
async def search_politicians(q: str):
    """정치인을 검색합니다."""
    try:
        if not q or len(q.strip()) < 2:
            raise HTTPException(status_code=400, detail="검색어는 2글자 이상이어야 합니다")
        
        politicians = politician_service.search_politicians(q.strip())
        return {
            "success": True,
            "data": politicians,
            "query": q,
            "count": len(politicians)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"정치인 검색 오류: {str(e)}")

@app.get("/api/politicians/party/{party}")
async def get_politicians_by_party(party: str):
    """정당별 정치인 목록을 반환합니다."""
    try:
        politicians = politician_service.get_politicians_by_party(party)
        return {
            "success": True,
            "data": politicians,
            "party": party,
            "count": len(politicians)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"정당별 정치인 조회 오류: {str(e)}")

@app.get("/api/politicians/stats")
async def get_politician_stats():
    """정치인 통계 정보를 반환합니다."""
    try:
        stats = politician_service.get_politician_summary()
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"정치인 통계 조회 오류: {str(e)}")

# 핫이슈 랭킹 관련 API는 제거됨 - 의미 없는 기능

@app.post("/api/politicians/init")
async def initialize_politicians():
    """정치인 데이터 초기화"""
    try:
        # 정치인 분석기 캐시 초기화
        politician_analyzer.reset_cache()
        return {"success": True, "message": "정치인 분석기 캐시 초기화 완료"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"정치인 데이터 초기화 실패: {str(e)}")

@app.get("/api/assembly/members")
async def get_assembly_members():
    """국회의원 현황 조회 (실시간 API)"""
    try:
        members = assembly_api.get_member_list()
        return {
            "success": True,
            "data": members,
            "total_count": len(members),
            "source": "국회 공공데이터포털 실시간 API"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"국회의원 조회 실패: {str(e)}")

@app.get("/api/assembly/members/party/{party_name}")
async def get_assembly_members_by_party(party_name: str):
    """소속정당별 국회의원 목록 조회 (실시간 API)"""
    try:
        members = assembly_api.get_members_by_party(party_name)
        return {
            "success": True,
            "data": members,
            "total_count": len(members),
            "party": party_name,
            "source": "국회 공공데이터포털 실시간 API"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"정당별 국회의원 조회 실패: {str(e)}")

@app.get("/api/assembly/members/{member_id}")
async def get_assembly_member_detail(member_id: str):
    """국회의원 상세 정보 조회 (실시간 API)"""
    try:
        member = assembly_api.get_member_detail(member_id)
        if member:
            return {
                "success": True,
                "data": member,
                "source": "국회 공공데이터포털 실시간 API"
            }
        else:
            raise HTTPException(status_code=404, detail="국회의원 정보를 찾을 수 없습니다")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"국회의원 상세 조회 실패: {str(e)}")

@app.get("/api/assembly/members/{member_id}/committee-activities")
async def get_member_committee_activities(member_id: str):
    """특정 국회의원의 상임위원회 활동 조회"""
    try:
        # 의원 정보에서 부서코드 가져오기
        member = assembly_api.get_member_detail(member_id)
        if not member:
            raise HTTPException(status_code=404, detail="국회의원을 찾을 수 없습니다")
        
        dept_cd = member.get('dept_code', '')
        if not dept_cd:
            raise HTTPException(status_code=400, detail="부서코드가 없습니다")
        
        activities = assembly_api.get_committee_activities(dept_cd)
        
        return {
            "success": True,
            "data": {
                "member_name": member.get('name', ''),
                "member_party": member.get('party', ''),
                "member_district": member.get('district', ''),
                "activities": activities,
                "total_count": len(activities)
            },
            "source": "국회 공공데이터포털 상임위원회 활동 API"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"상임위원회 활동 조회 실패: {str(e)}")

@app.get("/api/meetings/speakers")
async def get_meeting_speakers():
    """상임위원회 발언자 목록 조회"""
    try:
        speaker_data = meeting_processor.load_speaker_data()
        
        return {
            "success": True,
            "data": speaker_data,
            "total_speakers": len(speaker_data),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"발언자 목록 조회 실패: {str(e)}")

@app.get("/api/meetings/records")
async def get_meeting_records():
    """상임위원회 회의록 조회"""
    try:
        meeting_records = meeting_processor.load_meeting_records()
        
        return {
            "success": True,
            "data": meeting_records,
            "total_meetings": len(meeting_records),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"회의록 조회 실패: {str(e)}")

@app.get("/api/meetings/politician-speeches")
async def get_politician_speeches():
    """정치인별 발언 매칭 조회"""
    try:
        # 정치인 목록 로드
        politician_list = assembly_api.get_member_list()
        
        # 발언자 데이터 로드
        speaker_data = meeting_processor.load_speaker_data()
        
        # 정치인과 발언 매칭
        matched_speeches = meeting_processor.match_politicians_with_speeches(politician_list)
        
        return {
            "success": True,
            "data": matched_speeches,
            "total_politicians": len(matched_speeches),
            "total_speeches": sum(data['total_speeches'] for data in matched_speeches.values()),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"정치인 발언 매칭 실패: {str(e)}")

@app.get("/api/meetings/related-persons")
async def get_related_persons():
    """관련인물 목록 조회"""
    try:
        # 정치인 목록 로드
        politician_list = assembly_api.get_member_list()
        
        # 발언자 데이터 로드
        speaker_data = meeting_processor.load_speaker_data()
        
        # 정치인과 발언 매칭
        matched_speeches = meeting_processor.match_politicians_with_speeches(politician_list)
        
        # 관련인물 추출
        related_persons = meeting_processor.extract_related_persons()
        
        return {
            "success": True,
            "data": related_persons,
            "total_related_persons": len(related_persons),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"관련인물 조회 실패: {str(e)}")

@app.get("/api/meetings/summary")
async def get_meeting_summary():
    """상임위원회 발화록 요약 조회"""
    try:
        # 모든 데이터 로드
        speaker_data = meeting_processor.load_speaker_data()
        meeting_records = meeting_processor.load_meeting_records()
        politician_list = assembly_api.get_member_list()
        matched_speeches = meeting_processor.match_politicians_with_speeches(politician_list)
        related_persons = meeting_processor.extract_related_persons()
        
        # 요약 생성
        summary = meeting_processor.generate_speech_summary()
        
        return {
            "success": True,
            "data": summary,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"발화록 요약 조회 실패: {str(e)}")

# 추가 API 엔드포인트
@app.get("/api/assembly/statistics")
async def get_assembly_statistics():
    """국회의원 통계 정보 (전체 309명)"""
    try:
        stats = processed_full_assembly_service.get_statistics()
        return {
            "success": True,
            "data": stats,
            "source": "22대 국회의원 전체 데이터 (309명)"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"통계 조회 실패: {str(e)}")

@app.get("/api/assembly/members/committee/{committee}")
async def get_assembly_members_by_committee(committee: str):
    """위원회별 국회의원 목록 조회"""
    try:
        members = processed_assembly_service.get_members_by_committee(committee)
        return {
            "success": True,
            "data": members,
            "total_count": len(members),
            "committee": committee,
            "source": "가공된 국회 공식 API 데이터"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"위원회별 국회의원 조회 실패: {str(e)}")

@app.get("/api/assembly/members/orientation/{orientation}")
async def get_assembly_members_by_orientation(orientation: str):
    """정치 성향별 국회의원 목록 조회"""
    try:
        members = processed_assembly_service.get_members_by_orientation(orientation)
        return {
            "success": True,
            "data": members,
            "total_count": len(members),
            "orientation": orientation,
            "source": "가공된 국회 공식 API 데이터"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"정치 성향별 국회의원 조회 실패: {str(e)}")

@app.get("/api/assembly/search")
async def search_assembly_members(query: str):
    """국회의원 검색"""
    try:
        members = processed_assembly_service.search_members(query)
        return {
            "success": True,
            "data": members,
            "total_count": len(members),
            "query": query,
            "source": "가공된 국회 공식 API 데이터"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"국회의원 검색 실패: {str(e)}")

# 실시간 국회 API 엔드포인트들
@app.get("/api/assembly/realtime/members")
async def get_realtime_assembly_members():
    """실시간 국회의원 현황 조회"""
    try:
        members = assembly_api.get_member_list()
        return {
            "success": True,
            "data": members,
            "total_count": len(members),
            "source": "국회 공공데이터포털 실시간 API",
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"실시간 국회의원 조회 실패: {str(e)}")

@app.get("/api/assembly/realtime/members/party/{party_name}")
async def get_realtime_assembly_members_by_party(party_name: str):
    """실시간 소속정당별 국회의원 목록 조회"""
    try:
        members = assembly_api.get_members_by_party(party_name)
        return {
            "success": True,
            "data": members,
            "total_count": len(members),
            "party": party_name,
            "source": "국회 공공데이터포털 실시간 API",
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"실시간 정당별 국회의원 조회 실패: {str(e)}")

@app.get("/api/assembly/realtime/members/{member_id}")
async def get_realtime_assembly_member_detail(member_id: str):
    """실시간 국회의원 상세 정보 조회"""
    try:
        member = assembly_api.get_member_detail(member_id)
        if member:
            return {
                "success": True,
                "data": member,
                "source": "국회 공공데이터포털 실시간 API",
                "last_updated": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=404, detail="국회의원 정보를 찾을 수 없습니다")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"실시간 국회의원 상세 조회 실패: {str(e)}")


if __name__ == "__main__":
    import hashlib  # news_service에서 사용
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)
