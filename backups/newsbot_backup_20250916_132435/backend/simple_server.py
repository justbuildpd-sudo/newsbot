#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
단순화된 안정적인 서버
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from utils.data_loader import DataLoader
import uvicorn
import os
import signal
import sys

# 전역 변수
data_loader = None

def signal_handler(sig, frame):
    """시그널 핸들러 - 안전한 종료"""
    print('\n🛑 서버 종료 중...')
    sys.exit(0)

def create_app():
    """FastAPI 앱 생성"""
    app = FastAPI(
        title="NewsBot API - Simple Version",
        version="2.0.0",
        description="안정적인 국회의원 정보 API"
    )
    
    # CORS 설정
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 데이터 로더 초기화
    global data_loader
    data_loader = DataLoader()
    
    @app.get("/")
    async def root():
        return {"message": "NewsBot API Server", "status": "running"}
    
    @app.get("/api/health")
    async def health_check():
        """헬스 체크"""
        try:
            stats = data_loader.get_stats()
            return {
                "status": "healthy",
                "data_loaded": len(data_loader.data) > 0,
                "politician_count": len(data_loader.data),
                "stats": stats
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    @app.get("/api/assembly/members")
    async def get_assembly_members():
        """모든 국회의원 정보 조회"""
        try:
            politicians = data_loader.get_all_politicians()
            return {
                "success": True,
                "data": politicians,
                "count": len(politicians),
                "source": "local_json"
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"데이터 조회 실패: {str(e)}")
    
    @app.get("/api/assembly/members/{member_id}")
    async def get_assembly_member_detail(member_id: str):
        """특정 국회의원 상세 정보 조회"""
        try:
            politician = data_loader.get_politician_by_id(member_id)
            if not politician:
                raise HTTPException(status_code=404, detail="국회의원을 찾을 수 없습니다")
            
            return {
                "success": True,
                "data": politician,
                "source": "local_json"
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"상세 정보 조회 실패: {str(e)}")
    
    @app.get("/api/assembly/members/party/{party_name}")
    async def get_assembly_members_by_party(party_name: str):
        """정당별 국회의원 조회"""
        try:
            politicians = data_loader.get_politicians_by_party(party_name)
            return {
                "success": True,
                "data": politicians,
                "count": len(politicians),
                "party": party_name,
                "source": "local_json"
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"정당별 조회 실패: {str(e)}")
    
    @app.get("/api/assembly/stats")
    async def get_assembly_stats():
        """국회의원 통계 정보"""
        try:
            stats = data_loader.get_stats()
            return {
                "success": True,
                "data": stats,
                "source": "local_json"
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"통계 조회 실패: {str(e)}")
    
    return app

def main():
    """메인 함수"""
    # 시그널 핸들러 등록
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("🚀 NewsBot Simple Server 시작 중...")
    
    # 앱 생성
    app = create_app()
    
    # 서버 실행
    try:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8001,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n🛑 서버가 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"❌ 서버 실행 오류: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
