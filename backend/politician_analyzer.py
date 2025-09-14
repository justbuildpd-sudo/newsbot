#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
정치인 언급 분석기
뉴스 데이터에서 정치인 언급을 분석하고 영향력을 평가합니다.
"""

import re
from typing import List, Dict, Tuple
from collections import defaultdict, Counter
from politician_service import politician_service

class PoliticianAnalyzer:
    def __init__(self):
        self.politician_service = politician_service
        self.politicians = politician_service.get_all_politicians()
        
        # 정치인 이름 매핑 (한자명, 별명 포함)
        self.name_mapping = self._build_name_mapping()
        
        # 정치인별 언급 카운터
        self.mention_counts = defaultdict(int)
        self.mention_history = []
    
    def _build_name_mapping(self) -> Dict[str, int]:
        """정치인 이름 매핑을 구축합니다."""
        name_map = {}
        
        for politician in self.politicians:
            politician_id = politician['id']
            name = politician['name']
            hanja_name = politician.get('name_hanja', '')
            
            # 기본 이름
            name_map[name] = politician_id
            
            # 한자명
            if hanja_name:
                name_map[hanja_name] = politician_id
            
            # 성만으로도 매핑 (김, 이, 박 등)
            surname = name[0]
            if surname not in name_map:
                name_map[surname] = politician_id
            
            # 지역구 정보로도 매핑
            district = politician.get('district', '')
            if district:
                # "경기 안양시만안구" -> "안양시만안구", "안양시", "만안구"
                district_parts = district.split()
                for part in district_parts:
                    if len(part) > 2:  # 2글자 이상인 경우만
                        name_map[part] = politician_id
        
        return name_map
    
    def analyze_news_mentions(self, news_items: List[Dict]) -> List[Dict]:
        """뉴스 아이템들에서 정치인 언급을 분석합니다."""
        mention_counts = defaultdict(int)
        mention_details = defaultdict(list)
        
        for news_item in news_items:
            title = news_item.get('title', '')
            description = news_item.get('description', '')
            content = news_item.get('content', '')
            
            # 제목, 설명, 내용을 합쳐서 분석
            full_text = f"{title} {description} {content}"
            
            # 각 정치인에 대해 언급 확인
            for politician in self.politicians:
                politician_id = politician['id']
                name = politician['name']
                hanja_name = politician.get('name_hanja', '')
                
                # 이름으로 언급 확인
                if self._check_mention(full_text, name):
                    mention_counts[politician_id] += 1
                    mention_details[politician_id].append({
                        'news_title': title,
                        'news_id': news_item.get('id', 0),
                        'mention_type': 'name'
                    })
                
                # 한자명으로 언급 확인
                if hanja_name and self._check_mention(full_text, hanja_name):
                    mention_counts[politician_id] += 1
                    mention_details[politician_id].append({
                        'news_title': title,
                        'news_id': news_item.get('id', 0),
                        'mention_type': 'hanja'
                    })
        
        # 언급 수가 있는 정치인들만 필터링
        mentioned_politicians = []
        for politician_id, count in mention_counts.items():
            if count > 0:
                politician = self.politician_service.get_politician_by_id(politician_id)
                if politician:
                    mentioned_politicians.append({
                        'id': politician_id,
                        'name': politician['name'],
                        'party': politician['party'],
                        'district': politician['district'],
                        'committee': politician['committee'],
                        'mention_count': count,
                        'mention_details': mention_details[politician_id],
                        'influence_score': self._calculate_influence_score(count, politician)
                    })
        
        # 언급 수 기준으로 정렬 (내림차순)
        mentioned_politicians.sort(key=lambda x: x['mention_count'], reverse=True)
        
        return mentioned_politicians
    
    def _check_mention(self, text: str, name: str) -> bool:
        """텍스트에서 특정 이름이 언급되었는지 확인합니다."""
        if not name or not text:
            return False
        
        # 정확한 이름 매칭
        if name in text:
            return True
        
        # 부분 매칭 (2글자 이상인 경우)
        if len(name) >= 2:
            return name in text
        
        return False
    
    def _calculate_influence_score(self, mention_count: int, politician: Dict) -> float:
        """정치인의 영향력 점수를 계산합니다."""
        base_score = mention_count * 10
        
        # 정당별 가중치
        party_weights = {
            '더불어민주당': 1.2,
            '국민의힘': 1.2,
            '조국혁신당': 1.0,
            '개혁신당': 1.0,
            '무소속': 0.8
        }
        
        party = politician.get('party', '무소속')
        party_weight = party_weights.get(party, 1.0)
        
        # 위원회별 가중치
        committee = politician.get('committee', '')
        committee_weight = 1.0
        if '기획재정위원회' in committee:
            committee_weight = 1.3
        elif '외교통일위원회' in committee:
            committee_weight = 1.2
        elif '환경노동위원회' in committee:
            committee_weight = 1.1
        
        # 선거구수별 가중치
        terms = politician.get('terms', '')
        if '5선' in terms or '6선' in terms:
            terms_weight = 1.2
        elif '3선' in terms or '4선' in terms:
            terms_weight = 1.1
        else:
            terms_weight = 1.0
        
        final_score = base_score * party_weight * committee_weight * terms_weight
        return round(final_score, 2)
    
    def get_top_politicians(self, news_items: List[Dict], limit: int = 8) -> List[Dict]:
        """뉴스에서 언급된 상위 정치인들을 반환합니다."""
        mentioned_politicians = self.analyze_news_mentions(news_items)
        return mentioned_politicians[:limit]
    
    def get_politician_ranking_stats(self) -> Dict:
        """정치인 랭킹 통계를 반환합니다."""
        return {
            'total_politicians': len(self.politicians),
            'mentioned_politicians': len(self.mention_history),
            'last_analysis': len(self.mention_history) > 0
        }

# 전역 인스턴스
politician_analyzer = PoliticianAnalyzer()
