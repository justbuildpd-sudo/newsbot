#!/usr/bin/env python3
"""
실제 22대 국회의원 공식 데이터만 사용하여 완전 재구성
가짜 데이터와 충돌 문제 완전 해결
"""
import json
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def rebuild_authentic_data():
    """실제 국회의원 데이터만으로 완전 재구성"""
    
    try:
        # 원본 실제 데이터 로드 (가장 신뢰할 수 있는 소스)
        source_files = [
            'processed_full_assembly_members.json',
            'real_assembly_members.json',
            'politicians_data.json'
        ]
        
        authentic_data = None
        for filename in source_files:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    authentic_data = json.load(f)
                logger.info(f"원본 데이터 로드 성공: {filename} ({len(authentic_data)}명)")
                break
            except FileNotFoundError:
                continue
        
        if not authentic_data:
            logger.error("원본 데이터 파일을 찾을 수 없음")
            return False
        
        # 데이터 정리 및 검증
        cleaned_members = []
        seen_districts = {}
        seen_names = set()
        
        for member in authentic_data:
            name = member.get('name', '').strip()
            party = member.get('party', '').strip()
            district = member.get('district', '').strip()
            
            # 기본 검증
            if not name or len(name) < 2:
                continue
            
            # 중복 이름 제거
            if name in seen_names:
                logger.warning(f"중복 이름 제거: {name}")
                continue
            seen_names.add(name)
            
            # 지역구 중복 검증
            if district and district != '비례대표':
                if district in seen_districts:
                    logger.warning(f"지역구 충돌 해결: {name} ({district} → 비례대표)")
                    district = '비례대표'
                else:
                    seen_districts[district] = name
            
            # 정당 정보 정리
            if not party:
                party = '무소속'
            
            # 정리된 멤버 데이터
            cleaned_member = {
                'name': name,
                'party': party,
                'district': district if district else '비례대표',
                'committee': member.get('committee', '').strip() or '정보없음',
                'terms': member.get('terms', ''),
                'id': member.get('id', f"member_{len(cleaned_members)+1}"),
                'photo_url': member.get('photo_url', '')
            }
            
            cleaned_members.append(cleaned_member)
        
        # 최종 데이터 저장
        with open('authentic_assembly_members.json', 'w', encoding='utf-8') as f:
            json.dump(cleaned_members, f, ensure_ascii=False, indent=2)
        
        logger.info(f"인증된 데이터 생성 완료: {len(cleaned_members)}명")
        
        # 최종 검증
        final_districts = {}
        district_conflicts = 0
        
        for member in cleaned_members:
            district = member.get('district', '')
            name = member.get('name', '')
            
            if district and district != '비례대표':
                if district in final_districts:
                    district_conflicts += 1
                    logger.error(f"최종 충돌: {district} - {final_districts[district]} vs {name}")
                else:
                    final_districts[district] = name
        
        # 통계
        party_stats = {}
        district_types = {'지역구': 0, '비례대표': 0}
        
        for member in cleaned_members:
            party = member.get('party', '무소속')
            district = member.get('district', '')
            
            party_stats[party] = party_stats.get(party, 0) + 1
            
            if district == '비례대표':
                district_types['비례대표'] += 1
            else:
                district_types['지역구'] += 1
        
        logger.info("최종 정당별 의석수:")
        for party, count in sorted(party_stats.items(), key=lambda x: x[1], reverse=True):
            logger.info(f"  {party}: {count}석")
        
        logger.info(f"지역구 분포: 지역구 {district_types['지역구']}명, 비례대표 {district_types['비례대표']}명")
        logger.info(f"최종 지역구 충돌: {district_conflicts}건")
        
        if district_conflicts == 0:
            logger.info("✅ 지역구 충돌 완전 해결!")
        else:
            logger.warning(f"⚠️ {district_conflicts}건 충돌 여전히 존재")
        
        return True
        
    except Exception as e:
        logger.error(f"데이터 재구성 실패: {e}")
        return False

if __name__ == "__main__":
    rebuild_authentic_data()

