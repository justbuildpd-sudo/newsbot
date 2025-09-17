#!/usr/bin/env python3
"""
1. 국회의원통합API - 의원정보 전용 서비스
- 의원정보 (이름, 정당, 지역구, 위원회)
- 사진 정보 관리
- 잘못된 정보 검증용
"""
import json
import logging
from typing import List, Dict, Optional

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AssemblyMemberAPI:
    """국회의원통합API 클래스"""
    
    def __init__(self):
        self.members_data = []
        self.photo_mapping = {}
        self.load_member_data()
        self.load_photo_mapping()
    
    def load_member_data(self):
        """의원 데이터 로드"""
        # 실제 의원 데이터 파일들 우선순위
        data_files = [
            'processed_full_assembly_members.json',  # 가장 완전한 원본
            'real_assembly_members.json',
            '22nd_assembly_members_300.json',
            'authentic_assembly_members.json'
        ]
        
        for filename in data_files:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    self.members_data = json.load(f)
                logger.info(f"의원 데이터 로드 성공: {filename} ({len(self.members_data)}명)")
                break
            except FileNotFoundError:
                continue
        
        if not self.members_data:
            logger.error("의원 데이터 파일을 찾을 수 없음")
            return
        
        # 데이터 품질 검증
        self.validate_member_data()
    
    def load_photo_mapping(self):
        """사진 매핑 로드"""
        try:
            with open('../frontend/public/politician_photos.json', 'r', encoding='utf-8') as f:
                self.photo_mapping = json.load(f)
            logger.info(f"사진 매핑 로드 성공: {len(self.photo_mapping)}명")
        except FileNotFoundError:
            logger.warning("사진 매핑 파일을 찾을 수 없음")
            self.photo_mapping = {}
    
    def validate_member_data(self):
        """의원 데이터 품질 검증"""
        valid_members = []
        
        for member in self.members_data:
            name = member.get('name', '').strip()
            party = member.get('party', '').strip()
            
            # 기본 검증
            if not name or len(name) < 2:
                continue
            
            # 정당 정보 정리
            if not party:
                party = '무소속'
            
            # 사진 URL 추가
            photo_url = self.photo_mapping.get(name, '')
            if photo_url:
                member['photo_url'] = photo_url
            
            valid_members.append(member)
        
        self.members_data = valid_members
        logger.info(f"의원 데이터 검증 완료: {len(self.members_data)}명")
    
    def get_all_members(self) -> List[Dict]:
        """모든 의원 정보 반환"""
        return self.members_data
    
    def get_member_by_name(self, name: str) -> Optional[Dict]:
        """이름으로 의원 검색"""
        for member in self.members_data:
            if member.get('name') == name:
                return member
        return None
    
    def get_members_by_party(self, party: str) -> List[Dict]:
        """정당별 의원 검색"""
        return [m for m in self.members_data if m.get('party') == party]
    
    def get_members_by_committee(self, committee: str) -> List[Dict]:
        """위원회별 의원 검색"""
        return [m for m in self.members_data 
                if committee in m.get('committee', '')]
    
    def verify_member_info(self, name: str) -> Dict:
        """의원 정보 검증"""
        member = self.get_member_by_name(name)
        if not member:
            return {
                'verified': False,
                'error': '의원을 찾을 수 없습니다'
            }
        
        # 정보 완성도 검증
        completeness = {
            'name': bool(member.get('name')),
            'party': bool(member.get('party')),
            'district': bool(member.get('district')),
            'committee': bool(member.get('committee')),
            'photo': bool(member.get('photo_url') or self.photo_mapping.get(name))
        }
        
        score = sum(completeness.values()) / len(completeness) * 100
        
        return {
            'verified': True,
            'member': member,
            'completeness': completeness,
            'quality_score': score
        }
    
    def get_statistics(self) -> Dict:
        """의원 통계 정보"""
        party_stats = {}
        committee_stats = {}
        
        for member in self.members_data:
            party = member.get('party', '무소속')
            committee = member.get('committee', '')
            
            party_stats[party] = party_stats.get(party, 0) + 1
            
            if committee:
                committees = [c.strip() for c in committee.split(',')]
                for comm in committees:
                    if comm:
                        committee_stats[comm] = committee_stats.get(comm, 0) + 1
        
        return {
            'total_members': len(self.members_data),
            'party_distribution': party_stats,
            'committee_distribution': committee_stats,
            'photo_coverage': len(self.photo_mapping)
        }

# 전역 인스턴스
assembly_api = AssemblyMemberAPI()

if __name__ == "__main__":
    # 테스트
    stats = assembly_api.get_statistics()
    print("국회의원통합API 통계:")
    print(f"총 의원: {stats['total_members']}명")
    print(f"사진 보유: {stats['photo_coverage']}명")
    
    print("\\n정당별 분포:")
    for party, count in sorted(stats['party_distribution'].items(), 
                              key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {party}: {count}명")
