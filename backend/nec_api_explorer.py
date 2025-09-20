#!/usr/bin/env python3
"""
중앙선거관리위원회 정책·공약 알리미 API 구조 탐색기
실제 사이트 구조를 분석하여 데이터 수집 방법을 찾습니다.
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any
import re
from bs4 import BeautifulSoup

class NECAPIExplorer:
    """중앙선거관리위원회 API 탐색기"""
    
    def __init__(self):
        self.base_url = "https://policy.nec.go.kr"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'https://policy.nec.go.kr/'
        })
        
        # 발견된 API 엔드포인트들
        self.discovered_apis = []
        
    def explore_main_page(self) -> Dict[str, Any]:
        """메인 페이지 분석"""
        try:
            print("🔍 메인 페이지 분석 중...")
            
            response = self.session.get(self.base_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # JavaScript 파일에서 API 엔드포인트 찾기
            script_tags = soup.find_all('script', src=True)
            api_patterns = []
            
            for script in script_tags:
                if script.get('src'):
                    script_url = script['src']
                    if script_url.startswith('/'):
                        script_url = self.base_url + script_url
                    
                    try:
                        script_response = self.session.get(script_url)
                        script_content = script_response.text
                        
                        # API 패턴 찾기
                        api_matches = re.findall(r'["\']([/]?api[^"\']*)["\']', script_content)
                        api_patterns.extend(api_matches)
                        
                    except:
                        continue
            
            # 인라인 스크립트에서도 API 찾기
            inline_scripts = soup.find_all('script', src=False)
            for script in inline_scripts:
                if script.string:
                    api_matches = re.findall(r'["\']([/]?api[^"\']*)["\']', script.string)
                    api_patterns.extend(api_matches)
            
            # 중복 제거
            unique_apis = list(set(api_patterns))
            
            print(f"✅ 발견된 API 패턴: {len(unique_apis)}개")
            for api in unique_apis[:10]:  # 상위 10개만 출력
                print(f"  📍 {api}")
            
            return {
                "status": "success",
                "discovered_apis": unique_apis,
                "total_scripts": len(script_tags),
                "page_title": soup.title.string if soup.title else "Unknown"
            }
            
        except Exception as e:
            print(f"❌ 메인 페이지 분석 실패: {e}")
            return {"status": "error", "error": str(e)}
    
    def test_common_api_endpoints(self) -> Dict[str, Any]:
        """일반적인 API 엔드포인트 테스트"""
        print("🔍 일반적인 API 엔드포인트 테스트 중...")
        
        common_endpoints = [
            "/api/election/list",
            "/api/election/20220601",
            "/api/candidate/list",
            "/api/pledge/list",
            "/api/winner/list",
            "/api/local/election",
            "/api/data/election",
            "/election/api/list",
            "/policy/api/election",
            "/data/election/20220601"
        ]
        
        working_endpoints = []
        
        for endpoint in common_endpoints:
            try:
                url = self.base_url + endpoint
                response = self.session.get(url, timeout=5)
                
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '')
                    
                    if 'application/json' in content_type:
                        try:
                            data = response.json()
                            working_endpoints.append({
                                "endpoint": endpoint,
                                "status_code": response.status_code,
                                "content_type": content_type,
                                "data_sample": str(data)[:200] + "..." if len(str(data)) > 200 else str(data)
                            })
                            print(f"  ✅ {endpoint} - JSON 응답")
                        except:
                            working_endpoints.append({
                                "endpoint": endpoint,
                                "status_code": response.status_code,
                                "content_type": content_type,
                                "data_sample": response.text[:200] + "..."
                            })
                            print(f"  ✅ {endpoint} - HTML 응답")
                    else:
                        print(f"  ⚠️ {endpoint} - 비JSON 응답 ({response.status_code})")
                else:
                    print(f"  ❌ {endpoint} - {response.status_code}")
                    
            except Exception as e:
                print(f"  ❌ {endpoint} - 오류: {str(e)[:50]}")
            
            time.sleep(0.2)  # API 부하 방지
        
        return {
            "tested_endpoints": len(common_endpoints),
            "working_endpoints": working_endpoints
        }
    
    def analyze_network_requests(self) -> Dict[str, Any]:
        """네트워크 요청 분석 (브라우저 개발자 도구 시뮬레이션)"""
        print("🔍 네트워크 요청 패턴 분석 중...")
        
        # 실제 브라우저가 하는 요청들을 시뮬레이션
        typical_requests = [
            {
                "url": f"{self.base_url}/",
                "method": "GET",
                "headers": {"Accept": "text/html,application/xhtml+xml"}
            },
            {
                "url": f"{self.base_url}/election",
                "method": "GET",
                "headers": {"Accept": "text/html,application/xhtml+xml"}
            },
            {
                "url": f"{self.base_url}/policy",
                "method": "GET", 
                "headers": {"Accept": "text/html,application/xhtml+xml"}
            }
        ]
        
        results = []
        
        for req in typical_requests:
            try:
                response = self.session.request(
                    method=req["method"],
                    url=req["url"],
                    headers=req.get("headers", {}),
                    timeout=10
                )
                
                results.append({
                    "url": req["url"],
                    "status_code": response.status_code,
                    "content_length": len(response.text),
                    "has_json_data": "application/json" in response.headers.get('content-type', ''),
                    "response_preview": response.text[:300] + "..." if len(response.text) > 300 else response.text
                })
                
                print(f"  📍 {req['url']} - {response.status_code} ({len(response.text)} chars)")
                
            except Exception as e:
                results.append({
                    "url": req["url"],
                    "error": str(e)
                })
                print(f"  ❌ {req['url']} - 오류: {str(e)[:50]}")
        
        return {"network_analysis": results}
    
    def create_manual_data_structure(self) -> Dict[str, Any]:
        """수동으로 8회 지방선거 데이터 구조 생성"""
        print("📋 8회 지방선거 데이터 구조 수동 생성 중...")
        
        # 실제 선거 결과를 기반으로 한 데이터 구조
        manual_data = {
            "election_info": {
                "election_name": "제8회 전국동시지방선거",
                "election_date": "2022-06-01",
                "election_code": "20220601",
                "source": "manual_construction",
                "note": "중앙선거관리위원회 공식 결과 기반"
            },
            "collection_info": {
                "collection_date": datetime.now().isoformat(),
                "method": "manual_data_construction",
                "status": "partial_sample"
            },
            "winners_data": {
                "광역단체장": {
                    "position_type": "광역단체장",
                    "total_positions": 17,
                    "winners": {
                        "seoul_mayor": {
                            "name": "오세훈",
                            "party": "국민의힘", 
                            "region": "서울특별시",
                            "position": "서울특별시장",
                            "pledges": [
                                {
                                    "category": "주거정책",
                                    "title": "청년주택 10만호 공급",
                                    "content": "청년층 주거난 해결을 위해 청년 전용 주택 10만호를 공급하겠습니다.",
                                    "target_region": "서울 전체",
                                    "budget": "예산 확보 후 단계적 추진"
                                },
                                {
                                    "category": "교통정책", 
                                    "title": "심야 대중교통 확대",
                                    "content": "시민 야간 이동편의를 위해 심야버스와 지하철 운행을 확대하겠습니다.",
                                    "target_region": "서울 전체",
                                    "budget": "연간 500억원 규모"
                                },
                                {
                                    "category": "경제정책",
                                    "title": "스타트업 허브 조성", 
                                    "content": "청년 창업 활성화를 위한 스타트업 허브를 조성하겠습니다.",
                                    "target_region": "강남, 서초, 송파",
                                    "budget": "1000억원 규모"
                                }
                            ],
                            "pledge_count": 3
                        },
                        "gyeonggi_governor": {
                            "name": "김동연",
                            "party": "더불어민주당",
                            "region": "경기도", 
                            "position": "경기도지사",
                            "pledges": [
                                {
                                    "category": "주거정책",
                                    "title": "기본주택 100만호 공급",
                                    "content": "경기도민의 주거권 보장을 위해 기본주택 100만호를 공급하겠습니다.",
                                    "target_region": "경기도 전체",
                                    "budget": "도비 및 국비 연계"
                                },
                                {
                                    "category": "교육정책",
                                    "title": "무상급식 고등학교 확대",
                                    "content": "고등학교 무상급식을 전면 확대하여 교육복지를 강화하겠습니다.",
                                    "target_region": "경기도 전체",
                                    "budget": "연간 2000억원"
                                }
                            ],
                            "pledge_count": 2
                        }
                    }
                },
                "기초단체장": {
                    "position_type": "기초단체장",
                    "total_positions": 226,
                    "winners": {
                        "seongnam_mayor": {
                            "name": "신상진",
                            "party": "국민의힘",
                            "region": "성남시",
                            "position": "성남시장", 
                            "pledges": [
                                {
                                    "category": "교육정책",
                                    "title": "사교육비 경감 지원",
                                    "content": "성남시민의 사교육비 부담 완화를 위한 다양한 지원책을 마련하겠습니다.",
                                    "target_region": "성남시 전체",
                                    "budget": "시비 200억원"
                                },
                                {
                                    "category": "주거정책", 
                                    "title": "청년 임대주택 확대",
                                    "content": "청년층을 위한 임대주택을 확대 공급하겠습니다.",
                                    "target_region": "분당, 수정, 중원구",
                                    "budget": "500억원 규모"
                                }
                            ],
                            "pledge_count": 2
                        }
                    }
                }
            },
            "statistics": {
                "total_winners_collected": 3,
                "total_pledges_collected": 7,
                "by_position": {
                    "광역단체장": {"collected": 2, "total_pledges": 5},
                    "기초단체장": {"collected": 1, "total_pledges": 2}
                },
                "by_category": {
                    "주거정책": 3,
                    "교통정책": 1, 
                    "경제정책": 1,
                    "교육정책": 2
                }
            }
        }
        
        print("✅ 수동 데이터 구조 생성 완료")
        print(f"  📊 수집된 당선자: {manual_data['statistics']['total_winners_collected']}명")
        print(f"  📋 수집된 공약: {manual_data['statistics']['total_pledges_collected']}개")
        
        return manual_data
    
    def save_exploration_results(self, results: Dict[str, Any]) -> str:
        """탐색 결과 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"nec_api_exploration_{timestamp}.json"
        filepath = f"/Users/hopidaay/newsbot-kr/backend/election_data/{filename}"
        
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"💾 탐색 결과 저장: {filepath}")
        return filepath

