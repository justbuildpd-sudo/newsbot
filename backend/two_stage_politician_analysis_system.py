#!/usr/bin/env python3
"""
2단계 정치인 분석 시스템
1단계: 지역 분석 (기존 민생토픽 데이터 활용)
2단계: 정치인 요구사항 분석 (입법 발의 내용과 비교)
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class RegionalNeed:
    """지역 요구사항"""
    topic: str
    score: int
    description: str
    keywords: List[str]
    priority_level: str  # "높음", "중간", "낮음"

@dataclass
class PoliticianResponse:
    """정치인 대응"""
    bill_title: str
    bill_number: str
    proposal_date: str
    main_content: str
    target_topics: List[str]
    effectiveness_score: int  # 1-10점

@dataclass
class AnalysisResult:
    """분석 결과"""
    politician_name: str
    region_name: str
    regional_needs: List[RegionalNeed]
    politician_responses: List[PoliticianResponse]
    match_score: int  # 지역 요구와 정치인 대응의 매칭 점수
    gap_analysis: Dict[str, Any]

class TwoStagePoliticianAnalyzer:
    """2단계 정치인 분석기"""
    
    def __init__(self):
        self.base_dir = "/Users/hopidaay/newsbot-kr"
        self.backend_dir = "/Users/hopidaay/newsbot-kr/backend"
        
        # 기존 지역 민생토픽 데이터 로드
        self.regional_data = self._load_regional_data()
        
        # 샘플 국회의원 입법 데이터
        self.sample_legislation_data = self._create_sample_legislation_data()
        
        # 토픽별 가중치
        self.topic_weights = {
            "경제정책": 1.0,
            "주거정책": 1.0,
            "교육정책": 0.9,
            "복지정책": 0.8,
            "환경정책": 0.7,
            "교통정책": 0.8,
            "문화정책": 0.6,
            "안전정책": 0.9
        }
    
    def _load_regional_data(self) -> Dict[str, Any]:
        """기존 지역 민생토픽 데이터 로드"""
        try:
            # 실제 환경에서는 detailed_local_government_analysis 데이터를 로드
            detailed_analysis_dir = os.path.join(self.backend_dir, "detailed_local_government_analysis")
            if os.path.exists(detailed_analysis_dir):
                files = [f for f in os.listdir(detailed_analysis_dir) if f.startswith("detailed_local_government_analysis_")]
                if files:
                    latest_file = max(files)
                    with open(os.path.join(detailed_analysis_dir, latest_file), 'r', encoding='utf-8') as f:
                        return json.load(f)
            
            # 샘플 데이터
            return {
                "local_government_analysis": {
                    "강남구": {
                        "region_name": "강남구",
                        "parent_government": "서울특별시",
                        "dominant_topics": ["주거정책", "문화정책", "교통정책"],
                        "topic_scores": {"주거정책": 85, "문화정책": 51, "교통정책": 63},
                        "promises": ["주택공급확대", "문화시설건설", "교통인프라개선"]
                    },
                    "성남시": {
                        "region_name": "성남시",
                        "parent_government": "경기도",
                        "dominant_topics": ["교육정책", "주거정책", "경제정책"],
                        "topic_scores": {"교육정책": 68, "주거정책": 45, "경제정책": 38},
                        "promises": ["교육환경개선", "주택공급", "일자리창출"]
                    }
                }
            }
        except Exception as e:
            logger.error(f"지역 데이터 로드 실패: {e}")
            return {}
    
    def _create_sample_legislation_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """샘플 국회의원 입법 발의 데이터 생성"""
        return {
            "이재명": [
                {
                    "bill_title": "주택공급 촉진을 위한 특별법 개정안",
                    "bill_number": "2024-001",
                    "proposal_date": "2024-03-15",
                    "main_content": "공공주택 공급 확대 및 주택가격 안정화를 위한 제도 개선",
                    "target_topics": ["주거정책"],
                    "keywords": ["공공주택", "주택공급", "가격안정", "임대주택"],
                    "effectiveness_score": 8
                },
                {
                    "bill_title": "교육환경 개선 및 사교육비 경감 지원법",
                    "bill_number": "2024-002",
                    "proposal_date": "2024-04-20",
                    "main_content": "공교육 강화 및 사교육비 부담 완화를 위한 종합 지원책",
                    "target_topics": ["교육정책"],
                    "keywords": ["공교육", "사교육비", "교육지원", "학습환경"],
                    "effectiveness_score": 7
                },
                {
                    "bill_title": "지역경제 활성화를 위한 중소기업 지원법",
                    "bill_number": "2024-003",
                    "proposal_date": "2024-05-10",
                    "main_content": "중소기업 육성 및 일자리 창출을 위한 금융·세제 지원 확대",
                    "target_topics": ["경제정책"],
                    "keywords": ["중소기업", "일자리창출", "금융지원", "세제혜택"],
                    "effectiveness_score": 9
                }
            ],
            "김기현": [
                {
                    "bill_title": "부산 신공항 건설 특별법",
                    "bill_number": "2024-101",
                    "proposal_date": "2024-02-28",
                    "main_content": "부산 가덕도 신공항 건설을 위한 법적 근거 마련",
                    "target_topics": ["교통정책", "경제정책"],
                    "keywords": ["신공항", "교통인프라", "지역발전", "관광산업"],
                    "effectiveness_score": 8
                },
                {
                    "bill_title": "해양관광 진흥법 개정안",
                    "bill_number": "2024-102",
                    "proposal_date": "2024-06-05",
                    "main_content": "해양관광 활성화를 통한 지역경제 발전 및 일자리 창출",
                    "target_topics": ["문화정책", "경제정책"],
                    "keywords": ["해양관광", "관광산업", "지역경제", "문화콘텐츠"],
                    "effectiveness_score": 7
                }
            ],
            "안철수": [
                {
                    "bill_title": "디지털 교육 혁신법",
                    "bill_number": "2024-201",
                    "proposal_date": "2024-01-12",
                    "main_content": "AI·빅데이터 활용 맞춤형 교육시스템 구축",
                    "target_topics": ["교육정책"],
                    "keywords": ["디지털교육", "AI교육", "맞춤형학습", "교육혁신"],
                    "effectiveness_score": 9
                },
                {
                    "bill_title": "스타트업 육성 특별법 개정안",
                    "bill_number": "2024-202",
                    "proposal_date": "2024-07-18",
                    "main_content": "스타트업 생태계 조성 및 벤처투자 활성화 방안",
                    "target_topics": ["경제정책"],
                    "keywords": ["스타트업", "벤처투자", "창업지원", "혁신생태계"],
                    "effectiveness_score": 8
                }
            ]
        }
    
    def analyze_stage1_regional_needs(self, region_name: str) -> List[RegionalNeed]:
        """1단계: 지역 요구사항 분석"""
        regional_needs = []
        
        if region_name not in self.regional_data.get("local_government_analysis", {}):
            logger.warning(f"지역 데이터를 찾을 수 없습니다: {region_name}")
            return regional_needs
        
        region_info = self.regional_data["local_government_analysis"][region_name]
        
        for topic in region_info.get("dominant_topics", []):
            score = region_info.get("topic_scores", {}).get(topic, 0)
            
            # 우선순위 결정
            if score >= 70:
                priority = "높음"
            elif score >= 40:
                priority = "중간"
            else:
                priority = "낮음"
            
            # 토픽별 설명 및 키워드
            topic_info = self._get_topic_info(topic)
            
            regional_need = RegionalNeed(
                topic=topic,
                score=score,
                description=topic_info["description"],
                keywords=topic_info["keywords"],
                priority_level=priority
            )
            
            regional_needs.append(regional_need)
        
        # 점수 순으로 정렬
        regional_needs.sort(key=lambda x: x.score, reverse=True)
        
        return regional_needs
    
    def analyze_stage2_politician_response(self, politician_name: str) -> List[PoliticianResponse]:
        """2단계: 정치인 대응 분석"""
        politician_responses = []
        
        if politician_name not in self.sample_legislation_data:
            logger.warning(f"정치인 입법 데이터를 찾을 수 없습니다: {politician_name}")
            return politician_responses
        
        bills = self.sample_legislation_data[politician_name]
        
        for bill in bills:
            response = PoliticianResponse(
                bill_title=bill["bill_title"],
                bill_number=bill["bill_number"],
                proposal_date=bill["proposal_date"],
                main_content=bill["main_content"],
                target_topics=bill["target_topics"],
                effectiveness_score=bill["effectiveness_score"]
            )
            
            politician_responses.append(response)
        
        # 효과성 점수 순으로 정렬
        politician_responses.sort(key=lambda x: x.effectiveness_score, reverse=True)
        
        return politician_responses
    
    def calculate_match_score(self, regional_needs: List[RegionalNeed], politician_responses: List[PoliticianResponse]) -> int:
        """지역 요구와 정치인 대응의 매칭 점수 계산"""
        if not regional_needs or not politician_responses:
            return 0
        
        total_score = 0
        max_possible_score = 0
        
        for need in regional_needs:
            max_possible_score += need.score * self.topic_weights.get(need.topic, 1.0)
            
            # 해당 토픽에 대한 정치인 대응 찾기
            matching_responses = [
                response for response in politician_responses 
                if need.topic in response.target_topics
            ]
            
            if matching_responses:
                # 가장 높은 효과성 점수를 가진 대응 선택
                best_response = max(matching_responses, key=lambda x: x.effectiveness_score)
                match_contribution = (need.score * best_response.effectiveness_score / 10) * self.topic_weights.get(need.topic, 1.0)
                total_score += match_contribution
        
        if max_possible_score == 0:
            return 0
        
        return int((total_score / max_possible_score) * 100)
    
    def generate_gap_analysis(self, regional_needs: List[RegionalNeed], politician_responses: List[PoliticianResponse]) -> Dict[str, Any]:
        """격차 분석 생성"""
        gap_analysis = {
            "covered_topics": [],
            "uncovered_topics": [],
            "over_addressed_topics": [],
            "recommendations": []
        }
        
        # 지역 요구 토픽들
        regional_topics = {need.topic: need for need in regional_needs}
        
        # 정치인이 다룬 토픽들
        politician_topics = set()
        for response in politician_responses:
            politician_topics.update(response.target_topics)
        
        # 커버된 토픽
        for topic in regional_topics:
            if topic in politician_topics:
                gap_analysis["covered_topics"].append({
                    "topic": topic,
                    "regional_score": regional_topics[topic].score,
                    "priority": regional_topics[topic].priority_level
                })
        
        # 커버되지 않은 토픽 (높은 우선순위)
        for topic, need in regional_topics.items():
            if topic not in politician_topics and need.priority_level in ["높음", "중간"]:
                gap_analysis["uncovered_topics"].append({
                    "topic": topic,
                    "regional_score": need.score,
                    "priority": need.priority_level,
                    "description": need.description
                })
        
        # 과도하게 다룬 토픽 (지역 요구는 낮은데 많이 다룬 경우)
        for topic in politician_topics:
            if topic not in regional_topics or regional_topics[topic].priority_level == "낮음":
                gap_analysis["over_addressed_topics"].append(topic)
        
        # 추천사항 생성
        if gap_analysis["uncovered_topics"]:
            gap_analysis["recommendations"].append("높은 우선순위 미해결 토픽에 대한 입법 발의 필요")
        
        if gap_analysis["over_addressed_topics"]:
            gap_analysis["recommendations"].append("지역 요구도가 낮은 토픽보다 핵심 민생 이슈에 집중 필요")
        
        if len(gap_analysis["covered_topics"]) / len(regional_topics) > 0.8:
            gap_analysis["recommendations"].append("지역 요구사항을 잘 반영하고 있음. 효과성 강화에 집중")
        
        return gap_analysis
    
    def comprehensive_analysis(self, politician_name: str, region_name: str) -> AnalysisResult:
        """종합 분석 수행"""
        # 1단계: 지역 요구사항 분석
        regional_needs = self.analyze_stage1_regional_needs(region_name)
        
        # 2단계: 정치인 대응 분석
        politician_responses = self.analyze_stage2_politician_response(politician_name)
        
        # 매칭 점수 계산
        match_score = self.calculate_match_score(regional_needs, politician_responses)
        
        # 격차 분석
        gap_analysis = self.generate_gap_analysis(regional_needs, politician_responses)
        
        return AnalysisResult(
            politician_name=politician_name,
            region_name=region_name,
            regional_needs=regional_needs,
            politician_responses=politician_responses,
            match_score=match_score,
            gap_analysis=gap_analysis
        )
    
    def _get_topic_info(self, topic: str) -> Dict[str, Any]:
        """토픽 정보 반환"""
        topic_info_map = {
            "경제정책": {
                "description": "일자리 창출, 경제 활성화, 중소기업 지원",
                "keywords": ["일자리", "창업", "중소기업", "경제성장", "투자유치"]
            },
            "주거정책": {
                "description": "주택 공급, 부동산 안정화, 주거 복지",
                "keywords": ["주택공급", "임대주택", "주거안정", "부동산", "주택가격"]
            },
            "교육정책": {
                "description": "교육 환경 개선, 사교육비 경감",
                "keywords": ["교육환경", "사교육비", "공교육", "교육지원", "학습권"]
            },
            "복지정책": {
                "description": "사회복지 확충, 의료 서비스 개선",
                "keywords": ["사회복지", "의료서비스", "복지혜택", "돌봄서비스", "건강보험"]
            },
            "환경정책": {
                "description": "환경 보호, 지속가능한 발전",
                "keywords": ["환경보호", "기후변화", "재생에너지", "대기질", "친환경"]
            },
            "교통정책": {
                "description": "교통 인프라 개선, 대중교통 확충",
                "keywords": ["교통인프라", "대중교통", "교통체증", "도로건설", "교통안전"]
            },
            "문화정책": {
                "description": "문화 시설 확충, 관광 산업 발전",
                "keywords": ["문화시설", "관광산업", "문화행사", "예술지원", "여가활동"]
            },
            "안전정책": {
                "description": "안전한 생활 환경 조성",
                "keywords": ["치안", "재난안전", "방범", "응급의료", "안전시설"]
            }
        }
        
        return topic_info_map.get(topic, {
            "description": "기타 정책 분야",
            "keywords": []
        })

def create_sample_analysis():
    """샘플 분석 실행"""
    analyzer = TwoStagePoliticianAnalyzer()
    
    # 샘플 분석: 이재명 의원 vs 성남시 요구사항
    result = analyzer.comprehensive_analysis("이재명", "성남시")
    
    print("🎯 2단계 정치인 분석 결과")
    print("=" * 60)
    print(f"정치인: {result.politician_name}")
    print(f"지역: {result.region_name}")
    print(f"매칭 점수: {result.match_score}/100점")
    print()
    
    print("📊 1단계: 지역 요구사항 분석")
    print("-" * 40)
    for need in result.regional_needs:
        print(f"• {need.topic} ({need.score}점, {need.priority_level} 우선순위)")
        print(f"  - {need.description}")
    print()
    
    print("🏛️ 2단계: 정치인 대응 분석")
    print("-" * 40)
    for response in result.politician_responses:
        print(f"• {response.bill_title}")
        print(f"  - 발의일: {response.proposal_date}")
        print(f"  - 대상 토픽: {', '.join(response.target_topics)}")
        print(f"  - 효과성: {response.effectiveness_score}/10점")
        print(f"  - 내용: {response.main_content}")
    print()
    
    print("📈 격차 분석")
    print("-" * 40)
    print(f"커버된 토픽: {len(result.gap_analysis['covered_topics'])}개")
    print(f"미해결 토픽: {len(result.gap_analysis['uncovered_topics'])}개")
    print(f"과도 대응 토픽: {len(result.gap_analysis['over_addressed_topics'])}개")
    print()
    
    if result.gap_analysis['recommendations']:
        print("💡 추천사항:")
        for rec in result.gap_analysis['recommendations']:
            print(f"  - {rec}")
    
    return result

if __name__ == "__main__":
    create_sample_analysis()
