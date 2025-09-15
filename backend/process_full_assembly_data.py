#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
전체 국회의원 데이터 처리 스크립트
309명의 22대 국회의원 데이터를 처리하여 API에서 사용할 수 있는 형태로 변환
"""

import json
import re
from datetime import datetime

def load_assembly_data():
    """22대 국회의원 데이터 로드"""
    with open('data/assembly_members_22nd_verified.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['members']

def clean_party_name(party):
    """정당명 정리"""
    if not party:
        return "정당 정보 없음"
    
    # 정당명 정리
    party_cleanup = {
        "더불어민주당": "더불어민주당",
        "국민의힘": "국민의힘", 
        "조국혁신당": "조국혁신당",
        "개혁신당": "개혁신당",
        "새로운미래": "새로운미래",
        "진보당": "진보당",
        "개혁신당": "개혁신당",
        "무소속": "무소속"
    }
    
    return party_cleanup.get(party, party)

def clean_committee_name(committee):
    """위원회명 정리"""
    if not committee:
        return "위원회 정보 없음"
    
    # 위원회명 정리
    committee_cleanup = {
        "기획재정위원회": "기획재정위원회",
        "과학기술정보방송통신위원회": "과학기술정보방송통신위원회",
        "행정안전위원회": "행정안전위원회",
        "문화체육관광위원회": "문화체육관광위원회",
        "환경노동위원회": "환경노동위원회",
        "보건복지위원회": "보건복지위원회",
        "교육위원회": "교육위원회",
        "법제사법위원회": "법제사법위원회",
        "정무위원회": "정무위원회",
        "국방위원회": "국방위원회",
        "정보위원회": "정보위원회",
        "여성가족위원회": "여성가족위원회",
        "산업통상자원중소벤처기업위원회": "산업통상자원중소벤처기업위원회",
        "농림축산식품해양수산위원회": "농림축산식품해양수산위원회",
        "국토교통위원회": "국토교통위원회",
        "정보위원회": "정보위원회"
    }
    
    return committee_cleanup.get(committee, committee)

def infer_political_orientation(party, committee):
    """정치성향 추론"""
    if not party:
        return "중도"
    
    # 정당별 성향 분류
    party_orientation = {
        "더불어민주당": "진보",
        "국민의힘": "보수", 
        "조국혁신당": "진보",
        "개혁신당": "중도",
        "새로운미래": "중도",
        "진보당": "진보",
        "무소속": "중도"
    }
    
    return party_orientation.get(party, "중도")

def infer_key_issues(party, committee, district):
    """주요 이슈 추론"""
    issues = []
    
    # 정당별 주요 이슈
    if party == "더불어민주당":
        issues.extend(["복지", "노동", "환경"])
    elif party == "국민의힘":
        issues.extend(["경제", "안보", "자유시장"])
    elif party == "조국혁신당":
        issues.extend(["사법개혁", "민주주의", "인권"])
    elif party == "개혁신당":
        issues.extend(["개혁", "투명성", "효율성"])
    elif party == "새로운미래":
        issues.extend(["미래", "혁신", "통합"])
    elif party == "진보당":
        issues.extend(["진보", "평등", "사회정의"])
    
    # 위원회별 주요 이슈
    if "기획재정" in committee:
        issues.extend(["예산", "경제정책"])
    elif "환경노동" in committee:
        issues.extend(["환경", "노동"])
    elif "보건복지" in committee:
        issues.extend(["복지", "보건"])
    elif "교육" in committee:
        issues.extend(["교육", "청년"])
    elif "국방" in committee:
        issues.extend(["안보", "국방"])
    elif "여성가족" in committee:
        issues.extend(["여성", "가족"])
    
    # 지역별 이슈
    if "서울" in district:
        issues.extend(["도시", "교통"])
    elif "경기" in district:
        issues.extend(["신도시", "교통"])
    elif "부산" in district or "대구" in district or "인천" in district:
        issues.extend(["지역균형", "산업"])
    
    # 중복 제거 및 최대 5개로 제한
    return list(set(issues))[:5]

def process_member(member):
    """개별 의원 데이터 처리"""
    # 기본 정보
    processed = {
        "id": member.get("id", ""),
        "name": member.get("name", ""),
        "name_hanja": member.get("name_hanja", ""),
        "name_english": member.get("name_english", ""),
        "district": member.get("district", ""),
        "terms": member.get("terms", ""),
        "image_url": member.get("image_url", ""),
        "member_number": member.get("member_number", ""),
        "party": clean_party_name(member.get("party", "")),
        "committee": clean_committee_name(member.get("committee", "")),
        "orientation": infer_political_orientation(member.get("party", ""), member.get("committee", "")),
        "key_issues": infer_key_issues(member.get("party", ""), member.get("committee", ""), member.get("district", "")),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    return processed

def main():
    """메인 처리 함수"""
    print("22대 국회의원 전체 데이터 처리 시작...")
    
    # 데이터 로드
    members = load_assembly_data()
    print(f"총 {len(members)}명의 의원 데이터 로드 완료")
    
    # 데이터 처리
    processed_members = []
    for i, member in enumerate(members):
        try:
            processed = process_member(member)
            processed_members.append(processed)
            
            if (i + 1) % 50 == 0:
                print(f"처리 진행: {i + 1}/{len(members)}")
                
        except Exception as e:
            print(f"의원 {member.get('name', 'Unknown')} 처리 중 오류: {e}")
            continue
    
    print(f"총 {len(processed_members)}명의 의원 데이터 처리 완료")
    
    # 통계 생성
    stats = {
        "total_members": len(processed_members),
        "party_distribution": {},
        "committee_distribution": {},
        "orientation_distribution": {},
        "created_at": datetime.now().isoformat()
    }
    
    for member in processed_members:
        # 정당별 분포
        party = member.get("party", "정당 정보 없음")
        stats["party_distribution"][party] = stats["party_distribution"].get(party, 0) + 1
        
        # 위원회별 분포
        committee = member.get("committee", "위원회 정보 없음")
        stats["committee_distribution"][committee] = stats["committee_distribution"].get(committee, 0) + 1
        
        # 성향별 분포
        orientation = member.get("orientation", "중도")
        stats["orientation_distribution"][orientation] = stats["orientation_distribution"].get(orientation, 0) + 1
    
    # 파일 저장
    with open('processed_full_assembly_members.json', 'w', encoding='utf-8') as f:
        json.dump(processed_members, f, ensure_ascii=False, indent=2)
    
    with open('processed_full_assembly_stats.json', 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    
    print("파일 저장 완료:")
    print("- processed_full_assembly_members.json")
    print("- processed_full_assembly_stats.json")
    
    # 통계 출력
    print("\n=== 처리 결과 통계 ===")
    print(f"총 의원 수: {stats['total_members']}명")
    print(f"정당 수: {len(stats['party_distribution'])}개")
    print(f"위원회 수: {len(stats['committee_distribution'])}개")
    
    print("\n정당별 분포:")
    for party, count in sorted(stats['party_distribution'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {party}: {count}명")
    
    print("\n위원회별 분포 (상위 10개):")
    for committee, count in sorted(stats['committee_distribution'].items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {committee}: {count}명")

if __name__ == "__main__":
    main()
