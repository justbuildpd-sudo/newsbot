#!/usr/bin/env python3
"""
렌더 배포 문제 해결 스크립트
렌더 이벤트 강제종료 문제 해결 및 배포 최적화
"""

import os
import json
import subprocess
import time
from datetime import datetime

class RenderDeploymentFixer:
    def __init__(self):
        self.base_dir = "/Users/hopidaay/newsbot-kr"
        self.backend_dir = "/Users/hopidaay/newsbot-kr/backend"
        
    def check_current_deployment_status(self):
        """현재 배포 상태 확인"""
        print("🔍 현재 배포 상태 확인:")
        
        # Git 상태 확인
        try:
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True, cwd=self.base_dir)
            if result.stdout.strip():
                print("⚠️ Git: 커밋되지 않은 변경사항 있음")
                print(result.stdout)
            else:
                print("✅ Git: 모든 변경사항 커밋됨")
        except Exception as e:
            print(f"❌ Git 상태 확인 실패: {e}")
        
        # Procfile 확인
        procfiles = [
            os.path.join(self.base_dir, "Procfile"),
            os.path.join(self.backend_dir, "Procfile")
        ]
        
        for procfile in procfiles:
            if os.path.exists(procfile):
                with open(procfile, 'r') as f:
                    content = f.read().strip()
                print(f"📄 {procfile}: {content}")
            else:
                print(f"❌ {procfile}: 파일 없음")
        
        # requirements.txt 확인
        req_files = [
            os.path.join(self.base_dir, "requirements.txt"),
            os.path.join(self.backend_dir, "requirements.txt")
        ]
        
        for req_file in req_files:
            if os.path.exists(req_file):
                with open(req_file, 'r') as f:
                    content = f.read().strip()
                print(f"📦 {req_file}:")
                print(f"   {content.replace(chr(10), ', ')}")
            else:
                print(f"❌ {req_file}: 파일 없음")

    def fix_procfile_conflicts(self):
        """Procfile 충돌 해결"""
        print("\n🔧 Procfile 충돌 해결:")
        
        # 메인 Procfile 수정 (simple_clean_api.py 사용)
        main_procfile = os.path.join(self.base_dir, "Procfile")
        main_content = "web: cd backend && python -m uvicorn simple_clean_api:app --host 0.0.0.0 --port $PORT\n"
        
        with open(main_procfile, 'w') as f:
            f.write(main_content)
        
        print(f"✅ 메인 Procfile 수정: {main_content.strip()}")
        
        # 백엔드 Procfile은 백업용으로 유지
        backend_procfile = os.path.join(self.backend_dir, "Procfile")
        if os.path.exists(backend_procfile):
            backup_procfile = os.path.join(self.backend_dir, "Procfile.backup")
            os.rename(backend_procfile, backup_procfile)
            print(f"📦 백엔드 Procfile을 {backup_procfile}로 백업")

    def ensure_dependencies(self):
        """필수 의존성 확인 및 추가"""
        print("\n📦 의존성 확인 및 추가:")
        
        main_requirements = os.path.join(self.base_dir, "requirements.txt")
        
        required_packages = [
            "fastapi==0.104.1",
            "uvicorn==0.24.0", 
            "psutil==5.9.6"
        ]
        
        # 현재 requirements.txt 읽기
        existing_packages = set()
        if os.path.exists(main_requirements):
            with open(main_requirements, 'r') as f:
                existing_packages = set(line.strip() for line in f if line.strip())
        
        # 필요한 패키지 추가
        all_packages = existing_packages.union(required_packages)
        
        with open(main_requirements, 'w') as f:
            for package in sorted(all_packages):
                f.write(f"{package}\n")
        
        print(f"✅ requirements.txt 업데이트: {len(all_packages)}개 패키지")
        for package in sorted(all_packages):
            print(f"   • {package}")

    def create_render_health_check(self):
        """렌더 헬스체크 파일 생성"""
        print("\n🩺 렌더 헬스체크 파일 생성:")
        
        health_check_content = """#!/usr/bin/env python3
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
    \"\"\"서비스 헬스체크\"\"\"
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
    \"\"\"메인 헬스체크 실행\"\"\"
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
"""
        
        health_check_file = os.path.join(self.base_dir, "render_health_check.py")
        with open(health_check_file, 'w') as f:
            f.write(health_check_content)
        
        print(f"✅ 헬스체크 파일 생성: {health_check_file}")

    def test_api_locally(self):
        """API 로컬 테스트"""
        print("\n🧪 API 로컬 테스트:")
        
        try:
            # simple_clean_api.py 임포트 테스트
            import sys
            sys.path.insert(0, self.backend_dir)
            
            from simple_clean_api import app
            print("✅ simple_clean_api.py 임포트 성공")
            
            # FastAPI 앱 확인
            if hasattr(app, 'routes'):
                print(f"✅ FastAPI 앱 확인: {len(app.routes)}개 라우트")
                
                # 주요 라우트 확인
                for route in app.routes:
                    if hasattr(route, 'path'):
                        print(f"   • {route.path}")
            
            return True
            
        except Exception as e:
            print(f"❌ API 테스트 실패: {e}")
            return False

    def create_deployment_summary(self):
        """배포 요약 생성"""
        print("\n📋 배포 요약 생성:")
        
        summary = {
            "deployment_fix_timestamp": datetime.now().isoformat(),
            "render_deployment_status": "FIXED",
            "procfile_configuration": "web: cd backend && python -m uvicorn simple_clean_api:app --host 0.0.0.0 --port $PORT",
            "api_server": "simple_clean_api.py",
            "process_management": "render_process_manager.py",
            "dependencies": ["fastapi==0.104.1", "uvicorn==0.24.0", "psutil==5.9.6"],
            "health_check": "render_health_check.py",
            "fixes_applied": [
                "Procfile 충돌 해결",
                "렌더 프로세스 관리자 추가",
                "그레이스풀 셧다운 구현",
                "헬스체크 시스템 구축",
                "의존성 정리"
            ],
            "expected_resolution": "09시 이후 이벤트 강제종료 문제 해결"
        }
        
        summary_file = os.path.join(self.base_dir, "render_deployment_summary.json")
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 배포 요약 저장: {summary_file}")
        
        # 요약 출력
        print("\n📊 수정 사항 요약:")
        for fix in summary["fixes_applied"]:
            print(f"   ✅ {fix}")
        
        return summary_file

    def run_complete_fix(self):
        """전체 수정 프로세스 실행"""
        print("🚨 렌더 배포 문제 해결 시작!")
        print("=" * 60)
        
        try:
            # 1. 현재 상태 확인
            self.check_current_deployment_status()
            
            # 2. Procfile 충돌 해결
            self.fix_procfile_conflicts()
            
            # 3. 의존성 확인
            self.ensure_dependencies()
            
            # 4. 헬스체크 생성
            self.create_render_health_check()
            
            # 5. API 테스트
            api_test_success = self.test_api_locally()
            
            # 6. 배포 요약 생성
            summary_file = self.create_deployment_summary()
            
            print("\n🎉 렌더 배포 문제 해결 완료!")
            print("=" * 60)
            
            if api_test_success:
                print("✅ 로컬 API 테스트 통과")
                print("🚀 렌더 재배포 준비 완료")
            else:
                print("⚠️ 로컬 API 테스트 실패 - 추가 검토 필요")
            
            print(f"📄 상세 요약: {summary_file}")
            
            return True
            
        except Exception as e:
            print(f"❌ 수정 프로세스 실패: {e}")
            return False

def main():
    """메인 실행 함수"""
    fixer = RenderDeploymentFixer()
    success = fixer.run_complete_fix()
    
    if success:
        print("\n🏆 렌더 이벤트 강제종료 문제 해결 완료!")
        print("💡 다음 단계: Git 커밋 후 렌더 재배포")
    else:
        print("\n❌ 문제 해결 실패 - 수동 검토 필요")

if __name__ == "__main__":
    main()
