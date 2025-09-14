"""
국회의원 기본 정보 데이터 (점수제 없음)
실시간 뉴스 언급 기반 객관적 평가를 위한 기본 데이터
"""

def get_assembly_members():
    """국회의원 기본 정보를 반환합니다."""
    return [
        # 주요 민주당 의원들
        {
            "id": 1,
            "name": "서영교",
            "party": "민주당",
            "district": "서울 강서구 갑",
            "committee": "기획재정위원회",
            "orientation": "진보",
            "key_issues": ["경제", "재정", "복지"],
            "mention_count": 0,
            "influence_score": 0.0
        },
        {
            "id": 2,
            "name": "김용민",
            "party": "민주당",
            "district": "서울 강동구 갑",
            "committee": "환경노동위원회",
            "orientation": "진보",
            "key_issues": ["환경", "노동", "에너지"],
            "mention_count": 0,
            "influence_score": 0.0
        },
        {
            "id": 3,
            "name": "박홍배",
            "party": "민주당",
            "district": "서울 강북구 갑",
            "committee": "국방위원회",
            "orientation": "진보",
            "key_issues": ["국방", "안보", "군사"],
            "mention_count": 0,
            "influence_score": 0.0
        },
        {
            "id": 4,
            "name": "이수진",
            "party": "민주당",
            "district": "서울 양천구 갑",
            "committee": "보건복지위원회",
            "orientation": "진보",
            "key_issues": ["보건", "복지", "의료"],
            "mention_count": 0,
            "influence_score": 0.0
        },
        {
            "id": 5,
            "name": "문진석",
            "party": "민주당",
            "district": "서울 노원구 갑",
            "committee": "법제사법위원회",
            "orientation": "진보",
            "key_issues": ["법치", "인권", "개혁"],
            "mention_count": 0,
            "influence_score": 0.0
        },
        {
            "id": 6,
            "name": "민형배",
            "party": "민주당",
            "district": "서울 도봉구 갑",
            "committee": "과학기술정보방송통신위원회",
            "orientation": "진보",
            "key_issues": ["과학기술", "디지털", "방송통신"],
            "mention_count": 0,
            "influence_score": 0.0
        },
        {
            "id": 7,
            "name": "박해철",
            "party": "민주당",
            "district": "서울 동작구 갑",
            "committee": "교육위원회",
            "orientation": "진보",
            "key_issues": ["교육", "청년", "혁신"],
            "mention_count": 0,
            "influence_score": 0.0
        },
        {
            "id": 8,
            "name": "박주민",
            "party": "민주당",
            "district": "서울 마포구 갑",
            "committee": "문화체육관광위원회",
            "orientation": "진보",
            "key_issues": ["문화", "체육", "관광"],
            "mention_count": 0,
            "influence_score": 0.0
        },
        {
            "id": 9,
            "name": "강선우",
            "party": "민주당",
            "district": "서울 서초구 갑",
            "committee": "외교통일위원회",
            "orientation": "진보",
            "key_issues": ["외교", "통일", "안보"],
            "mention_count": 0,
            "influence_score": 0.0
        },
        {
            "id": 10,
            "name": "김현정",
            "party": "민주당",
            "district": "서울 송파구 갑",
            "committee": "환경노동위원회",
            "orientation": "진보",
            "key_issues": ["환경", "노동", "에너지"],
            "mention_count": 0,
            "influence_score": 0.0
        },
        
        # 주요 국민의힘 의원들
        {
            "id": 11,
            "name": "김예지",
            "party": "국민의힘",
            "district": "서울 강남구 갑",
            "committee": "여성가족위원회",
            "orientation": "보수",
            "key_issues": ["여성", "가족", "사회"],
            "mention_count": 0,
            "influence_score": 0.0
        },
        {
            "id": 12,
            "name": "안철수",
            "party": "국민의힘",
            "district": "서울 강남구 을",
            "committee": "과학기술정보방송통신위원회",
            "orientation": "중도",
            "key_issues": ["과학기술", "혁신", "미래"],
            "mention_count": 0,
            "influence_score": 0.0
        },
        {
            "id": 13,
            "name": "나경원",
            "party": "국민의힘",
            "district": "서울 강남구 병",
            "committee": "외교통일위원회",
            "orientation": "보수",
            "key_issues": ["외교", "통일", "안보"],
            "mention_count": 0,
            "influence_score": 0.0
        },
        {
            "id": 14,
            "name": "김종민",
            "party": "무소속",
            "district": "비례대표",
            "committee": "보건복지위원회",
            "orientation": "중도",
            "key_issues": ["복지", "의료", "사회"],
            "mention_count": 0,
            "influence_score": 0.0
        },
        {
            "id": 15,
            "name": "이준석",
            "party": "개혁신당",
            "district": "서울 광진구 갑",
            "committee": "과학기술정보방송통신위원회",
            "orientation": "진보",
            "key_issues": ["과학기술", "디지털", "혁신"],
            "mention_count": 0,
            "influence_score": 0.0
        },
        {
            "id": 16,
            "name": "이해민",
            "party": "조국혁신",
            "district": "서울 마포구 을",
            "committee": "교육위원회",
            "orientation": "진보",
            "key_issues": ["교육", "청년", "혁신"],
            "mention_count": 0,
            "influence_score": 0.0
        },
        {
            "id": 17,
            "name": "강경숙",
            "party": "조국혁신",
            "district": "서울 송파구 을",
            "committee": "외교통일위원회",
            "orientation": "진보",
            "key_issues": ["외교", "통일", "안보"],
            "mention_count": 0,
            "influence_score": 0.0
        },
        {
            "id": 18,
            "name": "최혁진",
            "party": "무소속",
            "district": "서울 종로구 갑",
            "committee": "법제사법위원회",
            "orientation": "중도",
            "key_issues": ["법치", "개혁", "정의"],
            "mention_count": 0,
            "influence_score": 0.0
        },
        {
            "id": 19,
            "name": "정성호",
            "party": "민주당",
            "district": "서울 영등포구 갑",
            "committee": "기획재정위원회",
            "orientation": "진보",
            "key_issues": ["경제", "재정", "복지"],
            "mention_count": 0,
            "influence_score": 0.0
        },
        {
            "id": 20,
            "name": "윤준병",
            "party": "민주당",
            "district": "서울 은평구 갑",
            "committee": "보건복지위원회",
            "orientation": "진보",
            "key_issues": ["보건", "복지", "의료"],
            "mention_count": 0,
            "influence_score": 0.0
        }
    ]

