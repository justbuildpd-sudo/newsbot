#!/usr/bin/env python3
"""
실제 22대 국회의원 데이터만 남기고 가짜 생성 인물 제거
"""
import json
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_assembly_data():
    """실제 국회의원 데이터만 정리"""
    
    # 가짜 생성 인물들 (국회의원이 아님)
    fake_politicians = [
        '한동훈',  # 국민의힘 대표, 국회의원 아님
        '조국',    # 조국혁신당 대표, 국회의원 아님 (확인 필요)
    ]
    
    try:
        # 가장 완전한 실제 데이터 로드
        with open('processed_full_assembly_members.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.info(f"원본 데이터: {len(data)}명")
        
        # 가짜 인물 제거
        cleaned_data = []
        removed_count = 0
        
        for member in data:
            name = member.get('name', '')
            
            # 가짜 인물 제거
            if name in fake_politicians:
                logger.warning(f"가짜 인물 제거: {name}")
                removed_count += 1
                continue
            
            # 이름이 없거나 비정상적인 데이터 제거
            if not name or name == '이름없음' or len(name) < 2:
                logger.warning(f"비정상 데이터 제거: {name}")
                removed_count += 1
                continue
            
            # 정당 정보가 없는 경우 무소속으로 설정
            if not member.get('party'):
                member['party'] = '무소속'
            
            cleaned_data.append(member)
        
        # 정리된 데이터 저장
        with open('real_assembly_members_only.json', 'w', encoding='utf-8') as f:
            json.dump(cleaned_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"데이터 정리 완료: {len(cleaned_data)}명 (제거: {removed_count}명)")
        
        # 정당별 통계
        party_stats = {}
        for member in cleaned_data:
            party = member.get('party', '무소속')
            party_stats[party] = party_stats.get(party, 0) + 1
        
        logger.info("정당별 의석수 (실제 데이터):")
        for party, count in sorted(party_stats.items(), key=lambda x: x[1], reverse=True):
            logger.info(f"  {party}: {count}석")
        
        # 샘플 출력
        logger.info("실제 의원 샘플:")
        for i, member in enumerate(cleaned_data[:8]):
            name = member.get('name')
            party = member.get('party')
            district = member.get('district', '').split('/')[0] if member.get('district') else '지역정보없음'
            logger.info(f"  {i+1}. {name} ({party}) - {district}")
        
        return True
        
    except Exception as e:
        logger.error(f"데이터 정리 실패: {e}")
        return False

if __name__ == "__main__":
    clean_assembly_data()
