#!/usr/bin/env python3
"""
종합 API 키 관리 시스템
모든 API 키를 용도별로 복원, 정리, 관리하는 통합 시스템
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from secure_credentials_manager import SecureCredentialsManager

logger = logging.getLogger(__name__)

class ComprehensiveAPIManager:
    def __init__(self):
        self.credentials_manager = SecureCredentialsManager()
        
        # 발견된 모든 API 키들 (코드베이스에서 추출)
        self.discovered_apis = {
            # 통계청 관련
            'kosis_api': {
                'name': '통계청 KOSIS API',
                'key': 'ZDkwNzNhY2Y4YTg3NjdlNWEyNjg0YmM1NDFlMmFjNmU=',
                'description': '인구주택총조사, 경제활동인구조사 등 국가통계 데이터',
                'endpoints': [
                    'https://kosis.kr/openapi/statisticsList.do',
                    'https://kosis.kr/openapi/statisticsData.do'
                ],
                'usage': ['인구 통계', '가구 통계', '지역별 통계', '시계열 분석'],
                'status': 'active'
            },
            
            # 네이버 API
            'naver_search_api': {
                'name': '네이버 검색 API',
                'client_id': 'kXwlSsFmb055ku9rWyx1',
                'client_secret': 'JZqw_LTiq_',
                'description': '네이버 뉴스 검색, 블로그 검색, 웹 검색 서비스',
                'endpoints': [
                    'https://openapi.naver.com/v1/search/news',
                    'https://openapi.naver.com/v1/search/blog',
                    'https://openapi.naver.com/v1/search/webkr'
                ],
                'usage': ['뉴스 검색', '여론 분석', '정치인 언급량', '이슈 트렌드'],
                'status': 'active'
            },
            
            # 공공데이터 포털
            'data_go_kr_api': {
                'name': '공공데이터포털 API',
                'key': 'RoSdWk52fty0NNpB6SxxmgXiC2vEXOpOSw1bHPcRxuBEmcXi91fT52waWOMDo67trsxWJcm59pVGNYExnLOa8A==',
                'description': '정부 공공데이터 통합 서비스',
                'endpoints': [
                    'https://apis.data.go.kr/1160100/service/',
                    'https://apis.data.go.kr/1741000/DisasterMsg3/'
                ],
                'usage': ['공공데이터', '재해정보', '행정구역', '시설정보'],
                'status': 'active'
            },
            
            # 뉴스 API (News API)
            'news_api': {
                'name': 'News API',
                'key': '57a5b206dc5341889b4ee3fbbb8757be',
                'description': '글로벌 뉴스 데이터 서비스',
                'endpoints': [
                    'https://newsapi.org/v2/everything',
                    'https://newsapi.org/v2/top-headlines'
                ],
                'usage': ['해외 뉴스', '글로벌 트렌드', '국제 정치', '경제 뉴스'],
                'status': 'active'
            },
            
            # Google APIs (OAuth2 필요)
            'google_apis': {
                'name': 'Google APIs',
                'account': 'justbuild.pd@gmail.com',
                'password': 'jsjs807883',
                'description': 'Google Drive, Data Studio, Maps, OAuth2 통합',
                'services': [
                    'Google Drive API',
                    'Google Sheets API', 
                    'Google Data Studio API',
                    'Google Maps API',
                    'Google Cloud Translation API'
                ],
                'usage': ['데이터 저장', '시각화', '지도 서비스', '번역'],
                'oauth2_required': True,
                'status': 'setup_required'
            }
        }
        
        # 추가 확인이 필요한 API들
        self.apis_to_investigate = {
            'national_assembly_api': {
                'name': '국회 의안정보시스템 API',
                'description': '의원 정보, 법안 정보, 회의록 등',
                'potential_endpoints': [
                    'https://open.assembly.go.kr/portal/openapi/',
                    'https://www.assembly.go.kr/portal/openapi/'
                ],
                'usage': ['의원 정보', '법안 추적', '입법 활동', '회의록 분석'],
                'status': 'investigation_needed'
            },
            
            'election_commission_api': {
                'name': '중앙선거관리위원회 API',
                'description': '선거 결과, 후보자 정보, 투표율 등',
                'potential_endpoints': [
                    'https://info.nec.go.kr/openapi/',
                    'https://www.nec.go.kr/portal/openapi/'
                ],
                'usage': ['선거 결과', '후보자 정보', '투표율', '선거구 정보'],
                'status': 'investigation_needed'
            },
            
            'sgis_housing_api': {
                'name': 'SGIS 주택통계 API',
                'description': '통계청 SGIS 주택 및 가구 통계',
                'endpoints': [
                    'https://sgisapi.kostat.go.kr/OpenAPI3/stats/house.json',
                    'https://sgisapi.kostat.go.kr/OpenAPI3/stats/household.json'
                ],
                'usage': ['주택 통계', '가구 통계', '주거 실태', '부동산 분석'],
                'status': 'authentication_needed'
            }
        }

    def restore_all_api_keys(self) -> Dict:
        """모든 API 키 복원 및 보안 저장"""
        logger.info("🔑 모든 API 키 복원 및 보안 저장")
        
        restoration_results = {
            'restored_count': 0,
            'failed_count': 0,
            'restored_apis': [],
            'failed_apis': [],
            'total_apis': len(self.discovered_apis)
        }
        
        try:
            for api_id, api_info in self.discovered_apis.items():
                try:
                    # API별 인증 정보 준비
                    credentials = {}
                    
                    if api_id == 'kosis_api':
                        credentials = {'api_key': api_info['key']}
                    
                    elif api_id == 'naver_search_api':
                        credentials = {
                            'client_id': api_info['client_id'],
                            'client_secret': api_info['client_secret']
                        }
                    
                    elif api_id == 'data_go_kr_api':
                        credentials = {'service_key': api_info['key']}
                    
                    elif api_id == 'news_api':
                        credentials = {'api_key': api_info['key']}
                    
                    elif api_id == 'google_apis':
                        credentials = {
                            'email': api_info['account'],
                            'password': api_info['password']
                        }
                    
                    if credentials:
                        # 보안 저장
                        success = self.credentials_manager.store_credentials(api_id, credentials)
                        
                        if success:
                            restoration_results['restored_count'] += 1
                            restoration_results['restored_apis'].append({
                                'api_id': api_id,
                                'name': api_info['name'],
                                'description': api_info['description']
                            })
                            logger.info(f"✅ {api_info['name']} 복원 완료")
                        else:
                            restoration_results['failed_count'] += 1
                            restoration_results['failed_apis'].append(api_id)
                            logger.error(f"❌ {api_info['name']} 복원 실패")
                    
                except Exception as e:
                    restoration_results['failed_count'] += 1
                    restoration_results['failed_apis'].append(api_id)
                    logger.error(f"❌ {api_id} 복원 중 오류: {e}")
            
            logger.info(f"✅ API 키 복원 완료: {restoration_results['restored_count']}/{restoration_results['total_apis']}")
            return restoration_results
            
        except Exception as e:
            logger.error(f"❌ API 키 복원 실패: {e}")
            return restoration_results

    def investigate_missing_apis(self) -> Dict:
        """누락된 API 키 조사 및 확인"""
        logger.info("🔍 누락된 API 키 조사")
        
        investigation_results = {
            'apis_to_check': [],
            'recommended_actions': [],
            'priority_apis': []
        }
        
        try:
            for api_id, api_info in self.apis_to_investigate.items():
                investigation_results['apis_to_check'].append({
                    'api_id': api_id,
                    'name': api_info['name'],
                    'description': api_info['description'],
                    'status': api_info['status'],
                    'usage': api_info['usage'],
                    'endpoints': api_info.get('potential_endpoints', api_info.get('endpoints', []))
                })
                
                # 우선순위 API 식별
                if api_id in ['national_assembly_api', 'election_commission_api']:
                    investigation_results['priority_apis'].append(api_id)
            
            # 권장 조치사항
            investigation_results['recommended_actions'] = [
                {
                    'action': '국회 의안정보시스템 API 키 발급',
                    'url': 'https://open.assembly.go.kr/portal/openapi/',
                    'description': '의원 정보, 법안 정보 API 키 신청',
                    'priority': 'HIGH'
                },
                {
                    'action': '중앙선거관리위원회 API 키 발급',
                    'url': 'https://info.nec.go.kr/openapi/',
                    'description': '선거 결과, 후보자 정보 API 키 신청',
                    'priority': 'HIGH'
                },
                {
                    'action': 'SGIS API 인증키 발급',
                    'url': 'https://sgis.kostat.go.kr/developer/html/newOpenApi/api/dataApi/addressBoundary.html',
                    'description': '통계청 SGIS 주택/가구 통계 API',
                    'priority': 'MEDIUM'
                },
                {
                    'action': 'Google Cloud Console OAuth2 설정',
                    'url': 'https://console.cloud.google.com/',
                    'description': 'Google APIs OAuth2 클라이언트 설정',
                    'priority': 'VERY_HIGH'
                }
            ]
            
            return investigation_results
            
        except Exception as e:
            logger.error(f"❌ API 조사 실패: {e}")
            return investigation_results

    def setup_oauth2_config(self) -> Dict:
        """OAuth2 설정 구성"""
        logger.info("🔐 OAuth2 설정 구성")
        
        oauth2_config = {
            'google_oauth2': {
                'project_name': 'newsbot-kr-analytics',
                'client_type': 'desktop_application',
                'scopes': [
                    'https://www.googleapis.com/auth/drive.file',
                    'https://www.googleapis.com/auth/drive.metadata',
                    'https://www.googleapis.com/auth/spreadsheets',
                    'https://www.googleapis.com/auth/presentations',
                    'https://www.googleapis.com/auth/analytics.readonly'
                ],
                'redirect_uris': [
                    'http://localhost:8080/oauth2callback',
                    'urn:ietf:wg:oauth:2.0:oob'
                ],
                'setup_steps': [
                    {
                        'step': 1,
                        'title': 'Google Cloud Console 프로젝트 생성',
                        'description': 'console.cloud.google.com에서 새 프로젝트 생성',
                        'url': 'https://console.cloud.google.com/projectcreate'
                    },
                    {
                        'step': 2,
                        'title': 'API 활성화',
                        'description': 'Drive API, Sheets API, Data Studio API 활성화',
                        'apis_to_enable': [
                            'Google Drive API',
                            'Google Sheets API',
                            'Google Data Studio API',
                            'Google Maps API'
                        ]
                    },
                    {
                        'step': 3,
                        'title': 'OAuth2 클라이언트 ID 생성',
                        'description': '사용자 인증 정보 → OAuth 2.0 클라이언트 ID → 데스크톱 애플리케이션',
                        'url': 'https://console.cloud.google.com/apis/credentials'
                    },
                    {
                        'step': 4,
                        'title': 'credentials.json 다운로드',
                        'description': '생성된 클라이언트 ID의 JSON 파일 다운로드',
                        'target_location': '/Users/hopidaay/newsbot-kr/backend/credentials.json'
                    },
                    {
                        'step': 5,
                        'title': 'OAuth2 동의 화면 설정',
                        'description': '테스트 사용자에 justbuild.pd@gmail.com 추가',
                        'url': 'https://console.cloud.google.com/apis/credentials/consent'
                    }
                ]
            }
        }
        
        return oauth2_config

    def create_api_usage_guide(self) -> Dict:
        """API 용도별 사용 가이드 생성"""
        logger.info("📚 API 용도별 사용 가이드 생성")
        
        usage_guide = {
            '선거_예측_분석': {
                'description': '선거 결과 예측 및 분석',
                'required_apis': [
                    'kosis_api',           # 인구통계
                    'naver_search_api',    # 여론 분석
                    'election_commission_api',  # 선거 데이터
                    'google_apis'          # 데이터 저장/시각화
                ],
                'data_flow': [
                    '1. KOSIS API → 인구/가구/주택 통계 수집',
                    '2. 네이버 API → 정치인/이슈 언급량 분석',
                    '3. 선관위 API → 과거 선거 결과 수집',
                    '4. Google APIs → 데이터 저장 및 시각화'
                ]
            },
            
            '정치인_분석': {
                'description': '정치인 활동 및 여론 분석',
                'required_apis': [
                    'national_assembly_api',  # 의정 활동
                    'naver_search_api',       # 언론 노출
                    'news_api',               # 해외 언급
                    'google_apis'             # 분석 결과 저장
                ],
                'data_flow': [
                    '1. 국회 API → 의원 법안 발의/표결 정보',
                    '2. 네이버 API → 국내 언론 언급량',
                    '3. News API → 해외 언론 언급',
                    '4. Google APIs → 종합 분석 리포트'
                ]
            },
            
            '지역_분석': {
                'description': '지역별 정치/사회 현황 분석',
                'required_apis': [
                    'kosis_api',           # 지역 통계
                    'sgis_housing_api',    # 주택 통계
                    'data_go_kr_api',      # 공공데이터
                    'google_apis'          # 지도 시각화
                ],
                'data_flow': [
                    '1. KOSIS API → 지역별 인구/경제 통계',
                    '2. SGIS API → 지역별 주택/가구 통계',
                    '3. 공공데이터 API → 지역 시설/서비스 정보',
                    '4. Google Maps API → 지리적 시각화'
                ]
            },
            
            '여론_분석': {
                'description': '실시간 여론 및 트렌드 분석',
                'required_apis': [
                    'naver_search_api',    # 검색 트렌드
                    'news_api',            # 뉴스 트렌드
                    'google_apis'          # 분석 저장
                ],
                'data_flow': [
                    '1. 네이버 API → 실시간 검색 트렌드',
                    '2. News API → 글로벌 뉴스 트렌드',
                    '3. Google APIs → 트렌드 분석 대시보드'
                ]
            }
        }
        
        return usage_guide

    def export_comprehensive_api_documentation(self) -> str:
        """종합 API 문서 생성"""
        logger.info("📄 종합 API 문서 생성")
        
        try:
            # 모든 정보 수집
            restoration_results = self.restore_all_api_keys()
            investigation_results = self.investigate_missing_apis()
            oauth2_config = self.setup_oauth2_config()
            usage_guide = self.create_api_usage_guide()
            
            # 종합 문서 구성
            comprehensive_doc = {
                'metadata': {
                    'title': 'NewsBot-KR 종합 API 관리 문서',
                    'created_at': datetime.now().isoformat(),
                    'version': '1.0',
                    'account_email': 'justbuild.pd@gmail.com'
                },
                
                'api_inventory': {
                    'discovered_apis': self.discovered_apis,
                    'restoration_results': restoration_results,
                    'missing_apis': self.apis_to_investigate,
                    'investigation_results': investigation_results
                },
                
                'oauth2_configuration': oauth2_config,
                'usage_guide_by_purpose': usage_guide,
                
                'security_info': {
                    'encryption_method': 'Fernet (AES 128)',
                    'key_storage': 'macOS Keychain',
                    'file_permissions': '600 (owner read only)',
                    'credential_location': 'secure_credentials.json'
                },
                
                'next_steps': [
                    {
                        'priority': 'IMMEDIATE',
                        'task': 'Google Cloud Console OAuth2 설정',
                        'description': 'credentials.json 파일 생성 및 OAuth2 인증 완료',
                        'estimated_time': '30분'
                    },
                    {
                        'priority': 'HIGH',
                        'task': '국회 의안정보시스템 API 키 발급',
                        'description': '의원/법안 정보 API 키 신청 및 등록',
                        'estimated_time': '1시간'
                    },
                    {
                        'priority': 'HIGH',
                        'task': '중앙선거관리위원회 API 키 발급',
                        'description': '선거 결과 API 키 신청 및 등록',
                        'estimated_time': '1시간'
                    },
                    {
                        'priority': 'MEDIUM',
                        'task': 'SGIS API 인증키 발급',
                        'description': '통계청 SGIS 주택/가구 통계 API 키 신청',
                        'estimated_time': '45분'
                    }
                ]
            }
            
            # JSON 파일로 저장
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            json_filename = f"comprehensive_api_documentation_{timestamp}.json"
            
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(comprehensive_doc, f, ensure_ascii=False, indent=2)
            
            # HTML 문서도 생성
            html_filename = self.generate_api_documentation_html(comprehensive_doc, timestamp)
            
            logger.info(f"✅ 종합 API 문서 생성: {json_filename}, {html_filename}")
            return json_filename
            
        except Exception as e:
            logger.error(f"❌ API 문서 생성 실패: {e}")
            return ""

    def generate_api_documentation_html(self, doc_data: Dict, timestamp: str) -> str:
        """API 문서 HTML 버전 생성"""
        html_content = f"""
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>NewsBot-KR 종합 API 관리 문서</title>
            <script src="https://cdn.tailwindcss.com"></script>
            <style>
                .api-card {{ transition: all 0.3s ease; }}
                .api-card:hover {{ transform: translateY(-4px); box-shadow: 0 8px 25px rgba(0,0,0,0.15); }}
                .status-active {{ background: #10B981; }}
                .status-setup-required {{ background: #F59E0B; }}
                .status-investigation-needed {{ background: #EF4444; }}
                .priority-immediate {{ border-left: 4px solid #EF4444; }}
                .priority-high {{ border-left: 4px solid #F59E0B; }}
                .priority-medium {{ border-left: 4px solid #10B981; }}
            </style>
        </head>
        <body class="bg-gray-50">
            <div class="container mx-auto px-4 py-8">
                <header class="text-center mb-12">
                    <h1 class="text-5xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-green-600 bg-clip-text text-transparent mb-4">
                        🔑 NewsBot-KR 종합 API 관리
                    </h1>
                    <p class="text-xl text-gray-700 mb-4">모든 API 키 통합 관리 및 OAuth2 설정 가이드</p>
                    <div class="flex justify-center space-x-6 text-sm">
                        <span class="bg-blue-100 px-4 py-2 rounded-full">📧 {doc_data['metadata']['account_email']}</span>
                        <span class="bg-green-100 px-4 py-2 rounded-full">📅 {doc_data['metadata']['created_at'][:10]}</span>
                        <span class="bg-purple-100 px-4 py-2 rounded-full">🔐 암호화 보안</span>
                    </div>
                </header>
                
                <!-- API 현황 대시보드 -->
                <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
                    <div class="bg-white rounded-xl shadow-md p-6 text-center">
                        <div class="text-3xl font-bold text-blue-600 mb-2">{len(doc_data['api_inventory']['discovered_apis'])}</div>
                        <div class="text-gray-600">복원된 API</div>
                    </div>
                    <div class="bg-white rounded-xl shadow-md p-6 text-center">
                        <div class="text-3xl font-bold text-orange-600 mb-2">{len(doc_data['api_inventory']['missing_apis'])}</div>
                        <div class="text-gray-600">추가 필요 API</div>
                    </div>
                    <div class="bg-white rounded-xl shadow-md p-6 text-center">
                        <div class="text-3xl font-bold text-green-600 mb-2">{len(doc_data['usage_guide_by_purpose'])}</div>
                        <div class="text-gray-600">용도별 가이드</div>
                    </div>
                    <div class="bg-white rounded-xl shadow-md p-6 text-center">
                        <div class="text-3xl font-bold text-purple-600 mb-2">1</div>
                        <div class="text-gray-600">OAuth2 설정</div>
                    </div>
                </div>
        """
        
        # 복원된 API 목록
        html_content += """
                <div class="mb-12">
                    <h2 class="text-3xl font-bold text-gray-800 mb-6">✅ 복원된 API 키들</h2>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        """
        
        for api_id, api_info in doc_data['api_inventory']['discovered_apis'].items():
            status_class = f"status-{api_info['status'].replace('_', '-')}"
            html_content += f"""
                        <div class="api-card bg-white rounded-xl shadow-md p-6">
                            <div class="flex items-center justify-between mb-4">
                                <h3 class="text-xl font-bold text-gray-800">{api_info['name']}</h3>
                                <span class="{status_class} text-white px-3 py-1 rounded-full text-sm">{api_info['status']}</span>
                            </div>
                            <p class="text-gray-600 mb-4">{api_info['description']}</p>
                            <div class="space-y-2">
                                <div class="text-sm font-semibold text-gray-700">주요 용도:</div>
                                <div class="flex flex-wrap gap-2">
            """
            for usage in api_info['usage']:
                html_content += f'<span class="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs">{usage}</span>'
            
            html_content += """
                                </div>
                            </div>
                        </div>
            """
        
        html_content += "</div></div>"
        
        # OAuth2 설정 가이드
        html_content += """
                <div class="mb-12">
                    <h2 class="text-3xl font-bold text-gray-800 mb-6">🔐 OAuth2 설정 가이드</h2>
                    <div class="bg-white rounded-xl shadow-md p-8">
        """
        
        for step_info in doc_data['oauth2_configuration']['google_oauth2']['setup_steps']:
            html_content += f"""
                        <div class="mb-6 p-6 border border-gray-200 rounded-lg">
                            <div class="flex items-center mb-4">
                                <div class="bg-blue-600 text-white rounded-full w-8 h-8 flex items-center justify-center font-bold mr-4">
                                    {step_info['step']}
                                </div>
                                <h3 class="text-xl font-bold text-gray-800">{step_info['title']}</h3>
                            </div>
                            <p class="text-gray-600 mb-4">{step_info['description']}</p>
            """
            
            if 'url' in step_info:
                html_content += f'<a href="{step_info["url"]}" class="text-blue-600 hover:underline" target="_blank">🔗 {step_info["url"]}</a>'
            
            html_content += "</div>"
        
        html_content += "</div></div>"
        
        # 다음 단계
        html_content += """
                <div class="mb-12">
                    <h2 class="text-3xl font-bold text-gray-800 mb-6">🎯 다음 단계</h2>
                    <div class="space-y-4">
        """
        
        for step in doc_data['next_steps']:
            priority_class = f"priority-{step['priority'].lower()}"
            html_content += f"""
                        <div class="bg-white rounded-xl shadow-md p-6 {priority_class}">
                            <div class="flex items-center justify-between mb-4">
                                <h3 class="text-xl font-bold text-gray-800">{step['task']}</h3>
                                <span class="bg-gray-100 px-3 py-1 rounded-full text-sm">{step['priority']}</span>
                            </div>
                            <p class="text-gray-600 mb-2">{step['description']}</p>
                            <div class="text-sm text-gray-500">예상 소요시간: {step['estimated_time']}</div>
                        </div>
            """
        
        html_content += """
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        html_filename = f"comprehensive_api_documentation_{timestamp}.html"
        with open(html_filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return html_filename

def main():
    """메인 실행 함수"""
    api_manager = ComprehensiveAPIManager()
    
    print("🔑 종합 API 키 관리 시스템")
    print("=" * 60)
    print("🎯 목적: 모든 API 키 복원, OAuth2 설정, 용도별 관리")
    print("📧 계정: justbuild.pd@gmail.com")
    print("🔐 보안: Fernet 암호화 + macOS 키체인")
    print("📚 문서: 용도별 사용 가이드 포함")
    print("=" * 60)
    
    try:
        # 종합 API 문서 생성
        print("\n🚀 종합 API 관리 시스템 실행...")
        doc_file = api_manager.export_comprehensive_api_documentation()
        
        if doc_file:
            print(f"\n🎉 종합 API 문서 생성 완료!")
            print(f"📄 JSON 문서: {doc_file}")
            print(f"🌐 HTML 문서: {doc_file.replace('.json', '.html')}")
            
            # 복원 결과 요약
            with open(doc_file, 'r', encoding='utf-8') as f:
                doc_data = json.load(f)
            
            restoration = doc_data['api_inventory']['restoration_results']
            print(f"\n📊 API 키 복원 결과:")
            print(f"  ✅ 성공: {restoration['restored_count']}/{restoration['total_apis']}")
            print(f"  ❌ 실패: {restoration['failed_count']}")
            
            print(f"\n🔑 복원된 API들:")
            for api in restoration['restored_apis']:
                print(f"  ✅ {api['name']}: {api['description']}")
            
            print(f"\n🔍 추가 필요 API들:")
            investigation = doc_data['api_inventory']['investigation_results']
            for action in investigation['recommended_actions']:
                priority_emoji = {'VERY_HIGH': '🚨', 'HIGH': '⚠️', 'MEDIUM': '📌'}.get(action['priority'], '📌')
                print(f"  {priority_emoji} {action['action']}")
                print(f"     🔗 {action['url']}")
            
            print(f"\n🎯 다음 단계:")
            for i, step in enumerate(doc_data['next_steps'], 1):
                priority_emoji = {'IMMEDIATE': '🚨', 'HIGH': '⚠️', 'MEDIUM': '📌'}.get(step['priority'], '📌')
                print(f"  {i}. {priority_emoji} {step['task']} ({step['estimated_time']})")
            
        else:
            print("\n❌ API 문서 생성 실패")
            
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()