def get_members_by_party(party_name):
    """특정 정당의 국회의원들을 반환합니다."""
    all_members = get_assembly_members()
    return [member for member in all_members if member['party'] == party_name]

def get_member_by_id(member_id):
    """특정 ID의 국회의원을 반환합니다."""
    all_members = get_assembly_members()
    for member in all_members:
        if member['id'] == member_id:
            return member
    return None

def search_members(keyword):
    """키워드로 국회의원을 검색합니다."""
    all_members = get_assembly_members()
    keyword = keyword.lower()
    
    results = []
    for member in all_members:
        if (keyword in member['name'].lower() or 
            keyword in member['party'].lower() or
            keyword in member['district'].lower() or
            keyword in member['committee'].lower()):
            results.append(member)
    
    return results

def get_members_by_orientation(orientation):
    """정치 성향별 국회의원들을 반환합니다."""
    all_members = get_assembly_members()
    return [member for member in all_members if member['orientation'] == orientation]

def get_members_by_committee(committee):
    """위원회별 국회의원들을 반환합니다."""
    all_members = get_assembly_members()
    return [member for member in all_members if committee in member['committee']]

def update_mention_count(member_id, count):
    """특정 의원의 언급 횟수를 업데이트합니다."""
    all_members = get_assembly_members()
    for member in all_members:
        if member['id'] == member_id:
            member['mention_count'] = count
            # 영향력 점수 계산 (언급 횟수 기반)
            member['influence_score'] = min(count * 0.1, 10.0)  # 최대 10점
            break

def get_top_influential_members(limit=10):
    """영향력이 높은 국회의원들을 반환합니다."""
    all_members = get_assembly_members()
    return sorted(all_members, key=lambda x: x['influence_score'], reverse=True)[:limit]
