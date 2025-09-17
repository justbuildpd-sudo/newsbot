// 백엔드 API 실패 시 사용할 폴백 데이터
export const FALLBACK_POLITICIANS = [
  {
    "name": "강경숙",
    "party": "조국혁신당", 
    "district": "비례대표",
    "committee": "교육위원회",
    "photo_url": "https://www.assembly.go.kr/static/portal/img/openassm/new/68f83caf0c9e4546b1694ead863f45ce.jpg"
  },
  {
    "name": "강대식",
    "party": "국민의힘",
    "district": "대구 동구군위군을", 
    "committee": "국방위원회",
    "photo_url": "https://www.assembly.go.kr/static/portal/img/openassm/new/d1fe9f0902d84f0ba74f721d3298be7f.png"
  },
  {
    "name": "강득구", 
    "party": "더불어민주당",
    "district": "경기 안양시만안구",
    "committee": "환경노동위원회",
    "photo_url": "https://www.assembly.go.kr/static/portal/img/openassm/new/0410a0c8e24b474cac2fd79c7700ca2f.jpg"
  },
  {
    "name": "강명구",
    "party": "국민의힘", 
    "district": "경북 구미시을",
    "committee": "농림축산식품해양수산위원회",
    "photo_url": "https://www.assembly.go.kr/static/portal/img/openassm/new/9f095290d68b47638983c7db100c2eb0.jpg"
  },
  {
    "name": "강민국",
    "party": "국민의힘",
    "district": "경남 진주시을", 
    "committee": "정무위원회",
    "photo_url": "https://www.assembly.go.kr/static/portal/img/openassm/new/70f21f66d1ea471192858adb6f379299.png"
  },
  {
    "name": "강선영",
    "party": "국민의힘",
    "district": "비례대표",
    "committee": "국방위원회",
    "photo_url": "https://www.assembly.go.kr/static/portal/img/openassm/new/89a10eac7851470598886907100ae5ad.jpg"
  },
  {
    "name": "강선우", 
    "party": "국민의힘",
    "district": "서울 강서구갑",
    "committee": "외교통일위원회",
    "photo_url": "https://www.assembly.go.kr/static/portal/img/openassm/new/129a16b2bcda41578deb4f1f1009f297.jpg"
  },
  {
    "name": "강승규",
    "party": "국민의힘",
    "district": "충남 홍성군예산군",
    "committee": "산업통상자원중소벤처기업위원회", 
    "photo_url": "https://www.assembly.go.kr/static/portal/img/openassm/new/ec481315df7b49b4b1a0e8761f41ca49.jpg"
  },
  {
    "name": "강준현",
    "party": "국민의힘",
    "district": "세종특별자치시을",
    "committee": "정무위원회",
    "photo_url": "https://www.assembly.go.kr/static/portal/img/openassm/new/cf61b325757141748e07e055e1541468.jpg"
  },
  {
    "name": "고동진",
    "party": "국민의힘", 
    "district": "서울 강남구병",
    "committee": "행정안전위원회",
    "photo_url": "https://www.assembly.go.kr/static/portal/img/openassm/new/8e0621184727401ea5537cbeb1557776.jpg"
  },
  {
    "name": "이재명",
    "party": "더불어민주당",
    "district": "경기 성남시분당구을", 
    "committee": "기획재정위원회",
    "photo_url": "https://www.assembly.go.kr/static/portal/img/openassm/new/sample.jpg"
  },
  {
    "name": "김기현",
    "party": "국민의힘",
    "district": "울산 북구",
    "committee": "정무위원회",
    "photo_url": "https://www.assembly.go.kr/static/portal/img/openassm/new/sample.jpg"
  },
  {
    "name": "정청래", 
    "party": "더불어민주당",
    "district": "서울 마포구을",
    "committee": "기획재정위원회",
    "photo_url": "https://www.assembly.go.kr/static/portal/img/openassm/new/sample.jpg"
  },
  {
    "name": "추경호",
    "party": "국민의힘",
    "district": "대구 달서구을",
    "committee": "기획재정위원회",
    "photo_url": "https://www.assembly.go.kr/static/portal/img/openassm/new/sample.jpg"
  },
  {
    "name": "박홍근",
    "party": "더불어민주당",
    "district": "부산 북구을", 
    "committee": "기획재정위원회",
    "photo_url": "https://www.assembly.go.kr/static/portal/img/openassm/new/sample.jpg"
  }
]

export const FALLBACK_BILL_SCORES = {
  "강경숙": { main_proposals: 5, co_proposals: 12, total_bills: 17 },
  "강대식": { main_proposals: 3, co_proposals: 8, total_bills: 11 },
  "강득구": { main_proposals: 7, co_proposals: 15, total_bills: 22 },
  "강명구": { main_proposals: 4, co_proposals: 9, total_bills: 13 },
  "강민국": { main_proposals: 2, co_proposals: 6, total_bills: 8 },
  "이재명": { main_proposals: 12, co_proposals: 25, total_bills: 37 },
  "김기현": { main_proposals: 8, co_proposals: 18, total_bills: 26 },
  "정청래": { main_proposals: 9, co_proposals: 20, total_bills: 29 },
  "추경호": { main_proposals: 6, co_proposals: 14, total_bills: 20 },
  "박홍근": { main_proposals: 5, co_proposals: 11, total_bills: 16 }
}

export const FALLBACK_NEWS = {
  "이재명": [
    { title: "이재명 대표, 국정감사 준비", pub_date: "2025-09-17", link: "#" }
  ],
  "김기현": [
    { title: "김기현 의원, 정무위원회 활동", pub_date: "2025-09-17", link: "#" }
  ]
}

export const FALLBACK_TRENDS = {
  ranking: [
    { politician: "이재명", trend_score: 85 },
    { politician: "김기현", trend_score: 72 },
    { politician: "정청래", trend_score: 68 }
  ]
}
