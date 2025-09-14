"""
newsbot.kr 보안 설정
DDoS 방지 및 보안 강화를 위한 설정
"""

# Rate Limiting 설정
RATE_LIMIT_CONFIG = {
    "max_requests_per_minute": 60,      # 분당 최대 요청 수
    "max_requests_per_hour": 1000,      # 시간당 최대 요청 수
    "max_requests_per_day": 10000,      # 일당 최대 요청 수
    "block_duration": 3600,             # 차단 시간 (초)
    "cleanup_interval": 300,            # 정리 간격 (초)
}

# IP 화이트리스트 (관리자 IP)
WHITELIST_IPS = [
    "127.0.0.1",        # 로컬호스트
    "::1",              # IPv6 로컬호스트
    # 실제 운영시 관리자 IP 추가
]

# IP 블랙리스트 (차단할 IP)
BLACKLIST_IPS = [
    # 악성 IP 주소들
]

# 요청 크기 제한
MAX_REQUEST_SIZE = 10 * 1024 * 1024  # 10MB

# 타임아웃 설정
TIMEOUT_CONFIG = {
    "request_timeout": 30,      # 요청 타임아웃 (초)
    "read_timeout": 30,         # 읽기 타임아웃 (초)
    "connect_timeout": 10,      # 연결 타임아웃 (초)
}

# User-Agent 필터링 (봇 차단)
BLOCKED_USER_AGENTS = [
    "bot", "crawler", "spider", "scraper",
    "python-requests", "curl", "wget"
]

# 허용된 도메인 (CORS)
ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "https://newsbot.kr",
    "https://aesthetic-kitsune-cb7c1c.netlify.app"
]

# 로그 설정
LOG_CONFIG = {
    "log_level": "INFO",
    "log_file": "security.log",
    "max_log_size": 10 * 1024 * 1024,  # 10MB
    "backup_count": 5
}

# 캐시 설정
CACHE_CONFIG = {
    "news_cache_ttl": 300,      # 뉴스 캐시 TTL (초)
    "rate_limit_cache_ttl": 60, # Rate limit 캐시 TTL (초)
    "max_cache_size": 1000      # 최대 캐시 항목 수
}

# 모니터링 설정
MONITORING_CONFIG = {
    "enable_metrics": True,
    "metrics_endpoint": "/metrics",
    "health_check_interval": 60,
    "alert_threshold": {
        "error_rate": 0.1,      # 10% 오류율
        "response_time": 5.0,   # 5초 응답시간
        "memory_usage": 0.8     # 80% 메모리 사용률
    }
}
