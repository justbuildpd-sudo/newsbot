#!/usr/bin/env python3
"""
22대 국회의원 정당명 정리 - 현재 정당명만 사용
"""
import json
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_party_names():
    """22대 국회의원 정당명 정리"""
    
    try:
        with open('verified_22nd_assembly_from_csv.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.info(f"원본 데이터: {len(data)}명")
        
        cleaned_data = []
        for member in data:
            name = member.get('name', '').strip()
            party = member.get('party', '').strip()
            district = member.get('district', '').strip()
            
            # 정당명 정리 (현재 정당만 추출)
            if '/' in party:
                # 마지막 정당명 사용 (현재 정당)
                party = party.split('/')[-1].strip()
            
            # 정당명 표준화
            party_mapping = {
                '더불어민주당': '더불어민주당',
                '국민의힘': '국민의힘', 
                '조국혁신당': '조국혁신당',
                '국민의미래': '국민의미래',
                '더불어민주연합': '더불어민주연합',
                '개혁신당': '개혁신당',
                '새로운미래': '새로운미래',
                '진보당': '진보당',
                '정의당': '정의당'
            }
            
            # 표준 정당명으로 변환
            cleaned_party = party_mapping.get(party, party)
            
            # 지역구명 정리
            if '/' in district:
                # 마지막 지역구명 사용 (현재 지역구)
                district = district.split('/')[-1].strip()
            
            # 정리된 멤버 데이터
            cleaned_member = {
                'name': name,
                'party': cleaned_party,
                'district': district if district else '비례대표',
                'committee': member.get('committee', '').strip(),
                'terms': member.get('terms', '').strip(),
                'photo_url': member.get('photo_url', '').strip(),
                'id': member.get('id', '').strip(),
                'phone': member.get('phone', '').strip(),
                'email': member.get('email', '').strip()
            }
            
            # 기본 검증
            if name and len(name) > 1:
                cleaned_data.append(cleaned_member)
        
        # 정리된 데이터 저장
        with open('final_22nd_assembly_verified.json', 'w', encoding='utf-8') as f:
            json.dump(cleaned_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"정당명 정리 완료: {len(cleaned_data)}명")
        
        # 정당별 통계
        party_stats = {}
        for member in cleaned_data:
            party = member.get('party', '무소속')
            party_stats[party] = party_stats.get(party, 0) + 1
        
        logger.info("정리된 정당별 분포:")
        for party, count in sorted(party_stats.items(), key=lambda x: x[1], reverse=True):
            logger.info(f"  {party}: {count}명")
        
        # HTML 의원 확인
        html_members = [
            '김승수', '김선교', '권영세', '김정재', '김한규', '김희정', 
            '김성원', '강유정', '문금주', '김영배', '강대식', '김용만',
            '고민정', '구자근', '김정호', '곽규택', '김상훈', '김예지',
            '김선민', '김문수', '남인순', '김영진', '김윤덕', '김미애',
            '고동진', '김남희', '김주영', '권칠승', '강민국', '나경원',
            '권성동', '정청래', '강득구', '김민석'
        ]
        
        cleaned_names = [m['name'] for m in cleaned_data]
        found_html_members = [name for name in html_members if name in cleaned_names]
        
        logger.info(f"HTML 의원 중 발견: {len(found_html_members)}/{len(html_members)}명")
        logger.info(f"발견된 HTML 의원: {found_html_members}")
        
        return True
        
    except Exception as e:
        logger.error(f"정당명 정리 실패: {e}")
        return False

if __name__ == "__main__":
    clean_party_names()

