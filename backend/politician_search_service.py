#!/usr/bin/env python3
"""
정치인 전용 검색 서비스
오직 22대 국회의원만 검색 가능한 제한적 검색 시스템
"""

import json
import re
from difflib import SequenceMatcher
import logging

logger = logging.getLogger(__name__)

class PoliticianSearchService:
    def __init__(self):
        self.load_politicians()
        self.create_search_index()
        
    def load_politicians(self):
        """22대 국회의원 목록 로드"""
        try:
            with open('22nd_assembly_members_300.json', 'r', encoding='utf-8') as f:
                members = json.load(f)
            
            self.politicians = {}
            self.politician_names = []
            
            for member in members:
                name = member.get('naas_nm', '')
                if name:
                    self.politicians[name] = member
                    self.politician_names.append(name)
            
            logger.info(f"정치인 검색 DB 구축: {len(self.politicians)}명")
            
        except FileNotFoundError:
            try:
                with open('../22nd_assembly_members_300.json', 'r', encoding='utf-8') as f:
                    members = json.load(f)
                
                self.politicians = {}
                self.politician_names = []
                
                for member in members:
                    name = member.get('naas_nm', '')
                    if name:
                        self.politicians[name] = member
                        self.politician_names.append(name)
                
                logger.info(f"정치인 검색 DB 구축: {len(self.politicians)}명")
                
            except FileNotFoundError:
                self.politicians = {}
                self.politician_names = []
                logger.error("정치인 데이터 파일을 찾을 수 없음")
    
    def create_search_index(self):
        """검색 인덱스 생성"""
        self.search_index = {}
        
        for name, info in self.politicians.items():
            # 기본 이름
            self.add_to_index(name, name, info)
            
            # 성씨만
            if len(name) >= 2:
                surname = name[0]
                self.add_to_index(surname, name, info)
            
            # 이름만 (성 제외)
            if len(name) >= 3:
                given_name = name[1:]
                self.add_to_index(given_name, name, info)
            
            # 정당명 포함 검색
            party = info.get('party_name', '')
            if party:
                party_search = f"{name} {party}"
                self.add_to_index(party_search, name, info)
            
            # 지역구 포함 검색
            district = info.get('district', '')
            if district:
                district_search = f"{name} {district}"
                self.add_to_index(district_search, name, info)
        
        logger.info(f"검색 인덱스 구축: {len(self.search_index)}개 키워드")
    
    def add_to_index(self, keyword, politician_name, politician_info):
        """검색 인덱스에 키워드 추가"""
        keyword_lower = keyword.lower().strip()
        if keyword_lower not in self.search_index:
            self.search_index[keyword_lower] = []
        
        self.search_index[keyword_lower].append({
            'name': politician_name,
            'info': politician_info,
            'match_type': 'exact' if keyword == politician_name else 'partial'
        })
    
    def search_politicians(self, query, max_results=10):
        """정치인 검색 (오직 정치인만)"""
        if not query or len(query.strip()) < 1:
            return {
                'success': False,
                'message': '검색어를 입력해주세요.',
                'results': []
            }
        
        query = query.strip()
        
        # 1단계: 정치인 이름 검증
        if not self.is_valid_politician_query(query):
            return {
                'success': False,
                'message': '정치인 이름만 검색 가능합니다.',
                'suggestion': self.suggest_politicians(query),
                'results': []
            }
        
        # 2단계: 정확한 매칭 검색
        exact_matches = self.find_exact_matches(query)
        
        # 3단계: 유사한 이름 검색
        similar_matches = self.find_similar_matches(query, max_results - len(exact_matches))
        
        # 결과 통합
        all_results = exact_matches + similar_matches
        
        # 중복 제거
        seen_names = set()
        unique_results = []
        for result in all_results:
            if result['name'] not in seen_names:
                unique_results.append(result)
                seen_names.add(result['name'])
        
        return {
            'success': True,
            'query': query,
            'results': unique_results[:max_results],
            'total_found': len(unique_results),
            'search_type': 'politician_only'
        }
    
    def is_valid_politician_query(self, query):
        """정치인 검색어인지 검증"""
        # 금지된 키워드들 (정치인이 아닌 검색어)
        forbidden_keywords = [
            '뉴스', '기사', '법안', '정책', '정부', '국회', '위원회',
            '선거', '투표', '정당', '민주당', '국민의힘', '조국혁신당',
            '발의안', '심사', '통과', '폐기', '국정감사', '본회의',
            '정치', '사건', '사고', '논란', '의혹', '특검', '탄핵'
        ]
        
        query_lower = query.lower()
        
        # 금지된 키워드만으로 구성된 검색어 차단
        if any(keyword in query_lower for keyword in forbidden_keywords):
            # 하지만 정치인 이름이 포함되어 있으면 허용
            if not any(name in query for name in self.politician_names):
                return False
        
        # 한글 이름 패턴 체크 (2-4글자 한글)
        korean_name_pattern = r'^[가-힣]{2,4}(\s+[가-힣]+)*$'
        if re.match(korean_name_pattern, query.strip()):
            return True
        
        # 정치인 이름이 포함된 복합 검색어 허용
        if any(name in query for name in self.politician_names):
            return True
        
        return False
    
    def find_exact_matches(self, query):
        """정확한 매칭 검색"""
        results = []
        query_lower = query.lower().strip()
        
        # 검색 인덱스에서 정확한 매칭 찾기
        if query_lower in self.search_index:
            for match in self.search_index[query_lower]:
                if match['match_type'] == 'exact':
                    results.append({
                        'name': match['name'],
                        'info': match['info'],
                        'match_score': 1.0,
                        'match_type': 'exact'
                    })
        
        # 완전 일치하는 이름 직접 검색
        for name in self.politician_names:
            if name == query:
                if name not in [r['name'] for r in results]:
                    results.append({
                        'name': name,
                        'info': self.politicians[name],
                        'match_score': 1.0,
                        'match_type': 'exact'
                    })
        
        return results
    
    def find_similar_matches(self, query, max_results=5):
        """유사한 이름 검색"""
        results = []
        
        for name in self.politician_names:
            # 문자열 유사도 계산
            similarity = SequenceMatcher(None, query.lower(), name.lower()).ratio()
            
            # 부분 문자열 매칭
            if query.lower() in name.lower() or name.lower() in query.lower():
                similarity = max(similarity, 0.8)
            
            # 초성 매칭 (ㄱㄱㅅ = 강경숙)
            if self.match_initials(query, name):
                similarity = max(similarity, 0.7)
            
            # 유사도 임계값 (0.6 이상)
            if similarity >= 0.6:
                results.append({
                    'name': name,
                    'info': self.politicians[name],
                    'match_score': round(similarity, 3),
                    'match_type': 'similar'
                })
        
        # 유사도 순으로 정렬
        results.sort(key=lambda x: x['match_score'], reverse=True)
        
        return results[:max_results]
    
    def match_initials(self, query, name):
        """초성 매칭 (ㄱㄱㅅ = 강경숙)"""
        # 한글 초성 추출
        initials_map = {
            'ㄱ': ['가', '나'], 'ㄴ': ['나', '다'], 'ㄷ': ['다', '라'], 'ㄹ': ['라', '마'],
            'ㅁ': ['마', '바'], 'ㅂ': ['바', '사'], 'ㅅ': ['사', '아'], 'ㅇ': ['아', '자'],
            'ㅈ': ['자', '차'], 'ㅊ': ['차', '카'], 'ㅋ': ['카', '타'], 'ㅌ': ['타', '파'],
            'ㅍ': ['파', '하'], 'ㅎ': ['하', '힣']
        }
        
        # 간단한 초성 매칭 (정확한 구현은 복잡함)
        if len(query) == len(name) and all(c in 'ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅊㅋㅌㅍㅎ' for c in query):
            return True
        
        return False
    
    def suggest_politicians(self, query):
        """검색어와 유사한 정치인 추천"""
        suggestions = []
        
        for name in self.politician_names:
            # 편집 거리 기반 유사도
            similarity = SequenceMatcher(None, query.lower(), name.lower()).ratio()
            
            if similarity >= 0.3:  # 낮은 임계값으로 추천
                suggestions.append({
                    'name': name,
                    'party': self.politicians[name].get('party_name', '무소속'),
                    'district': self.politicians[name].get('district', ''),
                    'similarity': round(similarity, 3)
                })
        
        # 유사도 순으로 정렬하여 상위 5명 반환
        suggestions.sort(key=lambda x: x['similarity'], reverse=True)
        return suggestions[:5]
    
    def get_all_politicians(self, page=0, per_page=20, party_filter=None):
        """전체 정치인 목록 (페이징)"""
        filtered_politicians = []
        
        for name, info in self.politicians.items():
            if party_filter and info.get('party_name') != party_filter:
                continue
            
            filtered_politicians.append({
                'name': name,
                'party': info.get('party_name', '무소속'),
                'district': info.get('district', ''),
                'committee': info.get('committee', ''),
                'photo_url': info.get('photo_url', ''),
                'terms': info.get('terms', '1')
            })
        
        # 이름순 정렬
        filtered_politicians.sort(key=lambda x: x['name'])
        
        # 페이징
        start_idx = page * per_page
        end_idx = start_idx + per_page
        page_results = filtered_politicians[start_idx:end_idx]
        
        return {
            'success': True,
            'results': page_results,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': len(filtered_politicians),
                'total_pages': (len(filtered_politicians) + per_page - 1) // per_page,
                'has_next': end_idx < len(filtered_politicians),
                'has_prev': page > 0
            }
        }
    
    def get_parties_list(self):
        """정당 목록"""
        parties = set()
        for info in self.politicians.values():
            party = info.get('party_name', '무소속')
            if party:
                parties.add(party)
        
        return sorted(list(parties))
    
    def validate_search_query(self, query):
        """검색어 유효성 검사"""
        if not query or len(query.strip()) < 1:
            return {
                'valid': False,
                'error': '검색어를 입력해주세요.',
                'error_code': 'EMPTY_QUERY'
            }
        
        query = query.strip()
        
        # 길이 제한
        if len(query) > 50:
            return {
                'valid': False,
                'error': '검색어가 너무 깁니다. (최대 50자)',
                'error_code': 'QUERY_TOO_LONG'
            }
        
        # 정치인 이름 형식 검증
        if not self.is_valid_politician_query(query):
            return {
                'valid': False,
                'error': '정치인 이름만 검색 가능합니다.',
                'error_code': 'INVALID_POLITICIAN_QUERY',
                'suggestions': self.suggest_politicians(query)
            }
        
        return {
            'valid': True,
            'normalized_query': query,
            'query_type': 'politician_search'
        }
    
    def get_search_stats(self):
        """검색 통계"""
        return {
            'total_politicians': len(self.politicians),
            'total_parties': len(self.get_parties_list()),
            'search_index_size': len(self.search_index),
            'searchable_keywords': list(self.search_index.keys())[:10]  # 샘플
        }

