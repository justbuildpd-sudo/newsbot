#!/usr/bin/env python3
"""
지역구 충돌 문제 해결 - 무소속 의원들의 지역구 정리
"""
import json
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_district_conflicts():
    """지역구 충돌 문제 해결"""
    
    try:
        # 현재 데이터 로드
        with open('verified_real_assembly_members.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.info(f"원본 데이터: {len(data)}명")
        
        # 지역구별 의원 매핑
        district_mapping = {}
        conflicts = []
        
        # 1차: 지역구 중복 확인
        for member in data:
            district = member.get('district', '')
            name = member.get('name', '')
            party = member.get('party', '')
            
            if district and district != '비례대표':
                if district in district_mapping:
                    conflicts.append({
                        'district': district,
                        'existing': district_mapping[district],
                        'conflicting': {'name': name, 'party': party}
                    })
                else:
                    district_mapping[district] = {'name': name, 'party': party}
        
        logger.info(f"지역구 충돌 발견: {len(conflicts)}건")
        
        # 2차: 충돌 해결 (무소속 우선 정리)
        fixed_data = []
        for member in data:
            name = member.get('name', '')
            party = member.get('party', '')
            district = member.get('district', '')
            
            # 무소속이면서 지역구가 있는 경우
            if party == '무소속' and district and district != '비례대표':
                # 해당 지역구에 다른 의원이 있는지 확인
                conflict_found = False
                for other in data:
                    if (other.get('name') != name and 
                        other.get('district') == district and 
                        other.get('party') != '무소속'):
                        conflict_found = True
                        break
                
                if conflict_found:
                    # 충돌하는 무소속 의원은 비례대표로 변경
                    member['district'] = '비례대표'
                    logger.warning(f"지역구 충돌 해결: {name} ({district} → 비례대표)")
            
            fixed_data.append(member)
        
        # 3차: 최종 검증
        final_district_mapping = {}
        final_conflicts = 0
        
        for member in fixed_data:
            district = member.get('district', '')
            name = member.get('name', '')
            
            if district and district != '비례대표':
                if district in final_district_mapping:
                    final_conflicts += 1
                    logger.error(f"여전한 충돌: {district} - {final_district_mapping[district]} vs {name}")
                else:
                    final_district_mapping[district] = name
        
        # 정리된 데이터 저장
        with open('conflict_free_assembly_members.json', 'w', encoding='utf-8') as f:
            json.dump(fixed_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"지역구 충돌 해결 완료: {len(fixed_data)}명")
        logger.info(f"최종 충돌: {final_conflicts}건")
        
        # 통계
        party_stats = {}
        district_stats = {'비례대표': 0, '지역구': 0}
        
        for member in fixed_data:
            party = member.get('party', '무소속')
            district = member.get('district', '')
            
            party_stats[party] = party_stats.get(party, 0) + 1
            
            if district == '비례대표':
                district_stats['비례대표'] += 1
            elif district:
                district_stats['지역구'] += 1
        
        logger.info("정당별 의석수:")
        for party, count in sorted(party_stats.items(), key=lambda x: x[1], reverse=True):
            logger.info(f"  {party}: {count}석")
        
        logger.info(f"지역구 분포: 지역구 {district_stats['지역구']}명, 비례대표 {district_stats['비례대표']}명")
        
        return True
        
    except Exception as e:
        logger.error(f"지역구 충돌 해결 실패: {e}")
        return False

if __name__ == "__main__":
    fix_district_conflicts()

