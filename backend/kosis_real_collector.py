#!/usr/bin/env python3
"""
KOSIS API 실제 데이터 수집기
비표준 JSON 응답 파싱 및 실제 통계 데이터 수집
"""

import requests
import re
import json
from datetime import datetime
import time

def parse_kosis_response(text):
    """KOSIS 비표준 JSON 응답 파싱"""
    try:
        # JavaScript 객체를 Python dict로 변환
        # 키를 따옴표로 감싸기
        text = re.sub(r'([a-zA-Z_][a-zA-Z0-9_]*):\"', r'"\1":"', text)
        text = re.sub(r'([a-zA-Z_][a-zA-Z0-9_]*):([0-9]+)', r'"\1":\2', text)
        
        # JSON 파싱 시도
        try:
            return json.loads(text)
        except:
            # 정규식으로 직접 파싱
            return parse_with_regex(text)
    except:
        return parse_with_regex(text)

def parse_with_regex(text):
    """정규식으로 직접 파싱"""
    results = []
    
    # 각 객체 추출
    objects = re.findall(r'\{([^}]+)\}', text)
    
    for obj in objects:
        item = {}
        
        # 각 필드 추출
        fields = [
            ('statJipyoId', r'statJipyoId:"?([^,"]+)"?'),
            ('statJipyoNm', r'statJipyoNm:"([^"]+)"'),
            ('unit', r'unit:"([^"]+)"'),
            ('areaTypeName', r'areaTypeName:"([^"]+)"'),
            ('prdSeName', r'prdSeName:"([^"]+)"'),
            ('strtPrdDe', r'strtPrdDe:"([^"]+)"'),
            ('endPrdDe', r'endPrdDe:"([^"]+)"'),
            ('rn', r'rn:"?([0-9]+)"?')
        ]
        
        for field_name, pattern in fields:
            match = re.search(pattern, obj)
            if match:
                item[field_name] = match.group(1)
        
        if item:
            results.append(item)
    
    return results

def collect_indicator_data(api_key, jipyo_id, area_code='00000', start_year='2020', end_year='2024'):
    """지표 데이터 수집"""
    try:
        url = 'https://kosis.kr/openapi/indDataSearchRequest.do'
        params = {
            'method': 'getList',
            'service': '4',
            'serviceDetail': 'indData',
            'apiKey': api_key,
            'jipyoId': jipyo_id,
            'areaCode': area_code,
            'startPrdDe': start_year,
            'endPrdDe': end_year,
            'format': 'json'
        }
        
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            # 데이터 응답 파싱
            text = response.text
            data_points = []
            
            # 데이터 포인트 추출
            objects = re.findall(r'\{([^}]+)\}', text)
            
            for obj in objects:
                point = {}
                
                # 데이터 필드 추출
                area_match = re.search(r'areaNm:"([^"]+)"', obj)
                period_match = re.search(r'prdDe:"([^"]+)"', obj)
                value_match = re.search(r'dt:"?([0-9,.-]+)"?', obj)
                
                if area_match and period_match and value_match:
                    point = {
                        'area': area_match.group(1),
                        'period': period_match.group(1),
                        'value': value_match.group(1).replace(',', '')
                    }
                    data_points.append(point)
            
            return data_points
        else:
            print(f'데이터 조회 실패: {response.status_code}')
            return []
            
    except Exception as e:
        print(f'데이터 수집 오류: {e}')
        return []

def main():
    api_key = 'ZDkwNzNhY2Y4YTg3NjdlNWEyNjg0YmM1NDFlMmFjNmU='
    
    print('🏛️ KOSIS API 실제 데이터 수집 시작')
    print('=' * 50)
    
    # 1. 인구 지표 검색
    print('1️⃣ 인구 지표 검색...')
    
    url = 'https://kosis.kr/openapi/indListSearchRequest.do'
    params = {
        'method': 'getList',
        'service': '4',
        'serviceDetail': 'indList',
        'apiKey': api_key,
        'jipyoNm': '인구',
        'pageNo': '1',
        'numOfRows': '20',
        'format': 'json'
    }
    
    try:
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            indicators = parse_kosis_response(response.text)
            print(f'✅ 인구 지표 {len(indicators)}개 발견')
            
            # 주요 지표 출력
            for i, ind in enumerate(indicators[:5]):
                jipyo_id = ind.get('statJipyoId', '?')
                jipyo_name = ind.get('statJipyoNm', '?')
                unit = ind.get('unit', '?')
                print(f'  {i+1}. {jipyo_id}: {jipyo_name} ({unit})')
            
            # 2. 실제 데이터 수집
            if indicators:
                target_id = indicators[0].get('statJipyoId', '1')
                target_name = indicators[0].get('statJipyoNm', '추계인구')
                
                print(f'\\n2️⃣ {target_name} 데이터 수집...')
                
                # 전국 데이터
                national_data = collect_indicator_data(api_key, target_id, '00000', '2020', '2024')
                print(f'📊 전국 데이터: {len(national_data)}개 포인트')
                
                for point in national_data:
                    try:
                        value = int(float(point['value']))
                        period = point['period']
                        print(f'  🇰🇷 {period}: {value:,}명')
                    except:
                        period = point['period']
                        value = point['value']
                        print(f'  🇰🇷 {period}: {value}')
                
                # 시도별 데이터 수집
                print(f'\\n3️⃣ 주요 시도별 데이터 수집...')
                
                regional_areas = [
                    ('11000', '서울특별시'),
                    ('21000', '부산광역시'),
                    ('31000', '경기도')
                ]
                
                regional_results = {}
                
                for area_code, area_name in regional_areas:
                    regional_data = collect_indicator_data(api_key, target_id, area_code, '2022', '2024')
                    regional_results[area_name] = regional_data
                    
                    print(f'  📍 {area_name}: {len(regional_data)}개 포인트')
                    for point in regional_data[:2]:  # 최근 2개만
                        try:
                            value = int(float(point['value']))
                            period = point['period']
                            print(f'    {period}: {value:,}명')
                        except:
                            period = point['period']
                            value = point['value']
                            print(f'    {period}: {value}')
                    
                    time.sleep(0.5)  # API 제한
                
                # 최종 결과 저장
                final_result = {
                    'collection_info': {
                        'timestamp': datetime.now().isoformat(),
                        'api_key_used': True,
                        'method': 'indListSearchRequest',
                        'success': True
                    },
                    'available_indicators': indicators,
                    'collected_data': {
                        'national': national_data,
                        'regional': regional_results
                    },
                    'summary': {
                        'indicators_found': len(indicators),
                        'national_data_points': len(national_data),
                        'regional_areas_collected': len(regional_results)
                    }
                }
                
                with open('kosis_comprehensive_real_data.json', 'w', encoding='utf-8') as f:
                    json.dump(final_result, f, ensure_ascii=False, indent=2)
                
                print(f'\\n💾 종합 실제 데이터 저장: kosis_comprehensive_real_data.json')
                print(f'✅ 실제 API 데이터 수집 성공!')
                
                return final_result
            
        else:
            print(f'❌ 지표 검색 실패: {response.status_code}')
            
    except Exception as e:
        print(f'❌ 수집 프로세스 실패: {e}')
    
    return None

if __name__ == "__main__":
    result = main()
    if result:
        print(f"\\n🎉 수집 완료: {result['summary']['indicators_found']}개 지표, {result['summary']['national_data_points']}개 전국 데이터")
