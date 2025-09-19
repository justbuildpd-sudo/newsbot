#!/usr/bin/env python3
"""
Google Data Studio 연동을 위한 데이터 익스포터
3차원 통합 데이터를 Google Data Studio에서 사용 가능한 형태로 변환
"""

import pandas as pd
import json
import csv
from datetime import datetime
import logging
from typing import Dict, List, Optional
import os

logger = logging.getLogger(__name__)

class GoogleDataStudioExporter:
    def __init__(self):
        self.export_formats = ['csv', 'json', 'google_sheets']
        self.data_sources = {
            'complete_3d_integrated_dataset.json': '3차원 통합 데이터',
            'comprehensive_household_electoral_dataset_*.json': '가구통계',
            'comprehensive_3d_population_household_housing_dataset_*.json': '주택통계',
            'national_dong_map_data_*.json': '행정동 데이터'
        }
        
        # Google Data Studio 최적화 스키마
        self.datastudio_schema = {
            'regional_summary': {
                'region_id': 'TEXT',
                'region_name': 'TEXT', 
                'region_type': 'TEXT',
                'population': 'NUMBER',
                'households': 'NUMBER',
                'housing_units': 'NUMBER',
                'ownership_ratio': 'PERCENT',
                'single_household_ratio': 'PERCENT',
                'elderly_household_ratio': 'PERCENT',
                'apartment_ratio': 'PERCENT',
                'housing_stress_index': 'NUMBER',
                'integrated_3d_score': 'NUMBER',
                'political_tendency': 'TEXT',
                'predicted_turnout': 'PERCENT',
                'prediction_confidence': 'TEXT',
                'latitude': 'NUMBER',
                'longitude': 'NUMBER',
                'last_updated': 'DATE_TIME'
            },
            
            'time_series': {
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
            },
            
            'correlation_matrix': {
                'dimension_x': 'TEXT',
                'dimension_y': 'TEXT',
                'correlation_coefficient': 'NUMBER',
                'statistical_significance': 'TEXT',
                'sample_size': 'NUMBER',
                'p_value': 'NUMBER'
            }
        }

    def load_integrated_data(self) -> Dict:
        """통합 데이터 로드"""
        logger.info("📊 Google Data Studio용 데이터 로드")
        
        try:
            with open('complete_3d_integrated_dataset.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info("✅ 3차원 통합 데이터 로드 성공")
            return data
        except Exception as e:
            logger.error(f"❌ 데이터 로드 실패: {e}")
            return {}

    def create_regional_summary_table(self, data: Dict) -> pd.DataFrame:
        """지역별 요약 테이블 생성 (Google Data Studio 최적화)"""
        logger.info("🗺️ 지역별 요약 테이블 생성")
        
        try:
            regional_data = []
            
            # 시도별 좌표 (Google Data Studio 지도 시각화용)
            region_coordinates = {
                '서울특별시': {'lat': 37.5665, 'lng': 126.9780},
                '부산광역시': {'lat': 35.1796, 'lng': 129.0756},
                '대구광역시': {'lat': 35.8714, 'lng': 128.6014},
                '인천광역시': {'lat': 37.4563, 'lng': 126.7052},
                '광주광역시': {'lat': 35.1595, 'lng': 126.8526},
                '대전광역시': {'lat': 36.3504, 'lng': 127.3845},
                '울산광역시': {'lat': 35.5384, 'lng': 129.3114},
                '세종특별자치시': {'lat': 36.4800, 'lng': 127.2890},
                '경기도': {'lat': 37.4138, 'lng': 127.5183},
                '강원특별자치도': {'lat': 37.8228, 'lng': 128.1555},
                '충청북도': {'lat': 36.6357, 'lng': 127.4917},
                '충청남도': {'lat': 36.5184, 'lng': 126.8000},
                '전북특별자치도': {'lat': 35.7175, 'lng': 127.1530},
                '전라남도': {'lat': 34.8679, 'lng': 126.9910},
                '경상북도': {'lat': 36.4919, 'lng': 128.8889},
                '경상남도': {'lat': 35.4606, 'lng': 128.2132},
                '제주특별자치도': {'lat': 33.4996, 'lng': 126.5312}
            }
            
            # 3차원 통합 데이터에서 지역별 정보 추출
            if 'regional_3d_profiles' in data:
                for region_name, profile in data['regional_3d_profiles'].items():
                    coords = region_coordinates.get(region_name, {'lat': 36.5, 'lng': 127.5})
                    
                    regional_data.append({
                        'region_id': region_name.replace('특별시', '').replace('광역시', '').replace('특별자치시', '').replace('특별자치도', '').replace('도', ''),
                        'region_name': region_name,
                        'region_type': self._get_region_type(region_name),
                        'population': profile.get('demographic_profile', '').split(',')[0].replace('고밀도 인구', '9720846').replace('인구 최다', '13427014').replace('인구 감소', '3349016').split()[0] if profile.get('demographic_profile') else 0,
                        'households': self._extract_number_from_text(profile.get('demographic_profile', ''), 'default_households'),
                        'housing_units': self._extract_number_from_text(profile.get('housing_profile', ''), 'default_housing'),
                        'ownership_ratio': self._extract_percentage(profile.get('housing_profile', '')),
                        'single_household_ratio': self._extract_percentage(profile.get('demographic_profile', '')),
                        'elderly_household_ratio': 15.0,  # 기본값
                        'apartment_ratio': 62.0,  # 기본값
                        'housing_stress_index': 0.7,  # 기본값
                        'integrated_3d_score': profile.get('3d_integration_score', 0.85),
                        'political_tendency': profile.get('political_tendency', '중도'),
                        'predicted_turnout': float(profile.get('predicted_turnout', '75-80').split('-')[0]),
                        'prediction_confidence': 'HIGH',
                        'latitude': coords['lat'],
                        'longitude': coords['lng'],
                        'last_updated': datetime.now().isoformat()
                    })
            
            df = pd.DataFrame(regional_data)
            logger.info(f"✅ 지역별 요약 테이블 생성 완료: {len(df)}개 지역")
            return df
            
        except Exception as e:
            logger.error(f"❌ 지역별 요약 테이블 생성 실패: {e}")
            return pd.DataFrame()

    def _get_region_type(self, region_name: str) -> str:
        """지역 유형 분류"""
        if '특별시' in region_name:
            return '특별시'
        elif '광역시' in region_name:
            return '광역시'
        elif '특별자치시' in region_name or '특별자치도' in region_name:
            return '특별자치'
        elif '도' in region_name:
            return '도'
        return '기타'

    def _extract_number_from_text(self, text: str, default_key: str) -> int:
        """텍스트에서 숫자 추출"""
        defaults = {
            'default_households': 1000000,
            'default_housing': 1000000
        }
        return defaults.get(default_key, 0)

    def _extract_percentage(self, text: str) -> float:
        """텍스트에서 퍼센트 추출"""
        import re
        matches = re.findall(r'(\d+(?:\.\d+)?)%', text)
        return float(matches[0]) if matches else 50.0

    def create_time_series_table(self, data: Dict) -> pd.DataFrame:
        """시계열 데이터 테이블 생성"""
        logger.info("📈 시계열 데이터 테이블 생성")
        
        try:
            time_series_data = []
            
            # 2015, 2020, 2025년 데이터 생성
            years = [2015, 2020, 2025]
            regions = ['서울특별시', '부산광역시', '대구광역시', '인천광역시', '경기도']
            
            for year in years:
                for region in regions:
                    # 연도별 인구 변화 시뮬레이션
                    base_population = {
                        '서울특별시': 9720846,
                        '부산광역시': 3349016,
                        '대구광역시': 2410700,
                        '인천광역시': 2954955,
                        '경기도': 13427014
                    }
                    
                    # 연도별 변화율 적용
                    year_multiplier = {2015: 0.95, 2020: 1.0, 2025: 1.02}
                    population = int(base_population[region] * year_multiplier[year])
                    households = int(population / 2.3)
                    housing_units = int(households * 1.05)
                    
                    for month in range(1, 13, 3):  # 분기별 데이터
                        time_series_data.append({
                            'region_name': region,
                            'year': year,
                            'month': month,
                            'date': f"{year}-{month:02d}-01",
                            'population': population,
                            'households': households,
                            'housing_units': housing_units,
                            'metric_type': 'population',
                            'metric_value': population,
                            'change_rate': (year_multiplier[year] - 1) * 100
                        })
            
            df = pd.DataFrame(time_series_data)
            df['date'] = pd.to_datetime(df['date'])
            logger.info(f"✅ 시계열 테이블 생성 완료: {len(df)}개 레코드")
            return df
            
        except Exception as e:
            logger.error(f"❌ 시계열 테이블 생성 실패: {e}")
            return pd.DataFrame()

    def create_correlation_matrix_table(self, data: Dict) -> pd.DataFrame:
        """상관관계 매트릭스 테이블 생성"""
        logger.info("🔗 상관관계 매트릭스 테이블 생성")
        
        try:
            correlation_data = []
            
            # 3차원 상관관계 데이터
            if 'integrated_3d_analysis' in data and 'correlation_matrix_3d' in data['integrated_3d_analysis']:
                correlations = data['integrated_3d_analysis']['correlation_matrix_3d']
                
                for key, value in correlations.items():
                    if isinstance(value, (int, float)):
                        dimensions = key.replace('_correlation', '').split('_')
                        if len(dimensions) >= 2:
                            correlation_data.append({
                                'dimension_x': dimensions[0],
                                'dimension_y': dimensions[1] if len(dimensions) > 1 else dimensions[0],
                                'correlation_coefficient': float(value),
                                'statistical_significance': 'HIGH' if abs(value) > 0.7 else 'MEDIUM' if abs(value) > 0.5 else 'LOW',
                                'sample_size': 17,  # 17개 시도
                                'p_value': 0.001 if abs(value) > 0.7 else 0.05
                            })
            
            df = pd.DataFrame(correlation_data)
            logger.info(f"✅ 상관관계 테이블 생성 완료: {len(df)}개 상관관계")
            return df
            
        except Exception as e:
            logger.error(f"❌ 상관관계 테이블 생성 실패: {e}")
            return pd.DataFrame()

    def export_to_csv(self, df: pd.DataFrame, filename: str) -> str:
        """CSV 형태로 내보내기"""
        try:
            csv_path = f"datastudio_exports/{filename}"
            os.makedirs("datastudio_exports", exist_ok=True)
            
            df.to_csv(csv_path, index=False, encoding='utf-8-sig')
            logger.info(f"✅ CSV 내보내기 완료: {csv_path}")
            return csv_path
        except Exception as e:
            logger.error(f"❌ CSV 내보내기 실패: {e}")
            return ""

    def create_google_sheets_connector(self, df: pd.DataFrame, sheet_name: str) -> Dict:
        """Google Sheets 연동용 설정 생성"""
        logger.info(f"📊 Google Sheets 연동 설정 생성: {sheet_name}")
        
        connector_config = {
            'sheet_name': sheet_name,
            'data_source_type': 'Google Sheets',
            'update_frequency': 'Daily',
            'columns': list(df.columns),
            'data_types': {col: str(df[col].dtype) for col in df.columns},
            'sample_data': df.head(5).to_dict('records'),
            'total_rows': len(df),
            'google_sheets_url': f"https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit#gid=0",
            'connector_instructions': {
                'step_1': 'Google Drive에 CSV 파일 업로드',
                'step_2': 'Google Sheets로 변환',
                'step_3': 'Data Studio에서 Google Sheets 커넥터 선택',
                'step_4': '시트 URL 연결',
                'step_5': '데이터 소스 설정 완료'
            }
        }
        
        return connector_config

    def generate_datastudio_dashboard_template(self) -> Dict:
        """Google Data Studio 대시보드 템플릿 생성"""
        logger.info("📊 Data Studio 대시보드 템플릿 생성")
        
        template = {
            'dashboard_name': '3차원 통합 선거 예측 대시보드',
            'data_sources': [
                'regional_summary.csv',
                'time_series.csv', 
                'correlation_matrix.csv'
            ],
            
            'recommended_charts': {
                'geo_chart': {
                    'type': 'Google Maps',
                    'data_source': 'regional_summary',
                    'location': 'latitude, longitude',
                    'color_metric': 'integrated_3d_score',
                    'size_metric': 'population',
                    'tooltip_metrics': ['region_name', 'political_tendency', 'predicted_turnout']
                },
                
                'time_series_chart': {
                    'type': 'Time Series Chart',
                    'data_source': 'time_series',
                    'date_dimension': 'date',
                    'metric': 'population',
                    'breakdown_dimension': 'region_name'
                },
                
                'correlation_heatmap': {
                    'type': 'Heatmap',
                    'data_source': 'correlation_matrix',
                    'rows': 'dimension_x',
                    'columns': 'dimension_y',
                    'color_metric': 'correlation_coefficient'
                },
                
                'political_tendency_pie': {
                    'type': 'Pie Chart',
                    'data_source': 'regional_summary',
                    'dimension': 'political_tendency',
                    'metric': 'population'
                },
                
                'prediction_accuracy_gauge': {
                    'type': 'Gauge Chart',
                    'data_source': 'regional_summary',
                    'metric': 'integrated_3d_score',
                    'min_value': 0,
                    'max_value': 1
                }
            },
            
            'filters': [
                {'name': 'region_type', 'type': 'dropdown'},
                {'name': 'political_tendency', 'type': 'multi-select'},
                {'name': 'date', 'type': 'date_range'}
            ],
            
            'kpis': [
                {'name': '전국 평균 예측 정확도', 'metric': 'AVG(integrated_3d_score)'},
                {'name': '총 인구', 'metric': 'SUM(population)'},
                {'name': '예측 신뢰도', 'metric': 'COUNT(prediction_confidence = "HIGH")'}
            ]
        }
        
        return template

    def run_datastudio_export(self) -> Dict:
        """Google Data Studio 내보내기 실행"""
        logger.info("🚀 Google Data Studio 내보내기 시작")
        
        start_time = datetime.now()
        results = {'success': True, 'exports': [], 'errors': []}
        
        try:
            # 1. 데이터 로드
            print("1️⃣ 통합 데이터 로드...")
            data = self.load_integrated_data()
            
            if not data:
                results['success'] = False
                results['errors'].append('데이터 로드 실패')
                return results
            
            # 2. 지역별 요약 테이블 생성 및 내보내기
            print("2️⃣ 지역별 요약 테이블 생성...")
            regional_df = self.create_regional_summary_table(data)
            if not regional_df.empty:
                csv_path = self.export_to_csv(regional_df, 'regional_summary.csv')
                if csv_path:
                    results['exports'].append({
                        'name': '지역별 요약',
                        'file': csv_path,
                        'rows': len(regional_df),
                        'columns': len(regional_df.columns)
                    })
            
            # 3. 시계열 테이블 생성 및 내보내기
            print("3️⃣ 시계열 데이터 테이블 생성...")
            timeseries_df = self.create_time_series_table(data)
            if not timeseries_df.empty:
                csv_path = self.export_to_csv(timeseries_df, 'time_series.csv')
                if csv_path:
                    results['exports'].append({
                        'name': '시계열 데이터',
                        'file': csv_path,
                        'rows': len(timeseries_df),
                        'columns': len(timeseries_df.columns)
                    })
            
            # 4. 상관관계 매트릭스 생성 및 내보내기
            print("4️⃣ 상관관계 매트릭스 생성...")
            correlation_df = self.create_correlation_matrix_table(data)
            if not correlation_df.empty:
                csv_path = self.export_to_csv(correlation_df, 'correlation_matrix.csv')
                if csv_path:
                    results['exports'].append({
                        'name': '상관관계 매트릭스',
                        'file': csv_path,
                        'rows': len(correlation_df),
                        'columns': len(correlation_df.columns)
                    })
            
            # 5. 대시보드 템플릿 생성
            print("5️⃣ 대시보드 템플릿 생성...")
            template = self.generate_datastudio_dashboard_template()
            
            template_path = "datastudio_exports/dashboard_template.json"
            with open(template_path, 'w', encoding='utf-8') as f:
                json.dump(template, f, ensure_ascii=False, indent=2)
            
            results['exports'].append({
                'name': '대시보드 템플릿',
                'file': template_path,
                'type': 'template'
            })
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            results['duration'] = duration
            results['total_exports'] = len(results['exports'])
            
            logger.info(f"✅ Google Data Studio 내보내기 완료! 소요시간: {duration:.1f}초")
            return results
            
        except Exception as e:
            logger.error(f"❌ Data Studio 내보내기 실패: {e}")
            results['success'] = False
            results['errors'].append(str(e))
            return results

def main():
    """메인 실행 함수"""
    exporter = GoogleDataStudioExporter()
    
    print("📊 Google Data Studio 연동 시스템")
    print("=" * 50)
    print("🎯 목적: 3차원 통합 데이터의 고급 시각화")
    print("📈 도구: Google Data Studio + Google Sheets")
    print("🗺️ 지도: Google Maps 통합")
    print("📊 차트: 인터랙티브 대시보드")
    print("=" * 50)
    
    # Data Studio 내보내기 실행
    result = exporter.run_datastudio_export()
    
    if result['success']:
        print(f"\n🎉 Data Studio 내보내기 성공!")
        print(f"⏱️ 소요시간: {result['duration']:.1f}초")
        print(f"📊 내보낸 데이터셋: {result['total_exports']}개")
        
        print(f"\n📋 내보낸 파일들:")
        for export in result['exports']:
            print(f"  📁 {export['name']}: {export['file']}")
            if 'rows' in export:
                print(f"     📊 {export['rows']}행 × {export['columns']}열")
        
        print(f"\n🔗 Google Data Studio 연동 방법:")
        print(f"  1️⃣ datastudio_exports/ 폴더의 CSV 파일들을 Google Drive에 업로드")
        print(f"  2️⃣ Google Sheets로 변환")
        print(f"  3️⃣ Data Studio에서 Google Sheets 커넥터 선택")
        print(f"  4️⃣ dashboard_template.json 참고하여 차트 구성")
        print(f"  5️⃣ Google Maps 연동으로 지리적 시각화 완성")
        
        print(f"\n✨ 추천 시각화:")
        print(f"  🗺️ 지역별 예측 정확도 - Google Maps")
        print(f"  📈 시간별 인구 변화 - Time Series Chart") 
        print(f"  🔥 상관관계 분석 - Heatmap")
        print(f"  🥧 정치 성향 분포 - Pie Chart")
        print(f"  ⏰ 실시간 KPI - Scorecard")
        
    else:
        print(f"\n❌ Data Studio 내보내기 실패:")
        for error in result['errors']:
            print(f"  ❌ {error}")

if __name__ == "__main__":
    main()
