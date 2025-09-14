# newsbot.kr 서버리스 배포 가이드

## Vercel + Railway 조합 배포

### 1단계: Vercel로 프론트엔드 배포

#### 1.1 Vercel 계정 생성 및 프로젝트 연결
1. [Vercel](https://vercel.com) 접속
2. GitHub 계정으로 로그인
3. "New Project" 클릭
4. `newsbot-kr` 저장소 선택
5. Root Directory: `/` (기본값)
6. Build Command: `echo 'Static site - no build needed'`
7. Output Directory: `/` (기본값)
8. "Deploy" 클릭

#### 1.2 도메인 설정
1. Vercel 대시보드에서 프로젝트 선택
2. Settings → Domains
3. `newsbot.kr` 도메인 추가
4. DNS 설정을 Vercel로 변경

### 2단계: Railway로 백엔드 배포

#### 2.1 Railway 계정 생성
1. [Railway](https://railway.app) 접속
2. GitHub 계정으로 로그인
3. "New Project" 클릭
4. "Deploy from GitHub repo" 선택

#### 2.2 PostgreSQL 데이터베이스 생성
1. Railway 대시보드에서 "New" 클릭
2. "Database" → "PostgreSQL" 선택
3. 데이터베이스 생성 완료 후 `DATABASE_URL` 복사

#### 2.3 백엔드 서비스 배포
1. "New Service" → "GitHub Repo" 선택
2. `newsbot-kr` 저장소 선택
3. Root Directory: `/backend`
4. Environment Variables 설정:
   ```
   DATABASE_URL=postgresql://...
   NAVER_CLIENT_ID=kXwlSsFmb055ku9rWyx1
   NAVER_CLIENT_SECRET=JZqw_LTiq_
   PORT=8001
   ```
5. "Deploy" 클릭

### 3단계: 프론트엔드 API 엔드포인트 업데이트

#### 3.1 Railway URL 확인
1. Railway 대시보드에서 백엔드 서비스 선택
2. "Settings" → "Domains"에서 생성된 URL 확인
3. 예: `https://newsbot-kr-backend-production.up.railway.app`

#### 3.2 프론트엔드 API URL 변경
`script.js` 파일에서 모든 `http://localhost:8001`을 Railway URL로 변경:

```javascript
// 기존
const response = await fetch('http://localhost:8001/api/news');

// 변경 후
const response = await fetch('https://newsbot-kr-backend-production.up.railway.app/api/news');
```

### 4단계: 도메인 연결

#### 4.1 Vercel 도메인 설정
1. Vercel 대시보드 → Settings → Domains
2. `newsbot.kr` 추가
3. DNS 레코드 설정:
   - A Record: `@` → Vercel IP
   - CNAME: `www` → Vercel 도메인

#### 4.2 DNS 설정 (가비아)
1. 가비아 DNS 관리 페이지 접속
2. A 레코드 변경: `@` → Vercel IP
3. CNAME 레코드 변경: `www` → Vercel 도메인

### 5단계: 테스트 및 확인

#### 5.1 API 테스트
```bash
# 뉴스 API 테스트
curl https://newsbot-kr-backend-production.up.railway.app/api/news

# 정치인 API 테스트
curl https://newsbot-kr-backend-production.up.railway.app/api/politicians/ranking
```

#### 5.2 프론트엔드 테스트
1. `https://newsbot.kr` 접속
2. 모든 기능 정상 작동 확인
3. 뉴스 새로고침 테스트
4. 정치인 랭킹 확인

### 6단계: 모니터링 설정

#### 6.1 Vercel Analytics
1. Vercel 대시보드 → Analytics
2. 실시간 트래픽 모니터링

#### 6.2 Railway 로그
1. Railway 대시보드 → Logs
2. API 요청 및 오류 모니터링

## 비용 예상

### Vercel (무료)
- 월 100GB 대역폭
- 무제한 정적 사이트 호스팅
- 자동 HTTPS

### Railway (무료)
- 월 $5 크레딧 (약 100만 요청 처리)
- PostgreSQL 데이터베이스 무료
- 자동 스케일링

## 장점

1. **완전 서버리스**: 서버 관리 불필요
2. **자동 스케일링**: 트래픽에 따라 자동 확장
3. **높은 가용성**: 99.9% 업타임
4. **빠른 배포**: Git push만으로 자동 배포
5. **비용 효율적**: 사용량 기반 과금

## 문제 해결

### 데이터베이스 연결 오류
```bash
# Railway에서 환경변수 확인
railway variables
```

### API CORS 오류
```python
# api_server.py에서 CORS 설정 확인
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://newsbot.kr", "https://*.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 도메인 연결 오류
1. DNS 전파 대기 (최대 24시간)
2. `nslookup newsbot.kr`로 확인
3. Vercel 도메인 설정 재확인
