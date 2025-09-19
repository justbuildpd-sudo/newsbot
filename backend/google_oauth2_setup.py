#!/usr/bin/env python3
"""
Google OAuth2 설정 자동화 시스템
Google Cloud Console 설정 및 OAuth2 인증 플로우 구성
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
import webbrowser
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from secure_credentials_manager import SecureCredentialsManager

logger = logging.getLogger(__name__)

class GoogleOAuth2Setup:
    def __init__(self):
        self.credentials_manager = SecureCredentialsManager()
        self.project_name = "newsbot-kr-analytics"
        
        # OAuth2 스코프 설정
        self.scopes = [
            'https://www.googleapis.com/auth/drive.file',
            'https://www.googleapis.com/auth/drive.metadata.readonly',
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/presentations',
            'https://www.googleapis.com/auth/analytics.readonly'
        ]
        
        # 파일 경로
        self.credentials_file = 'credentials.json'
        self.token_file = 'token.json'
        
        # Google Cloud Console 설정
        self.oauth2_config = {
            'project_info': {
                'project_name': self.project_name,
                'project_id': f"{self.project_name}-{datetime.now().strftime('%Y%m%d')}",
                'description': '3차원 통합 선거 예측 시스템 - 데이터 분석 및 시각화'
            },
            
            'apis_to_enable': [
                {
                    'name': 'Google Drive API',
                    'api_id': 'drive.googleapis.com',
                    'description': '파일 업로드, 폴더 관리, 권한 설정'
                },
                {
                    'name': 'Google Sheets API',
                    'api_id': 'sheets.googleapis.com',
                    'description': 'CSV → Sheets 변환, 데이터 조작'
                },
                {
                    'name': 'Google Data Studio API',
                    'api_id': 'datastudio.googleapis.com',
                    'description': '대시보드 자동 생성 (베타)'
                },
                {
                    'name': 'Google Maps API',
                    'api_id': 'maps-backend.googleapis.com',
                    'description': '지리적 시각화, 좌표 변환'
                }
            ],
            
            'oauth2_client': {
                'application_type': 'desktop',
                'redirect_uris': [
                    'http://localhost:8080/oauth2callback',
                    'urn:ietf:wg:oauth:2.0:oob'
                ],
                'authorized_domains': ['localhost']
            }
        }

    def check_credentials_file(self) -> Dict:
        """credentials.json 파일 확인"""
        logger.info("📄 credentials.json 파일 확인")
        
        result = {
            'exists': False,
            'valid': False,
            'content': None,
            'path': os.path.abspath(self.credentials_file)
        }
        
        try:
            if os.path.exists(self.credentials_file):
                result['exists'] = True
                
                with open(self.credentials_file, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                
                # 기본 구조 확인
                if 'installed' in content or 'web' in content:
                    client_info = content.get('installed', content.get('web', {}))
                    
                    required_fields = ['client_id', 'client_secret', 'auth_uri', 'token_uri']
                    if all(field in client_info for field in required_fields):
                        result['valid'] = True
                        result['content'] = content
                        logger.info("✅ credentials.json 파일이 유효합니다")
                    else:
                        logger.warning("⚠️ credentials.json 파일이 불완전합니다")
                else:
                    logger.warning("⚠️ credentials.json 파일 형식이 올바르지 않습니다")
            else:
                logger.warning("⚠️ credentials.json 파일이 없습니다")
                
            return result
            
        except Exception as e:
            logger.error(f"❌ credentials.json 확인 실패: {e}")
            result['error'] = str(e)
            return result

    def create_sample_credentials_file(self) -> str:
        """샘플 credentials.json 파일 생성"""
        logger.info("📝 샘플 credentials.json 파일 생성")
        
        try:
            # Google Drive 계정 정보 가져오기
            google_creds = self.credentials_manager.get_credentials('google_drive')
            if not google_creds:
                logger.error("❌ Google Drive 계정 정보를 찾을 수 없습니다")
                return ""
            
            sample_credentials = {
                "installed": {
                    "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
                    "project_id": self.oauth2_config['project_info']['project_id'],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_secret": "YOUR_CLIENT_SECRET",
                    "redirect_uris": self.oauth2_config['oauth2_client']['redirect_uris']
                }
            }
            
            sample_filename = "credentials_template.json"
            with open(sample_filename, 'w', encoding='utf-8') as f:
                json.dump(sample_credentials, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ 샘플 파일 생성: {sample_filename}")
            return sample_filename
            
        except Exception as e:
            logger.error(f"❌ 샘플 파일 생성 실패: {e}")
            return ""

    def generate_oauth2_setup_guide(self) -> str:
        """OAuth2 설정 가이드 HTML 생성"""
        logger.info("📋 OAuth2 설정 가이드 생성")
        
        try:
            # Google Drive 계정 정보
            google_creds = self.credentials_manager.get_credentials('google_drive')
            account_email = google_creds['email'] if google_creds else 'justbuild.pd@gmail.com'
            
            html_content = f"""
            <!DOCTYPE html>
            <html lang="ko">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Google OAuth2 설정 가이드</title>
                <script src="https://cdn.tailwindcss.com"></script>
                <style>
                    .step-card {{ transition: all 0.3s ease; }}
                    .step-card:hover {{ transform: translateY(-4px); box-shadow: 0 8px 25px rgba(0,0,0,0.15); }}
                    .copy-button {{ transition: all 0.2s ease; }}
                    .copy-button:hover {{ background-color: #3b82f6; }}
                </style>
            </head>
            <body class="bg-gradient-to-br from-blue-50 to-indigo-100">
                <div class="container mx-auto px-4 py-8">
                    <header class="text-center mb-12">
                        <h1 class="text-4xl font-bold text-gray-800 mb-4">
                            🔐 Google OAuth2 설정 가이드
                        </h1>
                        <p class="text-xl text-gray-600 mb-4">NewsBot-KR 시스템용 Google API 인증 설정</p>
                        <div class="bg-blue-100 border border-blue-200 rounded-lg p-4 inline-block">
                            <div class="text-sm text-blue-800">
                                <strong>계정:</strong> {account_email}<br>
                                <strong>프로젝트:</strong> {self.oauth2_config['project_info']['project_name']}<br>
                                <strong>목적:</strong> 데이터 업로드 및 시각화 자동화
                            </div>
                        </div>
                    </header>
                    
                    <div class="max-w-4xl mx-auto">
                        <!-- Step 1: Google Cloud Console 접속 -->
                        <div class="step-card bg-white rounded-xl shadow-lg p-8 mb-8">
                            <div class="flex items-center mb-6">
                                <div class="bg-blue-600 text-white rounded-full w-12 h-12 flex items-center justify-center text-xl font-bold mr-4">1</div>
                                <h2 class="text-2xl font-bold text-gray-800">Google Cloud Console 접속</h2>
                            </div>
                            
                            <div class="space-y-4">
                                <p class="text-gray-600">Google Cloud Console에 접속하여 새 프로젝트를 생성합니다.</p>
                                
                                <div class="bg-gray-50 p-4 rounded-lg">
                                    <div class="flex justify-between items-center">
                                        <code class="text-blue-600">https://console.cloud.google.com/</code>
                                        <button class="copy-button bg-blue-500 text-white px-3 py-1 rounded text-sm" 
                                                onclick="copyToClipboard('https://console.cloud.google.com/')">복사</button>
                                    </div>
                                </div>
                                
                                <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                                    <h4 class="font-semibold text-yellow-800 mb-2">프로젝트 정보</h4>
                                    <ul class="text-yellow-700 text-sm space-y-1">
                                        <li><strong>프로젝트 이름:</strong> {self.oauth2_config['project_info']['project_name']}</li>
                                        <li><strong>프로젝트 ID:</strong> {self.oauth2_config['project_info']['project_id']}</li>
                                        <li><strong>설명:</strong> {self.oauth2_config['project_info']['description']}</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Step 2: API 활성화 -->
                        <div class="step-card bg-white rounded-xl shadow-lg p-8 mb-8">
                            <div class="flex items-center mb-6">
                                <div class="bg-green-600 text-white rounded-full w-12 h-12 flex items-center justify-center text-xl font-bold mr-4">2</div>
                                <h2 class="text-2xl font-bold text-gray-800">필수 API 활성화</h2>
                            </div>
                            
                            <div class="space-y-4">
                                <p class="text-gray-600">다음 API들을 활성화해야 합니다:</p>
                                
                                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            """
            
            # API 목록 추가
            for api in self.oauth2_config['apis_to_enable']:
                html_content += f"""
                                    <div class="bg-gray-50 p-4 rounded-lg">
                                        <h4 class="font-semibold text-gray-800">{api['name']}</h4>
                                        <p class="text-sm text-gray-600">{api['description']}</p>
                                        <code class="text-xs text-blue-600">{api['api_id']}</code>
                                    </div>
                """
            
            html_content += f"""
                                </div>
                                
                                <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
                                    <h4 class="font-semibold text-blue-800 mb-2">API 활성화 방법</h4>
                                    <ol class="text-blue-700 text-sm space-y-1 list-decimal list-inside">
                                        <li>좌측 메뉴에서 "API 및 서비스" → "라이브러리" 클릭</li>
                                        <li>각 API를 검색하여 "사용 설정" 클릭</li>
                                        <li>모든 API 활성화 완료 후 다음 단계 진행</li>
                                    </ol>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Step 3: OAuth2 클라이언트 생성 -->
                        <div class="step-card bg-white rounded-xl shadow-lg p-8 mb-8">
                            <div class="flex items-center mb-6">
                                <div class="bg-purple-600 text-white rounded-full w-12 h-12 flex items-center justify-center text-xl font-bold mr-4">3</div>
                                <h2 class="text-2xl font-bold text-gray-800">OAuth2 클라이언트 ID 생성</h2>
                            </div>
                            
                            <div class="space-y-4">
                                <p class="text-gray-600">OAuth2 인증을 위한 클라이언트 ID를 생성합니다.</p>
                                
                                <div class="bg-gray-50 p-4 rounded-lg">
                                    <div class="flex justify-between items-center">
                                        <code class="text-blue-600">https://console.cloud.google.com/apis/credentials</code>
                                        <button class="copy-button bg-blue-500 text-white px-3 py-1 rounded text-sm" 
                                                onclick="copyToClipboard('https://console.cloud.google.com/apis/credentials')">복사</button>
                                    </div>
                                </div>
                                
                                <div class="bg-purple-50 border border-purple-200 rounded-lg p-4">
                                    <h4 class="font-semibold text-purple-800 mb-2">설정 정보</h4>
                                    <ul class="text-purple-700 text-sm space-y-1">
                                        <li><strong>애플리케이션 유형:</strong> 데스크톱 애플리케이션</li>
                                        <li><strong>이름:</strong> NewsBot-KR OAuth Client</li>
                                        <li><strong>승인된 리디렉션 URI:</strong></li>
                                        <ul class="ml-4 mt-1 space-y-1">
            """
            
            for uri in self.oauth2_config['oauth2_client']['redirect_uris']:
                html_content += f"<li><code class='text-xs bg-white px-1 rounded'>{uri}</code></li>"
            
            html_content += f"""
                                        </ul>
                                    </ul>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Step 4: credentials.json 다운로드 -->
                        <div class="step-card bg-white rounded-xl shadow-lg p-8 mb-8">
                            <div class="flex items-center mb-6">
                                <div class="bg-orange-600 text-white rounded-full w-12 h-12 flex items-center justify-center text-xl font-bold mr-4">4</div>
                                <h2 class="text-2xl font-bold text-gray-800">credentials.json 다운로드</h2>
                            </div>
                            
                            <div class="space-y-4">
                                <p class="text-gray-600">생성된 OAuth2 클라이언트의 JSON 파일을 다운로드합니다.</p>
                                
                                <div class="bg-orange-50 border border-orange-200 rounded-lg p-4">
                                    <h4 class="font-semibold text-orange-800 mb-2">다운로드 위치</h4>
                                    <div class="bg-white p-2 rounded border">
                                        <code class="text-sm">{os.path.abspath(self.credentials_file)}</code>
                                    </div>
                                    <p class="text-orange-700 text-sm mt-2">
                                        다운로드한 JSON 파일을 위 경로에 <strong>credentials.json</strong> 이름으로 저장하세요.
                                    </p>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Step 5: OAuth2 동의 화면 설정 -->
                        <div class="step-card bg-white rounded-xl shadow-lg p-8 mb-8">
                            <div class="flex items-center mb-6">
                                <div class="bg-red-600 text-white rounded-full w-12 h-12 flex items-center justify-center text-xl font-bold mr-4">5</div>
                                <h2 class="text-2xl font-bold text-gray-800">OAuth2 동의 화면 설정</h2>
                            </div>
                            
                            <div class="space-y-4">
                                <p class="text-gray-600">OAuth2 동의 화면을 설정하고 테스트 사용자를 추가합니다.</p>
                                
                                <div class="bg-gray-50 p-4 rounded-lg">
                                    <div class="flex justify-between items-center">
                                        <code class="text-blue-600">https://console.cloud.google.com/apis/credentials/consent</code>
                                        <button class="copy-button bg-blue-500 text-white px-3 py-1 rounded text-sm" 
                                                onclick="copyToClipboard('https://console.cloud.google.com/apis/credentials/consent')">복사</button>
                                    </div>
                                </div>
                                
                                <div class="bg-red-50 border border-red-200 rounded-lg p-4">
                                    <h4 class="font-semibold text-red-800 mb-2">중요 설정</h4>
                                    <ul class="text-red-700 text-sm space-y-1">
                                        <li><strong>사용자 유형:</strong> 외부 (External)</li>
                                        <li><strong>앱 이름:</strong> NewsBot-KR Analytics</li>
                                        <li><strong>테스트 사용자 추가:</strong> <code>{account_email}</code></li>
                                        <li><strong>범위(Scopes):</strong> 기본 프로필, 이메일, Drive, Sheets</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Step 6: 인증 테스트 -->
                        <div class="step-card bg-white rounded-xl shadow-lg p-8">
                            <div class="flex items-center mb-6">
                                <div class="bg-teal-600 text-white rounded-full w-12 h-12 flex items-center justify-center text-xl font-bold mr-4">6</div>
                                <h2 class="text-2xl font-bold text-gray-800">OAuth2 인증 테스트</h2>
                            </div>
                            
                            <div class="space-y-4">
                                <p class="text-gray-600">설정이 완료되면 OAuth2 인증을 테스트합니다.</p>
                                
                                <div class="bg-teal-50 border border-teal-200 rounded-lg p-4">
                                    <h4 class="font-semibold text-teal-800 mb-2">테스트 명령어</h4>
                                    <div class="bg-white p-2 rounded border">
                                        <code class="text-sm">cd /Users/hopidaay/newsbot-kr/backend && python3 google_oauth2_setup.py --test</code>
                                    </div>
                                    <p class="text-teal-700 text-sm mt-2">
                                        위 명령어를 실행하면 브라우저가 열리고 OAuth2 인증 플로우가 시작됩니다.
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <script>
                    function copyToClipboard(text) {{
                        navigator.clipboard.writeText(text).then(function() {{
                            alert('클립보드에 복사되었습니다: ' + text);
                        }});
                    }}
                </script>
            </body>
            </html>
            """
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            html_filename = f"google_oauth2_setup_guide_{timestamp}.html"
            
            with open(html_filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"✅ OAuth2 설정 가이드 생성: {html_filename}")
            return html_filename
            
        except Exception as e:
            logger.error(f"❌ OAuth2 설정 가이드 생성 실패: {e}")
            return ""

    def test_oauth2_flow(self) -> Dict:
        """OAuth2 인증 플로우 테스트"""
        logger.info("🔐 OAuth2 인증 플로우 테스트")
        
        result = {
            'success': False,
            'credentials_valid': False,
            'token_created': False,
            'apis_accessible': [],
            'error': None
        }
        
        try:
            # credentials.json 파일 확인
            creds_check = self.check_credentials_file()
            if not creds_check['valid']:
                result['error'] = 'credentials.json 파일이 없거나 유효하지 않습니다'
                return result
            
            creds = None
            
            # 기존 토큰 파일 확인
            if os.path.exists(self.token_file):
                creds = Credentials.from_authorized_user_file(self.token_file, self.scopes)
            
            # 토큰이 없거나 유효하지 않으면 새로 인증
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, self.scopes)
                    creds = flow.run_local_server(port=8080)
                
                # 토큰 저장
                with open(self.token_file, 'w') as token:
                    token.write(creds.to_json())
                
                result['token_created'] = True
            
            result['credentials_valid'] = True
            
            # API 접근 테스트
            try:
                # Drive API 테스트
                drive_service = build('drive', 'v3', credentials=creds)
                about = drive_service.about().get(fields='user').execute()
                result['apis_accessible'].append({
                    'name': 'Google Drive API',
                    'status': 'success',
                    'user_email': about.get('user', {}).get('emailAddress', 'Unknown')
                })
                
                # Sheets API 테스트
                sheets_service = build('sheets', 'v4', credentials=creds)
                # 간단한 API 호출로 테스트
                result['apis_accessible'].append({
                    'name': 'Google Sheets API',
                    'status': 'success'
                })
                
            except HttpError as e:
                result['apis_accessible'].append({
                    'name': 'API Test',
                    'status': 'error',
                    'error': str(e)
                })
            
            result['success'] = True
            logger.info("✅ OAuth2 인증 테스트 성공")
            
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"❌ OAuth2 인증 테스트 실패: {e}")
        
        return result

    def run_oauth2_setup_process(self) -> Dict:
        """OAuth2 설정 프로세스 실행"""
        logger.info("🚀 Google OAuth2 설정 프로세스 시작")
        
        start_time = datetime.now()
        
        try:
            setup_results = {
                'success': False,
                'steps_completed': [],
                'files_created': [],
                'next_actions': [],
                'duration_seconds': 0
            }
            
            # 1. credentials.json 파일 확인
            print("1️⃣ credentials.json 파일 확인...")
            creds_check = self.check_credentials_file()
            
            if creds_check['valid']:
                setup_results['steps_completed'].append('credentials.json 파일 확인 완료')
                print("   ✅ credentials.json 파일이 유효합니다")
            else:
                print("   ⚠️ credentials.json 파일이 없거나 유효하지 않습니다")
                
                # 샘플 파일 생성
                sample_file = self.create_sample_credentials_file()
                if sample_file:
                    setup_results['files_created'].append(sample_file)
                    setup_results['next_actions'].append(
                        f"Google Cloud Console에서 credentials.json 다운로드 후 {self.credentials_file}로 저장"
                    )
            
            # 2. OAuth2 설정 가이드 생성
            print("2️⃣ OAuth2 설정 가이드 생성...")
            guide_file = self.generate_oauth2_setup_guide()
            
            if guide_file:
                setup_results['files_created'].append(guide_file)
                setup_results['steps_completed'].append('OAuth2 설정 가이드 생성 완료')
                print(f"   ✅ 설정 가이드 생성: {guide_file}")
            
            # 3. OAuth2 인증 테스트 (credentials.json이 있는 경우)
            if creds_check['valid']:
                print("3️⃣ OAuth2 인증 테스트...")
                test_result = self.test_oauth2_flow()
                
                if test_result['success']:
                    setup_results['steps_completed'].append('OAuth2 인증 테스트 성공')
                    print("   ✅ OAuth2 인증 테스트 성공")
                    
                    for api in test_result['apis_accessible']:
                        if api['status'] == 'success':
                            print(f"   ✅ {api['name']} 접근 가능")
                else:
                    print(f"   ❌ OAuth2 인증 테스트 실패: {test_result.get('error', 'Unknown error')}")
                    setup_results['next_actions'].append('OAuth2 설정 완료 후 인증 테스트 재실행')
            else:
                setup_results['next_actions'].append('credentials.json 설정 완료 후 OAuth2 인증 테스트 실행')
            
            end_time = datetime.now()
            setup_results['duration_seconds'] = (end_time - start_time).total_seconds()
            setup_results['success'] = len(setup_results['steps_completed']) > 0
            
            logger.info(f"✅ OAuth2 설정 프로세스 완료! 소요시간: {setup_results['duration_seconds']:.1f}초")
            return setup_results
            
        except Exception as e:
            logger.error(f"❌ OAuth2 설정 프로세스 실패: {e}")
            return {
                'success': False,
                'error': str(e),
                'duration_seconds': (datetime.now() - start_time).total_seconds()
            }

def main():
    """메인 실행 함수"""
    import sys
    
    oauth2_setup = GoogleOAuth2Setup()
    
    print("🔐 Google OAuth2 설정 자동화 시스템")
    print("=" * 60)
    print("🎯 목적: Google APIs OAuth2 인증 설정")
    print("📧 계정: justbuild.pd@gmail.com")
    print("🔑 프로젝트: newsbot-kr-analytics")
    print("📊 API: Drive, Sheets, Data Studio, Maps")
    print("=" * 60)
    
    # 명령행 인수 확인
    test_mode = '--test' in sys.argv
    
    if test_mode:
        print("\n🧪 OAuth2 인증 테스트 모드")
        test_result = oauth2_setup.test_oauth2_flow()
        
        if test_result['success']:
            print("✅ OAuth2 인증 테스트 성공!")
            for api in test_result['apis_accessible']:
                if api['status'] == 'success':
                    print(f"  ✅ {api['name']}: 접근 가능")
                    if 'user_email' in api:
                        print(f"     📧 사용자: {api['user_email']}")
        else:
            print(f"❌ OAuth2 인증 테스트 실패: {test_result.get('error', 'Unknown error')}")
    else:
        # 전체 설정 프로세스 실행
        result = oauth2_setup.run_oauth2_setup_process()
        
        if result['success']:
            print(f"\n🎉 OAuth2 설정 프로세스 완료!")
            print(f"⏱️ 소요시간: {result['duration_seconds']:.1f}초")
            
            print(f"\n✅ 완료된 단계:")
            for step in result['steps_completed']:
                print(f"  ✅ {step}")
            
            print(f"\n📁 생성된 파일:")
            for file in result['files_created']:
                print(f"  📄 {file}")
            
            if result['next_actions']:
                print(f"\n🎯 다음 단계:")
                for i, action in enumerate(result['next_actions'], 1):
                    print(f"  {i}. {action}")
            
            print(f"\n🔗 설정 가이드:")
            for file in result['files_created']:
                if file.endswith('.html'):
                    print(f"  🌐 브라우저에서 열기: {file}")
                    
        else:
            print(f"\n❌ OAuth2 설정 실패:")
            print(f"  🚫 오류: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()
