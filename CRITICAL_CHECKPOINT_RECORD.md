# 🚨 CRITICAL CHECKPOINT RECORD - NewsBot.kr 작업 기록점

## 📅 작성일: 2025년 9월 17일 09:30
## ⚠️ 중요도: 최상급 (절대 삭제 금지)

---

## 🎯 현재 구축된 평가지표 시스템 완전 정리

### 1. 📊 종합 평가 시스템 (comprehensive_evaluation_system.py)
**위치**: `/Users/hopidaay/newsbot-kr/backend/comprehensive_evaluation_system.py`

#### 평가 지표 구성:
```python
@dataclass
class PoliticianScore:
    # 기본 정보
    name, party, district, committee
    
    # 뉴스 평가 (30% 가중치)
    news_mention_score: float      # 뉴스 언급 빈도
    news_sentiment_score: float    # 뉴스 감정 분석
    news_trend_score: float        # 뉴스 트렌드 분석
    
    # 의안발의 평가 (25% 가중치)  
    bill_sponsor_score: float      # 주발의 점수
    bill_co_sponsor_score: float   # 공동발의 점수
    bill_success_rate: float       # 의안 성공률
    
    # 의안결과 평가 (25% 가중치)
    bill_pass_rate: float          # 의안 통과율
    bill_impact_score: float       # 의안 영향력
    bill_quality_score: float      # 의안 품질
    
    # 연결성 평가 (20% 가중치)
    connectivity_score: float      # 전체 연결성
    influence_score: float         # 영향력 점수
    collaboration_score: float     # 협업 점수
    
    # 최종 점수
    total_score: float             # 100점 만점 종합 점수
```

#### 사용 방법:
```bash
cd /Users/hopidaay/newsbot-kr/backend
python3 comprehensive_evaluation_system.py
```

### 2. 🌐 통합 서버 (unified_server.py) - 포트 8000
**위치**: `/Users/hopidaay/newsbot-kr/backend/unified_server.py`

#### 제공 API:
- `GET /api/evaluation/ranking` - 정치인 랭킹
- `GET /api/evaluation/party-stats` - 정당별 통계
- `GET /api/evaluation/politician/{name}` - 개별 정치인 평가
- `GET /api/connectivity/stats` - 연결성 통계
- `GET /api/connectivity/politician/{name}` - 개별 연결성

#### 실행 방법:
```bash
cd /Users/hopidaay/newsbot-kr/backend
python3 unified_server.py
# 접속: http://localhost:8000
```

### 3. 📡 API 서버 (api_server.py) - 포트 8001
**위치**: `/Users/hopidaay/newsbot-kr/backend/api_server.py`

#### 제공 기능:
- 뉴스 수집 및 분석
- 국회의원 데이터 (309명)
- 회의록 분석 (4,814개)
- 정치인 매칭 시스템

#### 실행 방법:
```bash
cd /Users/hopidaay/newsbot-kr/backend
python3 api_server.py
# 접속: http://localhost:8001
```

### 4. 🌐 웹 서비스 (app.py) - 포트 5000
**위치**: `/Users/hopidaay/newsbot-kr/web_service/app.py`

#### 제공 기능:
- 기존 서버들을 연결하는 웹 인터페이스
- 정치인 프로필 표시
- 뉴스 및 평가 결과 시각화

#### 실행 방법:
```bash
cd /Users/hopidaay/newsbot-kr/web_service
python3 app.py
# 접속: http://localhost:5000
```

---

## 🗂️ 핵심 데이터 파일들

### 1. 국회의원 데이터
- `22nd_assembly_members_300.json` (464KB) - 22대 국회의원 300명 데이터
- `all_assembly_members.json` (902KB) - 전체 국회의원 데이터
- `politicians_data_with_party.json` - 정당 정보 포함 데이터

### 2. 의안 분석 데이터
- `advanced_legislative_activity.json` (2.5MB) - 고급 의안 활동 분석
- `co_sponsor_relationships.json` (3MB) - 공동발의 관계 분석
- `individual_legislative_profiles_22nd_300.json` (902KB) - 개인별 의안 프로필

### 3. 협업 네트워크 데이터
- `detailed_collaboration_analysis.json` (6.4MB) - 상세 협업 분석
- `collaboration_network_analysis.json` (738KB) - 협업 네트워크 분석

### 4. 회의록 데이터
- `meeting_records_simple.db` (15.8GB) - SQLite 회의록 데이터베이스
- 4,814개 회의록, 3,511,655개 발화자 데이터

---

## 🏗️ 관계나무 시각화 시스템

### 1. 맥패밀리트리 스타일 (mac_family_tree_style_visualizer.py)
**특징**: 중심 인물 기준 방사형 배치
```bash
cd /Users/hopidaay/newsbot-kr/backend
python3 mac_family_tree_style_visualizer.py
open mac_family_tree_widgets/widgets/radial_network_정청래.html
```

### 2. 세련된 패널 시스템 (sophisticated_panel_visualizer.py)  
**특징**: 사각형 패널, 클릭 시 확장
```bash
cd /Users/hopidaay/newsbot-kr/backend
python3 sophisticated_panel_visualizer.py
open sophisticated_panels/widgets/sophisticated_panel_정청래.html
```

