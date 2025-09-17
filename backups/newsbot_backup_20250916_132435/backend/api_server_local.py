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
from local_politician_service import LocalPoliticianService
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

# 로컬 국회의원 서비스 (샘플 데이터 절대 노출 방지)
local_politician_service = LocalPoliticianService()

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
        return JSONResponse(
            status_code=429,
            content={"error": "Rate limit exceeded", "message": message}
        )
    
    # 요청 처리
    response = await call_next(request)
    
    # 처리 시간 기록
    process_time = time.time() - start_time
    system_monitor.record_request(client_ip, request.url.path, response.status_code, process_time)
    
    return response

# 헬스 체크 엔드포인트
@app.get("/api/health")
async def health_check():
    """서버 상태 확인"""
    try:
        # 뉴스 서비스 상태 확인
        news_status = "healthy"
        try:
            news_service.get_cached_news()
        except Exception as e:
            news_status = f"error: {str(e)}"
        
        # 정치인 분석기 상태 확인
        politician_status = "healthy"
        try:
            politician_analyzer._ensure_initialized()
        except Exception as e:
            politician_status = f"error: {str(e)}"
        
        # 로컬 정치인 서비스 상태 확인
        local_politician_status = "healthy"
        try:
            if not local_politician_service.is_data_loaded():
                local_politician_status = "no_data_loaded"
        except Exception as e:
            local_politician_status = f"error: {str(e)}"
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "news_service": news_status,
                "politician_analyzer": politician_status,
                "local_politician_service": local_politician_status
            }
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "unhealthy", "error": str(e)}
        )

# 국회의원 관련 엔드포인트 (로컬 데이터 사용)
@app.get("/api/assembly/members")
async def get_assembly_members():
    """모든 국회의원 정보 조회 (로컬 데이터)"""
    try:
        politicians = local_politician_service.get_all_politicians()
        return {
            "success": True,
            "data": politicians,
            "count": len(politicians),
            "source": "local_data"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"국회의원 정보 조회 실패: {str(e)}")

@app.get("/api/assembly/members/{member_id}")
async def get_assembly_member_detail(member_id: str):
    """특정 국회의원 상세 정보 조회 (로컬 데이터)"""
    try:
        politician = local_politician_service.get_politician_by_id(member_id)
        if not politician:
            raise HTTPException(status_code=404, detail="국회의원을 찾을 수 없습니다")
        
        return {
            "success": True,
            "data": politician,
            "source": "local_data"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"국회의원 상세 정보 조회 실패: {str(e)}")

@app.get("/api/assembly/members/party/{party_name}")
async def get_assembly_members_by_party(party_name: str):
    """정당별 국회의원 조회 (로컬 데이터)"""
    try:
        # 정당 정보는 현재 API에서 제공하지 않으므로 빈 배열 반환
        politicians = local_politician_service.get_politicians_by_party(party_name)
        return {
            "success": True,
            "data": politicians,
            "count": len(politicians),
            "party": party_name,
            "source": "local_data"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"정당별 국회의원 조회 실패: {str(e)}")

@app.get("/api/assembly/members/search/{query}")
async def search_assembly_members(query: str):
    """국회의원 검색 (로컬 데이터)"""
    try:
        politicians = local_politician_service.search_politicians(query)
        return {
            "success": True,
            "data": politicians,
            "count": len(politicians),
            "query": query,
            "source": "local_data"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"국회의원 검색 실패: {str(e)}")

@app.get("/api/assembly/members/{member_id}/image")
async def get_assembly_member_image(member_id: str):
    """국회의원 이미지 경로 반환"""
    try:
        image_path = local_politician_service.get_politician_image_path(member_id)
        if not image_path:
            raise HTTPException(status_code=404, detail="이미지를 찾을 수 없습니다")
        
        return {
            "success": True,
            "image_path": image_path,
            "member_id": member_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"이미지 경로 조회 실패: {str(e)}")

@app.get("/api/assembly/stats")
async def get_assembly_stats():
    """국회의원 통계 정보"""
    try:
        stats = local_politician_service.get_politician_stats()
        return {
            "success": True,
            "data": stats,
            "source": "local_data"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"통계 정보 조회 실패: {str(e)}")

# 뉴스 관련 엔드포인트
@app.get("/api/news/with-politicians")
async def get_news_with_politicians():
    """정치인이 언급된 뉴스 조회"""
    try:
        news_with_politicians = politician_analyzer.get_news_with_politicians()
        
        response = JSONResponse(content={
            "success": True,
            "data": news_with_politicians,
            "count": len(news_with_politicians)
        })
        
        # 브라우저 캐시 방지
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"뉴스 조회 실패: {str(e)}")

