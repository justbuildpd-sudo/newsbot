# newsbot.kr - 정치 뉴스 분석 플랫폼

## 🎯 프로젝트 개요
newsbot.kr은 국회 발언 데이터와 뉴스 데이터를 연결하여 정치적 인사이트를 제공하는 혁신적인 플랫폼입니다.

## 🏗️ 아키텍처
- **Frontend**: React + Next.js + Tailwind CSS
- **Backend**: FastAPI + Python
- **Database**: PostgreSQL + Redis
- **AI/ML**: Hugging Face Transformers
- **Hosting**: Vercel + Railway

## 📊 핵심 기능
1. **실시간 뉴스 수집**: 네이버 뉴스 API를 통한 실시간 뉴스 수집
2. **AI 기반 분석**: 감정 분석, 키워드 추출, 주제 분류
3. **연결성 분석**: 뉴스와 국회 발언의 연결성 분석
4. **시각화**: 네트워크 그래프, 트렌드 차트, 대시보드
5. **검색**: 고급 검색 및 필터링 기능

## 🚀 개발 로드맵
- **Phase 1**: 기반 구축 (1주차)
- **Phase 2**: 기본 웹사이트 (2주차)
- **Phase 3**: 동적 기능 (3-4주차)
- **Phase 4**: AI 분석 (5-6주차)
- **Phase 5**: 고급 기능 (7-8주차)
- **Phase 6**: 최적화 및 배포 (9-10주차)

## 💻 개발 환경 설정
```bash
# 프로젝트 클론
git clone https://github.com/yourusername/newsbot-kr.git
cd newsbot-kr

# 의존성 설치
npm install
pip install -r requirements.txt

# 개발 서버 실행
npm run dev
python -m uvicorn main:app --reload
```

## 📝 라이선스
MIT License