def main():
    """테스트 실행"""
    search_service = PoliticianSearchService()
    
    print("🔍 정치인 전용 검색 서비스 테스트")
    print(f"📊 검색 가능한 정치인: {len(search_service.politicians)}명")
    
    # 테스트 검색어들
    test_queries = [
        "이재명",           # 정확한 이름
        "이재",             # 부분 이름
        "강경숙",           # 정확한 이름
        "강경",             # 부분 이름
        "뉴스",             # 금지된 키워드
        "정치",             # 금지된 키워드
        "이재명 뉴스",      # 정치인 + 금지 키워드
        "한동",             # 부분 이름
        "조국혁신당",       # 정당명
        ""                  # 빈 검색어
    ]
    
    for query in test_queries:
        print(f"\n검색어: '{query}'")
        
        # 1. 유효성 검사
        validation = search_service.validate_search_query(query)
        if not validation['valid']:
            print(f"❌ 유효성 검사 실패: {validation['error']}")
            if 'suggestions' in validation:
                suggestions = validation['suggestions'][:3]
                if suggestions:
                    print(f"💡 추천: {', '.join([s['name'] for s in suggestions])}")
            continue
        
        # 2. 검색 실행
        results = search_service.search_politicians(query)
        if results['success']:
            print(f"✅ 검색 성공: {len(results['results'])}명")
            for i, result in enumerate(results['results'][:3]):
                print(f"  {i+1}. {result['name']} ({result['info'].get('party_name', '무소속')}) - 매칭도: {result['match_score']}")
        else:
            print(f"❌ 검색 실패: {results['message']}")

if __name__ == "__main__":
    main()