@app.get("/api/news/politician-mentions")
async def get_politician_mentions():
    """정치인 언급 통계"""
    try:
        mentions = politician_analyzer.get_news_with_politicians()
        
        # 언급 통계 계산
        mention_counts = {}
        for news_item in mentions:
            for politician in news_item.get('mentioned_politicians', []):
                name = politician.get('name', 'Unknown')
                mention_counts[name] = mention_counts.get(name, 0) + 1
        
        response = JSONResponse(content={
            "success": True,
            "data": mention_counts,
            "total_mentions": sum(mention_counts.values())
        })
        
        # 브라우저 캐시 방지
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"정치인 언급 통계 조회 실패: {str(e)}")

# 정치인 분석기 초기화
@app.post("/api/politicians/init")
async def init_politician_analyzer():
    """정치인 분석기 초기화"""
    try:
        politician_analyzer.reset_cache()
        return {"success": True, "message": "정치인 분석기가 초기화되었습니다"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"정치인 분석기 초기화 실패: {str(e)}")

# 상임위원회 발화록 관련 엔드포인트
@app.get("/api/meetings/speakers")
async def get_meeting_speakers():
    """발화자 데이터 조회"""
    try:
        speakers = meeting_processor.get_speaker_data()
        return {
            "success": True,
            "data": speakers,
            "count": len(speakers)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"발화자 데이터 조회 실패: {str(e)}")

@app.get("/api/meetings/records")
async def get_meeting_records():
    """회의록 데이터 조회"""
    try:
        records = meeting_processor.get_meeting_records()
        return {
            "success": True,
            "data": records,
            "count": len(records)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"회의록 데이터 조회 실패: {str(e)}")

@app.get("/api/meetings/politician-speeches")
async def get_politician_speeches():
    """정치인 발화 매칭"""
    try:
        speeches = meeting_processor.get_politician_speeches()
        return {
            "success": True,
            "data": speeches,
            "count": len(speeches)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"정치인 발화 매칭 실패: {str(e)}")

@app.get("/api/meetings/related-persons")
async def get_related_persons():
    """관련 인물 추출"""
    try:
        persons = meeting_processor.get_related_persons()
        return {
            "success": True,
            "data": persons,
            "count": len(persons)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"관련 인물 추출 실패: {str(e)}")

@app.get("/api/meetings/summary")
async def get_meeting_summary():
    """회의록 요약"""
    try:
        summary = meeting_processor.get_meeting_summary()
        return {
            "success": True,
            "data": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"회의록 요약 실패: {str(e)}")

@app.get("/api/meetings/committees")
async def get_committees():
    """위원회 목록 조회"""
    try:
        committees = meeting_processor.get_committees()
        return {
            "success": True,
            "data": committees,
            "count": len(committees)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"위원회 목록 조회 실패: {str(e)}")

@app.get("/api/meetings/committee/{committee_name}")
async def get_committee_meetings(committee_name: str):
    """특정 위원회 회의록 조회"""
    try:
        meetings = meeting_processor.get_committee_meetings(committee_name)
        return {
            "success": True,
            "data": meetings,
            "count": len(meetings),
            "committee": committee_name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"위원회 회의록 조회 실패: {str(e)}")

@app.get("/api/meetings/{meeting_id}/details")
async def get_meeting_details(meeting_id: str):
    """특정 회의 상세 정보 조회"""
    try:
        details = meeting_processor.get_meeting_details(meeting_id)
        if not details:
            raise HTTPException(status_code=404, detail="회의를 찾을 수 없습니다")
        
        return {
            "success": True,
            "data": details
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"회의 상세 정보 조회 실패: {str(e)}")

@app.get("/api/meetings/speakers")
async def get_speaker_statistics():
    """발화자 통계"""
    try:
        stats = meeting_processor.get_speaker_statistics()
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"발화자 통계 조회 실패: {str(e)}")

@app.post("/api/meetings/process")
async def process_meeting_files():
    """회의록 파일 배치 처리"""
    try:
        result = meeting_processor.process_all_files_batch()
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"회의록 파일 처리 실패: {str(e)}")

@app.get("/api/meetings/stats")
async def get_meeting_stats():
    """회의록 데이터베이스 통계"""
    try:
        stats = meeting_processor.get_database_stats()
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"회의록 통계 조회 실패: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
