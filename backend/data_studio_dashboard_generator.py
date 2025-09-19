#!/usr/bin/env python3
"""
Google Data Studio 대시보드 자동 생성기
업로드된 데이터를 기반으로 완벽한 대시보드 구성 가이드 제공
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class DataStudioDashboardGenerator:
    def __init__(self):
        self.dashboard_config = {
            'dashboard_name': '🏠 3차원 통합 선거 예측 대시보드',
            'description': '인구+가구+주택 데이터 기반 선거 분석 시스템',
            'data_sources': [],
            'pages': [],
            'filters': [],
            'calculated_fields': []
        }
        
        # 차트 색상 팔레트
        self.color_palette = {
            'primary': '#3B82F6',      # 파랑
            'secondary': '#10B981',    # 초록
            'accent': '#8B5CF6',       # 보라
            'warning': '#F59E0B',      # 주황
            'danger': '#EF4444',       # 빨강
            'neutral': '#6B7280',      # 회색
            'conservative': '#DC2626', # 진한 빨강 (보수)
            'progressive': '#1D4ED8',  # 진한 파랑 (진보)
            'moderate': '#6B7280'      # 회색 (중도)
        }

    def create_data_sources_config(self) -> List[Dict]:
        """데이터 소스 설정 생성"""
        logger.info("📊 데이터 소스 설정 생성")
        
        data_sources = [
            {
                'name': '지역별_요약_데이터',
                'type': 'Google Sheets',
                'description': '17개 시도별 3차원 통합 분석 요약',
                'sheet_name': '지역별_요약_시트',
                'key_fields': [
                    'region_name', 'population', 'households', 'housing_units',
                    'ownership_ratio', 'single_household_ratio', 'integrated_3d_score',
                    'political_tendency', 'predicted_turnout', 'latitude', 'longitude'
                ],
                'field_types': {
                    'region_name': 'TEXT',
                    'population': 'NUMBER',
                    'households': 'NUMBER',
                    'housing_units': 'NUMBER',
                    'ownership_ratio': 'PERCENT',
                    'single_household_ratio': 'PERCENT',
                    'integrated_3d_score': 'NUMBER',
                    'political_tendency': 'TEXT',
                    'predicted_turnout': 'PERCENT',
                    'latitude': 'NUMBER',
                    'longitude': 'NUMBER'
                }
            },
            
            {
                'name': '시계열_데이터',
                'type': 'Google Sheets',
                'description': '2015-2025년 인구가구주택 변화 추이',
                'sheet_name': '시계열_데이터_시트',
                'key_fields': [
                    'region_name', 'year', 'month', 'date', 'population',
                    'households', 'housing_units', 'metric_type', 'metric_value', 'change_rate'
                ],
                'field_types': {
                    'region_name': 'TEXT',
                    'year': 'NUMBER',
                    'month': 'NUMBER',
                    'date': 'DATE',
                    'population': 'NUMBER',
                    'households': 'NUMBER',
                    'housing_units': 'NUMBER',
                    'metric_type': 'TEXT',
                    'metric_value': 'NUMBER',
                    'change_rate': 'PERCENT'
                }
            },
            
            {
                'name': '상관관계_매트릭스',
                'type': 'Google Sheets',
                'description': '3차원 데이터 상관관계 분석 결과',
                'sheet_name': '상관관계_매트릭스_시트',
                'key_fields': [
                    'dimension_x', 'dimension_y', 'correlation_coefficient',
                    'statistical_significance', 'sample_size', 'p_value'
                ],
                'field_types': {
                    'dimension_x': 'TEXT',
                    'dimension_y': 'TEXT',
                    'correlation_coefficient': 'NUMBER',
                    'statistical_significance': 'TEXT',
                    'sample_size': 'NUMBER',
                    'p_value': 'NUMBER'
                }
            }
        ]
        
        self.dashboard_config['data_sources'] = data_sources
        return data_sources

    def create_calculated_fields(self) -> List[Dict]:
        """계산된 필드 생성"""
        logger.info("🧮 계산된 필드 생성")
        
        calculated_fields = [
            {
                'name': '인구_밀도',
                'formula': 'population / 1000',
                'description': '인구 밀도 (천명 단위)',
                'data_type': 'NUMBER'
            },
            
            {
                'name': '가구당_인구',
                'formula': 'population / households',
                'description': '가구당 평균 인구수',
                'data_type': 'NUMBER'
            },
            
            {
                'name': '주택_공급률',
                'formula': '(housing_units / households) * 100',
                'description': '주택 공급률 (%)',
                'data_type': 'PERCENT'
            },
            
            {
                'name': '정치_성향_점수',
                'formula': '''
                CASE
                    WHEN political_tendency = "강한 보수" THEN -2
                    WHEN political_tendency = "보수" THEN -1
                    WHEN political_tendency = "중도" THEN 0
                    WHEN political_tendency = "진보" THEN 1
                    WHEN political_tendency = "강한 진보" THEN 2
                    ELSE 0
                END
                ''',
                'description': '정치 성향 수치화 (-2: 강한보수, +2: 강한진보)',
                'data_type': 'NUMBER'
            },
            
            {
                'name': '예측_신뢰도_등급',
                'formula': '''
                CASE
                    WHEN integrated_3d_score >= 0.95 THEN "매우 높음"
                    WHEN integrated_3d_score >= 0.90 THEN "높음"
                    WHEN integrated_3d_score >= 0.85 THEN "보통"
                    WHEN integrated_3d_score >= 0.80 THEN "낮음"
                    ELSE "매우 낮음"
                END
                ''',
                'description': '3차원 통합 점수 기반 신뢰도 등급',
                'data_type': 'TEXT'
            }
        ]
        
        self.dashboard_config['calculated_fields'] = calculated_fields
        return calculated_fields

    def create_filters_config(self) -> List[Dict]:
        """필터 설정 생성"""
        logger.info("🔍 필터 설정 생성")
        
        filters = [
            {
                'name': '지역_필터',
                'field': 'region_name',
                'type': 'dropdown_multi_select',
                'description': '분석할 지역 선택',
                'default_values': ['전체'],
                'position': {'row': 1, 'column': 1}
            },
            
            {
                'name': '정치성향_필터',
                'field': 'political_tendency',
                'type': 'dropdown_multi_select',
                'description': '정치 성향별 필터링',
                'default_values': ['전체'],
                'position': {'row': 1, 'column': 2}
            },
            
            {
                'name': '연도_필터',
                'field': 'year',
                'type': 'date_range',
                'description': '분석 기간 선택',
                'default_range': {'start': '2015', 'end': '2025'},
                'position': {'row': 1, 'column': 3}
            },
            
            {
                'name': '예측신뢰도_필터',
                'field': '예측_신뢰도_등급',
                'type': 'dropdown',
                'description': '예측 신뢰도별 필터링',
                'default_value': '전체',
                'position': {'row': 1, 'column': 4}
            }
        ]
        
        self.dashboard_config['filters'] = filters
        return filters

    def create_main_dashboard_page(self) -> Dict:
        """메인 대시보드 페이지 생성"""
        logger.info("🏠 메인 대시보드 페이지 생성")
        
        main_page = {
            'name': '🏠 메인 대시보드',
            'description': '3차원 통합 분석 개요',
            'layout': 'grid',
            'components': [
                # 상단 KPI 카드들
                {
                    'type': 'scorecard',
                    'title': '전국 인구',
                    'data_source': '지역별_요약_데이터',
                    'metric': 'SUM(population)',
                    'format': 'number',
                    'position': {'row': 1, 'column': 1, 'width': 2, 'height': 1},
                    'style': {
                        'background_color': self.color_palette['primary'],
                        'text_color': 'white'
                    }
                },
                
                {
                    'type': 'scorecard',
                    'title': '전국 가구',
                    'data_source': '지역별_요약_데이터',
                    'metric': 'SUM(households)',
                    'format': 'number',
                    'position': {'row': 1, 'column': 3, 'width': 2, 'height': 1},
                    'style': {
                        'background_color': self.color_palette['secondary'],
                        'text_color': 'white'
                    }
                },
                
                {
                    'type': 'scorecard',
                    'title': '전국 주택',
                    'data_source': '지역별_요약_데이터',
                    'metric': 'SUM(housing_units)',
                    'format': 'number',
                    'position': {'row': 1, 'column': 5, 'width': 2, 'height': 1},
                    'style': {
                        'background_color': self.color_palette['accent'],
                        'text_color': 'white'
                    }
                },
                
                {
                    'type': 'scorecard',
                    'title': '평균 예측 정확도',
                    'data_source': '지역별_요약_데이터',
                    'metric': 'AVG(integrated_3d_score)',
                    'format': 'percent',
                    'position': {'row': 1, 'column': 7, 'width': 2, 'height': 1},
                    'style': {
                        'background_color': self.color_palette['warning'],
                        'text_color': 'white'
                    }
                },
                
                # 중앙 지도
                {
                    'type': 'geo_chart',
                    'title': '🗺️ 지역별 3차원 통합 분석',
                    'data_source': '지역별_요약_데이터',
                    'geo_dimension': 'region_name',
                    'location_fields': ['latitude', 'longitude'],
                    'color_metric': 'integrated_3d_score',
                    'size_metric': 'population',
                    'position': {'row': 2, 'column': 1, 'width': 6, 'height': 4},
                    'style': {
                        'map_type': 'google_maps',
                        'color_scheme': 'blue_to_red',
                        'show_tooltips': True
                    },
                    'tooltips': [
                        'region_name',
                        'population',
                        'households',
                        'political_tendency',
                        'predicted_turnout',
                        'integrated_3d_score'
                    ]
                },
                
                # 우측 정치 성향 파이 차트
                {
                    'type': 'pie_chart',
                    'title': '🎯 정치 성향 분포',
                    'data_source': '지역별_요약_데이터',
                    'dimension': 'political_tendency',
                    'metric': 'COUNT(region_name)',
                    'position': {'row': 2, 'column': 7, 'width': 2, 'height': 2},
                    'style': {
                        'color_scheme': 'custom',
                        'colors': {
                            '강한 보수': self.color_palette['danger'],
                            '보수': self.color_palette['warning'],
                            '중도': self.color_palette['neutral'],
                            '진보': self.color_palette['primary'],
                            '강한 진보': self.color_palette['progressive']
                        }
                    }
                },
                
                # 우측 예측 정확도 게이지
                {
                    'type': 'gauge_chart',
                    'title': '📊 평균 예측 정확도',
                    'data_source': '지역별_요약_데이터',
                    'metric': 'AVG(integrated_3d_score)',
                    'position': {'row': 4, 'column': 7, 'width': 2, 'height': 2},
                    'style': {
                        'min_value': 0,
                        'max_value': 1,
                        'color_ranges': [
                            {'min': 0.0, 'max': 0.8, 'color': self.color_palette['danger']},
                            {'min': 0.8, 'max': 0.9, 'color': self.color_palette['warning']},
                            {'min': 0.9, 'max': 1.0, 'color': self.color_palette['secondary']}
                        ]
                    }
                },
                
                # 하단 지역별 상세 테이블
                {
                    'type': 'table',
                    'title': '📋 지역별 상세 분석',
                    'data_source': '지역별_요약_데이터',
                    'columns': [
                        'region_name',
                        'population',
                        'households',
                        'ownership_ratio',
                        'single_household_ratio',
                        'political_tendency',
                        'predicted_turnout',
                        'integrated_3d_score'
                    ],
                    'position': {'row': 6, 'column': 1, 'width': 8, 'height': 2},
                    'style': {
                        'show_pagination': True,
                        'rows_per_page': 10,
                        'sort_column': 'integrated_3d_score',
                        'sort_order': 'descending'
                    }
                }
            ]
        }
        
        return main_page

    def create_time_series_page(self) -> Dict:
        """시계열 분석 페이지 생성"""
        logger.info("📈 시계열 분석 페이지 생성")
        
        time_series_page = {
            'name': '📈 시계열 분석',
            'description': '2015-2025년 변화 추이 분석',
            'layout': 'grid',
            'components': [
                # 인구 변화 추이
                {
                    'type': 'time_series_chart',
                    'title': '👥 인구 변화 추이',
                    'data_source': '시계열_데이터',
                    'date_dimension': 'date',
                    'metric': 'population',
                    'breakdown_dimension': 'region_name',
                    'position': {'row': 1, 'column': 1, 'width': 4, 'height': 3},
                    'style': {
                        'line_style': 'smooth',
                        'show_data_points': True,
                        'color_scheme': 'category10'
                    }
                },
                
                # 가구 변화 추이
                {
                    'type': 'time_series_chart',
                    'title': '🏠 가구 변화 추이',
                    'data_source': '시계열_데이터',
                    'date_dimension': 'date',
                    'metric': 'households',
                    'breakdown_dimension': 'region_name',
                    'position': {'row': 1, 'column': 5, 'width': 4, 'height': 3},
                    'style': {
                        'line_style': 'smooth',
                        'show_data_points': True,
                        'color_scheme': 'category10'
                    }
                },
                
                # 주택 변화 추이
                {
                    'type': 'time_series_chart',
                    'title': '🏘️ 주택 변화 추이',
                    'data_source': '시계열_데이터',
                    'date_dimension': 'date',
                    'metric': 'housing_units',
                    'breakdown_dimension': 'region_name',
                    'position': {'row': 4, 'column': 1, 'width': 4, 'height': 3},
                    'style': {
                        'line_style': 'smooth',
                        'show_data_points': True,
                        'color_scheme': 'category10'
                    }
                },
                
                # 변화율 분석
                {
                    'type': 'bar_chart',
                    'title': '📊 변화율 분석 (2015-2025)',
                    'data_source': '시계열_데이터',
                    'dimension': 'region_name',
                    'metric': 'AVG(change_rate)',
                    'position': {'row': 4, 'column': 5, 'width': 4, 'height': 3},
                    'style': {
                        'orientation': 'horizontal',
                        'color_scheme': 'blue_to_red',
                        'show_data_labels': True
                    }
                }
            ]
        }
        
        return time_series_page

    def create_correlation_page(self) -> Dict:
        """상관관계 분석 페이지 생성"""
        logger.info("🔗 상관관계 분석 페이지 생성")
        
        correlation_page = {
            'name': '🔗 상관관계 분석',
            'description': '3차원 데이터 상관관계 매트릭스',
            'layout': 'grid',
            'components': [
                # 상관관계 히트맵
                {
                    'type': 'heatmap',
                    'title': '🔥 3차원 상관관계 매트릭스',
                    'data_source': '상관관계_매트릭스',
                    'row_dimension': 'dimension_x',
                    'column_dimension': 'dimension_y',
                    'color_metric': 'correlation_coefficient',
                    'position': {'row': 1, 'column': 1, 'width': 6, 'height': 4},
                    'style': {
                        'color_scheme': 'red_white_blue',
                        'min_value': -1,
                        'max_value': 1,
                        'show_values': True,
                        'cell_border': True
                    }
                },
                
                # 통계적 유의성 차트
                {
                    'type': 'bubble_chart',
                    'title': '📊 통계적 유의성 분석',
                    'data_source': '상관관계_매트릭스',
                    'x_axis': 'correlation_coefficient',
                    'y_axis': 'p_value',
                    'size_metric': 'sample_size',
                    'color_dimension': 'statistical_significance',
                    'position': {'row': 1, 'column': 7, 'width': 2, 'height': 2},
                    'style': {
                        'color_scheme': 'traffic_light',
                        'show_trend_line': True
                    }
                },
                
                # 상관관계 강도 분포
                {
                    'type': 'histogram',
                    'title': '📈 상관관계 강도 분포',
                    'data_source': '상관관계_매트릭스',
                    'dimension': 'correlation_coefficient',
                    'position': {'row': 3, 'column': 7, 'width': 2, 'height': 2},
                    'style': {
                        'bins': 10,
                        'color': self.color_palette['accent']
                    }
                },
                
                # 상관관계 상세 테이블
                {
                    'type': 'table',
                    'title': '📋 상관관계 상세 분석',
                    'data_source': '상관관계_매트릭스',
                    'columns': [
                        'dimension_x',
                        'dimension_y',
                        'correlation_coefficient',
                        'statistical_significance',
                        'p_value'
                    ],
                    'position': {'row': 5, 'column': 1, 'width': 8, 'height': 2},
                    'style': {
                        'conditional_formatting': [
                            {
                                'column': 'correlation_coefficient',
                                'rule': 'greater_than',
                                'value': 0.7,
                                'background_color': self.color_palette['secondary']
                            },
                            {
                                'column': 'correlation_coefficient',
                                'rule': 'less_than',
                                'value': -0.7,
                                'background_color': self.color_palette['danger']
                            }
                        ]
                    }
                }
            ]
        }
        
        return correlation_page

    def create_complete_dashboard_config(self) -> Dict:
        """완전한 대시보드 설정 생성"""
        logger.info("🎨 완전한 대시보드 설정 생성")
        
        try:
            # 각 구성 요소 생성
            self.create_data_sources_config()
            self.create_calculated_fields()
            self.create_filters_config()
            
            # 페이지들 생성
            main_page = self.create_main_dashboard_page()
            time_series_page = self.create_time_series_page()
            correlation_page = self.create_correlation_page()
            
            self.dashboard_config['pages'] = [
                main_page,
                time_series_page,
                correlation_page
            ]
            
            # 대시보드 메타데이터 추가
            self.dashboard_config['metadata'] = {
                'created_at': datetime.now().isoformat(),
                'version': '1.0',
                'total_pages': len(self.dashboard_config['pages']),
                'total_components': sum(len(page['components']) for page in self.dashboard_config['pages']),
                'data_sources_count': len(self.dashboard_config['data_sources']),
                'calculated_fields_count': len(self.dashboard_config['calculated_fields']),
                'filters_count': len(self.dashboard_config['filters'])
            }
            
            # 설정 가이드 추가
            self.dashboard_config['setup_guide'] = self.create_setup_guide()
            
            return self.dashboard_config
            
        except Exception as e:
            logger.error(f"❌ 대시보드 설정 생성 실패: {e}")
            return {}

    def create_setup_guide(self) -> Dict:
        """설정 가이드 생성"""
        return {
            'step_by_step': [
                {
                    'step': 1,
                    'title': 'Google Drive 파일 확인',
                    'description': 'justbuild.pd@gmail.com 계정의 Google Drive에서 업로드된 파일들 확인',
                    'files_to_check': [
                        '지역별_요약_데이터.csv',
                        '시계열_데이터.csv',
                        '상관관계_매트릭스.csv'
                    ]
                },
                
                {
                    'step': 2,
                    'title': 'Google Sheets 변환',
                    'description': 'CSV 파일들을 Google Sheets로 변환',
                    'actions': [
                        'CSV 파일 우클릭 → "연결 프로그램" → "Google 스프레드시트"',
                        '각 시트의 이름을 확인: 지역별_요약_시트, 시계열_데이터_시트, 상관관계_매트릭스_시트'
                    ]
                },
                
                {
                    'step': 3,
                    'title': 'Google Data Studio 접속',
                    'description': 'datastudio.google.com 접속하여 새 보고서 생성',
                    'url': 'https://datastudio.google.com'
                },
                
                {
                    'step': 4,
                    'title': '데이터 소스 연결',
                    'description': 'Google Sheets 커넥터를 사용하여 각 시트 연결',
                    'data_sources': [
                        {'name': '지역별_요약_데이터', 'sheet': '지역별_요약_시트'},
                        {'name': '시계열_데이터', 'sheet': '시계열_데이터_시트'},
                        {'name': '상관관계_매트릭스', 'sheet': '상관관계_매트릭스_시트'}
                    ]
                },
                
                {
                    'step': 5,
                    'title': '계산된 필드 생성',
                    'description': '고급 분석을 위한 계산된 필드들 추가',
                    'fields_to_create': [
                        '인구_밀도', '가구당_인구', '주택_공급률', 
                        '정치_성향_점수', '예측_신뢰도_등급'
                    ]
                },
                
                {
                    'step': 6,
                    'title': '페이지 및 차트 구성',
                    'description': '3개 페이지와 차트들을 이 설정 파일에 따라 구성',
                    'pages': [
                        '🏠 메인 대시보드 (지도, KPI, 테이블)',
                        '📈 시계열 분석 (트렌드 차트)',
                        '🔗 상관관계 분석 (히트맵, 버블차트)'
                    ]
                },
                
                {
                    'step': 7,
                    'title': '필터 및 인터랙션 설정',
                    'description': '사용자 인터랙션을 위한 필터들 추가',
                    'filters': ['지역_필터', '정치성향_필터', '연도_필터', '예측신뢰도_필터']
                },
                
                {
                    'step': 8,
                    'title': '스타일링 및 최종 확인',
                    'description': '색상, 폰트, 레이아웃 조정 후 공유 설정',
                    'final_checks': [
                        '모든 차트가 올바르게 표시되는지 확인',
                        '필터가 정상 작동하는지 테스트',
                        '모바일 반응형 확인',
                        '공유 권한 설정'
                    ]
                }
            ],
            
            'troubleshooting': {
                'data_not_loading': [
                    'Google Sheets 권한 확인',
                    '데이터 소스 새로고침',
                    '필드 타입 확인'
                ],
                'charts_not_displaying': [
                    '필드 매핑 확인',
                    '데이터 필터 확인',
                    '차트 타입과 데이터 호환성 확인'
                ],
                'performance_issues': [
                    '데이터 샘플링 활성화',
                    '불필요한 필드 제거',
                    '계산된 필드 최적화'
                ]
            }
        }

    def export_dashboard_config(self) -> str:
        """대시보드 설정을 파일로 내보내기"""
        logger.info("💾 대시보드 설정 내보내기")
        
        try:
            config = self.create_complete_dashboard_config()
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data_studio_complete_dashboard_config_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ 대시보드 설정 저장: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"❌ 대시보드 설정 내보내기 실패: {e}")
            return ""

    def generate_setup_instructions(self) -> str:
        """설정 가이드 HTML 생성"""
        logger.info("📋 설정 가이드 HTML 생성")
        
        try:
            config = self.create_complete_dashboard_config()
            setup_guide = config['setup_guide']
            
            html_content = f"""
            <!DOCTYPE html>
            <html lang="ko">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Google Data Studio 대시보드 설정 가이드</title>
                <script src="https://cdn.tailwindcss.com"></script>
            </head>
            <body class="bg-gray-50">
                <div class="container mx-auto px-4 py-8">
                    <header class="text-center mb-8">
                        <h1 class="text-4xl font-bold text-gray-800 mb-4">
                            🏠 Google Data Studio 대시보드 설정 가이드
                        </h1>
                        <p class="text-xl text-gray-600">3차원 통합 선거 예측 시스템</p>
                        <div class="mt-4 text-sm text-gray-500">
                            계정: justbuild.pd@gmail.com | 생성일: {datetime.now().strftime('%Y-%m-%d %H:%M')}
                        </div>
                    </header>
                    
                    <div class="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-8">
                        <h2 class="text-2xl font-bold text-blue-800 mb-4">📊 대시보드 개요</h2>
                        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                            <div class="bg-white p-4 rounded-lg">
                                <div class="text-2xl font-bold text-blue-600">{config['metadata']['total_pages']}</div>
                                <div class="text-sm text-gray-600">페이지</div>
                            </div>
                            <div class="bg-white p-4 rounded-lg">
                                <div class="text-2xl font-bold text-green-600">{config['metadata']['total_components']}</div>
                                <div class="text-sm text-gray-600">차트</div>
                            </div>
                            <div class="bg-white p-4 rounded-lg">
                                <div class="text-2xl font-bold text-purple-600">{config['metadata']['data_sources_count']}</div>
                                <div class="text-sm text-gray-600">데이터 소스</div>
                            </div>
                            <div class="bg-white p-4 rounded-lg">
                                <div class="text-2xl font-bold text-orange-600">{config['metadata']['calculated_fields_count']}</div>
                                <div class="text-sm text-gray-600">계산된 필드</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="space-y-8">
            """
            
            # 단계별 가이드 추가
            for step_info in setup_guide['step_by_step']:
                html_content += f"""
                        <div class="bg-white rounded-lg shadow-md p-6">
                            <div class="flex items-center mb-4">
                                <div class="bg-blue-600 text-white rounded-full w-8 h-8 flex items-center justify-center font-bold mr-4">
                                    {step_info['step']}
                                </div>
                                <h3 class="text-xl font-bold text-gray-800">{step_info['title']}</h3>
                            </div>
                            <p class="text-gray-600 mb-4">{step_info['description']}</p>
                """
                
                # 추가 정보가 있으면 표시
                if 'files_to_check' in step_info:
                    html_content += "<div class='bg-gray-50 p-4 rounded-lg'><h4 class='font-semibold mb-2'>확인할 파일:</h4><ul class='list-disc list-inside'>"
                    for file in step_info['files_to_check']:
                        html_content += f"<li>{file}</li>"
                    html_content += "</ul></div>"
                
                if 'actions' in step_info:
                    html_content += "<div class='bg-gray-50 p-4 rounded-lg'><h4 class='font-semibold mb-2'>수행할 작업:</h4><ul class='list-disc list-inside'>"
                    for action in step_info['actions']:
                        html_content += f"<li>{action}</li>"
                    html_content += "</ul></div>"
                
                html_content += "</div>"
            
            html_content += """
                    </div>
                    
                    <div class="mt-12 bg-red-50 border border-red-200 rounded-lg p-6">
                        <h2 class="text-2xl font-bold text-red-800 mb-4">🔧 문제 해결</h2>
                        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            """
            
            # 문제 해결 가이드 추가
            for issue, solutions in setup_guide['troubleshooting'].items():
                html_content += f"""
                            <div class="bg-white p-4 rounded-lg">
                                <h4 class="font-semibold text-red-700 mb-2">{issue.replace('_', ' ').title()}</h4>
                                <ul class="list-disc list-inside text-sm">
                """
                for solution in solutions:
                    html_content += f"<li>{solution}</li>"
                html_content += "</ul></div>"
            
            html_content += """
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            html_filename = f"data_studio_setup_guide_{timestamp}.html"
            
            with open(html_filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"✅ 설정 가이드 HTML 생성: {html_filename}")
            return html_filename
            
        except Exception as e:
            logger.error(f"❌ 설정 가이드 HTML 생성 실패: {e}")
            return ""

