#!/usr/bin/env python3
"""
매니페스토 검증 서비스
텍스트마이닝 결과를 기반으로 한 종합적인 공약 검증 시스템
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)

class VerificationStatus(Enum):
    """검증 상태"""
    VERIFIED = "검증완료"
    PARTIALLY_VERIFIED = "부분검증"
    UNVERIFIED = "미검증"
    CONTRADICTED = "모순발견"
    IMPOSSIBLE = "실현불가"

class FeasibilityLevel(Enum):
    """실현가능성 수준"""
    VERY_HIGH = "매우높음"
    HIGH = "높음"
    MEDIUM = "보통"
    LOW = "낮음"
    VERY_LOW = "매우낮음"

@dataclass
class PledgeVerification:
    """개별 공약 검증 결과"""
    pledge_title: str
    pledge_content: str
    category: str
    
    # 구체성 검증
    specificity_score: float
    has_budget: bool
    has_timeline: bool
    has_target: bool
    has_method: bool
    
    # 실현가능성 검증
    feasibility_level: FeasibilityLevel
    budget_realism: float
    timeline_realism: float
    method_clarity: float
    
    # 일관성 검증
    consistency_score: float
    contradictions: List[str]
    
    # 검증 상태
    verification_status: VerificationStatus
    verification_notes: List[str]
    
    # 참고 데이터
    similar_pledges: List[Dict[str, Any]]
    related_policies: List[str]

@dataclass
class CandidateVerification:
    """후보자별 종합 검증 결과"""
    candidate_name: str
    party: str
    region: str
    position_type: str
    
    # 전체 공약 검증
    total_pledges: int
    verified_pledges: int
    verification_rate: float
    
    # 품질 지표
    avg_specificity: float
    avg_feasibility: float
    consistency_score: float
    
    # 개별 공약 검증 결과
    pledge_verifications: List[PledgeVerification]
    
    # 종합 평가
    overall_grade: str
    credibility_score: float
    implementation_probability: float
    
    # 주요 발견사항
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]

class ManifestoVerificationService:
    """매니페스토 검증 서비스"""
    
    def __init__(self):
        self.base_dir = "/Users/hopidaay/newsbot-kr"
        self.analysis_dir = "/Users/hopidaay/newsbot-kr/backend/manifesto_analysis"
        self.verification_dir = "/Users/hopidaay/newsbot-kr/backend/manifesto_verification"
        
        # 디렉토리 생성
        Path(self.verification_dir).mkdir(parents=True, exist_ok=True)
        
        # 검증 기준
        self.verification_criteria = {
            "specificity_threshold": 50.0,  # 구체성 기준점
            "feasibility_threshold": 60.0,  # 실현가능성 기준점
            "consistency_threshold": 70.0,  # 일관성 기준점
            "credibility_weights": {
                "specificity": 0.3,
                "feasibility": 0.4,
                "consistency": 0.3
            }
        }
        
        # 정책 분야별 예산 기준 (연간 기준, 억원)
        self.budget_benchmarks = {
            "주거정책": {"min": 1000, "max": 50000, "avg": 10000},
            "교육정책": {"min": 500, "max": 20000, "avg": 5000},
            "교통정책": {"min": 2000, "max": 100000, "avg": 15000},
            "복지정책": {"min": 1000, "max": 30000, "avg": 8000},
            "경제정책": {"min": 500, "max": 200000, "avg": 20000},
            "환경정책": {"min": 300, "max": 10000, "avg": 3000},
            "문화정책": {"min": 100, "max": 5000, "avg": 1000},
            "안전정책": {"min": 500, "max": 15000, "avg": 4000}
        }
        
        # 직책별 권한 범위
        self.authority_scope = {
            "광역단체장": {
                "budget_limit": 100000,  # 10조원
                "policy_areas": ["주거", "교육", "교통", "복지", "경제", "환경", "문화", "안전"],
                "implementation_power": 0.8
            },
            "기초단체장": {
                "budget_limit": 10000,   # 1조원
                "policy_areas": ["주거", "교육", "복지", "환경", "문화", "안전"],
                "implementation_power": 0.6
            },
            "광역의회의원": {
                "budget_limit": 1000,    # 1000억원
                "policy_areas": ["교육", "복지", "환경", "문화"],
                "implementation_power": 0.4
            },
            "기초의회의원": {
                "budget_limit": 100,     # 100억원
                "policy_areas": ["복지", "환경", "문화"],
                "implementation_power": 0.3
            }
        }
        
        # 검증 결과 저장소
        self.verification_results = {}
    
    def load_analysis_results(self, analysis_file: str) -> List[Dict[str, Any]]:
        """텍스트마이닝 분석 결과 로드"""
        try:
            print("📂 텍스트마이닝 결과 로드 중...")
            
            with open(analysis_file, 'r', encoding='utf-8') as f:
                analyses = json.load(f)
            
            print(f"✅ 분석 결과 로드 완료: {len(analyses)}명 후보자")
            return analyses
            
        except Exception as e:
            logger.error(f"분석 결과 로드 실패: {e}")
            return []
    
    def load_candidates_data(self, candidates_file: str) -> Dict[str, Any]:
        """원본 후보자 데이터 로드"""
        try:
            with open(candidates_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"후보자 데이터 로드 실패: {e}")
            return {}
    
    def verify_pledge_specificity(self, pledge: Dict[str, Any]) -> Dict[str, Any]:
        """공약 구체성 검증"""
        content = pledge.get("content", "")
        
        # 구체성 요소 확인
        has_budget = bool(pledge.get("budget") and pledge["budget"] != "예산 확보 후 단계적 추진")
        has_timeline = bool(pledge.get("timeline") and "년" in pledge["timeline"])
        has_target = bool(pledge.get("target_region") and pledge["target_region"] != "전체")
        has_method = len([word for word in ["공급", "지원", "확대", "건설", "조성"] if word in content]) > 0
        
        # 구체성 점수 계산
        specificity_elements = [has_budget, has_timeline, has_target, has_method]
        specificity_score = sum(specificity_elements) / len(specificity_elements) * 100
        
        return {
            "specificity_score": specificity_score,
            "has_budget": has_budget,
            "has_timeline": has_timeline,
            "has_target": has_target,
            "has_method": has_method,
            "specificity_level": self._get_specificity_level(specificity_score)
        }
    
    def verify_pledge_feasibility(self, pledge: Dict[str, Any], position_type: str) -> Dict[str, Any]:
        """공약 실현가능성 검증"""
        category = pledge.get("category", "기타")
        budget_str = pledge.get("budget", "")
        timeline_str = pledge.get("timeline", "")
        
        # 예산 현실성 검증
        budget_realism = self._verify_budget_realism(budget_str, category, position_type)
        
        # 일정 현실성 검증
        timeline_realism = self._verify_timeline_realism(timeline_str, position_type)
        
        # 권한 범위 검증
        authority_check = self._verify_authority_scope(category, position_type)
        
        # 종합 실현가능성 점수
        feasibility_score = (budget_realism + timeline_realism + authority_check) / 3 * 100
        feasibility_level = self._get_feasibility_level(feasibility_score)
        
        return {
            "feasibility_score": feasibility_score,
            "feasibility_level": feasibility_level,
            "budget_realism": budget_realism,
            "timeline_realism": timeline_realism,
            "authority_check": authority_check,
            "implementation_barriers": self._identify_implementation_barriers(pledge, position_type)
        }
    
    def verify_pledge_consistency(self, pledge: Dict[str, Any], all_pledges: List[Dict[str, Any]]) -> Dict[str, Any]:
        """공약 일관성 검증"""
        contradictions = []
        consistency_issues = []
        
        current_category = pledge.get("category", "")
        current_budget = pledge.get("budget", "")
        current_target = pledge.get("target_region", "")
        
        # 다른 공약과의 모순 확인
        for other_pledge in all_pledges:
            if other_pledge == pledge:
                continue
                
            # 같은 분야에서 상충되는 내용 확인
            if other_pledge.get("category") == current_category:
                if self._check_content_contradiction(pledge, other_pledge):
                    contradictions.append(f"{other_pledge.get('title', '')}와 내용 상충")
            
            # 예산 중복 확인
            if self._check_budget_overlap(pledge, other_pledge):
                consistency_issues.append(f"{other_pledge.get('title', '')}와 예산 중복 가능성")
            
            # 대상 지역 중복 확인
            if current_target and other_pledge.get("target_region") == current_target:
                if current_category == other_pledge.get("category"):
                    consistency_issues.append(f"동일 지역 동일 분야 중복 정책")
        
        # 일관성 점수 계산
        consistency_score = max(0, 100 - len(contradictions) * 20 - len(consistency_issues) * 10)
        
        return {
            "consistency_score": consistency_score,
            "contradictions": contradictions,
            "consistency_issues": consistency_issues,
            "consistency_level": self._get_consistency_level(consistency_score)
        }
    
    def verify_individual_pledge(self, pledge: Dict[str, Any], all_pledges: List[Dict[str, Any]], position_type: str) -> PledgeVerification:
        """개별 공약 종합 검증"""
        
        # 구체성 검증
        specificity_result = self.verify_pledge_specificity(pledge)
        
        # 실현가능성 검증
        feasibility_result = self.verify_pledge_feasibility(pledge, position_type)
        
        # 일관성 검증
        consistency_result = self.verify_pledge_consistency(pledge, all_pledges)
        
        # 검증 상태 결정
        verification_status = self._determine_verification_status(
            specificity_result, feasibility_result, consistency_result
        )
        
        # 검증 노트 생성
        verification_notes = self._generate_verification_notes(
            specificity_result, feasibility_result, consistency_result
        )
        
        return PledgeVerification(
            pledge_title=pledge.get("title", ""),
            pledge_content=pledge.get("content", ""),
            category=pledge.get("category", ""),
            
            specificity_score=specificity_result["specificity_score"],
            has_budget=specificity_result["has_budget"],
            has_timeline=specificity_result["has_timeline"],
            has_target=specificity_result["has_target"],
            has_method=specificity_result["has_method"],
            
            feasibility_level=feasibility_result["feasibility_level"],
            budget_realism=feasibility_result["budget_realism"],
            timeline_realism=feasibility_result["timeline_realism"],
            method_clarity=feasibility_result["authority_check"],
            
            consistency_score=consistency_result["consistency_score"],
            contradictions=consistency_result["contradictions"],
            
            verification_status=verification_status,
            verification_notes=verification_notes,
            
            similar_pledges=[],
            related_policies=[]
        )
    
    def verify_candidate_manifesto(self, candidate_data: Dict[str, Any], analysis_data: Dict[str, Any]) -> CandidateVerification:
        """후보자 매니페스토 종합 검증"""
        print(f"🔍 {candidate_data['name']} 매니페스토 검증 중...")
        
        pledges = candidate_data.get("pledges", [])
        position_type = candidate_data.get("position_type", "")
        
        # 개별 공약 검증
        pledge_verifications = []
        for pledge in pledges:
            verification = self.verify_individual_pledge(pledge, pledges, position_type)
            pledge_verifications.append(verification)
        
        # 검증 통계 계산
        verified_count = len([v for v in pledge_verifications if v.verification_status == VerificationStatus.VERIFIED])
        verification_rate = verified_count / len(pledges) * 100 if pledges else 0
        
        avg_specificity = np.mean([v.specificity_score for v in pledge_verifications]) if pledge_verifications else 0
        avg_feasibility = np.mean([v.budget_realism + v.timeline_realism + v.method_clarity for v in pledge_verifications]) / 3 * 100 if pledge_verifications else 0
        avg_consistency = np.mean([v.consistency_score for v in pledge_verifications]) if pledge_verifications else 0
        
        # 신뢰도 점수 계산
        credibility_score = (
            avg_specificity * self.verification_criteria["credibility_weights"]["specificity"] +
            avg_feasibility * self.verification_criteria["credibility_weights"]["feasibility"] +
            avg_consistency * self.verification_criteria["credibility_weights"]["consistency"]
        )
        
        # 종합 등급 산정
        overall_grade = self._calculate_overall_grade(credibility_score)
        
        # 실행 확률 예측
        implementation_probability = self._predict_implementation_probability(
            pledge_verifications, position_type
        )
        
        # 강점, 약점, 권고사항 분석
        strengths, weaknesses, recommendations = self._analyze_candidate_profile(
            pledge_verifications, credibility_score
        )
        
        return CandidateVerification(
            candidate_name=candidate_data["name"],
            party=candidate_data["party"],
            region=candidate_data["region"],
            position_type=position_type,
            
            total_pledges=len(pledges),
            verified_pledges=verified_count,
            verification_rate=verification_rate,
            
            avg_specificity=avg_specificity,
            avg_feasibility=avg_feasibility,
            consistency_score=avg_consistency,
            
            pledge_verifications=pledge_verifications,
            
            overall_grade=overall_grade,
            credibility_score=credibility_score,
            implementation_probability=implementation_probability,
            
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations
        )
    
    def _verify_budget_realism(self, budget_str: str, category: str, position_type: str) -> float:
        """예산 현실성 검증"""
        if not budget_str or "확보 후" in budget_str:
            return 0.3  # 예산 불명확
        
        # 예산 규모 추출
        import re
        budget_match = re.search(r'(\d+)([조억천만]*원)', budget_str)
        if not budget_match:
            return 0.4  # 예산 파싱 실패
        
        amount = int(budget_match.group(1))
        unit = budget_match.group(2)
        
        # 억원 단위로 변환
        if "조" in unit:
            amount_billion = amount * 10000
        elif "억" in unit:
            amount_billion = amount
        elif "천만" in unit:
            amount_billion = amount / 100
        else:
            amount_billion = amount / 100  # 기본 단위 가정
        
        # 분야별 적정 예산과 비교
        benchmark = self.budget_benchmarks.get(category, {"min": 100, "max": 10000, "avg": 1000})
        
        if amount_billion < benchmark["min"]:
            return 0.6  # 과소 예산
        elif amount_billion > benchmark["max"]:
            return 0.4  # 과대 예산
        elif benchmark["min"] <= amount_billion <= benchmark["avg"] * 2:
            return 0.9  # 적정 범위
        else:
            return 0.7  # 다소 과다
    
    def _verify_timeline_realism(self, timeline_str: str, position_type: str) -> float:
        """일정 현실성 검증"""
        if not timeline_str:
            return 0.3  # 일정 불명확
        
        import re
        timeline_match = re.search(r'(\d+)([년개월])', timeline_str)
        if not timeline_match:
            return 0.4  # 일정 파싱 실패
        
        period = int(timeline_match.group(1))
        unit = timeline_match.group(2)
        
        # 월 단위로 변환
        if unit == "년":
            period_months = period * 12
        else:  # 개월
            period_months = period
        
        # 임기와 비교 (지방자치단체장: 4년, 의원: 4년)
        term_months = 48
        
        if period_months <= term_months:
            return 0.9  # 임기 내 실현 가능
        elif period_months <= term_months * 2:
            return 0.6  # 2임기 필요
        else:
            return 0.3  # 장기간 소요
    
    def _verify_authority_scope(self, category: str, position_type: str) -> float:
        """권한 범위 검증"""
        authority = self.authority_scope.get(position_type, {})
        allowed_areas = authority.get("policy_areas", [])
        
        # 카테고리를 간단한 키워드로 매핑
        category_mapping = {
            "주거정책": "주거",
            "교육정책": "교육", 
            "교통정책": "교통",
            "복지정책": "복지",
            "경제정책": "경제",
            "환경정책": "환경",
            "문화정책": "문화",
            "안전정책": "안전"
        }
        
        category_key = category_mapping.get(category, "기타")
        
        if category_key in allowed_areas:
            return authority.get("implementation_power", 0.5)
        else:
            return 0.2  # 권한 범위 벗어남
    
    def _identify_implementation_barriers(self, pledge: Dict[str, Any], position_type: str) -> List[str]:
        """실행 장벽 식별"""
        barriers = []
        
        budget_str = pledge.get("budget", "")
        if "국비" in budget_str and position_type in ["기초단체장", "기초의회의원"]:
            barriers.append("국비 확보 필요")
        
        if "조원" in budget_str:
            barriers.append("대규모 예산 소요")
        
        timeline_str = pledge.get("timeline", "")
        if "년" in timeline_str:
            years = int(timeline_str.split("년")[0].split()[-1])
            if years > 4:
                barriers.append("장기간 소요")
        
        content = pledge.get("content", "")
        if "법" in content or "제도" in content:
            barriers.append("법제도 개정 필요")
        
        return barriers
    
    def _check_content_contradiction(self, pledge1: Dict[str, Any], pledge2: Dict[str, Any]) -> bool:
        """내용 모순 확인"""
        content1 = pledge1.get("content", "").lower()
        content2 = pledge2.get("content", "").lower()
        
        # 간단한 모순 패턴 확인
        contradictory_pairs = [
            (["확대", "증가"], ["축소", "감소"]),
            (["지원", "투자"], ["삭감", "중단"]),
            (["건설", "신설"], ["철거", "폐지"])
        ]
        
        for positive_terms, negative_terms in contradictory_pairs:
            has_positive1 = any(term in content1 for term in positive_terms)
            has_negative2 = any(term in content2 for term in negative_terms)
            
            has_positive2 = any(term in content2 for term in positive_terms)
            has_negative1 = any(term in content1 for term in negative_terms)
            
            if (has_positive1 and has_negative2) or (has_positive2 and has_negative1):
                return True
        
        return False
    
    def _check_budget_overlap(self, pledge1: Dict[str, Any], pledge2: Dict[str, Any]) -> bool:
        """예산 중복 확인"""
        budget1 = pledge1.get("budget", "")
        budget2 = pledge2.get("budget", "")
        
        # 둘 다 대규모 예산인 경우 중복 가능성 높음
        if "조원" in budget1 and "조원" in budget2:
            return True
        
        return False
    
    def _determine_verification_status(self, specificity: Dict, feasibility: Dict, consistency: Dict) -> VerificationStatus:
        """검증 상태 결정"""
        if consistency["contradictions"]:
            return VerificationStatus.CONTRADICTED
        
        if feasibility["feasibility_score"] < 30:
            return VerificationStatus.IMPOSSIBLE
        
        if (specificity["specificity_score"] >= 70 and 
            feasibility["feasibility_score"] >= 70 and 
            consistency["consistency_score"] >= 70):
            return VerificationStatus.VERIFIED
        
        if (specificity["specificity_score"] >= 50 or 
            feasibility["feasibility_score"] >= 50):
            return VerificationStatus.PARTIALLY_VERIFIED
        
        return VerificationStatus.UNVERIFIED
    
    def _generate_verification_notes(self, specificity: Dict, feasibility: Dict, consistency: Dict) -> List[str]:
        """검증 노트 생성"""
        notes = []
        
        if specificity["specificity_score"] < 50:
            notes.append("구체성 부족 - 예산, 일정, 방법 등 세부사항 보완 필요")
        
        if feasibility["budget_realism"] < 0.6:
            notes.append("예산 현실성 검토 필요")
        
        if feasibility["timeline_realism"] < 0.6:
            notes.append("추진 일정 재검토 필요")
        
        if consistency["contradictions"]:
            notes.append(f"다른 공약과 모순: {', '.join(consistency['contradictions'])}")
        
        if len(feasibility.get("implementation_barriers", [])) > 2:
            notes.append("실행 장벽 다수 존재")
        
        return notes
    
    def _get_specificity_level(self, score: float) -> str:
        """구체성 수준 반환"""
        if score >= 75: return "매우구체적"
        elif score >= 50: return "구체적"
        elif score >= 25: return "보통"
        else: return "추상적"
    
    def _get_feasibility_level(self, score: float) -> str:
        """실현가능성 수준 반환"""
        if score >= 80: return "매우높음"
        elif score >= 60: return "높음"
        elif score >= 40: return "보통"
        elif score >= 20: return "낮음"
        else: return "매우낮음"
    
    def _get_consistency_level(self, score: float) -> str:
        """일관성 수준 반환"""
        if score >= 90: return "매우일관적"
        elif score >= 70: return "일관적"
        elif score >= 50: return "보통"
        else: return "비일관적"
    
    def _calculate_overall_grade(self, credibility_score: float) -> str:
        """종합 등급 산정"""
        if credibility_score >= 90: return "A+"
        elif credibility_score >= 85: return "A"
        elif credibility_score >= 80: return "A-"
        elif credibility_score >= 75: return "B+"
        elif credibility_score >= 70: return "B"
        elif credibility_score >= 65: return "B-"
        elif credibility_score >= 60: return "C+"
        elif credibility_score >= 55: return "C"
        elif credibility_score >= 50: return "C-"
        else: return "D"
    
    def _predict_implementation_probability(self, verifications: List[PledgeVerification], position_type: str) -> float:
        """실행 확률 예측"""
        if not verifications:
            return 0.0
        
        # 검증 상태별 가중치
        status_weights = {
            VerificationStatus.VERIFIED: 0.9,
            VerificationStatus.PARTIALLY_VERIFIED: 0.6,
            VerificationStatus.UNVERIFIED: 0.3,
            VerificationStatus.CONTRADICTED: 0.1,
            VerificationStatus.IMPOSSIBLE: 0.0
        }
        
        # 직책별 실행력 가중치
        position_weights = {
            "광역단체장": 0.8,
            "기초단체장": 0.7,
            "광역의회의원": 0.4,
            "기초의회의원": 0.3
        }
        
        total_weight = 0
        weighted_sum = 0
        
        for verification in verifications:
            status_weight = status_weights.get(verification.verification_status, 0.3)
            feasibility_weight = verification.budget_realism * verification.timeline_realism
            
            weight = status_weight * feasibility_weight
            total_weight += weight
            weighted_sum += weight
        
        base_probability = weighted_sum / len(verifications) if verifications else 0
        position_multiplier = position_weights.get(position_type, 0.5)
        
        return min(1.0, base_probability * position_multiplier) * 100
    
    def _analyze_candidate_profile(self, verifications: List[PledgeVerification], credibility_score: float) -> Tuple[List[str], List[str], List[str]]:
        """후보자 프로필 분석"""
        strengths = []
        weaknesses = []
        recommendations = []
        
        # 강점 분석
        verified_count = len([v for v in verifications if v.verification_status == VerificationStatus.VERIFIED])
        if verified_count > len(verifications) * 0.7:
            strengths.append("높은 공약 검증률")
        
        avg_specificity = np.mean([v.specificity_score for v in verifications])
        if avg_specificity > 70:
            strengths.append("구체적인 공약 제시")
        
        if credibility_score > 75:
            strengths.append("높은 신뢰도")
        
        # 약점 분석
        contradicted_count = len([v for v in verifications if v.verification_status == VerificationStatus.CONTRADICTED])
        if contradicted_count > 0:
            weaknesses.append("공약 간 모순 존재")
        
        impossible_count = len([v for v in verifications if v.verification_status == VerificationStatus.IMPOSSIBLE])
        if impossible_count > 0:
            weaknesses.append("실현 불가능한 공약 포함")
        
        if avg_specificity < 50:
            weaknesses.append("공약 구체성 부족")
        
        # 권고사항
        if avg_specificity < 60:
            recommendations.append("공약의 구체성 보완 필요")
        
        if contradicted_count > 0:
            recommendations.append("상충되는 공약 조정 필요")
        
        if impossible_count > 0:
            recommendations.append("실현 불가능한 공약 재검토 필요")
        
        return strengths, weaknesses, recommendations
    
    def generate_verification_report(self, verifications: List[CandidateVerification]) -> Dict[str, Any]:
        """종합 검증 보고서 생성"""
        print("📊 매니페스토 검증 보고서 생성 중...")
        
        total_candidates = len(verifications)
        total_pledges = sum(v.total_pledges for v in verifications)
        
        # 전체 통계
        avg_verification_rate = np.mean([v.verification_rate for v in verifications])
        avg_credibility = np.mean([v.credibility_score for v in verifications])
        avg_implementation_prob = np.mean([v.implementation_probability for v in verifications])
        
        # 등급별 분포
        grade_distribution = {}
        for verification in verifications:
            grade = verification.overall_grade
            grade_distribution[grade] = grade_distribution.get(grade, 0) + 1
        
        # 당별 분석
        party_analysis = {}
        for verification in verifications:
            party = verification.party
            if party not in party_analysis:
                party_analysis[party] = {
                    "candidates": 0,
                    "avg_credibility": 0,
                    "avg_verification_rate": 0,
                    "credibility_scores": []
                }
            
            party_analysis[party]["candidates"] += 1
            party_analysis[party]["credibility_scores"].append(verification.credibility_score)
        
        # 당별 평균 계산
        for party, data in party_analysis.items():
            scores = data["credibility_scores"]
            data["avg_credibility"] = np.mean(scores)
            data["avg_verification_rate"] = np.mean([
                v.verification_rate for v in verifications if v.party == party
            ])
        
        # 최고/최저 성과자
        best_performer = max(verifications, key=lambda x: x.credibility_score)
        worst_performer = min(verifications, key=lambda x: x.credibility_score)
        
        report = {
            "verification_date": datetime.now().isoformat(),
            "summary": {
                "total_candidates": total_candidates,
                "total_pledges": total_pledges,
                "avg_verification_rate": avg_verification_rate,
                "avg_credibility_score": avg_credibility,
                "avg_implementation_probability": avg_implementation_prob
            },
            "grade_distribution": grade_distribution,
            "party_analysis": party_analysis,
            "performance_ranking": {
                "best_performer": {
                    "name": best_performer.candidate_name,
                    "party": best_performer.party,
                    "credibility_score": best_performer.credibility_score,
                    "grade": best_performer.overall_grade
                },
                "worst_performer": {
                    "name": worst_performer.candidate_name,
                    "party": worst_performer.party,
                    "credibility_score": worst_performer.credibility_score,
                    "grade": worst_performer.overall_grade
                }
            },
            "verification_insights": self._generate_verification_insights(verifications),
            "recommendations": self._generate_system_recommendations(verifications)
        }
        
        return report
    
    def _generate_verification_insights(self, verifications: List[CandidateVerification]) -> List[str]:
        """검증 인사이트 생성"""
        insights = []
        
        # 공약 품질 분석
        high_quality = len([v for v in verifications if v.credibility_score >= 75])
        if high_quality > len(verifications) * 0.5:
            insights.append("전체적으로 공약 품질이 양호한 수준")
        else:
            insights.append("공약 품질 개선이 필요한 후보자가 다수")
        
        # 검증률 분석
        high_verification = len([v for v in verifications if v.verification_rate >= 70])
        if high_verification < len(verifications) * 0.3:
            insights.append("검증 가능한 구체적 공약이 부족")
        
        # 실현가능성 분석
        feasible_candidates = len([v for v in verifications if v.implementation_probability >= 60])
        if feasible_candidates < len(verifications) * 0.5:
            insights.append("실현 가능성이 낮은 공약들이 다수 포함")
        
        return insights
    
    def _generate_system_recommendations(self, verifications: List[CandidateVerification]) -> List[str]:
        """시스템 권고사항 생성"""
        recommendations = []
        
        # 공통 문제점 기반 권고
        low_specificity = len([v for v in verifications if v.avg_specificity < 50])
        if low_specificity > len(verifications) * 0.5:
            recommendations.append("후보자들의 공약 구체성 향상을 위한 가이드라인 제공 필요")
        
        contradictions = len([v for v in verifications if any(pv.contradictions for pv in v.pledge_verifications)])
        if contradictions > 0:
            recommendations.append("공약 간 일관성 검토 프로세스 강화 필요")
        
        recommendations.append("시민 참여형 공약 검증 시스템 도입 고려")
        recommendations.append("공약 이행 모니터링 체계 구축 필요")
        
        return recommendations
    
    def save_verification_results(self, verifications: List[CandidateVerification], report: Dict[str, Any]) -> Tuple[str, str]:
        """검증 결과 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 개별 검증 결과
        verifications_file = os.path.join(self.verification_dir, f"manifesto_verifications_{timestamp}.json")
        verifications_data = [asdict(v) for v in verifications]
        
        # Enum을 문자열로 변환
        for verification_data in verifications_data:
            for pledge_verification in verification_data["pledge_verifications"]:
                if hasattr(pledge_verification["feasibility_level"], 'value'):
                    pledge_verification["feasibility_level"] = pledge_verification["feasibility_level"].value
                if hasattr(pledge_verification["verification_status"], 'value'):
                    pledge_verification["verification_status"] = pledge_verification["verification_status"].value
        
        with open(verifications_file, 'w', encoding='utf-8') as f:
            json.dump(verifications_data, f, ensure_ascii=False, indent=2)
        
        # 종합 보고서
        report_file = os.path.join(self.verification_dir, f"verification_report_{timestamp}.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"💾 검증 결과 저장 완료:")
        print(f"  📊 개별 검증: {verifications_file}")
        print(f"  📋 종합 보고서: {report_file}")
        
        return verifications_file, report_file

def main():
    """메인 실행 함수"""
    print("🔍 매니페스토 검증 서비스")
    print("=" * 60)
    
    verification_service = ManifestoVerificationService()
    
    try:
        # 1. 분석 결과 로드
        analysis_file = "/Users/hopidaay/newsbot-kr/backend/manifesto_analysis/manifesto_analyses_20250920_155724.json"
        analysis_results = verification_service.load_analysis_results(analysis_file)
        
        # 2. 원본 후보자 데이터 로드
        candidates_file = "/Users/hopidaay/newsbot-kr/backend/election_data/comprehensive_8th_election_candidates_20250920_124544.json"
        candidates_data = verification_service.load_candidates_data(candidates_file)
        
        if not analysis_results or not candidates_data:
            print("❌ 데이터 로드 실패")
            return
        
        # 3. 후보자별 검증
        print("\n🔍 후보자별 매니페스토 검증 중...")
        verifications = []
        
        for district_id, district_info in candidates_data["districts"].items():
            for candidate_id, candidate_info in district_info["candidates"].items():
                # 분석 결과에서 해당 후보자 찾기
                analysis_data = next((a for a in analysis_results if a["candidate_name"] == candidate_info["name"]), {})
                
                verification = verification_service.verify_candidate_manifesto(candidate_info, analysis_data)
                verifications.append(verification)
        
        # 4. 종합 보고서 생성
        report = verification_service.generate_verification_report(verifications)
        
        # 5. 결과 저장
        verifications_file, report_file = verification_service.save_verification_results(verifications, report)
        
        print("\n" + "=" * 60)
        print("🎉 매니페스토 검증 서비스 완료!")
        
        # 주요 결과 출력
        print(f"\n📊 검증 결과 요약:")
        print(f"  검증 후보자: {report['summary']['total_candidates']}명")
        print(f"  총 공약: {report['summary']['total_pledges']}개")
        print(f"  평균 검증률: {report['summary']['avg_verification_rate']:.1f}%")
        print(f"  평균 신뢰도: {report['summary']['avg_credibility_score']:.1f}점")
        print(f"  평균 실현확률: {report['summary']['avg_implementation_probability']:.1f}%")
        
        print(f"\n🏆 등급 분포:")
        for grade, count in sorted(report['grade_distribution'].items()):
            print(f"  {grade}: {count}명")
        
        print(f"\n🥇 최고 성과자: {report['performance_ranking']['best_performer']['name']} ({report['performance_ranking']['best_performer']['grade']})")
        
        return verifications, report
        
    except Exception as e:
        logger.error(f"매니페스토 검증 실패: {e}")
        print(f"❌ 검증 실패: {e}")
        return None, None

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