### 3. 신분증 카드 시스템 (id_card_widget_system.py)
**특징**: 실제 신분증 형태 디자인
```bash
cd /Users/hopidaay/newsbot-kr/backend
python3 id_card_widget_system.py
open id_card_widgets/index.html
```

---

## 🚀 평가지표 활용 방안

### Phase 1: 기본 평가 시스템 (현재 구축 완료)
1. **뉴스 기반 평가** (30%)
   - 언급 빈도: 뉴스에서 언급되는 횟수
   - 감정 분석: 긍정/부정/중립 비율
   - 트렌드: 시간별 언급 변화

2. **의안 활동 평가** (50%)
   - 발의 점수: 주발의 + 공동발의
   - 성공률: 발의한 의안의 통과율
   - 품질: 의안의 사회적 영향도

3. **연결성 평가** (20%)
   - 네트워크 중심성
   - 협업 지수
   - 영향력 확산도

### Phase 2: 고도화 (진행 중)
1. **실시간 뉴스 반영**
   - 네이버 뉴스 API 연동
   - 30분마다 자동 업데이트
   - 감정 분석 자동화

2. **관계나무 시각화**
   - 3가지 스타일 지원
   - 인터랙티브 탐색
   - 연결 강도별 시각화

3. **종합 대시보드**
   - localhost:5000 웹 인터페이스
   - 실시간 랭킹 시스템
   - 검색 및 필터링

### Phase 3: 완성형 (계획)
1. **AI 기반 분석**
   - 발언 내용 감정 분석
   - 정책 유사도 계산
   - 예측 모델링

2. **사회적 영향도**
   - 언론 노출 가중치
   - SNS 반응 분석
   - 여론조사 연동

---

## 📋 서버 실행 순서 (중요!)

### 1단계: 기본 서버들 실행
```bash
# 터미널 1: 통합 서버 (포트 8000)
cd /Users/hopidaay/newsbot-kr/backend
python3 unified_server.py

# 터미널 2: API 서버 (포트 8001) 
cd /Users/hopidaay/newsbot-kr/backend
python3 api_server.py

# 터미널 3: 웹 서비스 (포트 5000)
cd /Users/hopidaay/newsbot-kr/web_service  
python3 app.py
```

### 2단계: 상태 확인
```bash
curl http://localhost:8000/api/health
curl http://localhost:8001/api/health
curl http://localhost:5000/api/health
```

### 3단계: 웹 접속
- 메인 웹 서비스: http://localhost:5000
- API 문서: http://localhost:8000/docs
- 백엔드 API: http://localhost:8001

---

## 🔧 평가지표 실제 사용법

### 1. 정치인 종합 평가 조회
```bash
curl "http://localhost:8000/api/evaluation/ranking?limit=10"
```

### 2. 특정 정치인 상세 평가
```bash
curl "http://localhost:8000/api/evaluation/politician/정청래"
```

### 3. 정당별 통계
```bash
curl "http://localhost:8000/api/evaluation/party-stats"
```

### 4. 연결성 분석
```bash
curl "http://localhost:8000/api/connectivity/politician/정청래"
```

### 5. 뉴스 기반 분석
```bash
curl "http://localhost:8001/api/news/with-politicians"
```

---

## 🗄️ 데이터베이스 구조

### SQLite 테이블들:
1. **politicians** - 기본 정치인 정보
2. **evaluation_scores** - 평가 점수들  
3. **connectivity_relations** - 연결성 관계
4. **meetings** - 회의록 메타데이터
5. **speakers** - 발화자 상세 정보

---

## 🚨 백업 및 복구 정보

### 중요 백업 위치:
- **전체 프로젝트**: `/Users/hopidaay/newsbot-kr/`
- **백업 폴더**: `/Users/hopidaay/newsbot-kr/backups/newsbot_backup_20250916_132435/`
- **데이터베이스**: `/Users/hopidaay/newsbot-kr/backend/meeting_records_simple.db` (15.8GB)

### GitHub 저장소:
- **원격 저장소**: https://github.com/justbuildpd-sudo/newsbot.git
- **최신 커밋**: 9월 15일 "상임위원회 활동 조회 API 연동 및 정치인 매칭 개선"

---

## ⚡ 긴급 복구 명령어

### 서버가 안 될 때:
```bash
cd /Users/hopidaay/newsbot-kr/backend
python3 server_manager_simple.py restart
```

### 데이터가 없을 때:
```bash
cd /Users/hopidaay/newsbot-kr/backend
python3 comprehensive_evaluation_system.py
```

### 전체 재시작:
```bash
cd /Users/hopidaay/newsbot-kr
git pull origin main
cd backend
python3 unified_server.py
```

---

## 🔗 관련 문서들
- `LATEST_STATUS_SUMMARY.md` - 최신 상황 요약
- `PROGRESS_SUMMARY.md` - 진행상황 요약  
- `project_summary_and_reminders.md` - 프로젝트 요약 및 리마인더
- `reflection_and_improvement.md` - 반성 및 개선 계획

---

**⚠️ 이 파일은 절대 삭제하지 마세요. 모든 작업의 핵심 기록점입니다.**

---
*작성자: AI Assistant*  
*최종 업데이트: 2025-09-17 09:30*  
*버전: 1.0.0*