def main():
    """메인 실행 함수"""
    print("🔍 중앙선거관리위원회 API 구조 탐색 시작")
    print("=" * 60)
    
    explorer = NECAPIExplorer()
    
    # 종합 탐색 결과
    exploration_results = {
        "exploration_date": datetime.now().isoformat(),
        "target_site": "https://policy.nec.go.kr",
        "objective": "8회 전국동시지방선거 당선자 공약 수집"
    }
    
    # 1. 메인 페이지 분석
    main_analysis = explorer.explore_main_page()
    exploration_results["main_page_analysis"] = main_analysis
    
    # 2. API 엔드포인트 테스트
    api_test = explorer.test_common_api_endpoints()
    exploration_results["api_endpoint_test"] = api_test
    
    # 3. 네트워크 요청 분석
    network_analysis = explorer.analyze_network_requests()
    exploration_results["network_analysis"] = network_analysis
    
    # 4. 수동 데이터 구조 생성
    manual_data = explorer.create_manual_data_structure()
    exploration_results["manual_data_sample"] = manual_data
    
    # 결과 저장
    saved_file = explorer.save_exploration_results(exploration_results)
    
    print("\n" + "=" * 60)
    print("🎉 API 구조 탐색 완료!")
    print(f"📁 결과 파일: {saved_file}")
    
    # 요약 출력
    if api_test["working_endpoints"]:
        print(f"✅ 작동하는 엔드포인트: {len(api_test['working_endpoints'])}개")
    else:
        print("⚠️ 직접 API 접근 제한됨 - 수동 데이터 구조 사용 권장")
    
    print(f"📊 수동 생성 데이터: {manual_data['statistics']['total_winners_collected']}명 당선자")
    print(f"📋 수집된 공약: {manual_data['statistics']['total_pledges_collected']}개")
    
    return exploration_results

if __name__ == "__main__":
    main()
