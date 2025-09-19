#!/usr/bin/env python3
"""
통계자료 시계열 검증기
2014년 시작시점 확인 및 데이터 시간적 연속성 검증
- 모든 수집된 통계 데이터의 시작시점 확인
- 선거 데이터와 통계 데이터 시점 매칭
- 시계열 분석 기준점 정확성 검증
"""

import json
import glob
import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class DataTimelineValidator:
    def __init__(self):
        self.base_dir = "/Users/hopidaay/newsbot-kr/backend"
        
        # 알려진 선거 시점들
        self.election_timeline = {
            "2014-06-04": "제6회 전국동시지방선거",
            "2016-04-13": "제20대 국회의원선거", 
            "2018-06-13": "제7회 전국동시지방선거",
            "2020-04-15": "제21대 국회의원선거",
            "2022-06-01": "제8회 전국동시지방선거"
        }
        
        # 통계 데이터 수집 주기
        self.statistical_cycles = {
            "인구주택총조사": {"cycle": 5, "years": [2015, 2020, 2025]},
            "농림어업총조사": {"cycle": 5, "years": [2015, 2020, 2025]}, 
            "전국사업체조사": {"cycle": 1, "start_year": 2014},
            "사회조사": {"cycle": 2, "years": [2014, 2016, 2018, 2020, 2022, 2024]},
            "생활시간조사": {"cycle": 5, "years": [2014, 2019, 2024]}
        }

    def extract_years_from_file(self, filepath: str) -> List[int]:
        """파일에서 연도 정보 추출"""
        years_found = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # 연도 패턴 찾기 (2014-2025)
                year_patterns = [
                    r'20[12][0-9]',  # 2010-2029
                    r'["\']20[12][0-9]["\']',  # 따옴표로 둘러싸인 연도
                    r'year.*?20[12][0-9]',  # year 키워드 포함
                    r'data_period.*?20[12][0-9]'  # data_period 키워드 포함
                ]
                
                for pattern in year_patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        # 숫자만 추출
                        year_str = re.search(r'20[12][0-9]', match)
                        if year_str:
                            year = int(year_str.group())
                            if 2014 <= year <= 2025:
                                years_found.append(year)
                
        except Exception as e:
            print(f"파일 읽기 오류: {filepath} - {e}")
        
        return sorted(list(set(years_found)))

    def analyze_data_timeline_coverage(self) -> Dict:
        """데이터 시계열 커버리지 분석"""
        print("📊 데이터 시계열 커버리지 분석...")
        
        timeline_analysis = {
            'files_analyzed': 0,
            'files_with_timeline': 0,
            'year_coverage': {str(year): 0 for year in range(2014, 2026)},
            'data_categories': {},
            'earliest_year': None,
            'latest_year': None,
            'timeline_completeness': 0.0
        }
        
        # JSON 파일들 분석
        json_files = glob.glob(os.path.join(self.base_dir, "*.json"))
        
        for filepath in json_files:
            timeline_analysis['files_analyzed'] += 1
            filename = os.path.basename(filepath)
            
            # 파일에서 연도 추출
            years_in_file = self.extract_years_from_file(filepath)
            
            if years_in_file:
                timeline_analysis['files_with_timeline'] += 1
                
                # 카테고리 분류
                category = self._categorize_file(filename)
                if category not in timeline_analysis['data_categories']:
                    timeline_analysis['data_categories'][category] = {
                        'files': 0,
                        'years_covered': set(),
                        'earliest_year': None,
                        'latest_year': None
                    }
                
                timeline_analysis['data_categories'][category]['files'] += 1
                timeline_analysis['data_categories'][category]['years_covered'].update(years_in_file)
                
                # 전체 연도 커버리지 업데이트
                for year in years_in_file:
                    timeline_analysis['year_coverage'][str(year)] += 1
                
                # 최조/최신 연도 업데이트
                min_year = min(years_in_file)
                max_year = max(years_in_file)
                
                if timeline_analysis['earliest_year'] is None or min_year < timeline_analysis['earliest_year']:
                    timeline_analysis['earliest_year'] = min_year
                if timeline_analysis['latest_year'] is None or max_year > timeline_analysis['latest_year']:
                    timeline_analysis['latest_year'] = max_year
                
                cat_data = timeline_analysis['data_categories'][category]
                if cat_data['earliest_year'] is None or min_year < cat_data['earliest_year']:
                    cat_data['earliest_year'] = min_year
                if cat_data['latest_year'] is None or max_year > cat_data['latest_year']:
                    cat_data['latest_year'] = max_year
        
        # 카테고리별 연도 커버리지 정리
        for category, data in timeline_analysis['data_categories'].items():
            data['years_covered'] = sorted(list(data['years_covered']))
            data['year_span'] = len(data['years_covered'])
        
        # 시계열 완성도 계산
        expected_years = list(range(2014, 2026))  # 2014-2025
        covered_years = [year for year, count in timeline_analysis['year_coverage'].items() if count > 0]
        timeline_analysis['timeline_completeness'] = len(covered_years) / len(expected_years)
        
        return timeline_analysis

    def _categorize_file(self, filename: str) -> str:
        """파일명 기반 카테고리 분류"""
        filename_lower = filename.lower()
        
        if any(keyword in filename_lower for keyword in ['population', 'household', 'dong_map']):
            return 'population_demographics'
        elif any(keyword in filename_lower for keyword in ['housing', 'house']):
            return 'housing_residential'
        elif any(keyword in filename_lower for keyword in ['company', 'business', 'corp']):
            return 'business_economic'
        elif any(keyword in filename_lower for keyword in ['university', 'academy', 'education']):
            return 'education'
        elif any(keyword in filename_lower for keyword in ['urban', 'city']):
            return 'urbanization'
        elif any(keyword in filename_lower for keyword in ['welfare', 'culture']):
            return 'welfare_culture'
        elif any(keyword in filename_lower for keyword in ['labor', 'economy']):
            return 'labor_economy'
        elif any(keyword in filename_lower for keyword in ['religion']):
            return 'religion_culture'
        elif any(keyword in filename_lower for keyword in ['social']):
            return 'social_structure'
        elif any(keyword in filename_lower for keyword in ['transport', 'traffic']):
            return 'transportation'
        else:
            return 'other'

    def verify_2014_start_point(self, timeline_analysis: Dict) -> Dict:
        """2014년 시작시점 검증"""
        print("📅 2014년 시작시점 검증...")
        
        verification_result = {
            'is_2014_start_confirmed': False,
            'actual_earliest_year': timeline_analysis['earliest_year'],
            'year_2014_coverage': timeline_analysis['year_coverage'].get('2014', 0),
            'categories_with_2014': [],
            'categories_without_2014': [],
            'start_point_assessment': 'UNKNOWN'
        }
        
        # 2014년 시작 확인
        if timeline_analysis['earliest_year'] == 2014:
            verification_result['is_2014_start_confirmed'] = True
            verification_result['start_point_assessment'] = 'CONFIRMED'
        elif timeline_analysis['earliest_year'] and timeline_analysis['earliest_year'] < 2014:
            verification_result['start_point_assessment'] = 'EARLIER_THAN_2014'
        elif timeline_analysis['earliest_year'] and timeline_analysis['earliest_year'] > 2014:
            verification_result['start_point_assessment'] = 'LATER_THAN_2014'
        
        # 카테고리별 2014년 포함 여부 확인
        for category, data in timeline_analysis['data_categories'].items():
            if 2014 in data['years_covered']:
                verification_result['categories_with_2014'].append({
                    'category': category,
                    'files': data['files'],
                    'year_span': data['year_span'],
                    'earliest': data['earliest_year']
                })
            else:
                verification_result['categories_without_2014'].append({
                    'category': category,
                    'files': data['files'],
                    'earliest': data['earliest_year'],
                    'missing_years': [year for year in range(2014, 2026) if year not in data['years_covered']]
                })
        
        return verification_result

    def check_statistical_survey_alignment(self, timeline_analysis: Dict) -> Dict:
        """통계조사 주기와 데이터 정렬 확인"""
        print("📋 통계조사 주기 정렬 확인...")
        
        alignment_check = {
            'survey_alignment': {},
            'data_gaps': [],
            'temporal_consistency': 0.0
        }
        
        for survey_name, survey_info in self.statistical_cycles.items():
            alignment_result = {
                'survey_name': survey_name,
                'expected_cycle': survey_info['cycle'],
                'expected_years': survey_info.get('years', []),
                'found_in_data': False,
                'coverage_assessment': 'NOT_FOUND'
            }
            
            # 관련 카테고리에서 해당 조사 데이터 찾기
            relevant_categories = []
            if '인구주택' in survey_name:
                relevant_categories = ['population_demographics', 'housing_residential']
            elif '농림어업' in survey_name:
                relevant_categories = ['business_economic']  # 1차 산업
            elif '사업체' in survey_name:
                relevant_categories = ['business_economic']
            elif '사회조사' in survey_name:
                relevant_categories = ['social_structure', 'welfare_culture']
            
            # 해당 카테고리에서 연도 확인
            found_years = set()
            for category in relevant_categories:
                if category in timeline_analysis['data_categories']:
                    cat_years = timeline_analysis['data_categories'][category]['years_covered']
                    found_years.update(cat_years)
            
            if found_years:
                alignment_result['found_in_data'] = True
                alignment_result['found_years'] = sorted(list(found_years))
                
                # 예상 연도와 비교
                if 'years' in survey_info:
                    expected = set(survey_info['years'])
                    overlap = expected.intersection(found_years)
                    if len(overlap) >= len(expected) * 0.7:
                        alignment_result['coverage_assessment'] = 'GOOD'
                    elif len(overlap) >= len(expected) * 0.4:
                        alignment_result['coverage_assessment'] = 'MODERATE'
                    else:
                        alignment_result['coverage_assessment'] = 'POOR'
                else:
                    # 연간 조사의 경우
                    start_year = survey_info.get('start_year', 2014)
                    expected_span = 2025 - start_year + 1
                    actual_span = len(found_years)
                    if actual_span >= expected_span * 0.7:
                        alignment_result['coverage_assessment'] = 'GOOD'
                    elif actual_span >= expected_span * 0.4:
                        alignment_result['coverage_assessment'] = 'MODERATE'
                    else:
                        alignment_result['coverage_assessment'] = 'POOR'
            
            alignment_check['survey_alignment'][survey_name] = alignment_result
        
        return alignment_check

    def generate_timeline_validation_report(self) -> str:
        """시계열 검증 보고서 생성"""
        print("📋 시계열 검증 보고서 생성...")
        
        try:
            # 1. 데이터 시계열 커버리지 분석
            timeline_analysis = self.analyze_data_timeline_coverage()
            
            # 2. 2014년 시작시점 검증
            start_verification = self.verify_2014_start_point(timeline_analysis)
            
            # 3. 통계조사 주기 정렬 확인
            survey_alignment = self.check_statistical_survey_alignment(timeline_analysis)
            
            # 종합 보고서
            comprehensive_report = {
                'metadata': {
                    'title': '통계자료 시계열 검증 보고서',
                    'created_at': datetime.now().isoformat(),
                    'version': '1.0',
                    'purpose': '2014년 시작시점 확인 및 시계열 연속성 검증',
                    'validation_scope': '전체 수집 통계 데이터'
                },
                
                'timeline_verification_summary': {
                    'files_analyzed': timeline_analysis['files_analyzed'],
                    'files_with_timeline': timeline_analysis['files_with_timeline'],
                    'earliest_year_found': timeline_analysis['earliest_year'],
                    'latest_year_found': timeline_analysis['latest_year'],
                    'is_2014_start_confirmed': start_verification['is_2014_start_confirmed'],
                    'start_point_assessment': start_verification['start_point_assessment'],
                    'timeline_completeness': timeline_analysis['timeline_completeness']
                },
                
                'detailed_timeline_analysis': timeline_analysis,
                'start_point_verification': start_verification,
                'statistical_survey_alignment': survey_alignment,
                
                'key_findings': {
                    'temporal_coverage_assessment': self._assess_temporal_coverage(timeline_analysis),
                    'data_continuity_status': self._assess_data_continuity(timeline_analysis),
                    'statistical_alignment_status': self._assess_survey_alignment(survey_alignment),
                    'recommendations': self._generate_timeline_recommendations(timeline_analysis, start_verification)
                },
                
                'election_data_context': {
                    'election_timeline': self.election_timeline,
                    'statistical_cycles': self.statistical_cycles,
                    'data_election_alignment': self._analyze_election_data_alignment(timeline_analysis)
                }
            }
            
            # JSON 파일로 저장
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'data_timeline_validation_report_{timestamp}.json'
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(comprehensive_report, f, ensure_ascii=False, indent=2)
            
            print(f'✅ 시계열 검증 보고서 저장: {filename}')
            return filename
            
        except Exception as e:
            print(f'❌ 보고서 생성 실패: {e}')
            return ''

    def _assess_temporal_coverage(self, timeline_analysis: Dict) -> str:
        """시간적 커버리지 평가"""
        completeness = timeline_analysis['timeline_completeness']
        
        if completeness >= 0.9:
            return 'EXCELLENT'
        elif completeness >= 0.7:
            return 'GOOD'
        elif completeness >= 0.5:
            return 'MODERATE'
        else:
            return 'POOR'

    def _assess_data_continuity(self, timeline_analysis: Dict) -> str:
        """데이터 연속성 평가"""
        year_coverage = timeline_analysis['year_coverage']
        
        # 연속성 확인 (2014-2025)
        consecutive_years = 0
        max_consecutive = 0
        
        for year in range(2014, 2026):
            if year_coverage.get(str(year), 0) > 0:
                consecutive_years += 1
                max_consecutive = max(max_consecutive, consecutive_years)
            else:
                consecutive_years = 0
        
        continuity_ratio = max_consecutive / 12  # 2014-2025 = 12년
        
        if continuity_ratio >= 0.9:
            return 'EXCELLENT'
        elif continuity_ratio >= 0.7:
            return 'GOOD'
        elif continuity_ratio >= 0.5:
            return 'MODERATE'
        else:
            return 'POOR'

    def _assess_survey_alignment(self, survey_alignment: Dict) -> str:
        """통계조사 정렬 평가"""
        good_alignments = 0
        total_surveys = len(survey_alignment['survey_alignment'])
        
        for survey_name, result in survey_alignment['survey_alignment'].items():
            if result['coverage_assessment'] in ['GOOD', 'MODERATE']:
                good_alignments += 1
        
        alignment_ratio = good_alignments / total_surveys if total_surveys > 0 else 0
        
        if alignment_ratio >= 0.8:
            return 'EXCELLENT'
        elif alignment_ratio >= 0.6:
            return 'GOOD'
        elif alignment_ratio >= 0.4:
            return 'MODERATE'
        else:
            return 'POOR'

    def _generate_timeline_recommendations(self, timeline_analysis: Dict, start_verification: Dict) -> List[str]:
        """시계열 관련 권장사항 생성"""
        recommendations = []
        
        # 2014년 시작시점 관련
        if not start_verification['is_2014_start_confirmed']:
            if start_verification['actual_earliest_year'] and start_verification['actual_earliest_year'] > 2014:
                recommendations.append(f"2014년 데이터 보완 필요 (현재 최초: {start_verification['actual_earliest_year']}년)")
            elif start_verification['actual_earliest_year'] and start_verification['actual_earliest_year'] < 2014:
                recommendations.append(f"시작시점 재정의 고려 (실제 최초: {start_verification['actual_earliest_year']}년)")
        
        # 시계열 완성도 관련
        if timeline_analysis['timeline_completeness'] < 0.8:
            missing_years = [year for year in range(2014, 2026) 
                           if timeline_analysis['year_coverage'].get(str(year), 0) == 0]
            if missing_years:
                recommendations.append(f"누락 연도 데이터 보완: {missing_years}")
        
        # 카테고리별 시계열 갭
        for category, data in timeline_analysis['data_categories'].items():
            if data['year_span'] < 8:  # 12년 중 8년 미만
                recommendations.append(f"{category} 카테고리 시계열 확장 필요")
        
        return recommendations

    def _analyze_election_data_alignment(self, timeline_analysis: Dict) -> Dict:
        """선거 데이터와 통계 데이터 정렬 분석"""
        alignment_analysis = {
            'election_years_in_data': [],
            'statistical_years_coverage': {},
            'alignment_quality': 'UNKNOWN'
        }
        
        # 선거 연도들이 데이터에 포함되어 있는지 확인
        election_years = [2014, 2016, 2018, 2020, 2022]
        
        for year in election_years:
            year_str = str(year)
            if timeline_analysis['year_coverage'].get(year_str, 0) > 0:
                alignment_analysis['election_years_in_data'].append(year)
        
        # 통계 연도별 커버리지
        for year_str, count in timeline_analysis['year_coverage'].items():
            year = int(year_str)
            if 2014 <= year <= 2025:
                alignment_analysis['statistical_years_coverage'][year] = {
                    'data_sources': count,
                    'is_election_year': year in election_years,
                    'coverage_quality': 'HIGH' if count >= 5 else 'MODERATE' if count >= 2 else 'LOW'
                }
        
        # 정렬 품질 평가
        election_coverage_ratio = len(alignment_analysis['election_years_in_data']) / len(election_years)
        
        if election_coverage_ratio >= 0.8:
            alignment_analysis['alignment_quality'] = 'EXCELLENT'
        elif election_coverage_ratio >= 0.6:
            alignment_analysis['alignment_quality'] = 'GOOD'
        elif election_coverage_ratio >= 0.4:
            alignment_analysis['alignment_quality'] = 'MODERATE'
        else:
            alignment_analysis['alignment_quality'] = 'POOR'
        
        return alignment_analysis

