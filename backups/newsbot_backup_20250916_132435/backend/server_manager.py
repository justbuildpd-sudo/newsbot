#!/usr/bin/env python3
"""
NewsBot 서버 관리자
서버 자동 재시작 및 모니터링 기능을 제공합니다.
"""

import os
import sys
import time
import signal
import subprocess
import logging
import requests
from datetime import datetime

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ServerManager:
    def __init__(self, server_script="stable_server.py", port=8000, max_restarts=5):
        self.server_script = server_script
        self.port = port
        self.max_restarts = max_restarts
        self.restart_count = 0
        self.server_process = None
        self.running = True
        
        # 시그널 핸들러 등록
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """시그널 핸들러"""
        logger.info(f"시그널 {signum} 수신. 서버를 종료합니다...")
        self.running = False
        self.stop_server()
        sys.exit(0)
    
    def start_server(self):
        """서버 시작"""
        try:
            logger.info(f"서버 시작 중... ({self.server_script})")
            self.server_process = subprocess.Popen(
                [sys.executable, self.server_script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 서버 시작 대기
            time.sleep(5)
            
            if self.is_server_healthy():
                logger.info(f"✅ 서버가 성공적으로 시작되었습니다. (PID: {self.server_process.pid})")
                return True
            else:
                logger.error("❌ 서버 시작 실패")
                return False
                
        except Exception as e:
            logger.error(f"서버 시작 중 오류 발생: {e}")
            return False
    
    def stop_server(self):
        """서버 중지"""
        if self.server_process:
            try:
                logger.info("서버 중지 중...")
                self.server_process.terminate()
                self.server_process.wait(timeout=10)
                logger.info("서버가 중지되었습니다.")
            except subprocess.TimeoutExpired:
                logger.warning("서버가 정상적으로 중지되지 않아 강제 종료합니다.")
                self.server_process.kill()
            except Exception as e:
                logger.error(f"서버 중지 중 오류 발생: {e}")
    
    def is_server_healthy(self):
        """서버 상태 확인"""
        try:
            response = requests.get(f"http://localhost:{self.port}/api/health", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.debug(f"서버 상태 확인 실패: {e}")
            return False
    
    def restart_server(self):
        """서버 재시작"""
        if self.restart_count >= self.max_restarts:
            logger.error(f"최대 재시작 횟수({self.max_restarts})에 도달했습니다. 서버를 종료합니다.")
            return False
        
        self.restart_count += 1
        logger.warning(f"서버 재시작 시도 {self.restart_count}/{self.max_restarts}")
        
        self.stop_server()
        time.sleep(2)
        
        if self.start_server():
            self.restart_count = 0  # 성공 시 카운터 리셋
            return True
        else:
            return False
    
    def monitor_server(self):
        """서버 모니터링"""
        logger.info("서버 모니터링 시작...")
        
        while self.running:
            try:
                if not self.is_server_healthy():
                    logger.warning("서버가 응답하지 않습니다. 재시작을 시도합니다...")
                    if not self.restart_server():
                        break
                else:
                    # 성공적인 상태 확인 시 재시작 카운터 리셋
                    if self.restart_count > 0:
                        self.restart_count = 0
                        logger.info("서버가 정상적으로 복구되었습니다.")
                
                time.sleep(30)  # 30초마다 확인
                
            except KeyboardInterrupt:
                logger.info("사용자에 의해 중단되었습니다.")
                break
            except Exception as e:
                logger.error(f"모니터링 중 오류 발생: {e}")
                time.sleep(10)
        
        self.stop_server()
        logger.info("서버 관리자가 종료되었습니다.")
    
    def run(self):
        """서버 실행 및 모니터링"""
        logger.info("=" * 50)
        logger.info("NewsBot 서버 관리자 시작")
        logger.info(f"서버 스크립트: {self.server_script}")
        logger.info(f"포트: {self.port}")
        logger.info(f"최대 재시작 횟수: {self.max_restarts}")
        logger.info("=" * 50)
        
        if self.start_server():
            self.monitor_server()
        else:
            logger.error("서버 시작에 실패했습니다.")
            sys.exit(1)

def main():
    """메인 함수"""
    server_manager = ServerManager()
    server_manager.run()

if __name__ == "__main__":
    main()