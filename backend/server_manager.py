#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
서버 관리 도구
뉴스봇 서버의 시작, 중지, 상태 확인, 로그 관리 등을 담당합니다.
"""

import os
import sys
import time
import signal
import subprocess
import requests
import json
from datetime import datetime
from typing import Optional, Dict, List

class ServerManager:
    def __init__(self):
        self.server_process = None
        self.port = 8001
        self.host = "0.0.0.0"
        self.log_file = "server.log"
        self.pid_file = "server.pid"
        
    def start_server(self, background: bool = True) -> bool:
        """서버 시작"""
        try:
            if self.is_server_running():
                print("⚠️ 서버가 이미 실행 중입니다.")
                return True
                
            print("🚀 서버 시작 중...")
            
            cmd = [
                sys.executable, "-m", "uvicorn", 
                "api_server:app", 
                "--host", self.host, 
                "--port", str(self.port),
                "--log-level", "info"
            ]
            
            if background:
                with open(self.log_file, 'a') as log:
                    self.server_process = subprocess.Popen(
                        cmd, 
                        stdout=log, 
                        stderr=subprocess.STDOUT,
                        preexec_fn=os.setsid
                    )
                
                # PID 저장
                with open(self.pid_file, 'w') as f:
                    f.write(str(self.server_process.pid))
                    
                print(f"✅ 서버가 백그라운드에서 시작되었습니다. (PID: {self.server_process.pid})")
            else:
                self.server_process = subprocess.Popen(cmd)
                print("✅ 서버가 포그라운드에서 시작되었습니다.")
                
            # 서버 준비 대기
            self.wait_for_server_ready()
            return True
            
        except Exception as e:
            print(f"❌ 서버 시작 실패: {e}")
            return False
    
    def stop_server(self) -> bool:
        """서버 중지"""
        try:
            if self.server_process:
                print("🛑 서버 중지 중...")
                os.killpg(os.getpgid(self.server_process.pid), signal.SIGTERM)
                self.server_process = None
                
                # PID 파일 삭제
                if os.path.exists(self.pid_file):
                    os.remove(self.pid_file)
                    
                print("✅ 서버가 중지되었습니다.")
                return True
            else:
                print("⚠️ 실행 중인 서버가 없습니다.")
                return False
                
        except Exception as e:
            print(f"❌ 서버 중지 실패: {e}")
            return False
    
    def restart_server(self) -> bool:
        """서버 재시작"""
        print("🔄 서버 재시작 중...")
        self.stop_server()
        time.sleep(2)
        return self.start_server()
    
    def is_server_running(self) -> bool:
        """서버 실행 상태 확인"""
        try:
            response = requests.get(f"http://localhost:{self.port}/api/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def wait_for_server_ready(self, timeout: int = 30) -> bool:
        """서버 준비 완료 대기"""
        print("⏳ 서버 준비 대기 중...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.is_server_running():
                print("✅ 서버가 준비되었습니다.")
                return True
            time.sleep(1)
            
        print("❌ 서버 준비 시간 초과")
        return False
    
    def get_server_status(self) -> Dict:
        """서버 상태 정보"""
        status = {
            "running": self.is_server_running(),
            "port": self.port,
            "host": self.host,
            "timestamp": datetime.now().isoformat()
        }
        
        if os.path.exists(self.pid_file):
            with open(self.pid_file, 'r') as f:
                status["pid"] = int(f.read().strip())
        
        return status
    
    def get_logs(self, lines: int = 50) -> List[str]:
        """서버 로그 조회"""
        if not os.path.exists(self.log_file):
            return ["로그 파일이 없습니다."]
            
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                return all_lines[-lines:] if lines > 0 else all_lines
        except Exception as e:
            return [f"로그 읽기 실패: {e}"]
    
    def clear_logs(self) -> bool:
        """로그 파일 초기화"""
        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, 'w') as f:
                    f.write("")
                print("✅ 로그가 초기화되었습니다.")
                return True
            return False
        except Exception as e:
            print(f"❌ 로그 초기화 실패: {e}")
            return False

def main():
    """메인 함수"""
    manager = ServerManager()
    
    if len(sys.argv) < 2:
        print("사용법: python server_manager.py [start|stop|restart|status|logs|clear]")
        return
    
    command = sys.argv[1].lower()
    
    if command == "start":
        background = len(sys.argv) > 2 and sys.argv[2] == "bg"
        manager.start_server(background)
    elif command == "stop":
        manager.stop_server()
    elif command == "restart":
        manager.restart_server()
    elif command == "status":
        status = manager.get_server_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))
    elif command == "logs":
        lines = int(sys.argv[2]) if len(sys.argv) > 2 else 50
        logs = manager.get_logs(lines)
        for log in logs:
            print(log.rstrip())
    elif command == "clear":
        manager.clear_logs()
    else:
        print("알 수 없는 명령어입니다.")

if __name__ == "__main__":
    main()