def main():
    """메인 실행 함수"""
    validator = DataTimelineValidator()
    
    print('📊⏰ 통계자료 시계열 검증기')
    print('=' * 50)
    print('🎯 목적: 2014년 시작시점 확인')
    print('📅 범위: 2014-2025년 시계열')
    print('🔍 대상: 전체 수집 통계 데이터')
    print('=' * 50)
    
    try:
        print('\n🚀 시계열 검증 실행...')
        
        # 시계열 검증 보고서 생성
        report_file = validator.generate_timeline_validation_report()
        
        if report_file:
            print(f'\n🎉 시계열 검증 완료!')
            print(f'📄 보고서: {report_file}')
            
            # 보고서 요약 출력
            with open(report_file, 'r', encoding='utf-8') as f:
                report = json.load(f)
            
            summary = report['timeline_verification_summary']
            findings = report['key_findings']
            
            print(f'\n🏆 시계열 검증 결과:')
            print(f'  📊 분석 파일: {summary["files_analyzed"]}개')
            print(f'  ⏰ 시계열 파일: {summary["files_with_timeline"]}개')
            print(f'  📅 최초 연도: {summary["earliest_year_found"]}년')
            print(f'  📅 최신 연도: {summary["latest_year_found"]}년')
            print(f'  🎯 2014년 시작: {summary["is_2014_start_confirmed"]}')
            print(f'  📊 시계열 완성도: {summary["timeline_completeness"]:.1%}')
            
            start_verification = report['start_point_verification']
            print(f'\n📅 2014년 시작시점 검증:')
            print(f'  🎯 확인 상태: {start_verification["start_point_assessment"]}')
            print(f'  📊 2014년 데이터: {start_verification["year_2014_coverage"]}개 파일')
            print(f'  ✅ 2014년 포함 카테고리: {len(start_verification["categories_with_2014"])}개')
            print(f'  ❌ 2014년 누락 카테고리: {len(start_verification["categories_without_2014"])}개')
            
            if start_verification['categories_with_2014']:
                print(f'\n✅ 2014년 포함 카테고리:')
                for cat in start_verification['categories_with_2014'][:3]:
                    print(f'  📊 {cat["category"]}: {cat["files"]}개 파일, {cat["year_span"]}년 스팬')
            
            if start_verification['categories_without_2014']:
                print(f'\n❌ 2014년 누락 카테고리:')
                for cat in start_verification['categories_without_2014'][:3]:
                    earliest = cat["earliest"] if cat["earliest"] else "N/A"
                    print(f'  📊 {cat["category"]}: 최초 {earliest}년')
            
            # 권장사항
            recommendations = findings.get('recommendations', [])
            if recommendations:
                print(f'\n💡 권장사항:')
                for rec in recommendations[:3]:
                    print(f'  🎯 {rec}')
            
        else:
            print('\n❌ 보고서 생성 실패')
            
    except Exception as e:
        print(f'\n❌ 오류 발생: {e}')

if __name__ == '__main__':
    main()
