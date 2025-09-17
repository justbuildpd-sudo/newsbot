#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
데이터 로더 유틸리티
"""

import json
import os
from typing import List, Dict, Optional

class DataLoader:
    def __init__(self, data_file: str = "politicians_data_with_party.json"):
        self.data_file = data_file
        self.data = []
        self.load_data()
    
    def load_data(self):
        """데이터 로드"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                print(f"✅ 데이터 로드 완료: {len(self.data)}명")
            else:
                print(f"❌ 데이터 파일을 찾을 수 없습니다: {self.data_file}")
                self.data = []
        except Exception as e:
            print(f"❌ 데이터 로드 실패: {e}")
            self.data = []
    
    def get_all_politicians(self) -> List[Dict]:
        """모든 국회의원 정보 반환"""
        return self.data
    
    def get_politician_by_id(self, member_id: str) -> Optional[Dict]:
        """ID로 특정 국회의원 정보 조회"""
        for politician in self.data:
            if politician.get('id') == member_id or politician.get('member_number') == member_id:
                return politician
        return None
    
    def get_politicians_by_party(self, party_name: str) -> List[Dict]:
        """정당별 국회의원 조회"""
        results = []
        for politician in self.data:
            if politician.get('party', '').lower() == party_name.lower():
                results.append(politician)
        return results
    
    def search_politicians(self, query: str) -> List[Dict]:
        """이름으로 국회의원 검색"""
        results = []
        query_lower = query.lower()
        
        for politician in self.data:
            name = politician.get('name', '').lower()
            if query_lower in name:
                results.append(politician)
        
        return results
    
    def get_stats(self) -> Dict:
        """통계 정보"""
        total_count = len(self.data)
        
        # 정당별 통계
        party_stats = {}
        for politician in self.data:
            party = politician.get('party', '정당정보없음')
            party_stats[party] = party_stats.get(party, 0) + 1
        
        return {
            'total_politicians': total_count,
            'party_distribution': party_stats,
            'data_source': 'local_json'
        }
