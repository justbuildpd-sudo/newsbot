#!/usr/bin/env python3
"""
매니페스토 텍스트마이닝 시스템
8회 지방선거 출마자 공약을 분석하여 검증 가능한 인사이트 제공
"""

import os
import json
import re
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from collections import Counter, defaultdict
import numpy as np
from pathlib import Path

# NLP 라이브러리
try:
    from konlpy.tag import Okt, Mecab, Komoran
    import pandas as pd
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    from sklearn.decomposition import LatentDirichletAllocation
    from sklearn.metrics.pairwise import cosine_similarity
    import matplotlib.pyplot as plt
    import seaborn as sns
    plt.rcParams['font.family'] = ['AppleGothic', 'Malgun Gothic', 'DejaVu Sans']
    NLP_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ NLP 라이브러리 설치 필요: {e}")
    NLP_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class ManifestoAnalysis:
    """매니페스토 분석 결과"""
    candidate_name: str
    party: str
    region: str
    position_type: str
    total_pledges: int
    
    # 텍스트 분석 결과
    total_words: int
    unique_words: int
    avg_pledge_length: float
    
    # 키워드 분석
    top_keywords: List[Tuple[str, int]]
    category_distribution: Dict[str, int]
    
    # 감정 분석
    sentiment_score: float
    confidence_level: str
    
    # 구체성 분석
    specificity_score: float
    budget_mentions: int
    timeline_mentions: int
    
    # 유사성 분석
    similar_candidates: List[Tuple[str, float]]

