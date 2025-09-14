# newsbot.kr 배포 가이드

## 🚀 GitHub Pages 배포 방법

### 1. GitHub 저장소 생성
1. GitHub.com에 로그인
2. "New repository" 클릭
3. Repository name: `newsbot-kr`
4. Public으로 설정
5. "Create repository" 클릭

### 2. 로컬 파일 업로드
```bash
# 현재 디렉토리에서 실행
cd /Users/hopidaay/newsbot-kr

# GitHub에 푸시 (인증 필요)
git push origin main
```

### 3. GitHub Pages 설정
1. GitHub 저장소 페이지에서 "Settings" 탭 클릭
2. 왼쪽 메뉴에서 "Pages" 클릭
3. Source를 "Deploy from a branch" 선택
4. Branch를 "main" 선택
5. Folder를 "/ (root)" 선택
6. "Save" 클릭

### 4. 도메인 연결 (newsbot.kr)
1. GitHub Pages 설정에서 "Custom domain" 입력
2. `newsbot.kr` 입력
3. "Save" 클릭
4. DNS 설정에서 CNAME 레코드 추가:
   - Name: `newsbot.kr`
   - Value: `hopidaay.github.io`

## 🌐 대안 배포 방법

### Netlify 배포 (추천)
1. [netlify.com](https://netlify.com) 접속
2. "Add new site" → "Deploy manually"
3. `/Users/hopidaay/newsbot-kr` 폴더를 드래그 앤 드롭
4. Site name: `newsbot-kr`
5. "Deploy site" 클릭
6. Custom domain에서 `newsbot.kr` 연결

### Vercel 배포
1. [vercel.com](https://vercel.com) 접속
2. "New Project" 클릭
3. GitHub 저장소 연결 또는 폴더 업로드
4. Deploy 클릭
5. Custom domain 설정

## 📁 현재 파일 구조
```
newsbot-kr/
├── index.html                    # 메인 페이지
├── political-family-tree.html    # MacFamilyTree 스타일 인맥관계도
├── styles.css                    # 메인 스타일
├── family-tree.css              # 인맥관계도 스타일
├── script.js                    # 메인 JavaScript
├── family-tree.js               # 인맥관계도 JavaScript
├── README.md                    # 프로젝트 설명
└── deploy-instructions.md       # 이 파일
```

## ✅ 완료된 기능들
- ✅ MacFamilyTree 스타일 정치인 인맥관계도
- ✅ 인터랙티브 네트워크 시각화 (D3.js)
- ✅ 실시간 뉴스 위젯
- ✅ 핫이슈 랭킹 위젯
- ✅ 트렌드 차트 위젯
- ✅ 정치인 프로필 위젯
- ✅ 분석 리포트 위젯
- ✅ 고급 필터링 시스템
- ✅ 반응형 디자인

## 🎯 다음 단계
1. GitHub Pages 또는 Netlify로 배포
2. newsbot.kr 도메인 연결
3. 실제 데이터 연동 (네이버 뉴스 API)
4. 백엔드 API 구축
5. 데이터베이스 연동

## 📞 지원
배포 과정에서 문제가 있으면 언제든 문의하세요!
