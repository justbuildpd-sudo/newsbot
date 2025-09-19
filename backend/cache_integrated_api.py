#!/usr/bin/env python3
"""
캐시 통합 API 서버
하이브리드 캐시 시스템과 통합된 출마자 정보 검색 API
"""

import os
import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# 하이브리드 캐시 시스템 임포트
from hybrid_cache_system import cache_system, initialize_cache_system, search_candidate, get_cache_stats
from render_process_manager import setup_render_process_management, get_render_status, shutdown_render_process

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title="NewsBot 하이브리드 캐시 API",
    description="3단계 티어드 캐싱 시스템을 통한 출마자 정보 검색 API",
    version="2.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 전역 변수
cache_initialized = False
api_stats = {
    'total_requests': 0,
    'successful_requests': 0,
    'failed_requests': 0,
    'average_response_time': 0,
    'start_time': datetime.now().isoformat()
}

@app.on_event("startup")
async def startup_event():
    """서버 시작 시 초기화"""
    global cache_initialized
    
    logger.info("🚀 캐시 통합 API 서버 시작")
    
    # 렌더 프로세스 관리 설정
    process_setup_success = setup_render_process_management()
    if process_setup_success:
        logger.info("✅ 렌더 프로세스 관리 시작 성공")
    else:
        logger.warning("⚠️ 렌더 프로세스 관리 시작 실패")
    
    # 하이브리드 캐시 시스템 초기화
    try:
        cache_success = await initialize_cache_system()
        if cache_success:
            cache_initialized = True
            logger.info("✅ 하이브리드 캐시 시스템 초기화 완료")
        else:
            logger.error("❌ 하이브리드 캐시 시스템 초기화 실패")
    except Exception as e:
        logger.error(f"❌ 캐시 시스템 초기화 오류: {e}")

@app.get("/")
async def root():
    """API 서버 상태"""
    cache_stats = get_cache_stats() if cache_initialized else {}
    
    return {
        "message": "NewsBot 하이브리드 캐시 API Server",
        "status": "running",
        "cache_system": "initialized" if cache_initialized else "failed",
        "cache_stats": cache_stats,
        "api_stats": api_stats,
        "architecture": {
            "tier1": "기본 정보 메모리 캐시 (150MB)",
            "tier2": "실시간 상세 분석 생성",
            "tier3": "인기 출마자 예측 캐시 (100MB)"
        }
    }

@app.get("/api/candidate/search")
async def search_candidate_api(
    name: str = Query(..., description="출마자 이름"),
    position: str = Query(..., description="출마자 직급"),
    detail: str = Query("basic", description="정보 상세도 (basic/detailed)")
):
    """출마자 정보 검색 API"""
    
    start_time = datetime.now()
    api_stats['total_requests'] += 1
    
    try:
        if not cache_initialized:
            api_stats['failed_requests'] += 1
            raise HTTPException(
                status_code=503, 
                detail="캐시 시스템이 초기화되지 않았습니다"
            )
        
        # 하이브리드 캐시를 통한 검색
        result = await search_candidate(name, position, detail)
        
        # 응답 시간 계산
        response_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # 통계 업데이트
        api_stats['successful_requests'] += 1
        api_stats['average_response_time'] = (
            (api_stats['average_response_time'] * (api_stats['successful_requests'] - 1) + response_time) / 
            api_stats['successful_requests']
        )
        
        if result['success']:
            return {
                "success": True,
                "candidate": result['data'],
                "meta": {
                    "cache_tier": result['cache_tier'],
                    "response_time_ms": result['response_time_ms'],
                    "data_source": result['data_source'],
                    "search_timestamp": start_time.isoformat(),
                    "detail_level": detail
                }
            }
        else:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "error": result['error'],
                    "meta": {
                        "cache_tier": result['cache_tier'],
                        "response_time_ms": result['response_time_ms'],
                        "search_timestamp": start_time.isoformat()
                    }
                }
            )
    
    except HTTPException:
        raise
    except Exception as e:
        api_stats['failed_requests'] += 1
        logger.error(f"❌ 출마자 검색 API 오류: {e}")
        
        raise HTTPException(
            status_code=500,
            detail=f"검색 중 오류 발생: {str(e)}"
        )

