#!/usr/bin/env python3
"""
보안 인증 정보 통합 관리 시스템
모든 API 키와 계정 정보를 안전하게 관리
"""

import os
import json
import base64
import logging
from datetime import datetime
from typing import Dict, Optional
from cryptography.fernet import Fernet
import keyring

logger = logging.getLogger(__name__)

class SecureCredentialsManager:
    def __init__(self):
        self.credentials_file = "secure_credentials.json"
        self.service_name = "newsbot_kr_system"
        
        # 암호화 키 생성 또는 로드
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # 지원하는 서비스들
        self.supported_services = {
            'google_drive': {
                'name': 'Google Drive',
                'required_fields': ['email', 'password'],
                'description': 'Google Drive 계정 (Data Studio 연동용)'
            },
            'kosis_api': {
                'name': 'KOSIS API',
                'required_fields': ['api_key'],
                'description': '통계청 KOSIS API 인증키'
            },
            'sgis_api': {
                'name': 'SGIS API',
                'required_fields': ['api_key'],
                'description': '통계청 SGIS API 인증키 (가구/주택통계)'
            },
            'naver_api': {
                'name': 'Naver API',
                'required_fields': ['client_id', 'client_secret'],
                'description': '네이버 API (지도, 검색 등)'
            },
            'github_api': {
                'name': 'GitHub API',
                'required_fields': ['token'],
                'description': 'GitHub Personal Access Token'
            }
        }

    def _get_or_create_encryption_key(self) -> bytes:
        """암호화 키 생성 또는 로드"""
        try:
            # 키링에서 암호화 키 로드 시도
            key_str = keyring.get_password(self.service_name, "encryption_key")
            if key_str:
                return key_str.encode()
            else:
                # 새 키 생성
                key = Fernet.generate_key()
                keyring.set_password(self.service_name, "encryption_key", key.decode())
                logger.info("✅ 새 암호화 키 생성 및 저장")
                return key
        except Exception as e:
            logger.warning(f"⚠️ 키링 사용 불가, 파일 기반 키 사용: {e}")
            # 키링 사용 불가 시 파일 기반 키 사용
            key_file = ".encryption_key"
            if os.path.exists(key_file):
                with open(key_file, 'rb') as f:
                    return f.read()
            else:
                key = Fernet.generate_key()
                with open(key_file, 'wb') as f:
                    f.write(key)
                # 파일 권한을 소유자만 읽기로 제한
                os.chmod(key_file, 0o600)
                return key

    def encrypt_data(self, data: str) -> str:
        """데이터 암호화"""
        encrypted_data = self.cipher_suite.encrypt(data.encode())
        return base64.b64encode(encrypted_data).decode()

    def decrypt_data(self, encrypted_data: str) -> str:
        """데이터 복호화"""
        encrypted_bytes = base64.b64decode(encrypted_data.encode())
        decrypted_data = self.cipher_suite.decrypt(encrypted_bytes)
        return decrypted_data.decode()

    def store_credentials(self, service: str, credentials: Dict[str, str]) -> bool:
        """인증 정보 저장"""
        logger.info(f"🔐 {service} 인증 정보 저장")
        
        try:
            if service not in self.supported_services:
                logger.error(f"❌ 지원하지 않는 서비스: {service}")
                return False
            
            # 필수 필드 확인
            required_fields = self.supported_services[service]['required_fields']
            for field in required_fields:
                if field not in credentials:
                    logger.error(f"❌ 필수 필드 누락: {field}")
                    return False
            
            # 기존 인증 정보 로드
            all_credentials = self._load_all_credentials()
            
            # 새 인증 정보 암호화 및 저장
            encrypted_credentials = {}
            for key, value in credentials.items():
                encrypted_credentials[key] = self.encrypt_data(value)
            
            all_credentials[service] = {
                'credentials': encrypted_credentials,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'service_info': self.supported_services[service]
            }
            
            # 파일에 저장
            with open(self.credentials_file, 'w', encoding='utf-8') as f:
                json.dump(all_credentials, f, ensure_ascii=False, indent=2)
            
            # 파일 권한을 소유자만 읽기로 제한
            os.chmod(self.credentials_file, 0o600)
            
            logger.info(f"✅ {service} 인증 정보 저장 완료")
            return True
            
        except Exception as e:
            logger.error(f"❌ 인증 정보 저장 실패: {e}")
            return False

    def get_credentials(self, service: str) -> Optional[Dict[str, str]]:
        """인증 정보 조회"""
        try:
            all_credentials = self._load_all_credentials()
            
            if service not in all_credentials:
                logger.warning(f"⚠️ {service} 인증 정보 없음")
                return None
            
            encrypted_credentials = all_credentials[service]['credentials']
            decrypted_credentials = {}
            
            for key, encrypted_value in encrypted_credentials.items():
                decrypted_credentials[key] = self.decrypt_data(encrypted_value)
            
            return decrypted_credentials
            
        except Exception as e:
            logger.error(f"❌ 인증 정보 조회 실패: {e}")
            return None

    def _load_all_credentials(self) -> Dict:
        """모든 인증 정보 로드"""
        if os.path.exists(self.credentials_file):
            with open(self.credentials_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def list_stored_services(self) -> Dict[str, Dict]:
        """저장된 서비스 목록 조회"""
        try:
            all_credentials = self._load_all_credentials()
            service_list = {}
            
            for service, data in all_credentials.items():
                service_list[service] = {
                    'name': data['service_info']['name'],
                    'description': data['service_info']['description'],
                    'created_at': data['created_at'],
                    'updated_at': data['updated_at'],
                    'has_credentials': True
                }
            
            return service_list
            
        except Exception as e:
            logger.error(f"❌ 서비스 목록 조회 실패: {e}")
            return {}

    def delete_credentials(self, service: str) -> bool:
        """인증 정보 삭제"""
        try:
            all_credentials = self._load_all_credentials()
            
            if service in all_credentials:
                del all_credentials[service]
                
                with open(self.credentials_file, 'w', encoding='utf-8') as f:
                    json.dump(all_credentials, f, ensure_ascii=False, indent=2)
                
                logger.info(f"✅ {service} 인증 정보 삭제 완료")
                return True
            else:
                logger.warning(f"⚠️ {service} 인증 정보 없음")
                return False
                
        except Exception as e:
            logger.error(f"❌ 인증 정보 삭제 실패: {e}")
            return False

    def update_credentials(self, service: str, credentials: Dict[str, str]) -> bool:
        """인증 정보 업데이트"""
        try:
            all_credentials = self._load_all_credentials()
            
            if service not in all_credentials:
                logger.warning(f"⚠️ {service} 인증 정보 없음, 새로 생성")
                return self.store_credentials(service, credentials)
            
            # 기존 정보 업데이트
            encrypted_credentials = {}
            for key, value in credentials.items():
                encrypted_credentials[key] = self.encrypt_data(value)
            
            all_credentials[service]['credentials'] = encrypted_credentials
            all_credentials[service]['updated_at'] = datetime.now().isoformat()
            
            with open(self.credentials_file, 'w', encoding='utf-8') as f:
                json.dump(all_credentials, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ {service} 인증 정보 업데이트 완료")
            return True
            
        except Exception as e:
            logger.error(f"❌ 인증 정보 업데이트 실패: {e}")
            return False

    def export_credentials_summary(self) -> Dict:
        """인증 정보 요약 내보내기 (민감한 정보 제외)"""
        try:
            all_credentials = self._load_all_credentials()
            summary = {
                'total_services': len(all_credentials),
                'services': {},
                'security_info': {
                    'encryption_enabled': True,
                    'key_storage': 'keyring' if keyring else 'file',
                    'last_updated': datetime.now().isoformat()
                }
            }
            
            for service, data in all_credentials.items():
                summary['services'][service] = {
                    'name': data['service_info']['name'],
                    'description': data['service_info']['description'],
                    'fields_count': len(data['credentials']),
                    'created_at': data['created_at'],
                    'updated_at': data['updated_at']
                }
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ 인증 정보 요약 내보내기 실패: {e}")
            return {}

def main():
    """메인 실행 함수"""
    manager = SecureCredentialsManager()
    
    print("🔐 보안 인증 정보 통합 관리 시스템")
    print("=" * 50)
    print("🎯 목적: 모든 API 키와 계정 정보 안전 관리")
    print("🔒 보안: 암호화 + 키링 저장")
    print("📊 지원 서비스: Google Drive, KOSIS, SGIS, Naver, GitHub")
    print("=" * 50)
    
    # Google Drive 계정 정보 저장
    print("\n1️⃣ Google Drive 계정 정보 저장...")
    google_drive_credentials = {
        'email': 'justbuild.pd@gmail.com',
        'password': 'jsjs807883'
    }
    
    success = manager.store_credentials('google_drive', google_drive_credentials)
    if success:
        print("✅ Google Drive 계정 정보 안전하게 저장 완료")
    else:
        print("❌ Google Drive 계정 정보 저장 실패")
    
    # 기존 KOSIS API 키 저장 (예시)
    print("\n2️⃣ 기존 API 키들 통합 관리...")
    kosis_credentials = {
        'api_key': 'ZDkwNzNhY2Y4YTg3NjdlNWEyNjg0YmM1NDFlMmFjNmU='
    }
    manager.store_credentials('kosis_api', kosis_credentials)
    
    # 저장된 서비스 목록 출력
    print("\n3️⃣ 저장된 인증 정보 요약...")
    summary = manager.export_credentials_summary()
    
    print(f"📊 총 관리 서비스: {summary['total_services']}개")
    for service, info in summary['services'].items():
        print(f"  🔑 {info['name']}: {info['fields_count']}개 필드")
        print(f"     📝 {info['description']}")
        print(f"     📅 생성: {info['created_at'][:10]}")
    
    print(f"\n🔒 보안 정보:")
    print(f"  🔐 암호화: {summary['security_info']['encryption_enabled']}")
    print(f"  🗝️ 키 저장: {summary['security_info']['key_storage']}")
    
    # 테스트: Google Drive 정보 조회
    print("\n4️⃣ Google Drive 정보 조회 테스트...")
    retrieved_creds = manager.get_credentials('google_drive')
    if retrieved_creds:
        print(f"✅ 이메일: {retrieved_creds['email']}")
        print(f"✅ 비밀번호: {'*' * len(retrieved_creds['password'])} (암호화됨)")
    
    print(f"\n🎉 보안 인증 정보 관리 시스템 설정 완료!")
    print(f"📁 저장 위치: {manager.credentials_file}")
    print(f"🔒 파일 권한: 소유자만 읽기 (600)")

if __name__ == "__main__":
    main()
