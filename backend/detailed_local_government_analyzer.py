#!/usr/bin/env python3
"""
개별 지자체별 상세 토픽 및 공약 분석기
정책선거문화 문서에서 시군구, 읍면동 단위까지 세밀하게 분석
"""

import os
import json
import re
import logging
from datetime import datetime
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Any
import fitz

logger = logging.getLogger(__name__)

class DetailedLocalGovernmentAnalyzer:
    """개별 지자체별 상세 분석기"""
    
    def __init__(self, pdf_file_path: str):
        self.pdf_file = pdf_file_path
        self.analysis_results = {}
        
        # 모든 지자체 매핑 (광역시도 → 시군구 → 읍면동)
        self.local_government_structure = self._load_local_government_structure()
        
        # 정책 공약 패턴
        self.policy_promise_patterns = [
            # 건설/개발 관련
            r'([가-힣]+건설|[가-힣]+개발|[가-힣]+조성|[가-힣]+구축|[가-힣]+설치)',
            r'([가-힣]+을\s*위한\s*[가-힣]+)',
            r'([가-힣]+를\s*위한\s*[가-힣]+)',
            r'([가-힣]+을\s*통한\s*[가-힣]+)',
            r'([가-힣]+를\s*통한\s*[가-힣]+)',
            # 지원/혜택 관련
            r'([가-힣]+지원|[가-힣]+혜택|[가-힣]+보조|[가-힣]+할인)',
            r'([가-힣]+확충|[가-힣]+강화|[가-힣]+개선|[가-힣]+증대)',
            # 정책 관련
            r'([가-힣]+정책|[가-힣]+제도|[가-힣]+사업|[가-힣]+프로그램)',
            r'([가-힣]+센터|[가-힣]+복지관|[가-힣]+문화관|[가-힣]+도서관)',
            # 인프라 관련
            r'([가-힣]+도로|[가-힣]+교통|[가-힣]+지하철|[가-힣]+버스)',
            r'([가-힣]+공원|[가-힣]+체육관|[가-힣]+병원|[가-힣]+학교)',
        ]
        
        # 토픽별 키워드 확장
        self.enhanced_topic_keywords = {
            "경제정책": {
                "keywords": ["일자리", "취업", "창업", "경제성장", "소득", "임금", "고용", "실업", "경제활동", "사업", "투자", "금융", "중소기업", "스타트업", "벤처", "경제지원", "경제개발", "산업육성", "수출", "수입", "무역", "경제협력", "고용창출", "일자리창출", "취업지원", "창업지원", "경제지원", "산업지원", "기업지원", "벤처지원", "스타트업지원", "중소기업지원"],
                "promise_keywords": ["일자리창출", "취업지원", "창업지원", "경제지원", "산업육성", "기업지원", "벤처지원", "스타트업지원"]
            },
            "주거정책": {
                "keywords": ["주택", "부동산", "임대", "전세", "월세", "아파트", "집값", "주거", "분양", "매매", "주택공급", "공공주택", "임대주택", "청년주택", "신축", "재개발", "재건축", "도시계획", "택지개발", "주거복지", "주거지원", "주택지원", "임대지원", "전세지원", "월세지원", "공공주택건설", "임대주택건설", "청년주택건설"],
                "promise_keywords": ["주택공급", "공공주택건설", "임대주택건설", "청년주택건설", "주거지원", "임대지원", "전세지원"]
            },
            "교육정책": {
                "keywords": ["교육", "학교", "대학", "입시", "사교육", "교육비", "학습", "학생", "교사", "교육과정", "학원", "보습", "교육혁신", "디지털교육", "온라인교육", "교육시설", "교육환경", "교육지원", "장학금", "교육복지", "교육시설건설", "학교건설", "교육지원", "사교육비지원", "교육비지원", "장학금지원", "교육복지지원"],
                "promise_keywords": ["교육시설건설", "학교건설", "교육지원", "사교육비지원", "교육비지원", "장학금지원", "교육복지지원"]
            },
            "복지정책": {
                "keywords": ["복지", "의료", "건강보험", "연금", "육아", "보육", "사회보장", "복지혜택", "지원금", "돌봄", "노인복지", "장애인복지", "기초생활보장", "생활보조", "의료비지원", "치료비", "간병", "요양", "복지시설", "복지센터", "복지관", "복지지원", "의료지원", "돌봄지원", "육아지원", "보육지원", "노인지원", "장애인지원"],
                "promise_keywords": ["복지시설건설", "복지센터건설", "복지관건설", "복지지원", "의료지원", "돌봄지원", "육아지원", "보육지원"]
            },
            "환경정책": {
                "keywords": ["환경", "기후", "에너지", "미세먼지", "재생에너지", "친환경", "탄소", "오염", "녹색", "지속가능", "대기질", "수질", "토양", "폐기물", "재활용", "에너지절약", "신재생에너지", "태양광", "풍력", "환경보전", "환경개선", "환경정화", "환경지원", "재생에너지지원", "친환경지원", "환경보전지원"],
                "promise_keywords": ["환경개선", "환경정화", "환경보전", "재생에너지지원", "친환경지원", "환경보전지원"]
            },
            "교통정책": {
                "keywords": ["교통", "대중교통", "지하철", "버스", "도로", "주차", "교통체증", "이동", "접근성", "인프라", "대중교통망", "교통망", "지하철연장", "버스노선", "도시철도", "고속도로", "국도", "지방도", "교통개선", "교통지원", "대중교통지원", "지하철지원", "버스지원", "도로지원", "교통인프라지원"],
                "promise_keywords": ["교통개선", "대중교통개선", "지하철연장", "버스노선개선", "도로개선", "교통인프라지원"]
            },
            "문화정책": {
                "keywords": ["문화", "예술", "공연", "전시", "축제", "관광", "여가", "스포츠", "체육", "도서관", "박물관", "문화시설", "문화공간", "문화행사", "문화프로그램", "문화유산", "전통문화", "현대문화", "문화지원", "예술지원", "공연지원", "전시지원", "축제지원", "관광지원", "스포츠지원", "체육지원"],
                "promise_keywords": ["문화시설건설", "문화센터건설", "도서관건설", "박물관건설", "문화지원", "예술지원", "공연지원", "축제지원"]
            },
            "안전정책": {
                "keywords": ["안전", "재난", "재해", "소방", "응급", "범죄", "사고", "위험", "보안", "치안", "방범", "CCTV", "안전시설", "재난대응", "응급의료", "구조", "구급", "화재", "지진", "태풍", "안전지원", "재난지원", "소방지원", "응급지원", "치안지원", "방범지원"],
                "promise_keywords": ["안전시설건설", "소방시설건설", "응급시설건설", "CCTV설치", "안전지원", "재난지원", "소방지원", "응급지원"]
            }
        }
    
    def _load_local_government_structure(self) -> Dict[str, Any]:
        """지방자치단체 구조 로드"""
        return {
            "서울특별시": {
                "level": "광역시도",
                "sigungu": [
                    "강남구", "강동구", "강북구", "강서구", "관악구", "광진구", "구로구", "금천구", "노원구", "도봉구", 
                    "동대문구", "동작구", "마포구", "서대문구", "서초구", "성동구", "성북구", "송파구", "양천구", 
                    "영등포구", "용산구", "은평구", "종로구", "중구", "중랑구"
                ]
            },
            "부산광역시": {
                "level": "광역시도", 
                "sigungu": [
                    "강서구", "금정구", "기장군", "남구", "동구", "동래구", "부산진구", "북구", "사상구", "사하구", 
                    "서구", "수영구", "연제구", "영도구", "중구", "해운대구"
                ]
            },
            "대구광역시": {
                "level": "광역시도",
                "sigungu": ["군위군", "남구", "달서구", "달성군", "동구", "북구", "서구", "수성구", "중구"]
            },
            "인천광역시": {
                "level": "광역시도",
                "sigungu": ["강화군", "계양구", "남동구", "동구", "미추홀구", "부평구", "서구", "연수구", "옹진군", "중구"]
            },
            "광주광역시": {
                "level": "광역시도",
                "sigungu": ["광산구", "남구", "동구", "북구", "서구"]
            },
            "대전광역시": {
                "level": "광역시도",
                "sigungu": ["대덕구", "동구", "서구", "유성구", "중구"]
            },
            "울산광역시": {
                "level": "광역시도",
                "sigungu": ["남구", "동구", "북구", "울주군", "중구"]
            },
            "세종특별자치시": {
                "level": "광역시도",
                "sigungu": ["세종시"]
            },
            "경기도": {
                "level": "도",
                "sigungu": [
                    "가평군", "고양시", "과천시", "광명시", "광주시", "구리시", "군포시", "김포시", "남양주시", "동두천시",
                    "부천시", "성남시", "수원시", "시흥시", "안산시", "안성시", "안양시", "양주시", "양평군", "여주시",
                    "연천군", "오산시", "용인시", "의왕시", "의정부시", "이천시", "파주시", "평택시", "포천시", "하남시", "화성시"
                ]
            },
            "강원도": {
                "level": "도",
                "sigungu": [
                    "강릉시", "고성군", "동해시", "삼척시", "속초시", "양구군", "양양군", "영월군", "원주시", "인제군",
                    "정선군", "철원군", "춘천시", "태백시", "평창군", "홍천군", "화천군", "횡성군"
                ]
            },
            "충청북도": {
                "level": "도",
                "sigungu": ["괴산군", "단양군", "보은군", "영동군", "옥천군", "음성군", "제천시", "증평군", "진천군", "청주시", "충주시"]
            },
            "충청남도": {
                "level": "도", 
                "sigungu": ["계룡시", "공주시", "금산군", "논산시", "당진시", "보령시", "부여군", "서산시", "서천군", "아산시", "예산군", "천안시", "청양군", "태안군", "홍성군"]
            },
            "전라북도": {
                "level": "도",
                "sigungu": ["고창군", "군산시", "김제시", "남원시", "무주군", "부안군", "순창군", "완주군", "익산시", "임실군", "장수군", "전주시", "정읍시", "진안군"]
            },
            "전라남도": {
                "level": "도",
                "sigungu": ["강진군", "고흥군", "곡성군", "광양시", "구례군", "나주시", "담양군", "목포시", "무안군", "보성군", "순천시", "신안군", "여수시", "영광군", "영암군", "완도군", "장성군", "장흥군", "진도군", "함평군", "해남군", "화순군"]
            },
            "경상북도": {
                "level": "도",
                "sigungu": ["경산시", "경주시", "고령군", "구미시", "김천시", "문경시", "봉화군", "상주시", "성주군", "안동시", "영덕군", "영양군", "영주시", "영천시", "예천군", "울릉군", "울진군", "의성군", "청도군", "청송군", "칠곡군", "포항시"]
            },
            "경상남도": {
                "level": "도",
                "sigungu": ["거제시", "거창군", "고성군", "김해시", "남해군", "밀양시", "사천시", "산청군", "양산시", "의령군", "진주시", "창녕군", "창원시", "통영시", "하동군", "함안군", "함양군", "합천군"]
            },
            "제주특별자치도": {
                "level": "도",
                "sigungu": ["제주시", "서귀포시"]
            }
        }
    
    def extract_document_structure(self) -> Dict[str, Any]:
        """문서 구조 분석"""
        print("📄 문서 구조 상세 분석 중...")
        
        doc = fitz.open(self.pdf_file)
        document_structure = {
            "total_pages": len(doc),
            "local_government_pages": defaultdict(list),
            "individual_sigungu_pages": defaultdict(list),
            "topic_structure": []
        }
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            
            # 광역 지자체 패턴 찾기
            for gov_name in self.local_government_structure.keys():
                if gov_name in text:
                    document_structure["local_government_pages"][gov_name].append(page_num + 1)
            
            # 개별 시군구 패턴 찾기
            for gov_name, gov_info in self.local_government_structure.items():
                if "sigungu" in gov_info:
                    for sigungu in gov_info["sigungu"]:
                        if sigungu in text:
                            document_structure["individual_sigungu_pages"][sigungu].append({
                                "page": page_num + 1,
                                "parent_government": gov_name,
                                "text_preview": text[:300] + "..." if len(text) > 300 else text
                            })
            
            # 토픽 구조 분석
            if any(topic in text for topic in ["토픽", "정책", "공약", "민생", "이슈"]):
                document_structure["topic_structure"].append({
                    "page": page_num + 1,
                    "has_topic_content": True,
                    "text_preview": text[:200] + "..." if len(text) > 200 else text
                })
        
        doc.close()
        
        print(f"✅ 문서 구조 분석 완료:")
        print(f"  📊 총 페이지: {document_structure['total_pages']}개")
        print(f"  🏛️ 광역 지자체 언급: {len(document_structure['local_government_pages'])}개")
        print(f"  🏘️ 개별 시군구 언급: {len(document_structure['individual_sigungu_pages'])}개")
        print(f"  📋 토픽 관련 페이지: {len(document_structure['topic_structure'])}개")
        
        return document_structure
    
    def extract_local_government_topics(self, document_structure: Dict[str, Any]) -> Dict[str, Any]:
        """개별 지자체별 토픽 추출"""
        print("🗺️ 개별 지자체별 토픽 추출 중...")
        
        doc = fitz.open(self.pdf_file)
        local_government_analysis = {}
        
        # 각 시군구별 분석
        for sigungu, page_info_list in document_structure["individual_sigungu_pages"].items():
            print(f"  📍 {sigungu} 분석 중...")
            
            sigungu_text = ""
            sigungu_pages = []
            
            # 해당 시군구가 언급된 모든 페이지의 텍스트 수집
            for page_info in page_info_list:
                page_num = page_info["page"] - 1  # 0-based index
                page = doc[page_num]
                page_text = page.get_text()
                sigungu_text += page_text + "\n"
                sigungu_pages.append(page_num + 1)
            
            if not sigungu_text:
                continue
            
            # 토픽별 점수 계산
            topic_scores = {}
            topic_sentences = defaultdict(list)
            
            for topic_name, topic_info in self.enhanced_topic_keywords.items():
                score = 0
                sentences = []
                
                for keyword in topic_info["keywords"]:
                    if keyword in sigungu_text:
                        # 해당 키워드가 포함된 문장들 찾기
                        sentences_with_keyword = self._extract_sentences_with_keyword(sigungu_text, keyword)
                        sentences.extend(sentences_with_keyword)
                        score += len(sentences_with_keyword)
                
                if score > 0:
                    topic_scores[topic_name] = score
                    topic_sentences[topic_name] = sentences[:10]  # 상위 10개 문장
            
            # 정책 공약 추출
            promises = self._extract_detailed_promises(sigungu_text)
            
            # 상위 토픽 선정
            dominant_topics = sorted(topic_scores.items(), key=lambda x: x[1], reverse=True)[:5]
            dominant_topic_names = [topic for topic, score in dominant_topics]
            
            local_government_analysis[sigungu] = {
                "sigungu_name": sigungu,
                "parent_government": page_info_list[0]["parent_government"] if page_info_list else "Unknown",
                "level": "시군구",
                "analyzed_pages": sigungu_pages,
                "mention_count": len(sigungu_pages),
                "dominant_topics": dominant_topic_names,
                "topic_scores": topic_scores,
                "topic_sentences": dict(topic_sentences),
                "promises": promises[:15],  # 상위 15개 공약
                "confidence_score": self._calculate_confidence_score(topic_scores),
                "interpretation": self._generate_detailed_interpretation(sigungu, dominant_topics, topic_scores),
                "text_length": len(sigungu_text)
            }
        
        doc.close()
        
        print(f"✅ 개별 지자체 분석 완료: {len(local_government_analysis)}개 시군구")
        return local_government_analysis
    
    def _extract_sentences_with_keyword(self, text: str, keyword: str) -> List[str]:
        """키워드가 포함된 문장들 추출"""
        sentences = []
        
        # 문장 단위로 분할
        text_sentences = re.split(r'[.!?。！？\n]', text)
        
        for sentence in text_sentences:
            sentence = sentence.strip()
            if keyword in sentence and len(sentence) > 10:
                sentences.append(sentence)
        
        return sentences
    
    def _extract_detailed_promises(self, text: str) -> List[str]:
        """상세한 정책 공약 추출"""
        promises = []
        
        for pattern in self.policy_promise_patterns:
            matches = re.findall(pattern, text)
            promises.extend(matches)
        
        # 토픽별 공약 키워드로 추가 추출
        for topic_name, topic_info in self.enhanced_topic_keywords.items():
            if "promise_keywords" in topic_info:
                for promise_keyword in topic_info["promise_keywords"]:
                    if promise_keyword in text:
                        # 해당 키워드 주변 문맥 추출
                        context = self._extract_context_around_keyword(text, promise_keyword)
                        promises.extend(context)
        
        # 중복 제거 및 정제
        unique_promises = list(set(promises))
        filtered_promises = []
        
        for promise in unique_promises:
            # 길이 및 품질 필터링
            if 3 <= len(promise) <= 100 and not re.match(r'^[0-9\s\-\.]+$', promise):
                filtered_promises.append(promise)
        
        return filtered_promises
    
    def _extract_context_around_keyword(self, text: str, keyword: str) -> List[str]:
        """키워드 주변 문맥 추출"""
        contexts = []
        
        # 키워드 위치 찾기
        start = 0
        while True:
            pos = text.find(keyword, start)
            if pos == -1:
                break
            
            # 키워드 앞뒤로 50자씩 추출
            context_start = max(0, pos - 50)
            context_end = min(len(text), pos + len(keyword) + 50)
            context = text[context_start:context_end].strip()
            
            if len(context) > 10:
                contexts.append(context)
            
            start = pos + 1
        
        return contexts
    
    def _calculate_confidence_score(self, topic_scores: Dict[str, int]) -> int:
        """신뢰도 점수 계산"""
        if not topic_scores:
            return 0
        
        max_score = max(topic_scores.values())
        total_score = sum(topic_scores.values())
        
        if total_score >= 50:
            return min(10, max_score // 3)
        elif total_score >= 30:
            return min(8, max_score // 2)
        elif total_score >= 15:
            return min(6, max_score)
        else:
            return min(4, max_score)
    
    def _generate_detailed_interpretation(self, sigungu: str, dominant_topics: List[Tuple[str, int]], topic_scores: Dict[str, int]) -> str:
        """상세한 해석 생성"""
        if not dominant_topics:
            return f"{sigungu}에 대한 구체적인 정책 논의가 확인되지 않음"
        
        top_topic, top_score = dominant_topics[0]
        
        if top_score >= 20:
            return f"{sigungu}은 {top_topic} 분야에서 매우 강한 관심을 보이며, 이는 해당 지역의 핵심 정책 이슈로 판단됨"
        elif top_score >= 10:
            return f"{sigungu}은 {top_topic} 분야에서 상당한 관심을 보이며, 관련 정책 개발이 활발히 진행되고 있음"
        elif top_score >= 5:
            return f"{sigungu}은 {top_topic} 분야에 관심을 보이며, 관련 정책 논의가 이루어지고 있음"
        else:
            return f"{sigungu}은 {top_topic} 분야에 기본적인 관심을 보이며, 향후 정책 개발이 필요함"
    
    def run_detailed_analysis(self) -> Dict[str, Any]:
        """상세 분석 실행"""
        print("🚀 개별 지자체별 상세 분석 시작!")
        print("=" * 60)
        
        # 1. 문서 구조 분석
        document_structure = self.extract_document_structure()
        
        # 2. 개별 지자체별 토픽 추출
        local_government_analysis = self.extract_local_government_topics(document_structure)
        
        # 3. 전체 통계 계산
        overall_statistics = self._calculate_overall_statistics(local_government_analysis)
        
        # 4. 결과 통합
        detailed_results = {
            "document_info": {
                "file_path": self.pdf_file,
                "analysis_date": datetime.now().isoformat(),
                "total_pages": document_structure["total_pages"]
            },
            "document_structure": document_structure,
            "local_government_analysis": local_government_analysis,
            "overall_statistics": overall_statistics,
            "enhanced_topic_keywords": self.enhanced_topic_keywords
        }
        
        print("=" * 60)
        print("🎉 상세 분석 완료!")
        print(f"📊 분석 결과 요약:")
        print(f"  • 분석된 시군구: {len(local_government_analysis)}개")
        print(f"  • 총 토픽 카테고리: {len(self.enhanced_topic_keywords)}개")
        print(f"  • 총 정책 공약: {sum(len(gov['promises']) for gov in local_government_analysis.values())}개")
        
        return detailed_results
    
    def _calculate_overall_statistics(self, local_government_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """전체 통계 계산"""
        statistics = {
            "total_sigungu_analyzed": len(local_government_analysis),
            "topic_frequency": defaultdict(int),
            "topic_total_scores": defaultdict(int),
            "parent_government_distribution": defaultdict(int),
            "average_promises_per_sigungu": 0,
            "most_active_sigungu": None,
            "topic_concentration": {}
        }
        
        total_promises = 0
        max_activity = 0
        
        for sigungu, analysis in local_government_analysis.items():
            # 토픽 빈도 계산
            for topic in analysis["dominant_topics"]:
                statistics["topic_frequency"][topic] += 1
            
            # 토픽 점수 합계
            for topic, score in analysis["topic_scores"].items():
                statistics["topic_total_scores"][topic] += score
            
            # 상위 지자체 분포
            statistics["parent_government_distribution"][analysis["parent_government"]] += 1
            
            # 공약 수 집계
            promise_count = len(analysis["promises"])
            total_promises += promise_count
            
            # 가장 활발한 시군구
            if promise_count > max_activity:
                max_activity = promise_count
                statistics["most_active_sigungu"] = sigungu
        
        statistics["average_promises_per_sigungu"] = total_promises / len(local_government_analysis) if local_government_analysis else 0
        
        # 토픽 집중도 계산
        for topic, freq in statistics["topic_frequency"].items():
            statistics["topic_concentration"][topic] = freq / len(local_government_analysis)
        
        return statistics
    
    def save_results(self, results: Dict[str, Any], output_dir: str = None) -> str:
        """분석 결과 저장"""
        if output_dir is None:
            output_dir = os.path.join(os.path.dirname(__file__), "detailed_local_government_analysis")
        
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # JSON 파일로 저장
        json_file = os.path.join(output_dir, f"detailed_local_government_analysis_{timestamp}.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"💾 상세 분석 결과 저장 완료: {json_file}")
        return json_file

def main():
    """메인 실행 함수"""
    pdf_file_path = "/Users/hopidaay/Desktop/231215_정책선거문화_확산을_위한_언론기사_빅데이터_분석.pdf"
    
    if not os.path.exists(pdf_file_path):
        print(f"❌ PDF 파일을 찾을 수 없습니다: {pdf_file_path}")
        return
    
    analyzer = DetailedLocalGovernmentAnalyzer(pdf_file_path)
    results = analyzer.run_detailed_analysis()
    analyzer.save_results(results)
    
    print("\n🎊 개별 지자체별 상세 분석 완료!")
    print("📈 시군구 단위까지 세밀한 토픽과 공약 분석이 완료되었습니다!")

if __name__ == "__main__":
    main()
