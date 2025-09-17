#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
단순화된 서버 관리 스크립트
"""

import subprocess
import time
import os
import signal
import sys
import requests

class SimpleServerManager:
    def __init__(self):
        self.server_process = None
        self.port = 8001
        
    def kill_existing_processes(self):
        """기존 프로세스 종료"""
        try:
            # Python 프로세스 종료
            subprocess.run(['pkill', '-f', 'python.*simple_server'], check=False)
            subprocess.run(['pkill', '-f', 'uvicorn'], check=False)
            time.sleep(2)
            print("✅ 기존 프로세스 종료 완료")
        except Exception as e:
            print(f"⚠️  프로세스 종료 중 오류: {e}")
    
    def check_port(self):
        """포트 사용 상태 확인"""
        try:
            response = requests.get(f"http://localhost:{self.port}/api/health", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def start_server(self):
        """서버 시작"""
        if self.check_port():
            print(f"⚠️  포트 {self.port}이 이미 사용 중입니다.")
            return False
        
        self.kill_existing_processes()
        
        try:
            print("🚀 서버 시작 중...")
            self.server_process = subprocess.Popen([
                sys.executable, 'simple_server.py'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # 서버 시작 대기
            for i in range(10):
                time.sleep(1)
                if self.check_port():
                    print(f"✅ 서버가 포트 {self.port}에서 시작되었습니다.")
                    return True
                print(f"⏳ 서버 시작 대기 중... ({i+1}/10)")
            
            print("❌ 서버 시작 실패")
            return False
            
        except Exception as e:
            print(f"❌ 서버 시작 오류: {e}")
            return False
    
    def stop_server(self):
        """서버 중지"""
        self.kill_existing_processes()
        print("🛑 서버 중지 완료")
    
    def restart_server(self):
        """서버 재시작"""
        print("🔄 서버 재시작 중...")
        self.stop_server()
        time.sleep(2)
        return self.start_server()
    
    def status(self):
        """서버 상태 확인"""
        if self.check_port():
            try:
                response = requests.get(f"http://localhost:{self.port}/api/health", timeout=2)
                data = response.json()
                print("✅ 서버가 정상 작동 중입니다.")
                print(f"   - 포트: {self.port}")
                print(f"   - 상태: {data.get('status', 'unknown')}")
                print(f"   - 데이터 로드: {data.get('data_loaded', False)}")
                print(f"   - 정치인 수: {data.get('politician_count', 0)}")
                return True
            except Exception as e:
                print(f"❌ 서버 상태 확인 실패: {e}")
                return False
        else:
            print("❌ 서버가 실행되지 않았습니다.")
            return False

def main():
    manager = SimpleServerManager()
    
    if len(sys.argv) < 2:
        print("사용법: python server_manager_simple.py [start|stop|restart|status]")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "start":
        manager.start_server()
    elif command == "stop":
        manager.stop_server()
    elif command == "restart":
        manager.restart_server()
    elif command == "status":
        manager.status()
    else:
        print("잘못된 명령어입니다. [start|stop|restart|status] 중 하나를 선택하세요.")

if __name__ == "__main__":
    main()
