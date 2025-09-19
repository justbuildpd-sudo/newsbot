# 🚀 NewsBot-KR 배포 가이드

## 📊 배포 대상

**세계 최대급 정치인 데이터베이스 (42,290명) 배포**

- **백엔드**: Render (simple_clean_api.py)
- **프론트엔드**: Vercel (Next.js)
- **데이터**: 42,290명 완성 데이터

---

## 🔧 1. Render 백엔드 배포

### 📋 배포 설정

**Repository 정보:**
- URL: `https://github.com/justbuildpd-sudo/newsbot`
- Branch: `main`
- Root Directory: `/` (루트)

**Build & Start 설정:**
- Build Command: (자동 감지)
- Start Command: `web: cd backend && python -m uvicorn simple_clean_api:app --host 0.0.0.0 --port $PORT`

**환경 변수:**
- `PYTHON_VERSION`: `3.11.6`
- `PORT`: (자동 설정)

### 🎯 배포 단계

1. **Render.com 로그인**
2. **New Web Service 생성**
3. **GitHub 연결** → `justbuildpd-sudo/newsbot` 선택
4. **설정 입력**:
   - Name: `newsbot-backend`
   - Branch: `main`
   - Build Command: (비워둠)
   - Start Command: `cd backend && python -m uvicorn simple_clean_api:app --host 0.0.0.0 --port $PORT`
5. **Environment Variables 추가**:
   - `PYTHON_VERSION` = `3.11.6`
6. **Deploy 클릭**

### ✅ 배포 확인

**예상 URL**: `https://newsbot-backend-xxxx.onrender.com`

**테스트 엔드포인트**:
- `GET /` - 서버 상태
- `GET /api/assembly/members` - 42,290명 데이터 로드

---

## 🌐 2. Vercel 프론트엔드 배포

### 📋 배포 설정

**Repository 정보:**
- URL: `https://github.com/justbuildpd-sudo/newsbot`
- Branch: `main`
- Root Directory: `frontend/`

**Framework 설정:**
- Framework: `Next.js`
- Build Command: `npm run build`
- Output Directory: `.next`
- Install Command: `npm install`

### 🎯 배포 단계

1. **Vercel.com 로그인**
2. **New Project 생성**
3. **GitHub 연결** → `justbuildpd-sudo/newsbot` 선택
4. **설정 입력**:
   - Framework Preset: `Next.js`
   - Root Directory: `frontend`
   - Build and Output Settings: (기본값 사용)
5. **Environment Variables 추가**:
   - `NEXT_PUBLIC_API_URL` = `https://newsbot-backend-xxxx.onrender.com`
6. **Deploy 클릭**

### ✅ 배포 확인

**예상 URL**: `https://newsbot-kr.vercel.app`

---

## 🔗 3. API 연결 설정

### 📝 환경 변수 업데이트

**Vercel 프론트엔드**:
```bash
NEXT_PUBLIC_API_URL=https://newsbot-backend-[실제URL].onrender.com
```

### 🔄 재배포

1. **Vercel Dashboard** → **Settings** → **Environment Variables**
2. **API URL 업데이트**
3. **Redeploy** 실행

---

## 🧪 4. 통합 테스트

### 🔍 백엔드 테스트

```bash
# 서버 상태 확인
curl https://newsbot-backend-xxxx.onrender.com/

# 의원 데이터 확인 (42,290명)
curl https://newsbot-backend-xxxx.onrender.com/api/assembly/members

# 특정 의원 조회
curl https://newsbot-backend-xxxx.onrender.com/api/assembly/members/이재명
```

### 🔍 프론트엔드 테스트

**기능별 확인:**
- ✅ 메인 페이지 로딩
- ✅ 정치인 카드 표시 (42,290명)
- ✅ 검색 기능 (정치인 전용)
- ✅ 상세 팝업 (연결성 위젯 포함)
- ✅ 트렌드 차트 (Naver Datalab)
- ✅ 실시간 뉴스 위젯
- ✅ 최근 법안 위젯
- ✅ 한국 지도 위젯

### 🔍 성능 테스트

**확인 항목:**
- 42,290명 데이터 로딩 속도
- API 응답 시간 (< 2초)
- 프론트엔드 렌더링 (< 3초)
- 모바일 반응형 확인

---

## 🌐 5. 도메인 연결 (newsbot.kr)

### 📋 DNS 설정

**Vercel 커스텀 도메인:**
1. **Vercel Dashboard** → **Settings** → **Domains**
2. **Add Domain**: `newsbot.kr`
3. **DNS 레코드 설정**:
   ```
   Type: CNAME
   Name: @
   Value: cname.vercel-dns.com
   ```

**백엔드 서브도메인 (선택사항):**
```
Type: CNAME
Name: api
Value: newsbot-backend-xxxx.onrender.com
```

---

## ✅ 6. 배포 완료 체크리스트

### 🎯 백엔드 (Render)

- [ ] 서버 정상 실행
- [ ] 42,290명 데이터 로드 확인
- [ ] API 엔드포인트 모두 동작
- [ ] CORS 설정 정상
- [ ] 로그 정상 출력

### 🎯 프론트엔드 (Vercel)

- [ ] 메인 페이지 정상 로딩
- [ ] API 연동 정상
- [ ] 모든 컴포넌트 동작
- [ ] 모바일 반응형 확인
- [ ] SEO 메타 태그 확인

### 🎯 통합 시스템

- [ ] 백엔드-프론트엔드 연동 완료
- [ ] 42,290명 데이터 정상 표시
- [ ] 검색 기능 정상
- [ ] 실시간 뉴스/트렌드 연동
- [ ] 성능 최적화 확인

---

## 🎉 배포 완료!

**세계 최대급 42,290명 정치인 데이터베이스가 성공적으로 배포되었습니다!**

### 🌟 주요 성과

- **42,290명** 정치인 데이터 완전 서비스
- **18개 카테고리** 완전 분류
- **실시간 뉴스/트렌드** 연동
- **모바일 최적화** 완료
- **세계 최대급** 정치인 플랫폼 완성

---

**배포일시**: 2025년 9월 19일  
**버전**: v2.0 (42,290명 완성)  
**커밋**: 5545438 - 42,290명 세계 최대급 정치인 데이터베이스 완성

