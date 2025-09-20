#!/usr/bin/env python3
"""
개선된 정책선거문화 텍스트마이닝 시스템
konlpy 없이도 작동하는 기본 텍스트 분석 + 지역별 미생토픽 추출
"""

import os
import json
import logging
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import re
import fitz  # PyMuPDF for PDF processing
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud

logger = logging.getLogger(__name__)

class EnhancedPolicyTextMiningSystem:
    """개선된 정책 텍스트마이닝 시스템"""
    
    def __init__(self):
        self.base_dir = "/Users/hopidaay/newsbot-kr"
        self.backend_dir = "/Users/hopidaay/newsbot-kr/backend"
        self.pdf_file = "/Users/hopidaay/Desktop/231215_정책선거문화_확산을_위한_언론기사_빅데이터_분석.pdf"
        
        # 분석 결과 저장 디렉토리
        self.output_dir = os.path.join(self.backend_dir, "enhanced_policy_analysis")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 미생토픽 카테고리 (확장)
        self.misaeng_topics = {
            '경제정책': {
                'keywords': ['일자리', '취업', '창업', '경제성장', '소득', '임금', '고용', '실업', '경제활동', '사업', '투자', '금융'],
                'description': '일자리 창출, 경제 활성화, 소득 증대'
            },
            '주거정책': {
                'keywords': ['주택', '부동산', '임대', '전세', '월세', '아파트', '집값', '주거', '분양', '매매', '주택공급'],
                'description': '주택 공급, 부동산 안정화, 주거 복지'
            },
            '교육정책': {
                'keywords': ['교육', '학교', '대학', '입시', '사교육', '교육비', '학습', '학생', '교사', '교육과정', '학원'],
                'description': '교육 환경 개선, 사교육 부담 해소'
            },
            '복지정책': {
                'keywords': ['복지', '의료', '건강보험', '연금', '육아', '보육', '사회보장', '복지혜택', '지원금', '돌봄'],
                'description': '사회복지 확충, 의료 서비스 개선'
            },
            '환경정책': {
                'keywords': ['환경', '기후', '에너지', '미세먼지', '재생에너지', '친환경', '탄소', '오염', '녹색', '지속가능'],
                'description': '환경 보호, 지속가능한 발전'
            },
            '교통정책': {
                'keywords': ['교통', '대중교통', '지하철', '버스', '도로', '주차', '교통체증', '이동', '접근성', '인프라'],
                'description': '교통 인프라 개선, 대중교통 확충'
            },
            '문화정책': {
                'keywords': ['문화', '예술', '체육', '관광', '축제', '공연', '문화시설', '여가', '스포츠', '콘텐츠'],
                'description': '문화 시설 확충, 관광 산업 발전'
            },
            '안전정책': {
                'keywords': ['안전', '치안', '재해', '방범', '소방', '응급', '범죄', '사고', '위험', '보안'],
                'description': '안전한 생활 환경 조성'
            }
        }
        
        # 지역 계층 구조
        self.region_hierarchy = {
            '광역시도': {
                '서울': '서울특별시',
                '부산': '부산광역시',
                '대구': '대구광역시',
                '인천': '인천광역시',
                '광주': '광주광역시',
                '대전': '대전광역시',
                '울산': '울산광역시',
                '세종': '세종특별자치시',
                '경기': '경기도',
                '강원': '강원도',
                '충북': '충청북도',
                '충남': '충청남도',
                '전북': '전라북도',
                '전남': '전라남도',
                '경북': '경상북도',
                '경남': '경상남도',
                '제주': '제주특별자치도'
            }
        }
        
        # 분석 결과
        self.analysis_results = {
            'document_info': {},
            'regional_misaeng_topics': {},
            'topic_interpretations': {},
            'policy_promises': {},
            'hierarchical_data': {},
            'visualization_ready_data': {}
        }

    def extract_pdf_content(self) -> str:
        """PDF 내용 추출"""
        try:
            print("📄 PDF 파일 내용 추출 중...")
            
            if not os.path.exists(self.pdf_file):
                raise FileNotFoundError(f"PDF 파일을 찾을 수 없습니다: {self.pdf_file}")
            
            doc = fitz.open(self.pdf_file)
            full_text = ""
            total_pages = len(doc)
            
            print(f"📊 총 {total_pages} 페이지 처리 중...")
            
            for page_num in range(total_pages):
                page = doc[page_num]
                page_text = page.get_text()
                full_text += page_text + '\n'
                
                if page_num % 50 == 0:
                    print(f"  📄 페이지 {page_num + 1}/{total_pages} 처리 완료")
            
            doc.close()
            
            self.analysis_results['document_info'] = {
                'file_path': self.pdf_file,
                'total_pages': total_pages,
                'total_text_length': len(full_text),
                'extraction_date': datetime.now().isoformat()
            }
            
            print(f"✅ PDF 추출 완료: {len(full_text):,} 문자")
            return full_text
            
        except Exception as e:
            logger.error(f"❌ PDF 추출 실패: {e}")
            return ""

    def basic_korean_tokenizer(self, text: str) -> List[str]:
        """기본 한국어 토큰화 (konlpy 없이)"""
        try:
            # 텍스트 정제
            text = re.sub(r'[^\w\s가-힣]', ' ', text)
            text = re.sub(r'\s+', ' ', text)
            text = text.strip()
            
            # 기본 토큰화 (공백 기준)
            tokens = text.split()
            
            # 한글 토큰만 필터링 (2글자 이상)
            korean_tokens = []
            for token in tokens:
                if re.search(r'[가-힣]{2,}', token):
                    korean_tokens.append(token)
            
            # 불용어 제거
            stopwords = {'그리고', '하지만', '그러나', '따라서', '이를', '이에', '대한', '위한', '통해', '있다', '없다', '된다', '한다', '이다', '것이다', '수있다'}
            filtered_tokens = [token for token in korean_tokens if token not in stopwords]
            
            return filtered_tokens[:100]  # 상위 100개 토큰만
            
        except Exception as e:
            logger.error(f"❌ 토큰화 실패: {e}")
            return []

    def extract_regional_misaeng_topics(self, full_text: str) -> Dict[str, Any]:
        """지역별 미생토픽 추출"""
        try:
            print("🗺️ 지역별 미생토픽 추출 중...")
            
            regional_topics = {}
            
            # 1. 광역시도별 분석
            print("  📍 광역시도 분석 중...")
            for region_short, region_full in self.region_hierarchy['광역시도'].items():
                region_data = self._analyze_region_topics(full_text, region_short, region_full, '광역시도')
                if region_data['mention_count'] > 0:
                    regional_topics[region_short] = region_data
            
            # 2. 주요 시군구 분석 (상위 언급)
            print("  📍 주요 시군구 분석 중...")
            sigungu_pattern = r'(\w{1,4}[시군구])'
            sigungu_matches = re.findall(sigungu_pattern, full_text)
            sigungu_counter = Counter(sigungu_matches)
            
            for sigungu, count in sigungu_counter.most_common(20):  # 상위 20개
                if count > 5:  # 5회 이상 언급된 곳만
                    region_data = self._analyze_region_topics(full_text, sigungu, sigungu, '시군구')
                    regional_topics[f"{sigungu}"] = region_data
            
            # 3. 주요 읍면동 분석
            print("  📍 주요 읍면동 분석 중...")
            emd_pattern = r'(\w{1,4}[읍면동])'
            emd_matches = re.findall(emd_pattern, full_text)
            emd_counter = Counter(emd_matches)
            
            for emd, count in emd_counter.most_common(30):  # 상위 30개
                if count > 3:  # 3회 이상 언급된 곳만
                    region_data = self._analyze_region_topics(full_text, emd, emd, '읍면동')
                    regional_topics[f"{emd}"] = region_data
            
            self.analysis_results['regional_misaeng_topics'] = regional_topics
            
            print(f"✅ 지역별 미생토픽 추출 완료: {len(regional_topics)}개 지역")
            return regional_topics
            
        except Exception as e:
            logger.error(f"❌ 지역별 토픽 추출 실패: {e}")
            return {}

    def _analyze_region_topics(self, full_text: str, region_key: str, region_name: str, level: str) -> Dict[str, Any]:
        """개별 지역의 토픽 분석"""
        try:
            # 해당 지역 관련 문장 추출
            region_sentences = []
            for sentence in full_text.split('.'):
                if region_key in sentence or region_name in sentence:
                    clean_sentence = sentence.strip()
                    if len(clean_sentence) > 10:
                        region_sentences.append(clean_sentence)
            
            if not region_sentences:
                return {
                    'region': region_name,
                    'level': level,
                    'mention_count': 0,
                    'dominant_topics': [],
                    'topic_scores': {},
                    'sentences': [],
                    'tokens': [],
                    'promises': []
                }
            
            # 지역 관련 텍스트 결합
            region_text = ' '.join(region_sentences)
            
            # 토큰화
            tokens = self.basic_korean_tokenizer(region_text)
            
            # 미생토픽별 점수 계산
            topic_scores = {}
            for topic, topic_info in self.misaeng_topics.items():
                score = 0
                keywords = topic_info['keywords']
                for token in tokens:
                    for keyword in keywords:
                        if keyword in token or token in keyword:
                            score += 1
                
                if score > 0:
                    topic_scores[topic] = score
            
            # 상위 토픽 정렬
            sorted_topics = sorted(topic_scores.items(), key=lambda x: x[1], reverse=True)
            dominant_topics = [topic for topic, score in sorted_topics[:3]]  # 상위 3개
            
            # 공약성 표현 추출
            promises = self._extract_promises_from_sentences(region_sentences)
            
            return {
                'region': region_name,
                'level': level,
                'mention_count': len(region_sentences),
                'dominant_topics': dominant_topics,
                'topic_scores': topic_scores,
                'sentences': region_sentences[:5],  # 상위 5개 문장
                'tokens': tokens[:20],  # 상위 20개 토큰
                'promises': promises
            }
            
        except Exception as e:
            logger.error(f"❌ 지역 {region_name} 분석 실패: {e}")
            return {}

    def _extract_promises_from_sentences(self, sentences: List[str]) -> List[str]:
        """문장에서 공약성 표현 추출"""
        promises = []
        
        # 공약 관련 패턴
        promise_patterns = [
            r'(\w+을/를?\s*(?:확대|강화|개선|지원|추진|도입|실시|시행))',
            r'(\w+\s*(?:정책|사업|프로그램|제도|계획)을/를?\s*(?:마련|수립|추진|실행))',
            r'(\w+을/를?\s*위한\s*\w+)',
            r'(\w+\s*(?:조성|건설|설치|구축|확충))',
            r'(\w+에\s*대한\s*\w+\s*(?:강화|개선|확대))'
        ]
        
        for sentence in sentences:
            for pattern in promise_patterns:
                matches = re.findall(pattern, sentence)
                for match in matches:
                    clean_match = match.strip()
                    if len(clean_match) > 3 and clean_match not in promises:
                        promises.append(clean_match)
        
        return promises[:5]  # 상위 5개

    def interpret_regional_topics(self, regional_topics: Dict[str, Any]) -> Dict[str, Any]:
        """지역별 토픽 해석"""
        try:
            print("🎯 지역별 토픽 해석 중...")
            
            interpretations = {}
            
            for region, data in regional_topics.items():
                if data['mention_count'] > 0:
                    interpretation = self._generate_region_interpretation(region, data)
                    interpretations[region] = interpretation
            
            self.analysis_results['topic_interpretations'] = interpretations
            
            print(f"✅ 토픽 해석 완료: {len(interpretations)}개 지역")
            return interpretations
            
        except Exception as e:
            logger.error(f"❌ 토픽 해석 실패: {e}")
            return {}

    def _generate_region_interpretation(self, region: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """개별 지역 해석 생성"""
        try:
            dominant_topics = data['dominant_topics']
            topic_scores = data['topic_scores']
            level = data['level']
            mention_count = data['mention_count']
            promises = data['promises']
            
            # 기본 해석 생성
            if dominant_topics:
                main_topic = dominant_topics[0]
                topic_description = self.misaeng_topics[main_topic]['description']
                
                interpretation = f"{region}은 {main_topic} 분야가 주요 관심사로, {topic_description}에 대한 논의가 활발함"
                
                # 추가 토픽들
                if len(dominant_topics) > 1:
                    additional_topics = ', '.join(dominant_topics[1:])
                    interpretation += f". 또한 {additional_topics} 분야도 함께 주목받고 있음"
            else:
                interpretation = f"{region}에 대한 정책적 논의가 진행되고 있으나 특정 분야에 집중되지는 않음"
            
            # 공약 요약
            promise_summary = ""
            if promises:
                promise_summary = f"주요 공약: {', '.join(promises)}"
            
            return {
                'region': region,
                'level': level,
                'main_interpretation': interpretation,
                'dominant_topics': dominant_topics,
                'topic_scores': topic_scores,
                'mention_count': mention_count,
                'promise_summary': promise_summary,
                'promises': promises,
                'confidence_score': sum(topic_scores.values()) if topic_scores else 0
            }
            
        except Exception as e:
            logger.error(f"❌ 지역 {region} 해석 생성 실패: {e}")
            return {}

    def create_hierarchical_data(self, regional_topics: Dict[str, Any]) -> Dict[str, Any]:
        """계층적 지역 데이터 생성"""
        try:
            print("🏗️ 계층적 지역 데이터 생성 중...")
            
            hierarchical_data = {
                '광역시도': [],
                '시군구': [],
                '읍면동': []
            }
            
            for region, data in regional_topics.items():
                level = data.get('level', '기타')
                
                if level in hierarchical_data:
                    hierarchical_data[level].append({
                        'region': region,
                        'mention_count': data['mention_count'],
                        'dominant_topics': data['dominant_topics'][:3],
                        'confidence_score': sum(data['topic_scores'].values()) if data['topic_scores'] else 0
                    })
            
            # 각 레벨별로 언급 횟수 순으로 정렬
            for level in hierarchical_data:
                hierarchical_data[level].sort(key=lambda x: x['mention_count'], reverse=True)
            
            self.analysis_results['hierarchical_data'] = hierarchical_data
            
            print(f"✅ 계층적 데이터 생성 완료")
            return hierarchical_data
            
        except Exception as e:
            logger.error(f"❌ 계층적 데이터 생성 실패: {e}")
            return {}

    def create_visualization_data(self, regional_topics: Dict[str, Any], interpretations: Dict[str, Any]) -> Dict[str, Any]:
        """시각화용 데이터 생성"""
        try:
            print("📊 시각화 데이터 생성 중...")
            
            viz_data = {
                'regional_topic_distribution': self._create_topic_distribution_data(regional_topics),
                'top_regions_by_topic': self._create_top_regions_by_topic(regional_topics),
                'promise_analysis': self._create_promise_analysis_data(regional_topics),
                'regional_network': self._create_regional_network_data(regional_topics),
                'topic_hierarchy_map': self._create_topic_hierarchy_map(regional_topics)
            }
            
            self.analysis_results['visualization_ready_data'] = viz_data
            
            print(f"✅ 시각화 데이터 생성 완료")
            return viz_data
            
        except Exception as e:
            logger.error(f"❌ 시각화 데이터 생성 실패: {e}")
            return {}

    def _create_topic_distribution_data(self, regional_topics: Dict[str, Any]) -> Dict[str, Any]:
        """토픽 분포 데이터 생성"""
        topic_distribution = defaultdict(int)
        level_distribution = defaultdict(int)
        
        for region, data in regional_topics.items():
            level = data.get('level', '기타')
            level_distribution[level] += 1
            
            for topic in data.get('dominant_topics', []):
                topic_distribution[topic] += 1
        
        return {
            'topic_counts': dict(topic_distribution),
            'level_counts': dict(level_distribution),
            'total_regions': len(regional_topics)
        }

    def _create_top_regions_by_topic(self, regional_topics: Dict[str, Any]) -> Dict[str, List]:
        """토픽별 상위 지역 데이터"""
        topic_regions = defaultdict(list)
        
        for region, data in regional_topics.items():
            for topic in data.get('dominant_topics', []):
                topic_score = data.get('topic_scores', {}).get(topic, 0)
                topic_regions[topic].append({
                    'region': region,
                    'score': topic_score,
                    'mention_count': data['mention_count']
                })
        
        # 각 토픽별로 점수 순 정렬
        for topic in topic_regions:
            topic_regions[topic].sort(key=lambda x: x['score'], reverse=True)
            topic_regions[topic] = topic_regions[topic][:10]  # 상위 10개만
        
        return dict(topic_regions)

    def _create_promise_analysis_data(self, regional_topics: Dict[str, Any]) -> Dict[str, Any]:
        """공약 분석 데이터"""
        all_promises = []
        promise_by_topic = defaultdict(list)
        
        for region, data in regional_topics.items():
            promises = data.get('promises', [])
            all_promises.extend(promises)
            
            for topic in data.get('dominant_topics', []):
                promise_by_topic[topic].extend(promises)
        
        return {
            'total_promises': len(all_promises),
            'unique_promises': len(set(all_promises)),
            'promise_by_topic': {k: len(set(v)) for k, v in promise_by_topic.items()},
            'common_promises': [item for item, count in Counter(all_promises).most_common(10)]
        }

    def _create_regional_network_data(self, regional_topics: Dict[str, Any]) -> Dict[str, Any]:
        """지역 네트워크 데이터"""
        nodes = []
        edges = []
        
        # 노드 생성 (지역)
        for region, data in regional_topics.items():
            nodes.append({
                'id': region,
                'label': region,
                'level': data.get('level', '기타'),
                'size': data['mention_count'],
                'topics': data.get('dominant_topics', [])
            })
        
        # 엣지 생성 (공통 토픽을 가진 지역들 연결)
        regions_list = list(regional_topics.items())
        for i, (region1, data1) in enumerate(regions_list):
            for region2, data2 in regions_list[i+1:]:
                common_topics = set(data1.get('dominant_topics', [])) & set(data2.get('dominant_topics', []))
                if common_topics:
                    edges.append({
                        'source': region1,
                        'target': region2,
                        'weight': len(common_topics),
                        'common_topics': list(common_topics)
                    })
        
        return {'nodes': nodes, 'edges': edges}

    def _create_topic_hierarchy_map(self, regional_topics: Dict[str, Any]) -> Dict[str, Any]:
        """토픽 계층 맵 데이터"""
        hierarchy_map = {}
        
        for level in ['광역시도', '시군구', '읍면동']:
            level_data = []
            for region, data in regional_topics.items():
                if data.get('level') == level:
                    level_data.append({
                        'region': region,
                        'topics': data.get('dominant_topics', []),
                        'mention_count': data['mention_count'],
                        'promises': len(data.get('promises', []))
                    })
            
            hierarchy_map[level] = sorted(level_data, key=lambda x: x['mention_count'], reverse=True)
        
        return hierarchy_map

    def save_results(self) -> str:
        """분석 결과 저장"""
        try:
            print("💾 분석 결과 저장 중...")
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            results_file = os.path.join(self.output_dir, f"enhanced_policy_analysis_{timestamp}.json")
            
            # 전체 결과 저장
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(self.analysis_results, f, ensure_ascii=False, indent=2)
            
            # 지역별 결과창용 데이터 별도 저장
            frontend_data = self._prepare_frontend_data()
            frontend_file = os.path.join(self.output_dir, f"regional_misaeng_topics_frontend_{timestamp}.json")
            
            with open(frontend_file, 'w', encoding='utf-8') as f:
                json.dump(frontend_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 분석 결과 저장 완료:")
            print(f"  📄 전체 결과: {results_file}")
            print(f"  🖥️ 프론트엔드용: {frontend_file}")
            
            return results_file
            
        except Exception as e:
            logger.error(f"❌ 결과 저장 실패: {e}")
            return None

    def _prepare_frontend_data(self) -> Dict[str, Any]:
        """프론트엔드용 데이터 준비"""
        frontend_data = {
            'last_updated': datetime.now().isoformat(),
            'total_regions': len(self.analysis_results.get('regional_misaeng_topics', {})),
            'misaeng_topic_categories': self.misaeng_topics,
            'regional_data': {}
        }
        
        # 지역별 데이터 구조화
        for region, data in self.analysis_results.get('regional_misaeng_topics', {}).items():
            if data['mention_count'] > 0:
                frontend_data['regional_data'][region] = {
                    'region_name': data['region'],
                    'level': data['level'],
                    'mention_count': data['mention_count'],
                    'dominant_topics': data['dominant_topics'],
                    'topic_scores': data['topic_scores'],
                    'interpretation': self.analysis_results.get('topic_interpretations', {}).get(region, {}).get('main_interpretation', ''),
                    'promises': data['promises'],
                    'confidence_score': sum(data['topic_scores'].values()) if data['topic_scores'] else 0,
                    'sample_sentences': data['sentences'][:3]  # 상위 3개 문장
                }
        
        return frontend_data

    def run_complete_analysis(self) -> Dict[str, Any]:
        """전체 분석 실행"""
        print("🚀 개선된 정책선거문화 텍스트마이닝 시작")
        print("=" * 80)
        
        try:
            # 1. PDF 내용 추출
            print("\n📄 1단계: PDF 내용 추출")
            full_text = self.extract_pdf_content()
            if not full_text:
                raise Exception("PDF 내용 추출 실패")
            
            # 2. 지역별 미생토픽 추출
            print("\n🗺️ 2단계: 지역별 미생토픽 추출")
            regional_topics = self.extract_regional_misaeng_topics(full_text)
            
            # 3. 토픽 해석
            print("\n🎯 3단계: 지역별 토픽 해석")
            interpretations = self.interpret_regional_topics(regional_topics)
            
            # 4. 계층적 데이터 생성
            print("\n🏗️ 4단계: 계층적 지역 데이터 생성")
            hierarchical_data = self.create_hierarchical_data(regional_topics)
            
            # 5. 시각화 데이터 생성
            print("\n📊 5단계: 시각화 데이터 생성")
            viz_data = self.create_visualization_data(regional_topics, interpretations)
            
            # 6. 결과 저장
            print("\n💾 6단계: 결과 저장")
            results_file = self.save_results()
            
            print("\n🎉 개선된 정책선거문화 분석 완료!")
            print("=" * 80)
            
            # 요약 통계
            summary = self._generate_summary()
            
            return {
                'success': True,
                'results_file': results_file,
                'summary': summary,
                'completion_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"\n❌ 분석 실패: {e}")
            return {
                'success': False,
                'error': str(e),
                'completion_time': datetime.now().isoformat()
            }

    def _generate_summary(self) -> Dict[str, Any]:
        """분석 요약 생성"""
        regional_topics = self.analysis_results.get('regional_misaeng_topics', {})
        
        # 레벨별 통계
        level_stats = defaultdict(int)
        topic_stats = defaultdict(int)
        
        for region, data in regional_topics.items():
            level_stats[data.get('level', '기타')] += 1
            for topic in data.get('dominant_topics', []):
                topic_stats[topic] += 1
        
        return {
            'total_regions_analyzed': len(regional_topics),
            'regions_by_level': dict(level_stats),
            'top_topics': dict(Counter(topic_stats).most_common(5)),
            'total_promises_extracted': sum(len(data.get('promises', [])) for data in regional_topics.values()),
            'document_pages': self.analysis_results.get('document_info', {}).get('total_pages', 0),
            'text_length': self.analysis_results.get('document_info', {}).get('total_text_length', 0)
        }

def main():
    """메인 실행 함수"""
    analyzer = EnhancedPolicyTextMiningSystem()
    results = analyzer.run_complete_analysis()
    
    if results['success']:
        print(f"\n✅ 분석 성공!")
        print(f"📄 결과 파일: {results['results_file']}")
        
        summary = results['summary']
        print(f"\n📊 분석 요약:")
        print(f"  🗺️ 분석 지역: {summary['total_regions_analyzed']}개")
        print(f"  📄 문서 페이지: {summary['document_pages']}페이지")
        print(f"  📝 텍스트 길이: {summary['text_length']:,}자")
        print(f"  🎯 추출 공약: {summary['total_promises_extracted']}개")
        
        print(f"\n🏛️ 레벨별 지역:")
        for level, count in summary['regions_by_level'].items():
            print(f"    {level}: {count}개")
        
        print(f"\n🔥 주요 토픽:")
        for topic, count in summary['top_topics'].items():
            print(f"    {topic}: {count}개 지역")
        
    else:
        print(f"\n❌ 분석 실패: {results['error']}")

if __name__ == "__main__":
    main()