class ManifestoTextMiningSystem:
    """매니페스토 텍스트마이닝 시스템"""
    
    def __init__(self):
        self.base_dir = "/Users/hopidaay/newsbot-kr"
        self.data_dir = "/Users/hopidaay/newsbot-kr/backend/election_data"
        self.analysis_dir = "/Users/hopidaay/newsbot-kr/backend/manifesto_analysis"
        
        # 디렉토리 생성
        Path(self.analysis_dir).mkdir(parents=True, exist_ok=True)
        
        # 한국어 형태소 분석기 초기화
        self.analyzer = None
        self._initialize_korean_analyzer()
        
        # 정치 도메인 특화 사전
        self.political_keywords = {
            "정책분야": ["경제", "주거", "교육", "복지", "환경", "교통", "문화", "안전", "보건", "일자리"],
            "실행동사": ["공급", "지원", "확대", "강화", "개선", "건설", "조성", "도입", "운영", "제공"],
            "대상": ["시민", "청년", "어르신", "학생", "주민", "가정", "기업", "소상공인"],
            "규모": ["만호", "억원", "조원", "천명", "만명", "%", "배", "년", "개월"],
            "감정": {
                "긍정": ["발전", "성장", "향상", "개선", "혁신", "활성화", "증진", "확충"],
                "부정": ["해결", "완화", "경감", "방지", "개선", "극복", "해소"]
            }
        }
        
        # 분석 결과 저장소
        self.analysis_results = {}
        self.candidates_data = {}
        
    def _initialize_korean_analyzer(self):
        """한국어 형태소 분석기 초기화"""
        if not NLP_AVAILABLE:
            print("⚠️ NLP 라이브러리 없음 - 기본 분석만 수행")
            return
        
        # Okt > Komoran > Mecab 순으로 시도
        analyzers = [
            ("Okt", Okt),
            ("Komoran", Komoran),
            ("Mecab", Mecab)
        ]
        
        for name, analyzer_class in analyzers:
            try:
                self.analyzer = analyzer_class()
                print(f"✅ {name} 형태소 분석기 초기화 성공")
                return
            except Exception as e:
                print(f"⚠️ {name} 초기화 실패: {e}")
                continue
        
        print("⚠️ 모든 형태소 분석기 초기화 실패 - 기본 텍스트 분석 사용")
    
    def load_candidates_data(self, json_file_path: str) -> Dict[str, Any]:
        """출마자 데이터 로드"""
        try:
            print("📂 출마자 데이터 로드 중...")
            
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.candidates_data = data
            
            # 통계 정보
            total_candidates = data["statistics"]["total_candidates"]
            total_pledges = data["statistics"]["total_pledges"]
            
            print(f"✅ 데이터 로드 완료")
            print(f"  👥 출마자: {total_candidates}명")
            print(f"  📋 공약: {total_pledges}개")
            
            return data
            
        except Exception as e:
            logger.error(f"데이터 로드 실패: {e}")
            return {}
    
    def extract_text_features(self, text: str) -> Dict[str, Any]:
        """텍스트에서 특징 추출"""
        features = {
            "total_chars": len(text),
            "total_words": len(text.split()),
            "sentences": len(re.split(r'[.!?。！？]', text)),
            "numbers": len(re.findall(r'\d+', text)),
            "budget_mentions": len(re.findall(r'\d+[조억천만]*원', text)),
            "timeline_mentions": len(re.findall(r'\d+[년개월주일]', text)),
            "percentage_mentions": len(re.findall(r'\d+%', text))
        }
        
        # 한국어 형태소 분석 (가능한 경우)
        if self.analyzer:
            try:
                morphs = self.analyzer.morphs(text)
                pos_tags = self.analyzer.pos(text)
                
                features.update({
                    "morphs": morphs,
                    "unique_morphs": len(set(morphs)),
                    "pos_distribution": Counter([pos for word, pos in pos_tags]),
                    "nouns": [word for word, pos in pos_tags if pos.startswith('N')],
                    "verbs": [word for word, pos in pos_tags if pos.startswith('V')]
                })
            except Exception as e:
                logger.warning(f"형태소 분석 실패: {e}")
        
        return features
    
    def analyze_pledge_specificity(self, pledge: Dict[str, Any]) -> Dict[str, Any]:
        """공약의 구체성 분석"""
        content = pledge.get("content", "")
        
        specificity_indicators = {
            "has_budget": bool(re.search(r'\d+[조억천만]*원', content)),
            "has_timeline": bool(re.search(r'\d+[년개월주일]', content)),
            "has_quantity": bool(re.search(r'\d+[만천백십]*[호개명]', content)),
            "has_percentage": bool(re.search(r'\d+%', content)),
            "has_location": bool(pledge.get("target_region") and pledge["target_region"] != "전체"),
            "has_method": any(keyword in content for keyword in self.political_keywords["실행동사"])
        }
        
        # 구체성 점수 계산 (0-100)
        specificity_score = sum(specificity_indicators.values()) / len(specificity_indicators) * 100
        
        # 실현가능성 평가
        feasibility_factors = {
            "realistic_budget": self._assess_budget_realism(content),
            "reasonable_timeline": self._assess_timeline_realism(content),
            "clear_method": self._assess_method_clarity(content)
        }
        
        feasibility_score = sum(feasibility_factors.values()) / len(feasibility_factors) * 100
        
        return {
            "specificity_indicators": specificity_indicators,
            "specificity_score": specificity_score,
            "feasibility_factors": feasibility_factors,
            "feasibility_score": feasibility_score,
            "overall_quality": (specificity_score + feasibility_score) / 2
        }
    
    def _assess_budget_realism(self, content: str) -> float:
        """예산 현실성 평가"""
        budget_matches = re.findall(r'(\d+)([조억천만]*원)', content)
        if not budget_matches:
            return 0.5  # 예산 언급 없음
        
        for amount_str, unit in budget_matches:
            try:
                amount = int(amount_str)
                if "조" in unit and amount > 100:  # 100조원 초과시 비현실적
                    return 0.2
                elif "조" in unit and amount > 10:  # 10조원 초과시 어려움
                    return 0.6
                elif "억" in unit and amount > 10000:  # 1조원 초과시 검토 필요
                    return 0.7
                else:
                    return 0.9  # 현실적 범위
            except ValueError:
                continue
        
        return 0.8
    
    def _assess_timeline_realism(self, content: str) -> float:
        """일정 현실성 평가"""
        timeline_matches = re.findall(r'(\d+)([년개월])', content)
        if not timeline_matches:
            return 0.5  # 일정 언급 없음
        
        for period_str, unit in timeline_matches:
            try:
                period = int(period_str)
                if unit == "년" and period <= 4:  # 임기 내
                    return 0.9
                elif unit == "년" and period <= 8:  # 2임기 내
                    return 0.7
                elif unit == "개월" and period <= 48:  # 4년 내
                    return 0.9
                else:
                    return 0.4  # 장기간 소요
            except ValueError:
                continue
        
        return 0.8
    
    def _assess_method_clarity(self, content: str) -> float:
        """실행방법 명확성 평가"""
        method_keywords = self.political_keywords["실행동사"]
        method_count = sum(1 for keyword in method_keywords if keyword in content)
        
        if method_count == 0:
            return 0.3  # 실행방법 불명확
        elif method_count <= 2:
            return 0.7  # 적절한 수준
        else:
            return 0.9  # 구체적 방법 제시
    
    def analyze_candidate_manifesto(self, candidate_data: Dict[str, Any]) -> ManifestoAnalysis:
        """개별 후보자 매니페스토 종합 분석"""
        print(f"🔍 {candidate_data['name']} 매니페스토 분석 중...")
        
        pledges = candidate_data.get("pledges", [])
        all_text = " ".join([pledge.get("content", "") for pledge in pledges])
        
        # 기본 텍스트 특징 추출
        text_features = self.extract_text_features(all_text)
        
        # 공약별 구체성 분석
        pledge_analyses = []
        total_specificity = 0
        total_feasibility = 0
        
        for pledge in pledges:
            analysis = self.analyze_pledge_specificity(pledge)
            pledge_analyses.append(analysis)
            total_specificity += analysis["specificity_score"]
            total_feasibility += analysis["feasibility_score"]
        
        avg_specificity = total_specificity / len(pledges) if pledges else 0
        avg_feasibility = total_feasibility / len(pledges) if pledges else 0
        
        # 키워드 분석
        top_keywords = self._extract_top_keywords(all_text)
        
        # 카테고리 분포
        category_dist = Counter([pledge.get("category", "기타") for pledge in pledges])
        
        # 감정 분석 (간단한 규칙 기반)
        sentiment_score = self._analyze_sentiment(all_text)
        
        # 신뢰도 평가
        confidence_level = self._assess_confidence_level(avg_specificity, avg_feasibility)
        
        analysis = ManifestoAnalysis(
            candidate_name=candidate_data["name"],
            party=candidate_data["party"],
            region=candidate_data["region"],
            position_type=candidate_data["position_type"],
            total_pledges=len(pledges),
            
            total_words=text_features["total_words"],
            unique_words=text_features.get("unique_morphs", text_features["total_words"]),
            avg_pledge_length=text_features["total_words"] / len(pledges) if pledges else 0,
            
            top_keywords=top_keywords,
            category_distribution=dict(category_dist),
            
            sentiment_score=sentiment_score,
            confidence_level=confidence_level,
            
            specificity_score=avg_specificity,
            budget_mentions=text_features["budget_mentions"],
            timeline_mentions=text_features["timeline_mentions"],
            
            similar_candidates=[]  # 나중에 계산
        )
        
        return analysis
    
    def _extract_top_keywords(self, text: str, top_k: int = 10) -> List[Tuple[str, int]]:
        """상위 키워드 추출"""
        if self.analyzer:
            try:
                nouns = [word for word, pos in self.analyzer.pos(text) if pos.startswith('N') and len(word) > 1]
                return Counter(nouns).most_common(top_k)
            except:
                pass
        
        # 기본 단어 분리
        words = [word for word in text.split() if len(word) > 1]
        return Counter(words).most_common(top_k)
    
    def _analyze_sentiment(self, text: str) -> float:
        """감정 분석 (규칙 기반)"""
        positive_words = self.political_keywords["감정"]["긍정"]
        negative_words = self.political_keywords["감정"]["부정"]
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        total_count = positive_count + negative_count
        if total_count == 0:
            return 0.5  # 중립
        
        return positive_count / total_count
    
    def _assess_confidence_level(self, specificity: float, feasibility: float) -> str:
        """신뢰도 수준 평가"""
        avg_score = (specificity + feasibility) / 2
        
        if avg_score >= 80:
            return "매우 높음"
        elif avg_score >= 60:
            return "높음"
        elif avg_score >= 40:
            return "보통"
        elif avg_score >= 20:
            return "낮음"
        else:
            return "매우 낮음"
    
    def calculate_similarity_matrix(self, analyses: List[ManifestoAnalysis]) -> np.ndarray:
        """후보자 간 유사성 매트릭스 계산"""
        if not NLP_AVAILABLE:
            print("⚠️ scikit-learn 없음 - 유사성 분석 건너뜀")
            return np.eye(len(analyses))
        
        try:
            # 각 후보자의 키워드를 텍스트로 변환
            texts = []
            for analysis in analyses:
                keywords_text = " ".join([kw for kw, count in analysis.top_keywords])
                texts.append(keywords_text)
            
            # TF-IDF 벡터화
            vectorizer = TfidfVectorizer(max_features=100)
            tfidf_matrix = vectorizer.fit_transform(texts)
            
            # 코사인 유사도 계산
            similarity_matrix = cosine_similarity(tfidf_matrix)
            
            return similarity_matrix
            
        except Exception as e:
            logger.warning(f"유사성 계산 실패: {e}")
            return np.eye(len(analyses))
    
    def generate_comprehensive_report(self, analyses: List[ManifestoAnalysis]) -> Dict[str, Any]:
        """종합 분석 보고서 생성"""
        print("📊 종합 분석 보고서 생성 중...")
        
        # 전체 통계
        total_candidates = len(analyses)
        total_pledges = sum(a.total_pledges for a in analyses)
        
        # 당별 분석
        party_stats = defaultdict(list)
        for analysis in analyses:
            party_stats[analysis.party].append(analysis)
        
        # 지역별 분석
        region_stats = defaultdict(list)
        for analysis in analyses:
            region_stats[analysis.region].append(analysis)
        
        # 직책별 분석
        position_stats = defaultdict(list)
        for analysis in analyses:
            position_stats[analysis.position_type].append(analysis)
        
        # 품질 분석
        quality_distribution = {
            "매우 높음": len([a for a in analyses if a.confidence_level == "매우 높음"]),
            "높음": len([a for a in analyses if a.confidence_level == "높음"]),
            "보통": len([a for a in analyses if a.confidence_level == "보통"]),
            "낮음": len([a for a in analyses if a.confidence_level == "낮음"]),
            "매우 낮음": len([a for a in analyses if a.confidence_level == "매우 낮음"])
        }
        
        # 카테고리별 공약 분포
        all_categories = defaultdict(int)
        for analysis in analyses:
            for category, count in analysis.category_distribution.items():
                all_categories[category] += count
        
        report = {
            "analysis_date": datetime.now().isoformat(),
            "summary": {
                "total_candidates": total_candidates,
                "total_pledges": total_pledges,
                "avg_pledges_per_candidate": total_pledges / total_candidates if total_candidates > 0 else 0,
                "avg_specificity_score": np.mean([a.specificity_score for a in analyses]),
                "avg_words_per_candidate": np.mean([a.total_words for a in analyses])
            },
            "quality_distribution": quality_distribution,
            "category_distribution": dict(all_categories),
            "party_analysis": {
                party: {
                    "candidates": len(candidates),
                    "avg_specificity": np.mean([c.specificity_score for c in candidates]),
                    "avg_pledges": np.mean([c.total_pledges for c in candidates]),
                    "confidence_levels": Counter([c.confidence_level for c in candidates])
                }
                for party, candidates in party_stats.items()
            },
            "region_analysis": {
                region: {
                    "candidates": len(candidates),
                    "avg_specificity": np.mean([c.specificity_score for c in candidates]),
                    "dominant_categories": Counter([
                        cat for c in candidates 
                        for cat in c.category_distribution.keys()
                    ]).most_common(3)
                }
                for region, candidates in region_stats.items()
            },
            "position_analysis": {
                position: {
                    "candidates": len(candidates),
                    "avg_specificity": np.mean([c.specificity_score for c in candidates]),
                    "avg_budget_mentions": np.mean([c.budget_mentions for c in candidates])
                }
                for position, candidates in position_stats.items()
            },
            "top_performers": {
                "highest_specificity": sorted(analyses, key=lambda x: x.specificity_score, reverse=True)[:3],
                "most_comprehensive": sorted(analyses, key=lambda x: x.total_pledges, reverse=True)[:3],
                "most_detailed": sorted(analyses, key=lambda x: x.total_words, reverse=True)[:3]
            }
        }
        
        return report
    
    def save_analysis_results(self, analyses: List[ManifestoAnalysis], report: Dict[str, Any]) -> Tuple[str, str]:
        """분석 결과 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 개별 분석 결과
        analyses_file = os.path.join(self.analysis_dir, f"manifesto_analyses_{timestamp}.json")
        analyses_data = [
            {
                "candidate_name": a.candidate_name,
                "party": a.party,
                "region": a.region,
                "position_type": a.position_type,
                "total_pledges": a.total_pledges,
                "total_words": a.total_words,
                "unique_words": a.unique_words,
                "avg_pledge_length": a.avg_pledge_length,
                "top_keywords": a.top_keywords,
                "category_distribution": a.category_distribution,
                "sentiment_score": a.sentiment_score,
                "confidence_level": a.confidence_level,
                "specificity_score": a.specificity_score,
                "budget_mentions": a.budget_mentions,
                "timeline_mentions": a.timeline_mentions
            }
            for a in analyses
        ]
        
        with open(analyses_file, 'w', encoding='utf-8') as f:
            json.dump(analyses_data, f, ensure_ascii=False, indent=2)
        
        # 종합 보고서
        report_file = os.path.join(self.analysis_dir, f"comprehensive_report_{timestamp}.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"💾 분석 결과 저장 완료:")
        print(f"  📊 개별 분석: {analyses_file}")
        print(f"  📋 종합 보고서: {report_file}")
        
        return analyses_file, report_file

def main():
    """메인 실행 함수"""
    print("🔍 매니페스토 텍스트마이닝 시스템")
    print("=" * 60)
    
    mining_system = ManifestoTextMiningSystem()
    
    try:
        # 1. 출마자 데이터 로드
        data_file = "/Users/hopidaay/newsbot-kr/backend/election_data/comprehensive_8th_election_candidates_20250920_124544.json"
        candidates_data = mining_system.load_candidates_data(data_file)
        
        if not candidates_data:
            print("❌ 데이터 로드 실패")
            return
        
        # 2. 개별 후보자 분석
        print("\n🔍 개별 후보자 매니페스토 분석 중...")
        analyses = []
        
        for district_id, district_info in candidates_data["districts"].items():
            for candidate_id, candidate_info in district_info["candidates"].items():
                analysis = mining_system.analyze_candidate_manifesto(candidate_info)
                analyses.append(analysis)
        
        # 3. 유사성 분석
        print("\n📊 후보자 간 유사성 분석 중...")
        similarity_matrix = mining_system.calculate_similarity_matrix(analyses)
        
        # 4. 종합 보고서 생성
        report = mining_system.generate_comprehensive_report(analyses)
        
        # 5. 결과 저장
        analyses_file, report_file = mining_system.save_analysis_results(analyses, report)
        
        print("\n" + "=" * 60)
        print("🎉 매니페스토 텍스트마이닝 완료!")
        
        # 주요 결과 출력
        print(f"\n📊 분석 결과 요약:")
        print(f"  분석 후보자: {report['summary']['total_candidates']}명")
        print(f"  총 공약: {report['summary']['total_pledges']}개")
        print(f"  평균 구체성: {report['summary']['avg_specificity_score']:.1f}점")
        
        print(f"\n🏆 품질 분포:")
        for level, count in report['quality_distribution'].items():
            print(f"  {level}: {count}명")
        
        print(f"\n📋 주요 공약 분야:")
        for category, count in sorted(report['category_distribution'].items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {category}: {count}개")
        
        return analyses, report
        
    except Exception as e:
        logger.error(f"텍스트마이닝 실패: {e}")
        print(f"❌ 분석 실패: {e}")
        return None, None

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
