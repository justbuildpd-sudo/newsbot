"""
newsbot.kr 모니터링 시스템
서버 상태, 성능, 보안 이벤트 모니터링
"""

import time
import psutil
import logging
from datetime import datetime, timedelta
from typing import Dict, List
from collections import defaultdict, deque
import threading

class SystemMonitor:
    """시스템 모니터링 클래스"""
    
    def __init__(self):
        self.start_time = time.time()
        self.request_count = 0
        self.error_count = 0
        self.response_times = deque(maxlen=1000)
        self.error_log = deque(maxlen=100)
        
        # 로깅 설정
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('monitoring.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('newsbot_monitor')
    
    def record_request(self, response_time: float, status_code: int):
        """요청 기록"""
        self.request_count += 1
        self.response_times.append(response_time)
        
        if status_code >= 400:
            self.error_count += 1
            self.error_log.append({
                'timestamp': datetime.now(),
                'status_code': status_code,
                'response_time': response_time
            })
    
    def get_system_stats(self) -> Dict:
        """시스템 통계 반환"""
        current_time = time.time()
        uptime = current_time - self.start_time
        
        # CPU 사용률
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # 메모리 사용률
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # 디스크 사용률
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        
        # 응답 시간 통계
        if self.response_times:
            avg_response_time = sum(self.response_times) / len(self.response_times)
            max_response_time = max(self.response_times)
            min_response_time = min(self.response_times)
        else:
            avg_response_time = max_response_time = min_response_time = 0
        
        # 오류율 계산
        error_rate = (self.error_count / self.request_count) if self.request_count > 0 else 0
        
        return {
            "uptime_seconds": uptime,
            "uptime_formatted": str(timedelta(seconds=int(uptime))),
            "cpu_percent": cpu_percent,
            "memory_percent": memory_percent,
            "disk_percent": disk_percent,
            "total_requests": self.request_count,
            "error_count": self.error_count,
            "error_rate": error_rate,
            "avg_response_time": avg_response_time,
            "max_response_time": max_response_time,
            "min_response_time": min_response_time,
            "timestamp": datetime.now().isoformat()
        }
    
    def check_alerts(self) -> List[Dict]:
        """알림 확인"""
        alerts = []
        stats = self.get_system_stats()
        
        # CPU 사용률 알림
        if stats["cpu_percent"] > 80:
            alerts.append({
                "type": "high_cpu",
                "message": f"CPU 사용률이 높습니다: {stats['cpu_percent']:.1f}%",
                "severity": "warning"
            })
        
        # 메모리 사용률 알림
        if stats["memory_percent"] > 80:
            alerts.append({
                "type": "high_memory",
                "message": f"메모리 사용률이 높습니다: {stats['memory_percent']:.1f}%",
                "severity": "warning"
            })
        
        # 오류율 알림
        if stats["error_rate"] > 0.1:
            alerts.append({
                "type": "high_error_rate",
                "message": f"오류율이 높습니다: {stats['error_rate']:.1%}",
                "severity": "error"
            })
        
        # 응답 시간 알림
        if stats["avg_response_time"] > 5.0:
            alerts.append({
                "type": "slow_response",
                "message": f"응답 시간이 느립니다: {stats['avg_response_time']:.2f}초",
                "severity": "warning"
            })
        
        return alerts
    
    def log_security_event(self, event_type: str, details: Dict):
        """보안 이벤트 로깅"""
        self.logger.warning(f"Security Event - {event_type}: {details}")
    
    def get_recent_errors(self, limit: int = 10) -> List[Dict]:
        """최근 오류 반환"""
        return list(self.error_log)[-limit:]

# 전역 모니터 인스턴스
system_monitor = SystemMonitor()
