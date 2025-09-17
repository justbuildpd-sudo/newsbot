import time
from collections import defaultdict, deque
from typing import Dict, Optional
import threading

class RateLimiter:
    """DDoS 방지를 위한 Rate Limiter"""
    
    def __init__(self):
        # IP별 요청 기록
        self.ip_requests = defaultdict(lambda: deque())
        # IP별 차단 상태
        self.blocked_ips = set()
        # 락 (thread-safe)
        self.lock = threading.Lock()
        
        # 설정값
        self.max_requests_per_minute = 60  # 분당 최대 요청 수
        self.max_requests_per_hour = 1000  # 시간당 최대 요청 수
        self.block_duration = 3600  # 차단 시간 (초)
        self.cleanup_interval = 300  # 정리 간격 (초)
        
        # 마지막 정리 시간
        self.last_cleanup = time.time()
    
    def is_allowed(self, ip: str) -> tuple[bool, str]:
        """IP가 요청을 허용받을 수 있는지 확인"""
        current_time = time.time()
        
        with self.lock:
            # 차단된 IP 확인
            if ip in self.blocked_ips:
                return False, "IP가 차단되었습니다. 잠시 후 다시 시도해주세요."
            
            # 정리 작업 (5분마다)
            if current_time - self.last_cleanup > self.cleanup_interval:
                self._cleanup_old_requests(current_time)
                self.last_cleanup = current_time
            
            # 요청 기록 추가
            self.ip_requests[ip].append(current_time)
            
            # 분당 요청 수 확인
            minute_ago = current_time - 60
            recent_requests = [req_time for req_time in self.ip_requests[ip] if req_time > minute_ago]
            
            if len(recent_requests) > self.max_requests_per_minute:
                self.blocked_ips.add(ip)
                return False, "분당 요청 한도를 초과했습니다. IP가 차단되었습니다."
            
            # 시간당 요청 수 확인
            hour_ago = current_time - 3600
            hourly_requests = [req_time for req_time in self.ip_requests[ip] if req_time > hour_ago]
            
            if len(hourly_requests) > self.max_requests_per_hour:
                self.blocked_ips.add(ip)
                return False, "시간당 요청 한도를 초과했습니다. IP가 차단되었습니다."
            
            return True, "요청이 허용되었습니다."
    
    def _cleanup_old_requests(self, current_time: float):
        """오래된 요청 기록 정리"""
        cutoff_time = current_time - 3600  # 1시간 이전
        
        for ip in list(self.ip_requests.keys()):
            # 1시간 이전 요청들 제거
            self.ip_requests[ip] = deque(
                req_time for req_time in self.ip_requests[ip] 
                if req_time > cutoff_time
            )
            
            # 빈 deque 제거
            if not self.ip_requests[ip]:
                del self.ip_requests[ip]
        
        # 차단 시간이 지난 IP들 해제
        self.blocked_ips.clear()  # 간단하게 모든 차단 해제
    
    def get_stats(self) -> Dict:
        """현재 상태 통계 반환"""
        with self.lock:
            current_time = time.time()
            active_ips = len(self.ip_requests)
            blocked_count = len(self.blocked_ips)
            
            # 최근 1분간 총 요청 수
            minute_ago = current_time - 60
            recent_requests = sum(
                len([req_time for req_time in requests if req_time > minute_ago])
                for requests in self.ip_requests.values()
            )
            
            return {
                "active_ips": active_ips,
                "blocked_ips": blocked_count,
                "recent_requests_per_minute": recent_requests,
                "max_requests_per_minute": self.max_requests_per_minute,
                "max_requests_per_hour": self.max_requests_per_hour
            }

# 전역 Rate Limiter 인스턴스
rate_limiter = RateLimiter()
