#!/usr/bin/env python3
'''
Render Health Check Script
렌더 서비스 상태 확인 및 자동 복구
'''

import requests
import sys
import time
import os
from datetime import datetime

def check_service_health():
    """서비스 헬스체크"""
    try:
        # 로컬 서비스 확인
        port = os.environ.get('PORT', '8000')
        url = f"http://localhost:{port}/"
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ 서비스 정상: {datetime.now()}")
            return True
        else:
            print(f"⚠️ 서비스 응답 오류: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 서비스 헬스체크 실패: {e}")
        return False

def main():
    """메인 헬스체크 실행"""
    print("🩺 Render Health Check 시작")
    
    # 3회 재시도
    for attempt in range(3):
        if check_service_health():
            sys.exit(0)  # 성공
        
        if attempt < 2:
            print(f"⏳ 재시도 {attempt + 1}/3...")
            time.sleep(5)
    
    print("❌ 헬스체크 최종 실패")
    sys.exit(1)  # 실패

if __name__ == "__main__":
    main()
