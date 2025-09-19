#!/usr/bin/env python3
"""
Render 프로세스 관리자
렌더 이벤트 강제종료 문제 해결 및 프로세스 안정화
"""

import os
import sys
import json
import logging
import signal
import asyncio
import threading
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import subprocess
import psutil

logger = logging.getLogger(__name__)

class RenderProcessManager:
    def __init__(self):
        self.app_name = "newsbot-kr"
        self.process_id = None
        self.start_time = None
        self.is_running = False
        self.shutdown_requested = False
        
        # 렌더 환경 감지
        self.is_render_env = os.getenv('RENDER') == 'true' or os.getenv('RENDER_SERVICE_ID') is not None
        
        # 프로세스 관리 설정
        self.max_runtime_hours = 12  # 최대 12시간 실행
        self.health_check_interval = 300  # 5분마다 헬스체크
        self.graceful_shutdown_timeout = 30  # 30초 그레이스풀 셧다운
        
        logger.info(f"🔧 Render Process Manager 초기화")
        logger.info(f"📊 Render 환경: {self.is_render_env}")
        logger.info(f"⏰ 최대 실행시간: {self.max_runtime_hours}시간")

    def setup_signal_handlers(self):
        """시그널 핸들러 설정"""
        def signal_handler(signum, frame):
            logger.info(f"📡 시그널 수신: {signum}")
            self.graceful_shutdown()
        
        # SIGTERM, SIGINT 핸들러 등록
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
        
        if hasattr(signal, 'SIGUSR1'):
            signal.signal(signal.SIGUSR1, signal_handler)
        
        logger.info("✅ 시그널 핸들러 설정 완료")

    def start_process_monitor(self):
        """프로세스 모니터링 시작"""
        def monitor_loop():
            while not self.shutdown_requested:
                try:
                    self.health_check()
                    self.check_runtime_limit()
                    time.sleep(self.health_check_interval)
                except Exception as e:
                    logger.error(f"❌ 모니터링 오류: {e}")
                    time.sleep(60)  # 오류 시 1분 대기
        
        # 백그라운드 스레드로 모니터링 실행
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        
        logger.info("🔍 프로세스 모니터링 시작")

    def health_check(self):
        """헬스체크 실행"""
        try:
            current_process = psutil.Process()
            
            # 메모리 사용량 확인
            memory_info = current_process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            
            # CPU 사용량 확인
            cpu_percent = current_process.cpu_percent()
            
            # 실행 시간 확인
            runtime = datetime.now() - self.start_time if self.start_time else timedelta(0)
            
            logger.info(f"💚 헬스체크: 메모리 {memory_mb:.1f}MB, CPU {cpu_percent:.1f}%, 실행시간 {runtime}")
            
            # 메모리 임계값 확인 (512MB 이상 시 경고)
            if memory_mb > 512:
                logger.warning(f"⚠️ 높은 메모리 사용량: {memory_mb:.1f}MB")
                self.cleanup_memory()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 헬스체크 실패: {e}")
            return False

    def check_runtime_limit(self):
        """실행 시간 제한 확인"""
        if not self.start_time:
            return
        
        runtime = datetime.now() - self.start_time
        max_runtime = timedelta(hours=self.max_runtime_hours)
        
        if runtime > max_runtime:
            logger.warning(f"⏰ 최대 실행시간 초과: {runtime} > {max_runtime}")
            self.graceful_shutdown(reason="MAX_RUNTIME_EXCEEDED")

    def cleanup_memory(self):
        """메모리 정리"""
        try:
            import gc
            gc.collect()
            logger.info("🧹 메모리 정리 완료")
        except Exception as e:
            logger.error(f"❌ 메모리 정리 실패: {e}")

    def graceful_shutdown(self, reason: str = "SIGNAL_RECEIVED"):
        """그레이스풀 셧다운"""
        if self.shutdown_requested:
            logger.info("⚠️ 이미 셧다운 진행 중")
            return
        
        self.shutdown_requested = True
        logger.info(f"🛑 그레이스풀 셧다운 시작: {reason}")
        
        try:
            # 1. 새로운 요청 차단
            self.is_running = False
            
            # 2. 현재 처리 중인 요청 완료 대기
            logger.info("⏳ 현재 요청 처리 완료 대기...")
            time.sleep(2)
            
            # 3. 데이터 저장 (필요시)
            self.save_shutdown_state()
            
            # 4. 리소스 정리
            self.cleanup_resources()
            
            logger.info("✅ 그레이스풀 셧다운 완료")
            
            # 5. 프로세스 종료
            os._exit(0)
            
        except Exception as e:
            logger.error(f"❌ 셧다운 오류: {e}")
            os._exit(1)

    def save_shutdown_state(self):
        """셧다운 상태 저장"""
        try:
            shutdown_state = {
                'timestamp': datetime.now().isoformat(),
                'reason': 'graceful_shutdown',
                'runtime_seconds': (datetime.now() - self.start_time).total_seconds() if self.start_time else 0,
                'process_id': os.getpid(),
                'render_environment': self.is_render_env
            }
            
            with open('/tmp/render_shutdown_state.json', 'w') as f:
                json.dump(shutdown_state, f, indent=2)
            
            logger.info("💾 셧다운 상태 저장 완료")
            
        except Exception as e:
            logger.error(f"❌ 셧다운 상태 저장 실패: {e}")

    def cleanup_resources(self):
        """리소스 정리"""
        try:
            # 임시 파일 정리
            temp_files = [
                '/tmp/render_health_check.json',
                '/tmp/render_process_log.json'
            ]
            
            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            
            # 메모리 정리
            self.cleanup_memory()
            
            logger.info("🧹 리소스 정리 완료")
            
        except Exception as e:
            logger.error(f"❌ 리소스 정리 실패: {e}")

    def force_terminate_if_needed(self):
        """필요시 강제 종료"""
        try:
            current_time = datetime.now()
            
            # 09시 이후 실행 중인 경우 강제 종료 준비
            if current_time.hour >= 9 and self.is_render_env:
                logger.warning("⚠️ 09시 이후 실행 감지 - 강제 종료 준비")
                
                # 그레이스풀 셧다운 시도
                self.graceful_shutdown(reason="SCHEDULED_TERMINATION")
                
                # 5초 대기 후 강제 종료
                time.sleep(5)
                logger.error("🚨 강제 종료 실행")
                os._exit(0)
                
        except Exception as e:
            logger.error(f"❌ 강제 종료 처리 실패: {e}")
            os._exit(1)

    def start_managed_process(self, app_module: str = "simple_clean_api"):
        """관리되는 프로세스 시작"""
        try:
            self.start_time = datetime.now()
            self.process_id = os.getpid()
            self.is_running = True
            
            logger.info(f"🚀 관리되는 프로세스 시작")
            logger.info(f"📊 모듈: {app_module}")
            logger.info(f"🔢 PID: {self.process_id}")
            logger.info(f"⏰ 시작시간: {self.start_time}")
            
            # 시그널 핸들러 설정
            self.setup_signal_handlers()
            
            # 프로세스 모니터링 시작
            self.start_process_monitor()
            
            # 렌더 환경에서 09시 이후 체크
            if self.is_render_env:
                current_hour = datetime.now().hour
                if current_hour >= 9:
                    logger.warning(f"⚠️ 09시 이후 시작 감지 ({current_hour}시) - 제한된 실행")
                    # 즉시 종료하지 않고 짧은 시간만 실행
                    self.max_runtime_hours = 1
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 관리되는 프로세스 시작 실패: {e}")
            return False

    def get_process_status(self) -> Dict[str, Any]:
        """프로세스 상태 반환"""
        try:
            current_process = psutil.Process()
            memory_info = current_process.memory_info()
            
            status = {
                'is_running': self.is_running,
                'process_id': self.process_id,
                'start_time': self.start_time.isoformat() if self.start_time else None,
                'runtime_seconds': (datetime.now() - self.start_time).total_seconds() if self.start_time else 0,
                'memory_mb': memory_info.rss / 1024 / 1024,
                'cpu_percent': current_process.cpu_percent(),
                'render_environment': self.is_render_env,
                'shutdown_requested': self.shutdown_requested,
                'max_runtime_hours': self.max_runtime_hours
            }
            
            return status
            
        except Exception as e:
            logger.error(f"❌ 프로세스 상태 조회 실패: {e}")
            return {'error': str(e)}

# 전역 프로세스 매니저 인스턴스
process_manager = RenderProcessManager()

def setup_render_process_management():
    """렌더 프로세스 관리 설정"""
    return process_manager.start_managed_process()

def get_render_status():
    """렌더 상태 조회"""
    return process_manager.get_process_status()

def shutdown_render_process(reason: str = "API_REQUEST"):
    """렌더 프로세스 셧다운"""
    process_manager.graceful_shutdown(reason)

if __name__ == "__main__":
    # 직접 실행 시 테스트
    print("🔧 Render Process Manager 테스트")
    
    manager = RenderProcessManager()
    success = manager.start_managed_process("test_module")
    
    if success:
        print("✅ 프로세스 관리 시작 성공")
        
        # 5초 대기 후 상태 확인
        time.sleep(5)
        status = manager.get_process_status()
        print(f"📊 상태: {json.dumps(status, indent=2)}")
        
        # 그레이스풀 셧다운 테스트
        manager.graceful_shutdown("TEST_SHUTDOWN")
    else:
        print("❌ 프로세스 관리 시작 실패")
