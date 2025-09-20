#!/usr/bin/env python3
"""
정책선거문화 문서 종합 토픽 분석기
635페이지 문서를 더 상세하게 분석하여 다양한 토픽 추출
"""

import os
import json
import re
import logging
from datetime import datetime
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Any
import pickle

# 텍스트마이닝 라이브러리
try:
    import fitz  # PyMuPDF
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
    from sklearn.cluster import KMeans, DBSCAN
    from sklearn.decomposition import LatentDirichletAllocation, TruncatedSVD
    from sklearn.manifold import TSNE
    from sklearn.metrics.pairwise import cosine_similarity
    import networkx as nx
    
    # 한국어 형태소 분석
    try:
        from konlpy.tag import Okt, Mecab, Komoran
        KOREAN_ANALYZER = "okt"
    except ImportError:
        try:
            import mecab
            KOREAN_ANALYZER = "mecab"
        except ImportError:
            KOREAN_ANALYZER = None
    
    NLP_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ 텍스트마이닝 라이브러리 설치 필요: {e}")
    NLP_AVAILABLE = False

logger = logging.getLogger(__name__)

class ComprehensivePolicyTopicAnalyzer:
    """정책선거문화 문서 종합 토픽 분석기"""
    
    def __init__(self, pdf_file_path: str):
        self.pdf_file = pdf_file_path
        self.analysis_results = {}
        
        # 한국어 분석기 초기화 (Java 없이도 작동하도록)
        self.analyzer = None
        if KOREAN_ANALYZER == "okt":
            try:
                self.analyzer = Okt()
                print("✅ Okt 형태소 분석기 초기화 성공")
            except Exception as e:
                print(f"⚠️ Okt 초기화 실패: {e}")
                self.analyzer = None
        elif KOREAN_ANALYZER == "mecab":
            try:
                self.analyzer = Mecab()
                print("✅ Mecab 형태소 분석기 초기화 성공")
            except Exception as e:
                print(f"⚠️ Mecab 초기화 실패: {e}")
                self.analyzer = None
        elif KOREAN_ANALYZER == "komoran":
            try:
                self.analyzer = Komoran()
                print("✅ Komoran 형태소 분석기 초기화 성공")
            except Exception as e:
                print(f"⚠️ Komoran 초기화 실패: {e}")
                self.analyzer = None
        else:
            print("⚠️ 형태소 분석기 없이 실행합니다. 기본 단어 분할을 사용합니다.")
        
        # 확장된 토픽 카테고리 (8개 → 20개+)
        self.comprehensive_topic_categories = {
            # 기본 경제/사회 토픽
            "경제정책": {
                "keywords": ["일자리", "취업", "창업", "경제성장", "소득", "임금", "고용", "실업", "경제활동", "사업", "투자", "금융", "중소기업", "스타트업", "벤처", "경제지원", "경제개발", "산업육성", "수출", "수입", "무역", "경제협력"],
                "description": "일자리 창출, 경제 활성화, 소득 증대, 중소기업 지원"
            },
            "주거정책": {
                "keywords": ["주택", "부동산", "임대", "전세", "월세", "아파트", "집값", "주거", "분양", "매매", "주택공급", "공공주택", "임대주택", "청년주택", "신축", "재개발", "재건축", "도시계획", "택지개발"],
                "description": "주택 공급, 부동산 안정화, 주거 복지, 도시 개발"
            },
            "교육정책": {
                "keywords": ["교육", "학교", "대학", "입시", "사교육", "교육비", "학습", "학생", "교사", "교육과정", "학원", "보습", "교육혁신", "디지털교육", "온라인교육", "교육시설", "교육환경", "교육지원", "장학금", "교육복지"],
                "description": "교육 환경 개선, 사교육 부담 해소, 교육 혁신"
            },
            "복지정책": {
                "keywords": ["복지", "의료", "건강보험", "연금", "육아", "보육", "사회보장", "복지혜택", "지원금", "돌봄", "노인복지", "장애인복지", "기초생활보장", "생활보조", "의료비지원", "치료비", "간병", "요양"],
                "description": "사회복지 확충, 의료 서비스 개선, 돌봄 서비스"
            },
            "환경정책": {
                "keywords": ["환경", "기후", "에너지", "미세먼지", "재생에너지", "친환경", "탄소", "오염", "녹색", "지속가능", "대기질", "수질", "토양", "폐기물", "재활용", "에너지절약", "신재생에너지", "태양광", "풍력"],
                "description": "환경 보호, 지속가능한 발전, 청정 에너지"
            },
            "교통정책": {
                "keywords": ["교통", "대중교통", "지하철", "버스", "도로", "주차", "교통체증", "이동", "접근성", "인프라", "대중교통망", "교통망", "지하철연장", "버스노선", "도시철도", "고속도로", "국도", "지방도"],
                "description": "교통 인프라 개선, 대중교통 확충, 교통 체증 해소"
            },
            "문화정책": {
                "keywords": ["문화", "예술", "공연", "전시", "축제", "관광", "여가", "스포츠", "체육", "도서관", "박물관", "문화시설", "문화공간", "문화행사", "문화프로그램", "문화유산", "전통문화", "현대문화"],
                "description": "문화 예술 활성화, 여가 생활 증진, 관광 발전"
            },
            "안전정책": {
                "keywords": ["안전", "재난", "재해", "소방", "응급", "범죄", "사고", "위험", "보안", "치안", "방범", "CCTV", "안전시설", "재난대응", "응급의료", "구조", "구급", "화재", "지진", "태풍"],
                "description": "안전한 생활 환경 조성, 재난 대응 체계 구축"
            },
            
            # 추가 세분화 토픽들
            "보건의료정책": {
                "keywords": ["의료", "병원", "의료진", "의료기관", "진료", "치료", "예방", "건강", "질병", "의료서비스", "의료시설", "응급실", "수술", "입원", "외래", "의료기기", "의약품", "의료비"],
                "description": "의료 서비스 확충, 의료 인프라 구축, 공공의료 강화"
            },
            "농업정책": {
                "keywords": ["농업", "농민", "농촌", "농지", "농산물", "농작물", "농기계", "농업기술", "농업지원", "농업정책", "농업인", "농업소득", "농업시설", "농업경영", "농업협동조합", "농산물유통"],
                "description": "농업 발전, 농민 소득 증대, 농촌 활성화"
            },
            "수산업정책": {
                "keywords": ["수산업", "어업", "양식", "어촌", "어선", "수산물", "어업자", "어업지원", "수산업정책", "양식업", "어업기술", "수산업시설", "어촌개발", "어업협동조합", "수산물유통"],
                "description": "수산업 발전, 어업인 지원, 어촌 활성화"
            },
            "관광정책": {
                "keywords": ["관광", "관광지", "관광객", "관광시설", "관광산업", "관광정책", "관광지역", "관광자원", "관광상품", "관광마케팅", "관광객유치", "관광인프라", "관광숙박", "관광식당", "관광교통"],
                "description": "관광 산업 발전, 관광지 개발, 관광객 유치"
            },
            "스포츠정책": {
                "keywords": ["스포츠", "체육", "운동", "체육시설", "체육관", "운동장", "스포츠센터", "체육교육", "스포츠교육", "체육프로그램", "스포츠프로그램", "체육대회", "스포츠대회", "체육단체", "스포츠단체"],
                "description": "스포츠 인프라 구축, 체육 활성화, 건강한 생활"
            },
            "정보통신정책": {
                "keywords": ["정보통신", "IT", "디지털", "인터넷", "통신", "스마트시티", "빅데이터", "인공지능", "AI", "디지털정부", "전자정부", "정보화", "디지털화", "스마트기기", "모바일", "앱"],
                "description": "디지털 전환, 스마트시티 구축, 정보통신 인프라"
            },
            "여성가족정책": {
                "keywords": ["여성", "가족", "육아", "출산", "임신", "산후조리", "보육", "어린이집", "유치원", "아동", "청소년", "다문화", "가족지원", "여성지원", "출산지원", "육아지원"],
                "description": "여성 지원, 가족 친화 정책, 출산 장려"
            },
            "청년정책": {
                "keywords": ["청년", "청소년", "대학생", "취업준비", "청년창업", "청년지원", "청년정책", "청년일자리", "청년주택", "청년복지", "청년활동", "청년기관", "청년센터", "청년공간"],
                "description": "청년 지원, 청년 일자리 창출, 청년 창업 지원"
            },
            "노인정책": {
                "keywords": ["노인", "어르신", "고령자", "노인복지", "노인지원", "노인정책", "노인일자리", "노인활동", "노인센터", "노인복지관", "노인요양", "노인돌봄", "노인건강", "노인교육"],
                "description": "노인 복지, 노인 지원, 고령화 대응"
            },
            "장애인정책": {
                "keywords": ["장애인", "장애", "장애인복지", "장애인지원", "장애인정책", "장애인시설", "장애인복지관", "장애인활동", "장애인일자리", "장애인교육", "장애인의료", "장애인돌봄"],
                "description": "장애인 복지, 장애인 지원, 장애인 권리 보장"
            },
            "환경보전정책": {
                "keywords": ["환경보전", "자연보전", "생태보전", "환경보호", "자연환경", "생태환경", "환경복원", "자연복원", "생태복원", "환경조사", "환경모니터링", "환경영향평가"],
                "description": "환경 보전, 자연 생태 보호, 환경 복원"
            },
            "재정정책": {
                "keywords": ["재정", "예산", "세금", "지방세", "국세", "재정지원", "보조금", "지원금", "재정투자", "재정운영", "재정계획", "재정정책", "재정건전성"],
                "description": "재정 운영, 예산 배분, 세수 확충"
            },
            "행정정책": {
                "keywords": ["행정", "정부", "지방자치", "행정서비스", "민원", "행정처리", "행정절차", "행정개혁", "행정효율", "전자정부", "행정정보화", "행정투명성"],
                "description": "행정 서비스 개선, 행정 효율성, 전자정부 구축"
            },
            "국방안보정책": {
                "keywords": ["국방", "안보", "군사", "국방정책", "안보정책", "국방력", "군사력", "국방비", "군사시설", "국방시설", "안보시설", "국방협력", "안보협력"],
                "description": "국방력 강화, 안보 체계 구축, 국방 협력"
            }
        }
        
        # 지역 키워드 매핑
        self.regional_keywords = self._load_regional_keywords()
    
    def _load_regional_keywords(self) -> Dict[str, List[str]]:
        """지역별 키워드 로드"""
        return {
            "서울": ["서울", "서울시", "서울특별시", "강남", "강북", "강동", "강서", "관악", "광진", "구로", "금천", "노원", "도봉", "동대문", "동작", "마포", "서대문", "서초", "성동", "성북", "송파", "양천", "영등포", "용산", "은평", "종로", "중구", "중랑"],
            "부산": ["부산", "부산시", "부산광역시", "강서", "금정", "기장", "남구", "동구", "동래", "부산진", "북구", "사상", "사하", "서구", "수영", "연제", "영도", "중구", "해운대"],
            "대구": ["대구", "대구시", "대구광역시", "군위", "남구", "달서", "달성", "동구", "북구", "서구", "수성", "중구"],
            "인천": ["인천", "인천시", "인천광역시", "강화", "계양", "남동", "동구", "미추홀", "부평", "서구", "연수", "옹진", "중구"],
            "광주": ["광주", "광주시", "광주광역시", "광산", "남구", "동구", "북구", "서구"],
            "대전": ["대전", "대전시", "대전광역시", "대덕", "동구", "서구", "유성", "중구"],
            "울산": ["울산", "울산시", "울산광역시", "남구", "동구", "북구", "울주", "중구"],
            "세종": ["세종", "세종시", "세종특별자치시"],
            "경기": ["경기", "경기도", "가평", "고양", "과천", "광명", "광주", "구리", "군포", "김포", "남양주", "동두천", "부천", "성남", "수원", "시흥", "안산", "안성", "안양", "양주", "양평", "여주", "연천", "오산", "용인", "의왕", "의정부", "이천", "파주", "평택", "포천", "하남", "화성"],
            "강원": ["강원", "강원도", "강릉", "고성", "동해", "삼척", "속초", "양구", "양양", "영월", "원주", "인제", "정선", "철원", "춘천", "태백", "평창", "홍천", "화천", "횡성"],
            "충북": ["충북", "충청북도", "괴산", "단양", "보은", "영동", "옥천", "음성", "제천", "증평", "진천", "청주", "충주"],
            "충남": ["충남", "충청남도", "계룡", "공주", "금산", "논산", "당진", "보령", "부여", "서산", "서천", "아산", "예산", "천안", "청양", "태안", "홍성"],
            "전북": ["전북", "전라북도", "고창", "군산", "김제", "남원", "무주", "부안", "순창", "완주", "익산", "임실", "장수", "전주", "정읍", "진안"],
            "전남": ["전남", "전라남도", "강진", "고흥", "곡성", "광양", "구례", "나주", "담양", "목포", "무안", "보성", "순천", "신안", "여수", "영광", "영암", "완도", "장성", "장흥", "진도", "함평", "해남", "화순"],
            "경북": ["경북", "경상북도", "경산", "경주", "고령", "구미", "김천", "문경", "봉화", "상주", "성주", "안동", "영덕", "영양", "영주", "영천", "예천", "울릉", "울진", "의성", "청도", "청송", "칠곡", "포항"],
            "경남": ["경남", "경상남도", "거제", "거창", "고성", "김해", "남해", "밀양", "사천", "산청", "양산", "의령", "진주", "창녕", "창원", "통영", "하동", "함안", "함양", "합천"],
            "제주": ["제주", "제주도", "제주특별자치도", "제주시", "서귀포"]
        }
    
    def extract_text_from_pdf(self) -> str:
        """PDF에서 텍스트 추출"""
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
    
    def preprocess_text(self, text: str) -> List[str]:
        """텍스트 전처리"""
        print("🔧 텍스트 전처리 중...")
        
        # 문장 구분자로 분리 (더 다양한 구분자 사용)
        sentence_endings = ['.', '!', '?', '。', '！', '？', '\n', '\r\n']
        
        sentences = []
        current_sentence = ""
        
        for char in text:
            current_sentence += char
            
            if char in sentence_endings and len(current_sentence.strip()) > 5:
                cleaned_sentence = current_sentence.strip()
                # 불필요한 문자 제거
                cleaned_sentence = re.sub(r'[^\w\s가-힣]', ' ', cleaned_sentence)
                cleaned_sentence = re.sub(r'\s+', ' ', cleaned_sentence)
                
                if len(cleaned_sentence) > 10:  # 최소 길이 확인
                    sentences.append(cleaned_sentence)
                
                current_sentence = ""
        
        # 마지막 문장 처리
        if current_sentence.strip():
            cleaned_sentence = re.sub(r'[^\w\s가-힣]', ' ', current_sentence.strip())
            cleaned_sentence = re.sub(r'\s+', ' ', cleaned_sentence)
            if len(cleaned_sentence) > 10:
                sentences.append(cleaned_sentence)
        
        print(f"✅ 전처리 완료: {len(sentences):,}개 문장")
        return sentences
    
    def extract_keywords_with_frequency(self, sentences: List[str]) -> Dict[str, int]:
        """키워드 빈도 분석"""
        print("🔍 키워드 빈도 분석 중...")
        
        all_words = []
        
        for sentence in sentences:
            if self.analyzer:
                # 한국어 형태소 분석
                try:
                    words = self.analyzer.morphs(sentence)
                    # 명사만 추출
                    nouns = [word for word in words if len(word) > 1 and word.isalpha()]
                    all_words.extend(nouns)
                except:
                    # 형태소 분석 실패시 단순 분할
                    words = sentence.split()
                    all_words.extend([word for word in words if len(word) > 1])
            else:
                # 형태소 분석기 없이 단순 분할
                words = sentence.split()
                all_words.extend([word for word in words if len(word) > 1])
        
        # 불용어 제거
        stop_words = {'것', '등', '및', '또한', '따라서', '그러나', '하지만', '그리고', '또는', '따라', '이에', '이를', '이로', '이와', '이의', '이를', '이에', '이로', '이와', '이의'}
        filtered_words = [word for word in all_words if word not in stop_words]
        
        # 빈도 계산
        word_freq = Counter(filtered_words)
        
        print(f"✅ 키워드 빈도 분석 완료: {len(word_freq):,}개 고유 단어")
        return dict(word_freq)
    
    def analyze_regional_topics(self, sentences: List[str]) -> Dict[str, Any]:
        """지역별 토픽 분석"""
        print("🗺️ 지역별 토픽 분석 중...")
        
        regional_data = {}
        
        for region_name, region_keywords in self.regional_keywords.items():
            print(f"  📍 {region_name} 분석 중...")
            
            # 해당 지역 언급 문장들 찾기
            region_sentences = []
            for sentence in sentences:
                if any(keyword in sentence for keyword in region_keywords):
                    region_sentences.append(sentence)
            
            if not region_sentences:
                continue
            
            # 토픽별 점수 계산
            topic_scores = {}
            dominant_topics = []
            
            for topic_name, topic_info in self.comprehensive_topic_categories.items():
                score = 0
                for sentence in region_sentences:
                    for keyword in topic_info['keywords']:
                        if keyword in sentence:
                            score += 1
                
                if score > 0:
                    topic_scores[topic_name] = score
            
            # 상위 토픽 선정 (점수 기준)
            if topic_scores:
                sorted_topics = sorted(topic_scores.items(), key=lambda x: x[1], reverse=True)
                dominant_topics = [topic for topic, score in sorted_topics[:5]]
            
            # 정책 공약 추출
            promises = self._extract_promises(region_sentences)
            
            regional_data[region_name] = {
                'region_name': region_name,
                'level': self._get_region_level(region_name),
                'mention_count': len(region_sentences),
                'dominant_topics': dominant_topics,
                'topic_scores': topic_scores,
                'interpretation': self._generate_interpretation(region_name, dominant_topics, topic_scores),
                'promises': promises[:10],  # 상위 10개 공약
                'confidence_score': self._calculate_confidence_score(topic_scores),
                'sample_sentences': region_sentences[:5]  # 샘플 문장 5개
            }
        
        print(f"✅ 지역별 토픽 분석 완료: {len(regional_data)}개 지역")
        return regional_data
    
    def _extract_promises(self, sentences: List[str]) -> List[str]:
        """정책 공약 추출"""
        promises = []
        
        # 공약 관련 키워드 패턴
        promise_patterns = [
            r'을\s*위한\s*[가-힣]+',
            r'를\s*위한\s*[가-힣]+',
            r'을\s*통한\s*[가-힣]+',
            r'를\s*통한\s*[가-힣]+',
            r'을\s*위해\s*[가-힣]+',
            r'를\s*위해\s*[가-힣]+',
            r'건설',
            r'조성',
            r'구축',
            r'개발',
            r'확충',
            r'지원',
            r'강화',
            r'개선'
        ]
        
        for sentence in sentences:
            for pattern in promise_patterns:
                matches = re.findall(pattern, sentence)
                promises.extend(matches)
        
        # 중복 제거 및 길이 제한
        unique_promises = list(set(promises))
        filtered_promises = [p for p in unique_promises if 3 <= len(p) <= 50]
        
        return filtered_promises
    
    def _get_region_level(self, region_name: str) -> str:
        """지역 레벨 판단"""
        if region_name in ["서울", "부산", "대구", "인천", "광주", "대전", "울산", "세종"]:
            return "광역시도"
        elif region_name in ["경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주"]:
            return "도"
        else:
            return "시군구"
    
    def _generate_interpretation(self, region_name: str, dominant_topics: List[str], topic_scores: Dict[str, int]) -> str:
        """지역별 해석 생성"""
        if not dominant_topics:
            return f"{region_name}에 대한 정책적 논의가 진행되고 있으나 특정 분야에 집중되지는 않음"
        
        top_topic = dominant_topics[0]
        top_score = topic_scores.get(top_topic, 0)
        
        if top_score >= 10:
            return f"{region_name}은 {top_topic} 분야에서 강한 관심을 보이며, 이는 해당 지역의 주요 정책 이슈임"
        elif top_score >= 5:
            return f"{region_name}은 {top_topic} 분야에 상당한 관심을 보이며, 관련 정책 논의가 활발함"
        else:
            return f"{region_name}은 {top_topic} 분야에 관심을 보이며, 관련 정책 개발이 필요함"
    
    def _calculate_confidence_score(self, topic_scores: Dict[str, int]) -> int:
        """신뢰도 점수 계산 (0-10)"""
        if not topic_scores:
            return 0
        
        max_score = max(topic_scores.values())
        total_score = sum(topic_scores.values())
        
        if total_score >= 20:
            return min(10, max_score // 2)
        elif total_score >= 10:
            return min(8, max_score // 2)
        elif total_score >= 5:
            return min(6, max_score)
        else:
            return min(4, max_score)
    
    def run_comprehensive_analysis(self) -> Dict[str, Any]:
        """종합 분석 실행"""
        print("🚀 정책선거문화 문서 종합 분석 시작!")
        print("=" * 60)
        
        # 1. PDF 텍스트 추출
        full_text = self.extract_text_from_pdf()
        
        # 2. 텍스트 전처리
        sentences = self.preprocess_text(full_text)
        
        # 3. 키워드 빈도 분석
        keyword_frequency = self.extract_keywords_with_frequency(sentences)
        
        # 4. 지역별 토픽 분석
        regional_topics = self.analyze_regional_topics(sentences)
        
        # 5. 전체 토픽 통계
        overall_topic_stats = self._calculate_overall_topic_stats(regional_topics)
        
        # 6. 결과 통합
        comprehensive_results = {
            "document_info": self.analysis_results['document_info'],
            "analysis_metadata": {
                "analysis_date": datetime.now().isoformat(),
                "total_sentences": len(sentences),
                "total_keywords": len(keyword_frequency),
                "total_regions": len(regional_topics),
                "total_topics": len(self.comprehensive_topic_categories),
                "analyzer_used": KOREAN_ANALYZER or "none"
            },
            "comprehensive_topic_categories": self.comprehensive_topic_categories,
            "keyword_frequency_analysis": dict(list(keyword_frequency.items())[:100]),  # 상위 100개
            "regional_topics": regional_topics,
            "overall_topic_statistics": overall_topic_stats,
            "top_promises_by_region": self._extract_top_promises_by_region(regional_topics)
        }
        
        print("=" * 60)
        print("🎉 종합 분석 완료!")
        print(f"📊 분석 결과 요약:")
        print(f"  • 총 지역: {len(regional_topics)}개")
        print(f"  • 총 토픽: {len(self.comprehensive_topic_categories)}개")
        print(f"  • 총 문장: {len(sentences):,}개")
        print(f"  • 총 키워드: {len(keyword_frequency):,}개")
        
        return comprehensive_results
    
    def _calculate_overall_topic_stats(self, regional_topics: Dict[str, Any]) -> Dict[str, Any]:
        """전체 토픽 통계 계산"""
        topic_counts = defaultdict(int)
        topic_total_scores = defaultdict(int)
        
        for region_data in regional_topics.values():
            for topic, score in region_data['topic_scores'].items():
                topic_counts[topic] += 1
                topic_total_scores[topic] += score
        
        # 상위 토픽 선정
        sorted_topics = sorted(topic_total_scores.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "most_discussed_topics": [topic for topic, score in sorted_topics[:10]],
            "topic_frequency": dict(topic_counts),
            "topic_total_scores": dict(topic_total_scores),
            "average_topics_per_region": sum(topic_counts.values()) / len(regional_topics) if regional_topics else 0
        }
    
    def _extract_top_promises_by_region(self, regional_topics: Dict[str, Any]) -> Dict[str, List[str]]:
        """지역별 주요 공약 추출"""
        top_promises = {}
        
        for region_name, region_data in regional_topics.items():
            promises = region_data.get('promises', [])
            if promises:
                top_promises[region_name] = promises[:5]  # 상위 5개
        
        return top_promises
    
    def save_results(self, results: Dict[str, Any], output_dir: str = None) -> str:
        """분석 결과 저장"""
        if output_dir is None:
            output_dir = os.path.join(os.path.dirname(__file__), "comprehensive_policy_analysis")
        
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # JSON 파일로 저장
        json_file = os.path.join(output_dir, f"comprehensive_policy_analysis_{timestamp}.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        # 프론트엔드용 요약 파일 저장
        frontend_data = {
            "last_updated": results["analysis_metadata"]["analysis_date"],
            "total_regions": results["analysis_metadata"]["total_regions"],
            "comprehensive_topic_categories": results["comprehensive_topic_categories"],
            "regional_data": results["regional_topics"]
        }
        
        frontend_file = os.path.join(output_dir, f"comprehensive_regional_topics_frontend_{timestamp}.json")
        with open(frontend_file, 'w', encoding='utf-8') as f:
            json.dump(frontend_data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 분석 결과 저장 완료:")
        print(f"  📄 전체 결과: {json_file}")
        print(f"  🖥️ 프론트엔드용: {frontend_file}")
        
        return json_file

def main():
    """메인 실행 함수"""
    pdf_file_path = "/Users/hopidaay/Desktop/231215_정책선거문화_확산을_위한_언론기사_빅데이터_분석.pdf"
    
    if not os.path.exists(pdf_file_path):
        print(f"❌ PDF 파일을 찾을 수 없습니다: {pdf_file_path}")
        return
    
    analyzer = ComprehensivePolicyTopicAnalyzer(pdf_file_path)
    results = analyzer.run_comprehensive_analysis()
    analyzer.save_results(results)
    
    print("\n🎊 정책선거문화 문서 종합 분석 완료!")
    print("📈 더 많은 토픽과 세밀한 분석이 완료되었습니다!")

if __name__ == "__main__":
    main()
