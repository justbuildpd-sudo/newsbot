#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
정치인 데이터 서비스
22대 국회의원 정보를 관리합니다.
"""

import json
import os
from typing import List, Dict, Optional
from datetime import datetime
from database import db

class PoliticianService:
    def __init__(self):
        self.politicians = []
        self.load_politicians()
    
    def load_politicians(self):
        """정치인 데이터를 데이터베이스에서 로드합니다."""
        try:
            # 데이터베이스에서 정치인 데이터 조회
            self.politicians = db.get_politicians(limit=1000)
            
            if not self.politicians:
                # 데이터베이스가 비어있으면 JSON 파일에서 로드하여 삽입
                self.load_from_json_and_insert()
                self.politicians = db.get_politicians(limit=1000)
            
            print(f"✅ 정치인 데이터 로드 완료: {len(self.politicians)}명")
        except Exception as e:
            print(f"❌ 정치인 데이터 로드 오류: {e}")
            self.politicians = []
    
    def load_from_json_and_insert(self):
        """JSON 파일에서 데이터를 로드하여 데이터베이스에 삽입합니다."""
        try:
            data_file = os.path.join(os.path.dirname(__file__), 'data', 'assembly_members_22nd_verified.json')
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                politicians = data.get('members', [])
                
                # 데이터베이스에 삽입
                db.insert_politicians(politicians)
                print(f"✅ JSON에서 {len(politicians)}명의 정치인 데이터를 데이터베이스에 삽입했습니다")
        except Exception as e:
            print(f"❌ JSON 데이터 로드 및 삽입 오류: {e}")
    
    def get_all_politicians(self) -> List[Dict]:
        """모든 정치인 정보를 반환합니다."""
        return self.politicians
    
    def get_politician_by_id(self, politician_id: int) -> Optional[Dict]:
        """ID로 특정 정치인 정보를 반환합니다."""
        for politician in self.politicians:
            if politician.get('id') == politician_id:
                return politician
        return None
    
    def get_politicians_by_party(self, party: str) -> List[Dict]:
        """정당별 정치인 목록을 반환합니다."""
        return [p for p in self.politicians if p.get('party') == party]
    
    def get_politicians_by_committee(self, committee: str) -> List[Dict]:
        """위원회별 정치인 목록을 반환합니다."""
        return [p for p in self.politicians if committee in p.get('committee', '')]
    
    def get_politicians_by_orientation(self, orientation: str) -> List[Dict]:
        """정치성향별 정치인 목록을 반환합니다."""
        return [p for p in self.politicians if p.get('political_orientation') == orientation]
    
    def search_politicians(self, query: str) -> List[Dict]:
        """이름, 지역구, 정당으로 정치인을 검색합니다."""
        query = query.lower()
        results = []
        
        for politician in self.politicians:
            # 이름 검색
            if query in politician.get('name', '').lower():
                results.append(politician)
                continue
            
            # 지역구 검색
            if query in politician.get('district', '').lower():
                results.append(politician)
                continue
            
            # 정당 검색
            if query in politician.get('party', '').lower():
                results.append(politician)
                continue
            
            # 위원회 검색
            if query in politician.get('committee', '').lower():
                results.append(politician)
                continue
        
        return results
    
    def get_party_statistics(self) -> Dict:
        """정당별 통계를 반환합니다."""
        stats = {}
        for politician in self.politicians:
            party = politician.get('party', '무소속')
            stats[party] = stats.get(party, 0) + 1
        return stats
    
    def get_committee_statistics(self) -> Dict:
        """위원회별 통계를 반환합니다."""
        stats = {}
        for politician in self.politicians:
            committees = politician.get('committee', '').split(', ')
            for committee in committees:
                if committee.strip():
                    stats[committee.strip()] = stats.get(committee.strip(), 0) + 1
        return stats
    
    def get_orientation_statistics(self) -> Dict:
        """정치성향별 통계를 반환합니다."""
        stats = {}
        for politician in self.politicians:
            orientation = politician.get('political_orientation', '미분류')
            stats[orientation] = stats.get(orientation, 0) + 1
        return stats
    
    def get_featured_politicians(self, limit: int = 6) -> List[Dict]:
        """주요 정치인 목록을 반환합니다 (다양한 정당과 위원회에서 선별)."""
        featured = []
        
        # 정당별로 대표 의원 선별
        parties = list(set(p.get('party') for p in self.politicians))
        
        for party in parties[:3]:  # 상위 3개 정당
            party_members = self.get_politicians_by_party(party)
            if party_members:
                # 각 정당에서 2명씩 선별
                featured.extend(party_members[:2])
        
        return featured[:limit]
    
    def get_politician_summary(self) -> Dict:
        """정치인 데이터 요약 정보를 반환합니다."""
        if not self.politicians:
            return {
                "total_count": 0,
                "parties": {},
                "committees": {},
                "orientations": {}
            }
        
        return {
            "total_count": len(self.politicians),
            "parties": self.get_party_statistics(),
            "committees": self.get_committee_statistics(),
            "orientations": self.get_orientation_statistics(),
            "last_updated": datetime.now().isoformat()
        }

# 전역 인스턴스
politician_service = PoliticianService()
