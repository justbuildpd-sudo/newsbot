#!/usr/bin/env python3
"""
정책선거문화 확산을 위한 언론기사 빅데이터 분석 시스템
지역별 미생토픽 분석 및 텍스트마이닝을 통한 토픽-해석-공약 데이터화

파일: 231215_정책선거문화_확산을_위한_언론기사_빅데이터_분석.pdf
목표: 광역에서 동단위까지 지역별 결과창에 미생토픽 표시
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
import matplotlib.font_manager as fm

# 한글 폰트 설정
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

# 텍스트 마이닝 라이브러리
try:
    from konlpy.tag import Okt, Mecab, Komoran
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    from sklearn.decomposition import LatentDirichletAllocation
    from sklearn.manifold import TSNE
    import networkx as nx
    # textrank는 선택적 라이브러리
    try:
        from textrank import TextRank
        TEXTRANK_AVAILABLE = True
    except ImportError:
        TEXTRANK_AVAILABLE = False
    NLP_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ 텍스트마이닝 라이브러리 설치 필요: {e}")
    NLP_AVAILABLE = False
    TEXTRANK_AVAILABLE = False

logger = logging.getLogger(__name__)

class PolicyElectionCultureAnalyzer:
    """정책선거문화 빅데이터 분석기"""
    
    def __init__(self):
        self.base_dir = "/Users/hopidaay/newsbot-kr"
        self.backend_dir = "/Users/hopidaay/newsbot-kr/backend"
        self.pdf_file = "/Users/hopidaay/Desktop/231215_정책선거문화_확산을_위한_언론기사_빅데이터_분석.pdf"
        
        # 분석 결과 저장 디렉토리
        self.output_dir = os.path.join(self.backend_dir, "policy_election_culture_analysis")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 텍스트 마이닝 도구 초기화
        if NLP_AVAILABLE:
            self.okt = Okt()
            self.tfidf = TfidfVectorizer(max_features=1000, stop_words=None)
            self.lda_model = None
            self.kmeans_model = None
        
        # 지역 매핑 정보
        self.region_hierarchy = {
            '광역시도': ['서울', '부산', '대구', '인천', '광주', '대전', '울산', '세종', '경기', '강원', '충북', '충남', '전북', '전남', '경북', '경남', '제주'],
            '시군구': [],  # 동적으로 로드
            '읍면동': []   # 동적으로 로드
        }
        
        # 미생토픽 카테고리
        self.misaeng_topics = {
            '경제정책': ['일자리', '취업', '창업', '경제성장', '소득', '임금'],
            '주거정책': ['주택', '부동산', '임대', '전세', '월세', '아파트'],
            '교육정책': ['교육', '학교', '대학', '입시', '사교육', '교육비'],
            '복지정책': ['복지', '의료', '건강보험', '연금', '육아', '보육'],
            '환경정책': ['환경', '기후', '에너지', '미세먼지', '재생에너지'],
            '교통정책': ['교통', '대중교통', '지하철', '버스', '도로', '주차'],
            '문화정책': ['문화', '예술', '체육', '관광', '축제', '공연'],
            '안전정책': ['안전', '치안', '재해', '방범', '소방', '응급']
        }
        
        # 분석 결과 저장
        self.analysis_results = {
            'document_info': {},
            'regional_topics': {},
            'topic_interpretation': {},
            'policy_promises': {},
            'text_mining_results': {},
            'visualization_data': {}
        }

    def extract_pdf_content(self) -> Dict[str, Any]:
        """PDF 파일에서 텍스트 내용 추출"""
        try:
            print("📄 PDF 파일 내용 추출 중...")
            
            if not os.path.exists(self.pdf_file):
                raise FileNotFoundError(f"PDF 파일을 찾을 수 없습니다: {self.pdf_file}")
            
            # PDF 문서 열기
            doc = fitz.open(self.pdf_file)
            
            extracted_content = {
                'total_pages': len(doc),
                'pages': [],
                'full_text': '',
                'metadata': doc.metadata,
                'creation_date': datetime.now().isoformat()
            }
            
            print(f"📊 총 {len(doc)} 페이지 PDF 문서 분석 시작")
            
            # 각 페이지별 텍스트 추출
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_text = page.get_text()
                
                page_info = {
                    'page_number': page_num + 1,
                    'text': page_text,
                    'text_length': len(page_text),
                    'has_content': len(page_text.strip()) > 0
                }
                
                extracted_content['pages'].append(page_info)
                extracted_content['full_text'] += page_text + '\n'
                
                if page_num % 10 == 0:
                    print(f"  📄 페이지 {page_num + 1}/{len(doc)} 처리 완료")
            
            doc.close()
            
            # 문서 정보 저장
            self.analysis_results['document_info'] = {
                'file_path': self.pdf_file,
                'total_pages': extracted_content['total_pages'],
                'total_text_length': len(extracted_content['full_text']),
                'metadata': extracted_content['metadata'],
                'extraction_date': extracted_content['creation_date']
            }
            
            print(f"✅ PDF 추출 완료: {len(extracted_content['full_text'])} 문자")
            return extracted_content
            
        except Exception as e:
            logger.error(f"❌ PDF 추출 실패: {e}")
            return None

    def preprocess_text(self, text: str) -> List[str]:
        """텍스트 전처리 및 토큰화"""
        if not NLP_AVAILABLE:
            print("⚠️ 텍스트마이닝 라이브러리가 설치되지 않음")
            return []
        
        try:
            # 텍스트 정제
            text = re.sub(r'[^\w\s가-힣]', ' ', text)
            text = re.sub(r'\s+', ' ', text)
            text = text.strip()
            
            # 형태소 분석 및 명사 추출
            tokens = self.okt.nouns(text)
            
            # 불용어 제거 및 길이 필터링
            stopwords = {'것', '등', '및', '또한', '그리고', '하지만', '그러나', '따라서', '이를', '이에', '대한', '위한', '통해', '있다', '없다', '된다', '한다', '이다'}
            filtered_tokens = [token for token in tokens if len(token) > 1 and token not in stopwords]
            
            return filtered_tokens
            
        except Exception as e:
            logger.error(f"❌ 텍스트 전처리 실패: {e}")
            return []

    def extract_regional_topics(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """지역별 토픽 추출"""
        try:
            print("🗺️ 지역별 토픽 추출 중...")
            
            full_text = content['full_text']
            regional_topics = defaultdict(list)
            
            # 지역명 패턴 정의
            region_patterns = {
                '광역시도': r'(서울|부산|대구|인천|광주|대전|울산|세종|경기|강원|충북|충남|전북|전남|경북|경남|제주)(?:특별시|광역시|특별자치시|도|특별자치도)?',
                '시군구': r'(\w+)(?:시|군|구)',
                '읍면동': r'(\w+)(?:읍|면|동)'
            }
            
            # 각 지역 레벨별 토픽 추출
            for level, pattern in region_patterns.items():
                matches = re.findall(pattern, full_text)
                region_counter = Counter(matches)
                
                print(f"  📍 {level}: {len(region_counter)}개 지역 발견")
                
                for region, count in region_counter.most_common(50):  # 상위 50개 지역
                    # 해당 지역 관련 문장 추출
                    region_sentences = []
                    for sentence in full_text.split('.'):
                        if region in sentence:
                            region_sentences.append(sentence.strip())
                    
                    if region_sentences:
                        # 토픽 분석
                        region_text = ' '.join(region_sentences)
                        tokens = self.preprocess_text(region_text)
                        
                        if tokens:
                            # 토픽 카테고리별 키워드 매칭
                            topic_scores = {}
                            for topic, keywords in self.misaeng_topics.items():
                                score = sum(1 for token in tokens if any(keyword in token for keyword in keywords))
                                if score > 0:
                                    topic_scores[topic] = score
                            
                            regional_topics[level].append({
                                'region': region,
                                'mention_count': count,
                                'sentences': region_sentences[:5],  # 상위 5개 문장
                                'tokens': tokens[:20],  # 상위 20개 토큰
                                'topic_scores': topic_scores,
                                'dominant_topic': max(topic_scores.items(), key=lambda x: x[1])[0] if topic_scores else '기타'
                            })
            
            self.analysis_results['regional_topics'] = dict(regional_topics)
            
            print(f"✅ 지역별 토픽 추출 완료")
            return dict(regional_topics)
            
        except Exception as e:
            logger.error(f"❌ 지역별 토픽 추출 실패: {e}")
            return {}

    def perform_topic_modeling(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """토픽 모델링 수행"""
        if not NLP_AVAILABLE:
            print("⚠️ 토픽 모델링을 위한 라이브러리가 설치되지 않음")
            return {}
        
        try:
            print("🧠 토픽 모델링 수행 중...")
            
            # 전체 텍스트를 문장 단위로 분할
            sentences = [s.strip() for s in content['full_text'].split('.') if len(s.strip()) > 20]
            print(f"  📝 총 {len(sentences)}개 문장 분석")
            
            # 각 문장을 토큰화
            tokenized_sentences = []
            for sentence in sentences[:1000]:  # 처리 속도를 위해 상위 1000개 문장만
                tokens = self.preprocess_text(sentence)
                if len(tokens) > 3:  # 최소 3개 이상의 토큰이 있는 문장만
                    tokenized_sentences.append(' '.join(tokens))
            
            if not tokenized_sentences:
                print("⚠️ 토큰화된 문장이 없음")
                return {}
            
            print(f"  🔤 {len(tokenized_sentences)}개 문장 토큰화 완료")
            
            # TF-IDF 벡터화
            tfidf_matrix = self.tfidf.fit_transform(tokenized_sentences)
            feature_names = self.tfidf.get_feature_names_out()
            
            # LDA 토픽 모델링
            n_topics = 8  # 미생토픽 카테고리 수
            self.lda_model = LatentDirichletAllocation(
                n_components=n_topics, 
                random_state=42, 
                max_iter=100
            )
            lda_result = self.lda_model.fit_transform(tfidf_matrix)
            
            # 토픽별 주요 키워드 추출
            topics_info = []
            for topic_idx, topic in enumerate(self.lda_model.components_):
                top_words_idx = topic.argsort()[-10:][::-1]  # 상위 10개 키워드
                top_words = [feature_names[i] for i in top_words_idx]
                top_weights = [topic[i] for i in top_words_idx]
                
                # 토픽 카테고리 자동 분류
                topic_category = self._classify_topic_category(top_words)
                
                topics_info.append({
                    'topic_id': topic_idx,
                    'category': topic_category,
                    'keywords': top_words,
                    'weights': top_weights.tolist(),
                    'keyword_weight_pairs': list(zip(top_words, top_weights.tolist()))
                })
            
            # K-means 클러스터링
            n_clusters = 5
            self.kmeans_model = KMeans(n_clusters=n_clusters, random_state=42)
            cluster_labels = self.kmeans_model.fit_predict(tfidf_matrix)
            
            # 클러스터별 대표 키워드
            clusters_info = []
            for cluster_id in range(n_clusters):
                cluster_sentences_idx = np.where(cluster_labels == cluster_id)[0]
                cluster_tfidf = tfidf_matrix[cluster_sentences_idx].mean(axis=0).A1
                top_features_idx = cluster_tfidf.argsort()[-10:][::-1]
                cluster_keywords = [feature_names[i] for i in top_features_idx]
                
                clusters_info.append({
                    'cluster_id': cluster_id,
                    'size': len(cluster_sentences_idx),
                    'keywords': cluster_keywords,
                    'representative_sentences': [sentences[i] for i in cluster_sentences_idx[:3]]
                })
            
            topic_modeling_results = {
                'lda_topics': topics_info,
                'kmeans_clusters': clusters_info,
                'total_sentences': len(sentences),
                'processed_sentences': len(tokenized_sentences),
                'vocabulary_size': len(feature_names),
                'modeling_date': datetime.now().isoformat()
            }
            
            self.analysis_results['text_mining_results'] = topic_modeling_results
            
            print(f"✅ 토픽 모델링 완료: {n_topics}개 토픽, {n_clusters}개 클러스터")
            return topic_modeling_results
            
        except Exception as e:
            logger.error(f"❌ 토픽 모델링 실패: {e}")
            return {}

    def _classify_topic_category(self, keywords: List[str]) -> str:
        """키워드를 기반으로 토픽 카테고리 자동 분류"""
        category_scores = {}
        
        for category, category_keywords in self.misaeng_topics.items():
            score = 0
            for keyword in keywords:
                for cat_keyword in category_keywords:
                    if cat_keyword in keyword or keyword in cat_keyword:
                        score += 1
            category_scores[category] = score
        
        if category_scores:
            return max(category_scores.items(), key=lambda x: x[1])[0]
        else:
            return '기타정책'

    def interpret_topics_and_extract_promises(self, regional_topics: Dict[str, Any], topic_modeling: Dict[str, Any]) -> Dict[str, Any]:
        """토픽 해석 및 공약 추출"""
        try:
            print("🎯 토픽 해석 및 공약 추출 중...")
            
            interpretations = {}
            policy_promises = {}
            
            # 지역별 토픽 해석
            for level, regions in regional_topics.items():
                interpretations[level] = []
                policy_promises[level] = []
                
                for region_info in regions:
                    region = region_info['region']
                    dominant_topic = region_info['dominant_topic']
                    topic_scores = region_info['topic_scores']
                    sentences = region_info['sentences']
                    
                    # 토픽 해석 생성
                    interpretation = self._generate_topic_interpretation(
                        region, dominant_topic, topic_scores, sentences
                    )
                    
                    # 공약 추출
                    promises = self._extract_policy_promises(sentences, dominant_topic)
                    
                    interpretations[level].append({
                        'region': region,
                        'dominant_topic': dominant_topic,
                        'interpretation': interpretation,
                        'confidence_score': max(topic_scores.values()) if topic_scores else 0
                    })
                    
                    policy_promises[level].append({
                        'region': region,
                        'topic': dominant_topic,
                        'promises': promises,
                        'promise_count': len(promises)
                    })
            
            # LDA 토픽별 해석
            lda_interpretations = []
            if 'lda_topics' in topic_modeling:
                for topic_info in topic_modeling['lda_topics']:
                    topic_interpretation = self._generate_lda_topic_interpretation(topic_info)
                    lda_interpretations.append(topic_interpretation)
            
            results = {
                'regional_interpretations': interpretations,
                'regional_policy_promises': policy_promises,
                'lda_topic_interpretations': lda_interpretations,
                'interpretation_date': datetime.now().isoformat()
            }
            
            self.analysis_results['topic_interpretation'] = interpretations
            self.analysis_results['policy_promises'] = policy_promises
            
            print(f"✅ 토픽 해석 및 공약 추출 완료")
            return results
            
        except Exception as e:
            logger.error(f"❌ 토픽 해석 및 공약 추출 실패: {e}")
            return {}

    def _generate_topic_interpretation(self, region: str, topic: str, scores: Dict[str, int], sentences: List[str]) -> str:
        """지역별 토픽 해석 생성"""
        try:
            # 토픽별 해석 템플릿
            topic_templates = {
                '경제정책': f"{region} 지역은 일자리 창출과 경제 활성화가 주요 관심사로 나타남",
                '주거정책': f"{region} 지역은 주택 공급과 부동산 안정화가 핵심 이슈임",
                '교육정책': f"{region} 지역은 교육 환경 개선과 사교육 부담 해소가 중요함",
                '복지정책': f"{region} 지역은 사회복지 확충과 의료 서비스 개선이 필요함",
                '환경정책': f"{region} 지역은 환경 보호와 지속가능한 발전이 관심사임",
                '교통정책': f"{region} 지역은 교통 인프라 개선과 대중교통 확충이 중요함",
                '문화정책': f"{region} 지역은 문화 시설 확충과 관광 산업 발전이 필요함",
                '안전정책': f"{region} 지역은 안전한 생활 환경 조성이 우선 과제임"
            }
            
            base_interpretation = topic_templates.get(topic, f"{region} 지역의 {topic} 관련 이슈가 주목받고 있음")
            
            # 점수 기반 상세 해석 추가
            if scores:
                sorted_topics = sorted(scores.items(), key=lambda x: x[1], reverse=True)
                if len(sorted_topics) > 1:
                    secondary_topic = sorted_topics[1][0]
                    base_interpretation += f". 또한 {secondary_topic} 분야도 함께 관심을 받고 있음"
            
            return base_interpretation
            
        except Exception as e:
            return f"{region} 지역의 {topic} 관련 분석 결과"

    def _extract_policy_promises(self, sentences: List[str], topic: str) -> List[str]:
        """문장에서 정책 공약 추출"""
        try:
            promises = []
            
            # 공약 관련 키워드 패턴
            promise_patterns = [
                r'(\w+을/를\s*(?:추진|실시|시행|도입|확대|강화|개선))',
                r'(\w+\s*(?:정책|사업|프로그램|제도)을/를\s*(?:마련|수립|추진))',
                r'(\w+을/를\s*위한\s*\w+)',
                r'(\w+\s*(?:지원|확충|조성|건설|설치))'
            ]
            
            for sentence in sentences:
                for pattern in promise_patterns:
                    matches = re.findall(pattern, sentence)
                    for match in matches:
                        if len(match) > 5 and match not in promises:
                            promises.append(match.strip())
            
            # 토픽별 특화 공약 추출
            topic_specific_promises = self._extract_topic_specific_promises(sentences, topic)
            promises.extend(topic_specific_promises)
            
            return list(set(promises))[:10]  # 중복 제거 및 상위 10개
            
        except Exception as e:
            return []

    def _extract_topic_specific_promises(self, sentences: List[str], topic: str) -> List[str]:
        """토픽별 특화 공약 추출"""
        topic_keywords = self.misaeng_topics.get(topic, [])
        promises = []
        
        for sentence in sentences:
            for keyword in topic_keywords:
                if keyword in sentence:
                    # 해당 키워드가 포함된 문장에서 공약성 표현 추출
                    if any(word in sentence for word in ['확대', '강화', '개선', '지원', '추진', '도입']):
                        clean_sentence = sentence.strip()
                        if len(clean_sentence) > 10 and clean_sentence not in promises:
                            promises.append(clean_sentence)
        
        return promises

    def _generate_lda_topic_interpretation(self, topic_info: Dict[str, Any]) -> Dict[str, Any]:
        """LDA 토픽 해석 생성"""
        keywords = topic_info['keywords']
        category = topic_info['category']
        
        # 키워드 기반 해석 생성
        main_keywords = keywords[:5]
        interpretation = f"{category} 분야에서 {', '.join(main_keywords)} 등이 주요 관심사로 나타남"
        
        return {
            'topic_id': topic_info['topic_id'],
            'category': category,
            'main_keywords': main_keywords,
            'interpretation': interpretation,
            'all_keywords': keywords
        }

    def create_visualization_data(self) -> Dict[str, Any]:
        """시각화를 위한 데이터 생성"""
        try:
            print("📊 시각화 데이터 생성 중...")
            
            viz_data = {
                'regional_topic_distribution': self._create_regional_topic_distribution(),
                'topic_keyword_networks': self._create_topic_keyword_networks(),
                'regional_hierarchy_data': self._create_regional_hierarchy_data(),
                'topic_timeline_data': self._create_topic_timeline_data(),
                'promise_category_data': self._create_promise_category_data()
            }
            
            self.analysis_results['visualization_data'] = viz_data
            
            print("✅ 시각화 데이터 생성 완료")
            return viz_data
            
        except Exception as e:
            logger.error(f"❌ 시각화 데이터 생성 실패: {e}")
            return {}

    def _create_regional_topic_distribution(self) -> Dict[str, Any]:
        """지역별 토픽 분포 데이터 생성"""
        distribution_data = {}
        
        if 'regional_topics' in self.analysis_results:
            for level, regions in self.analysis_results['regional_topics'].items():
                topic_counts = defaultdict(int)
                for region_info in regions:
                    topic = region_info.get('dominant_topic', '기타')
                    topic_counts[topic] += 1
                
                distribution_data[level] = dict(topic_counts)
        
        return distribution_data

    def _create_topic_keyword_networks(self) -> Dict[str, Any]:
        """토픽-키워드 네트워크 데이터 생성"""
        network_data = {'nodes': [], 'edges': []}
        
        if 'text_mining_results' in self.analysis_results and 'lda_topics' in self.analysis_results['text_mining_results']:
            for topic_info in self.analysis_results['text_mining_results']['lda_topics']:
                topic_node = {
                    'id': f"topic_{topic_info['topic_id']}",
                    'label': topic_info['category'],
                    'type': 'topic',
                    'size': 20
                }
                network_data['nodes'].append(topic_node)
                
                for keyword, weight in topic_info['keyword_weight_pairs'][:5]:
                    keyword_node = {
                        'id': f"keyword_{keyword}",
                        'label': keyword,
                        'type': 'keyword',
                        'size': weight * 10
                    }
                    network_data['nodes'].append(keyword_node)
                    
                    edge = {
                        'source': topic_node['id'],
                        'target': keyword_node['id'],
                        'weight': weight
                    }
                    network_data['edges'].append(edge)
        
        return network_data

    def _create_regional_hierarchy_data(self) -> Dict[str, Any]:
        """지역 계층 구조 데이터 생성"""
        hierarchy_data = {
            'levels': ['광역시도', '시군구', '읍면동'],
            'regions': {}
        }
        
        if 'regional_topics' in self.analysis_results:
            for level, regions in self.analysis_results['regional_topics'].items():
                hierarchy_data['regions'][level] = [
                    {
                        'name': region_info['region'],
                        'topic': region_info.get('dominant_topic', '기타'),
                        'mention_count': region_info.get('mention_count', 0)
                    }
                    for region_info in regions
                ]
        
        return hierarchy_data

    def _create_topic_timeline_data(self) -> Dict[str, Any]:
        """토픽 시간선 데이터 생성 (문서 내 위치 기반)"""
        # 실제 구현에서는 PDF의 페이지나 섹션 정보를 활용
        return {'timeline': 'PDF 구조 분석 후 구현'}

    def _create_promise_category_data(self) -> Dict[str, Any]:
        """공약 카테고리별 데이터 생성"""
        category_data = defaultdict(int)
        
        if 'policy_promises' in self.analysis_results:
            for level, regions in self.analysis_results['policy_promises'].items():
                for region_info in regions:
                    topic = region_info.get('topic', '기타')
                    promise_count = region_info.get('promise_count', 0)
                    category_data[topic] += promise_count
        
        return dict(category_data)

    def save_analysis_results(self) -> str:
        """분석 결과 저장"""
        try:
            print("💾 분석 결과 저장 중...")
            
            # 결과 파일 경로
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            results_file = os.path.join(self.output_dir, f"policy_election_culture_analysis_{timestamp}.json")
            
            # JSON으로 저장
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(self.analysis_results, f, ensure_ascii=False, indent=2)
            
            # 요약 통계 생성
            summary = self._generate_analysis_summary()
            summary_file = os.path.join(self.output_dir, f"analysis_summary_{timestamp}.json")
            
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 분석 결과 저장 완료:")
            print(f"  📄 상세 결과: {results_file}")
            print(f"  📊 요약 통계: {summary_file}")
            
            return results_file
            
        except Exception as e:
            logger.error(f"❌ 분석 결과 저장 실패: {e}")
            return None

    def _generate_analysis_summary(self) -> Dict[str, Any]:
        """분석 요약 통계 생성"""
        summary = {
            'analysis_date': datetime.now().isoformat(),
            'document_info': self.analysis_results.get('document_info', {}),
            'regional_statistics': {},
            'topic_statistics': {},
            'promise_statistics': {},
            'overall_insights': []
        }
        
        # 지역별 통계
        if 'regional_topics' in self.analysis_results:
            regional_stats = {}
            for level, regions in self.analysis_results['regional_topics'].items():
                regional_stats[level] = {
                    'total_regions': len(regions),
                    'top_regions': [r['region'] for r in sorted(regions, key=lambda x: x.get('mention_count', 0), reverse=True)[:5]]
                }
            summary['regional_statistics'] = regional_stats
        
        # 토픽별 통계
        if 'text_mining_results' in self.analysis_results:
            topic_stats = {
                'total_topics': len(self.analysis_results['text_mining_results'].get('lda_topics', [])),
                'total_clusters': len(self.analysis_results['text_mining_results'].get('kmeans_clusters', [])),
                'vocabulary_size': self.analysis_results['text_mining_results'].get('vocabulary_size', 0)
            }
            summary['topic_statistics'] = topic_stats
        
        # 공약별 통계
        if 'policy_promises' in self.analysis_results:
            promise_stats = {}
            total_promises = 0
            for level, regions in self.analysis_results['policy_promises'].items():
                level_promises = sum(r.get('promise_count', 0) for r in regions)
                promise_stats[level] = level_promises
                total_promises += level_promises
            
            promise_stats['total_promises'] = total_promises
            summary['promise_statistics'] = promise_stats
        
        return summary

    def run_complete_analysis(self) -> Dict[str, Any]:
        """전체 분석 프로세스 실행"""
        print("🚀 정책선거문화 빅데이터 분석 시작")
        print("=" * 80)
        
        try:
            # 1. PDF 내용 추출
            print("\n📄 1단계: PDF 내용 추출")
            content = self.extract_pdf_content()
            if not content:
                raise Exception("PDF 내용 추출 실패")
            
            # 2. 지역별 토픽 추출
            print("\n🗺️ 2단계: 지역별 토픽 추출")
            regional_topics = self.extract_regional_topics(content)
            
            # 3. 토픽 모델링
            print("\n🧠 3단계: 토픽 모델링")
            topic_modeling = self.perform_topic_modeling(content)
            
            # 4. 토픽 해석 및 공약 추출
            print("\n🎯 4단계: 토픽 해석 및 공약 추출")
            interpretations = self.interpret_topics_and_extract_promises(regional_topics, topic_modeling)
            
            # 5. 시각화 데이터 생성
            print("\n📊 5단계: 시각화 데이터 생성")
            viz_data = self.create_visualization_data()
            
            # 6. 결과 저장
            print("\n💾 6단계: 결과 저장")
            results_file = self.save_analysis_results()
            
            print("\n🎉 정책선거문화 빅데이터 분석 완료!")
            print("=" * 80)
            
            final_results = {
                'success': True,
                'results_file': results_file,
                'analysis_summary': self._generate_analysis_summary(),
                'completion_time': datetime.now().isoformat()
            }
            
            return final_results
            
        except Exception as e:
            print(f"\n❌ 분석 실패: {e}")
            return {
                'success': False,
                'error': str(e),
                'completion_time': datetime.now().isoformat()
            }

def main():
    """메인 실행 함수"""
    analyzer = PolicyElectionCultureAnalyzer()
    results = analyzer.run_complete_analysis()
    
    if results['success']:
        print(f"\n✅ 분석 성공!")
        print(f"📄 결과 파일: {results['results_file']}")
        print(f"📊 분석 요약:")
        
        summary = results['analysis_summary']
        if 'regional_statistics' in summary:
            for level, stats in summary['regional_statistics'].items():
                print(f"  🗺️ {level}: {stats['total_regions']}개 지역")
        
        if 'topic_statistics' in summary:
            topic_stats = summary['topic_statistics']
            print(f"  🧠 토픽: {topic_stats.get('total_topics', 0)}개")
            print(f"  📚 어휘: {topic_stats.get('vocabulary_size', 0)}개")
        
        if 'promise_statistics' in summary:
            promise_stats = summary['promise_statistics']
            print(f"  🎯 공약: {promise_stats.get('total_promises', 0)}개")
        
    else:
        print(f"\n❌ 분석 실패: {results['error']}")

if __name__ == "__main__":
    main()
