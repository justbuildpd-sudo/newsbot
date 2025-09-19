# 🚀 NewsBot-KR 배포 가이드

## 📋 배포 준비 완료 상태

### ✅ GitHub 저장소
- **저장소**: https://github.com/justbuildpd-sudo/newsbot.git
- **최신 커밋**: 웹 서비스 완성 및 배포 준비 (2025-09-17)
- **브랜치**: main

### 🌐 배포 옵션

#### 1. Vercel 배포 (권장)
```bash
# Vercel CLI 설치
npm i -g vercel

# 프로젝트 디렉토리에서 배포
cd /Users/hopidaay/newsbot-kr
vercel --prod
```

#### 2. Heroku 배포
```bash
# Heroku CLI 설치 후
heroku create newsbot-kr
git push heroku main
```

#### 3. 직접 서버 배포
```bash
# 서버에서 클론
git clone https://github.com/justbuildpd-sudo/newsbot.git
cd newsbot

# 의존성 설치
pip install -r requirements.txt

# 서버 실행
cd web_service
gunicorn --bind 0.0.0.0:5000 app:app
```

## 🔧 환경 변수 설정

### 필수 환경 변수
```bash
export FLASK_ENV=production
export FLASK_APP=web_service/app.py
export PORT=5000
```

### 선택적 환경 변수
```bash
export BACKEND_API_URL=http://localhost:8001/api
export UNIFIED_API_URL=http://localhost:8000/api
```

## 📊 배포된 기능

### 1. 웹 인터페이스 (Port 5000)
- **메인 페이지**: 정치인 목록 및 검색
- **정치인 상세**: 개별 평가 및 위젯 시각화
- **실시간 통계**: 서버 상태 및 데이터 현황

### 2. API 서비스
- **평가 API**: 정치인 랭킹 및 점수
- **연결성 API**: 네트워크 관계 분석
- **뉴스 API**: 실시간 뉴스 분석

### 3. 시각화 위젯
- **신분증 카드**: 개인 정보 카드 형태
- **맥패밀리트리**: 방사형 관계 네트워크
- **세련된 패널**: 인터랙티브 패널 시스템

## 🔒 보안 설정

### 프로덕션 환경 설정
```python
# web_service/app.py에서 수정 필요
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key')
app.run(debug=False)  # 프로덕션에서는 debug=False
```

### CORS 설정
```python
# 특정 도메인만 허용하도록 수정
allow_origins=["https://newsbot.kr", "https://www.newsbot.kr"]
```

## 📈 성능 최적화

### 1. 데이터베이스 최적화
- SQLite → PostgreSQL 마이그레이션 권장
- 인덱스 최적화
- 캐시 시스템 구축

### 2. 정적 파일 최적화
- CDN 사용 권장
- 이미지 압축
- CSS/JS 최소화

### 3. 서버 최적화
- Redis 캐시 시스템
- 로드 밸런싱
- 모니터링 시스템

## 🚨 주의사항

### 1. 데이터 파일 크기
- 일부 JSON 파일이 대용량 (6.9MB)
- 배포 시 압축 또는 데이터베이스 이전 권장

### 2. API 키 보안
- 네이버 뉴스 API 키 환경변수 처리
- 국회 API 키 보안 관리

### 3. 서버 리소스
- 메모리 사용량 모니터링
- CPU 사용률 최적화

## 📞 배포 후 확인사항

### 1. 서비스 상태 확인
```bash
curl https://newsbot.kr/api/health
```

### 2. 주요 기능 테스트
- 정치인 목록 로드
- 검색 기능
- 상세 페이지 위젯 표시
- API 응답 속도

### 3. 모니터링 설정
- 서버 로그 확인
- 에러 추적
- 성능 모니터링

## 🎯 배포 완료 후 할 일

1. **도메인 연결**: newsbot.kr 도메인 설정
2. **SSL 인증서**: HTTPS 설정
3. **모니터링**: 서버 상태 모니터링
4. **백업**: 정기적 데이터 백업
5. **업데이트**: 정기적 데이터 업데이트

---
*배포 가이드 작성일: 2025-09-17*
*배포 대상: newsbot.kr*