def main():
    """메인 실행 함수"""
    generator = DataStudioDashboardGenerator()
    
    print("🎨 Google Data Studio 대시보드 자동 생성기")
    print("=" * 60)
    print("🎯 목적: 업로드된 데이터 기반 완벽한 대시보드 구성")
    print("📧 계정: justbuild.pd@gmail.com")
    print("🏠 대시보드: 3차원 통합 선거 예측 시스템")
    print("📊 구성: 3페이지, 다중 차트, 인터랙티브 필터")
    print("=" * 60)
    
    try:
        # 1. 대시보드 설정 생성
        print("\n1️⃣ 완전한 대시보드 설정 생성...")
        config_file = generator.export_dashboard_config()
        
        # 2. 설정 가이드 HTML 생성
        print("2️⃣ 설정 가이드 HTML 생성...")
        guide_file = generator.generate_setup_instructions()
        
        if config_file and guide_file:
            print(f"\n🎉 대시보드 설정 생성 완료!")
            print(f"📊 설정 파일: {config_file}")
            print(f"📋 가이드 파일: {guide_file}")
            
            # 설정 요약 출력
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            print(f"\n📈 대시보드 구성 요약:")
            print(f"  🏠 페이지: {config['metadata']['total_pages']}개")
            print(f"  📊 차트: {config['metadata']['total_components']}개")
            print(f"  📁 데이터 소스: {config['metadata']['data_sources_count']}개")
            print(f"  🧮 계산된 필드: {config['metadata']['calculated_fields_count']}개")
            print(f"  🔍 필터: {config['metadata']['filters_count']}개")
            
            print(f"\n📋 페이지 구성:")
            for i, page in enumerate(config['pages'], 1):
                print(f"  {i}. {page['name']} ({len(page['components'])}개 컴포넌트)")
            
            print(f"\n🔗 다음 단계:")
            print(f"  1. {guide_file} 파일을 브라우저에서 열어 단계별 가이드 확인")
            print(f"  2. Google Data Studio (datastudio.google.com) 접속")
            print(f"  3. 새 보고서 생성 후 가이드에 따라 설정")
            print(f"  4. justbuild.pd@gmail.com 계정의 Google Sheets 연결")
            print(f"  5. {config_file} 설정에 따라 차트 구성")
            
        else:
            print("\n❌ 대시보드 설정 생성 실패")
            
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()
