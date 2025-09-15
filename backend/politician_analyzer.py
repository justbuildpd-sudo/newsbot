#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
정치인 언급 분석기
뉴스 데이터에서 정치인 언급을 분석하고 영향력을 평가합니다.
"""

import re
from typing import List, Dict, Tuple, Optional
from collections import defaultdict, Counter
from politician_service import politician_service
from assembly_api_service import AssemblyAPIService

class PoliticianAnalyzer:
    def __init__(self):
        self.politician_service = politician_service
        self.assembly_api = None  # 지연 초기화
        self.politicians = []
        self.name_mapping = {}
        self.mention_counts = defaultdict(int)
        self.mention_history = []
        self._initialized = False
    
    def reset_cache(self):
        """캐시 초기화"""
        self._initialized = False
        self.politicians = []
        self.name_mapping = {}
        self.mention_counts = defaultdict(int)
        self.mention_history = []
        print("🔄 정치인 분석기 캐시 초기화 완료")
        
    def _ensure_initialized(self):
        """필요할 때만 초기화 (국회의원 API 데이터 직접 사용)"""
        if not self._initialized:
            print("🔧 정치인 분석기 초기화 중...")
            
            # 국회의원 API를 직접 사용 (실시간 데이터 + 정당 정보)
            if not self.assembly_api:
                self.assembly_api = AssemblyAPIService()
            
            try:
                # 국회의원 API에서 완전한 데이터 가져오기 (정당 정보 포함)
                self.politicians = self.assembly_api.get_member_list()
                print(f"✅ 국회의원 API에서 {len(self.politicians)}명 로드 (정당 정보 포함)")
                
                # 정당 정보가 있는지 확인
                party_count = sum(1 for p in self.politicians if p.get('party'))
                print(f"📊 정당 정보 포함: {party_count}/{len(self.politicians)}명")
                
                # 샘플 데이터 확인
                if self.politicians:
                    sample = self.politicians[0]
                    print(f"🔍 샘플 데이터: {sample.get('name')} - {sample.get('party')} - {sample.get('district')}")
                
                # 정당 정보가 없으면 오류
                if party_count == 0:
                    print("❌ 정당 정보가 없습니다. API 데이터를 확인하세요.")
                    raise Exception("정당 정보가 없습니다")
                
            except Exception as e:
                print(f"⚠️ 국회의원 API 실패: {e}")
                # API 실패 시 JSON 파일에서 직접 로드
                self.politicians = self._load_politicians_from_json()
                print(f"✅ JSON 파일에서 {len(self.politicians)}명 로드")
            
            if not self.politicians:
                print("❌ 정치인 데이터를 로드할 수 없습니다.")
                return
            
            # 정치인 이름 매핑 (한자명, 별명 포함)
            self.name_mapping = self._build_name_mapping()
            self._initialized = True
            print(f"✅ 정치인 분석기 초기화 완료: {len(self.politicians)}명, 매핑 {len(self.name_mapping)}개")
    
    def _load_politicians_from_json(self) -> List[Dict]:
        """JSON 파일에서 정치인 데이터 직접 로드"""
        try:
            import json
            import os
            
            # processed_assembly_members.json 파일 사용
            json_file = os.path.join(os.path.dirname(__file__), 'processed_assembly_members.json')
            if os.path.exists(json_file):
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data if isinstance(data, list) else []
            
            # real_assembly_members.json 파일 사용
            json_file = os.path.join(os.path.dirname(__file__), 'real_assembly_members.json')
            if os.path.exists(json_file):
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data if isinstance(data, list) else []
            
            return []
        except Exception as e:
            print(f"❌ JSON 파일 로드 실패: {e}")
            return []
    
    def _build_name_mapping(self) -> Dict[str, Dict]:
        """정치인 이름 매핑을 구축합니다 (이름 -> 정치인 객체)"""
        name_map = {}
        
        for politician in self.politicians:
            name = politician['name']
            hanja_name = politician.get('name_hanja', '')
            english_name = politician.get('name_english', '')
            party = politician.get('party', '')
            
            # 기본 이름 매핑 (정치인 객체 자체를 저장)
            name_map[name] = politician
            
            # 한자명 매핑
            if hanja_name:
                name_map[hanja_name] = politician
            
            # 영문명 매핑
            if english_name:
                name_map[english_name] = politician
            
            # 정당 + 이름 조합 매핑
            if party and name:
                name_map[f"{party} {name}"] = politician
                name_map[f"{name} {party}"] = politician
        
        return name_map
    
    def analyze_news_mentions(self, news_items: List[Dict]) -> List[Dict]:
        """뉴스 아이템들에서 정치인 언급을 분석합니다."""
        self._ensure_initialized()
        mention_counts = defaultdict(int)
        mention_details = defaultdict(list)
        
        for news_item in news_items:
            title = news_item.get('title', '')
            description = news_item.get('description', '')
            content = news_item.get('content', '')
            
            # 제목, 설명, 내용을 합쳐서 분석
            full_text = f"{title} {description} {content}"
            
            # 이름 매핑을 사용하여 더 정확한 매칭
            for name_pattern, politician in self.name_mapping.items():
                if self._check_mention(full_text, name_pattern):
                    politician_name = politician['name']
                    mention_counts[politician_name] += 1
                    mention_details[politician_name].append({
                        'news_title': title,
                        'news_id': news_item.get('id', 0),
                        'mention_type': self._get_mention_type(name_pattern, politician),
                        'matched_pattern': name_pattern
                    })
        
        # 언급 수가 있는 정치인들만 필터링
        mentioned_politicians = []
        for politician_name, count in mention_counts.items():
            if count > 0:
                # name_mapping에서 직접 정치인 객체 가져오기
                politician = self.name_mapping.get(politician_name)
                
                if politician:
                    mentioned_politicians.append({
                        'id': politician.get('id', politician.get('member_number', '')),
                        'name': politician['name'],
                        'party': politician.get('party', ''),
                        'district': politician.get('district', ''),
                        'committee': politician.get('committee', ''),
                        'mention_count': count,
                        'mention_details': mention_details[politician_name],
                        'influence_score': self._calculate_influence_score(count, politician)
                    })
        
        # 언급 수 기준으로 정렬 (내림차순)
        mentioned_politicians.sort(key=lambda x: x['mention_count'], reverse=True)
        
        return mentioned_politicians
    
    def get_news_with_politicians(self, news_items: List[Dict]) -> List[Dict]:
        """뉴스별로 언급된 정치인 정보를 포함하여 반환합니다."""
        self._ensure_initialized()
        news_with_politicians = []
        
        # 로깅 최적화 - 너무 자주 출력하지 않음
        if len(news_items) > 0:
            print(f"🔍 뉴스 {len(news_items)}개에서 정치인 매칭 시작")
        
        for news_item in news_items:
            title = news_item.get('title', '')
            description = news_item.get('description', '')
            content = news_item.get('content', '')
            
            # 제목, 설명, 내용을 합쳐서 분석
            full_text = f"{title} {description} {content}"
            
            # 이 뉴스에 언급된 정치인들 찾기
            mentioned_politicians = []
            for name_pattern, politician in self.name_mapping.items():
                if self._check_mention(full_text, name_pattern):
                    politician_id = politician.get('id', politician.get('member_number', ''))
                    mentioned_politicians.append({
                        'id': politician_id,
                        'name': politician['name'],
                        'party': politician.get('party', ''),
                        'district': politician.get('district', ''),
                        'committee': politician.get('committee', ''),
                        'mention_type': self._get_mention_type(name_pattern, politician),
                        'matched_pattern': name_pattern
                    })
                    # 매칭 로그 최적화 - 중요한 매칭만 출력
                    if len(name_pattern) > 2:  # 2글자 이상인 경우만
                        print(f"✅ 매칭됨: {name_pattern} -> {politician['name']}")
            
            # 뉴스 정보에 정치인 정보 추가
            news_with_politicians.append({
                **news_item,
                'mentioned_politicians': mentioned_politicians,
                'politician_count': len(mentioned_politicians)
            })
        
        print(f"📊 매칭 완료: {len(news_with_politicians)}개 뉴스 중 {sum(1 for n in news_with_politicians if n['politician_count'] > 0)}개에 정치인 언급")
        return news_with_politicians
    
    def _check_mention(self, text: str, name: str) -> bool:
        """텍스트에서 특정 이름이 언급되었는지 확인합니다."""
        if not name or not text:
            return False
        
        # 정확한 이름 매칭 (단어 경계 고려)
        import re
        pattern = r'\b' + re.escape(name) + r'\b'
        if re.search(pattern, text):
            return True
        
        # 부분 매칭 (2글자 이상인 경우, 단어 경계 고려)
        if len(name) >= 2:
            pattern = r'\b' + re.escape(name) + r'\b'
            return bool(re.search(pattern, text))
        
        return False
    
    def _get_politician_by_id(self, politician_id: str) -> Optional[Dict]:
        """ID로 정치인을 찾습니다."""
        for politician in self.politicians:
            if politician.get('id') == politician_id or politician.get('member_number') == politician_id:
                return politician
        return None
    
    def _get_mention_type(self, matched_pattern: str, politician: Dict) -> str:
        """매칭된 패턴의 타입을 반환합니다."""
        if not politician:
            return 'unknown'
        
        name = politician['name']
        hanja_name = politician.get('name_hanja', '')
        english_name = politician.get('name_english', '')
        party = politician.get('party', '')
        
        if matched_pattern == name:
            return 'name'
        elif matched_pattern == hanja_name:
            return 'hanja'
        elif matched_pattern == english_name:
            return 'english'
        elif matched_pattern in [f"{party} {name}", f"{name} {party}"]:
            return 'party_name'
        else:
            return 'other'
    
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
    
    # 랭킹 관련 메서드 제거됨 - 의미 없는 기능

# 전역 인스턴스
politician_analyzer = PoliticianAnalyzer()