@app.get("/api/candidate/batch")
async def batch_search_candidates(
    names: str = Query(..., description="출마자 이름들 (쉼표로 구분)"),
    position: str = Query(..., description="출마자 직급"),
    detail: str = Query("basic", description="정보 상세도 (basic/detailed)")
):
    """출마자 일괄 검색 API"""
    
    start_time = datetime.now()
    api_stats['total_requests'] += 1
    
    try:
        if not cache_initialized:
            api_stats['failed_requests'] += 1
            raise HTTPException(
                status_code=503, 
                detail="캐시 시스템이 초기화되지 않았습니다"
            )
        
        # 이름 목록 파싱
        name_list = [name.strip() for name in names.split(',') if name.strip()]
        
        if not name_list:
            raise HTTPException(
                status_code=400,
                detail="검색할 출마자 이름이 없습니다"
            )
        
        if len(name_list) > 20:
            raise HTTPException(
                status_code=400,
                detail="한 번에 최대 20명까지만 검색 가능합니다"
            )
        
        # 병렬 검색 실행
        search_tasks = [
            search_candidate(name, position, detail) 
            for name in name_list
        ]
        
        results = await asyncio.gather(*search_tasks, return_exceptions=True)
        
        # 결과 정리
        successful_results = []
        failed_results = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                failed_results.append({
                    "name": name_list[i],
                    "error": str(result)
                })
            elif result['success']:
                successful_results.append({
                    "name": name_list[i],
                    "data": result['data'],
                    "cache_tier": result['cache_tier'],
                    "response_time_ms": result['response_time_ms']
                })
            else:
                failed_results.append({
                    "name": name_list[i],
                    "error": result['error']
                })
        
        # 응답 시간 계산
        total_response_time = (datetime.now() - start_time).total_seconds() * 1000
        
        api_stats['successful_requests'] += 1
        
        return {
            "success": True,
            "results": {
                "successful": successful_results,
                "failed": failed_results,
                "summary": {
                    "total_requested": len(name_list),
                    "successful_count": len(successful_results),
                    "failed_count": len(failed_results),
                    "success_rate": round(len(successful_results) / len(name_list) * 100, 2)
                }
            },
            "meta": {
                "total_response_time_ms": round(total_response_time, 2),
                "average_per_candidate_ms": round(total_response_time / len(name_list), 2),
                "search_timestamp": start_time.isoformat(),
                "detail_level": detail
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        api_stats['failed_requests'] += 1
        logger.error(f"❌ 일괄 검색 API 오류: {e}")
        
        raise HTTPException(
            status_code=500,
            detail=f"일괄 검색 중 오류 발생: {str(e)}"
        )

@app.get("/api/cache/stats")
async def get_cache_statistics():
    """캐시 시스템 통계 조회"""
    
    try:
        if not cache_initialized:
            raise HTTPException(
                status_code=503,
                detail="캐시 시스템이 초기화되지 않았습니다"
            )
        
        cache_stats = get_cache_stats()
        
        return {
            "success": True,
            "cache_statistics": cache_stats,
            "api_statistics": api_stats,
            "system_info": {
                "cache_system_version": "2.0.0",
                "architecture": "3-tier hybrid caching",
                "total_capacity": "250MB",
                "compression": "gzip enabled"
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 캐시 통계 조회 오류: {e}")
        
        raise HTTPException(
            status_code=500,
            detail=f"통계 조회 중 오류 발생: {str(e)}"
        )

@app.post("/api/cache/clear")
async def clear_cache_api(
    tier: str = Query("all", description="정리할 캐시 티어 (tier1/tier3/all)")
):
    """캐시 정리 API"""
    
    try:
        if not cache_initialized:
            raise HTTPException(
                status_code=503,
                detail="캐시 시스템이 초기화되지 않았습니다"
            )
        
        valid_tiers = ['tier1', 'tier3', 'all']
        if tier not in valid_tiers:
            raise HTTPException(
                status_code=400,
                detail=f"유효하지 않은 티어: {tier}. 가능한 값: {valid_tiers}"
            )
        
        # 캐시 정리 실행
        cache_system.clear_cache(tier)
        
        # 정리 후 통계
        updated_stats = get_cache_stats()
        
        return {
            "success": True,
            "message": f"{tier} 캐시 정리 완료",
            "cleared_tier": tier,
            "updated_statistics": updated_stats,
            "timestamp": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 캐시 정리 오류: {e}")
        
        raise HTTPException(
            status_code=500,
            detail=f"캐시 정리 중 오류 발생: {str(e)}"
        )

@app.get("/api/cache/warmup")
async def warmup_cache(background_tasks: BackgroundTasks):
    """캐시 워밍업 API"""
    
    try:
        if not cache_initialized:
            raise HTTPException(
                status_code=503,
                detail="캐시 시스템이 초기화되지 않았습니다"
            )
        
        # 백그라운드에서 인기 출마자들의 상세 정보 미리 로드
        async def warmup_popular_candidates():
            popular_positions = ['국회의원', '광역단체장', '교육감']
            
            for position in popular_positions:
                for i in range(1, 11):  # 각 직급별 상위 10명
                    candidate_name = f"{position}_{i:04d}"
                    try:
                        await search_candidate(candidate_name, position, "detailed")
                        await asyncio.sleep(0.1)  # 부하 방지
                    except Exception as e:
                        logger.warning(f"워밍업 중 오류: {candidate_name} - {e}")
        
        background_tasks.add_task(warmup_popular_candidates)
        
        return {
            "success": True,
            "message": "캐시 워밍업 시작됨",
            "status": "백그라운드에서 인기 출마자 정보 사전 로드 중",
            "estimated_duration": "30-60초",
            "timestamp": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 캐시 워밍업 오류: {e}")
        
        raise HTTPException(
            status_code=500,
            detail=f"캐시 워밍업 중 오류 발생: {str(e)}"
        )

@app.get("/api/render/status")
async def get_render_process_status():
    """렌더 프로세스 상태 조회"""
    try:
        status = get_render_status()
        return {
            "success": True,
            "render_status": status,
            "message": "렌더 프로세스 상태 조회 완료"
        }
    except Exception as e:
        logger.error(f"렌더 상태 조회 오류: {e}")
        return {
            "success": False,
            "error": f"상태 조회 실패: {str(e)}"
        }

@app.post("/api/render/shutdown")
async def request_render_shutdown():
    """렌더 프로세스 그레이스풀 셧다운 요청"""
    try:
        logger.info("🛑 API를 통한 렌더 셧다운 요청")
        shutdown_render_process("API_REQUEST")
        return {
            "success": True,
            "message": "렌더 프로세스 셧다운 요청 완료"
        }
    except Exception as e:
        logger.error(f"렌더 셧다운 요청 오류: {e}")
        return {
            "success": False,
            "error": f"셧다운 요청 실패: {str(e)}"
        }

@app.get("/health")
async def health_check():
    """헬스체크 엔드포인트"""
    
    cache_status = "healthy" if cache_initialized else "unhealthy"
    cache_stats = get_cache_stats() if cache_initialized else {}
    
    health_status = {
        "status": "healthy" if cache_initialized else "degraded",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "cache_system": {
                "status": cache_status,
                "details": cache_stats
            },
            "api_server": {
                "status": "healthy",
                "uptime_seconds": (datetime.now() - datetime.fromisoformat(api_stats['start_time'])).total_seconds(),
                "total_requests": api_stats['total_requests'],
                "success_rate": round(
                    (api_stats['successful_requests'] / api_stats['total_requests'] * 100) 
                    if api_stats['total_requests'] > 0 else 100, 2
                )
            }
        },
        "version": "2.0.0"
    }
    
    status_code = 200 if cache_initialized else 503
    return JSONResponse(status_code=status_code, content=health_status)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
