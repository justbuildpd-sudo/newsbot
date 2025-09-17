#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
최적화된 서버 시작 스크립트
불필요한 초기화를 최소화하고 안정적인 서버 시작을 보장합니다.
"""

import os
import sys
import time
import logging
from datetime import datetime

# 로깅 설정 최적화
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('server.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def preload_services():
    """서비스 사전 로드 (최적화)"""
    try:
        logger.info("🔧 서비스 사전 로드 시작...")
        
        # 정치인 분석기는 지연 초기화로 변경됨
        from politician_analyzer import PoliticianAnalyzer
        logger.info("✅ 정치인 분석기 모듈 로드 완료")
        
        # 뉴스 서비스도 지연 초기화
        from news_service import NewsService
        logger.info("✅ 뉴스 서비스 모듈 로드 완료")
        
        # 국회의원 API 서비스
        from assembly_api_service import AssemblyAPIService
        logger.info("✅ 국회의원 API 서비스 모듈 로드 완료")
        
        logger.info("🎯 모든 서비스 모듈 로드 완료")
        return True
        
    except Exception as e:
        logger.error(f"❌ 서비스 로드 실패: {e}")
        return False

def main():
    """메인 실행 함수"""
    print("=" * 50)
    print("🚀 뉴스봇 서버 시작")
    print("=" * 50)
    
    start_time = time.time()
    
    # 1. 서비스 사전 로드
    if not preload_services():
        print("❌ 서비스 로드 실패로 서버를 시작할 수 없습니다.")
        sys.exit(1)
    
    # 2. 서버 시작
    try:
        import uvicorn
        from api_server import app
        
        print("🌐 서버 시작 중...")
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8001,
            log_level="info",
            access_log=True,
            reload=False  # 프로덕션에서는 False
        )
        
    except KeyboardInterrupt:
        print("\n🛑 서버가 사용자에 의해 중지되었습니다.")
    except Exception as e:
        print(f"❌ 서버 실행 오류: {e}")
        sys.exit(1)
    finally:
        end_time = time.time()
        print(f"⏱️ 서버 실행 시간: {end_time - start_time:.2f}초")

if __name__ == "__main__":
    main()
