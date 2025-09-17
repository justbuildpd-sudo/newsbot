#!/usr/bin/env python3
"""
프로젝트 백업 및 복원 스크립트
모든 작업 내용을 안전하게 백업하고 필요시 복원
"""

import os
import shutil
import json
import zipfile
from datetime import datetime
from typing import List, Dict
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProjectBackupManager:
    """프로젝트 백업 및 복원 관리자"""
    
    def __init__(self, project_root: str = "/Users/hopidaay/newsbot-kr"):
        self.project_root = project_root
        self.backup_dir = os.path.join(project_root, "backups")
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 백업할 디렉토리들
        self.backup_targets = [
            "backend",
            "frontend", 
            "data",
            "static"
        ]
        
        # 백업할 파일들
        self.backup_files = [
            "index.html",
            "politician.html",
            "styles.css",
            "script.js"
        ]
        
        # 생성된 위젯 디렉토리들
        self.widget_directories = [
            "id_card_widgets",
            "mac_family_tree_widgets", 
            "sophisticated_panels",
            "stable_network_widgets"
        ]
    
    def create_backup(self) -> str:
        """프로젝트 전체 백업 생성"""
        try:
            # 백업 디렉토리 생성
            backup_name = f"newsbot_backup_{self.timestamp}"
            backup_path = os.path.join(self.backup_dir, backup_name)
            os.makedirs(backup_path, exist_ok=True)
            
            logger.info(f"백업 생성 시작: {backup_path}")
            
            # 1. 백엔드 디렉토리 백업
            backend_src = os.path.join(self.project_root, "backend")
            backend_dst = os.path.join(backup_path, "backend")
            if os.path.exists(backend_src):
                shutil.copytree(backend_src, backend_dst)
                logger.info("백엔드 디렉토리 백업 완료")
            
            # 2. 프론트엔드 디렉토리 백업
            frontend_src = os.path.join(self.project_root, "frontend")
            frontend_dst = os.path.join(backup_path, "frontend")
            if os.path.exists(frontend_src):
                shutil.copytree(frontend_src, frontend_dst)
                logger.info("프론트엔드 디렉토리 백업 완료")
            
            # 3. 데이터 디렉토리 백업
            data_src = os.path.join(self.project_root, "data")
            data_dst = os.path.join(backup_path, "data")
            if os.path.exists(data_src):
                shutil.copytree(data_src, data_dst)
                logger.info("데이터 디렉토리 백업 완료")
            
            # 4. 정적 파일들 백업
            static_dst = os.path.join(backup_path, "static_files")
            os.makedirs(static_dst, exist_ok=True)
            
            for file_name in self.backup_files:
                file_src = os.path.join(self.project_root, file_name)
                if os.path.exists(file_src):
                    shutil.copy2(file_src, static_dst)
                    logger.info(f"정적 파일 백업 완료: {file_name}")
            
            # 5. 생성된 위젯들 백업
            widgets_dst = os.path.join(backup_path, "generated_widgets")
            os.makedirs(widgets_dst, exist_ok=True)
            
            for widget_dir in self.widget_directories:
                widget_src = os.path.join(self.project_root, "backend", widget_dir)
                if os.path.exists(widget_src):
                    widget_dst = os.path.join(widgets_dst, widget_dir)
                    shutil.copytree(widget_src, widget_dst)
                    logger.info(f"위젯 디렉토리 백업 완료: {widget_dir}")
            
            # 6. 프로젝트 메타데이터 저장
            metadata = {
                "backup_timestamp": self.timestamp,
                "project_root": self.project_root,
                "backup_targets": self.backup_targets,
                "backup_files": self.backup_files,
                "widget_directories": self.widget_directories,
                "backup_size": self._calculate_backup_size(backup_path)
            }
            
            metadata_file = os.path.join(backup_path, "backup_metadata.json")
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            # 7. 압축 파일 생성
            zip_path = f"{backup_path}.zip"
            self._create_zip_archive(backup_path, zip_path)
            
            logger.info(f"백업 완료: {zip_path}")
            return zip_path
            
        except Exception as e:
            logger.error(f"백업 생성 실패: {e}")
            return None
    
    def _calculate_backup_size(self, backup_path: str) -> str:
        """백업 크기 계산"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(backup_path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                total_size += os.path.getsize(filepath)
        
        # MB 단위로 변환
        size_mb = total_size / (1024 * 1024)
        return f"{size_mb:.2f} MB"
    
    def _create_zip_archive(self, source_dir: str, zip_path: str):
        """ZIP 압축 파일 생성"""
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, source_dir)
                    zipf.write(file_path, arcname)
    
    def list_backups(self) -> List[Dict]:
        """백업 목록 조회"""
        backups = []
        
        if not os.path.exists(self.backup_dir):
            return backups
        
        for item in os.listdir(self.backup_dir):
            if item.startswith("newsbot_backup_"):
                backup_path = os.path.join(self.backup_dir, item)
                if os.path.isdir(backup_path):
                    # 메타데이터 파일 읽기
                    metadata_file = os.path.join(backup_path, "backup_metadata.json")
                    if os.path.exists(metadata_file):
                        with open(metadata_file, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                        backups.append(metadata)
                    else:
                        # 메타데이터가 없는 경우 기본 정보
                        backups.append({
                            "backup_timestamp": item.replace("newsbot_backup_", ""),
                            "backup_size": "알 수 없음"
                        })
        
        # 시간순으로 정렬 (최신순)
        backups.sort(key=lambda x: x.get("backup_timestamp", ""), reverse=True)
        return backups
    
    def restore_backup(self, backup_timestamp: str) -> bool:
        """백업 복원"""
        try:
            backup_path = os.path.join(self.backup_dir, f"newsbot_backup_{backup_timestamp}")
            
            if not os.path.exists(backup_path):
                logger.error(f"백업을 찾을 수 없습니다: {backup_path}")
                return False
            
            logger.info(f"백업 복원 시작: {backup_timestamp}")
            
            # 1. 백엔드 복원
            backend_src = os.path.join(backup_path, "backend")
            backend_dst = os.path.join(self.project_root, "backend")
            if os.path.exists(backend_src):
                if os.path.exists(backend_dst):
                    shutil.rmtree(backend_dst)
                shutil.copytree(backend_src, backend_dst)
                logger.info("백엔드 복원 완료")
            
            # 2. 프론트엔드 복원
            frontend_src = os.path.join(backup_path, "frontend")
            frontend_dst = os.path.join(self.project_root, "frontend")
            if os.path.exists(frontend_src):
                if os.path.exists(frontend_dst):
                    shutil.rmtree(frontend_dst)
                shutil.copytree(frontend_src, frontend_dst)
                logger.info("프론트엔드 복원 완료")
            
            # 3. 데이터 복원
            data_src = os.path.join(backup_path, "data")
            data_dst = os.path.join(self.project_root, "data")
            if os.path.exists(data_src):
                if os.path.exists(data_dst):
                    shutil.rmtree(data_dst)
                shutil.copytree(data_src, data_dst)
                logger.info("데이터 복원 완료")
            
            # 4. 정적 파일 복원
            static_src = os.path.join(backup_path, "static_files")
            if os.path.exists(static_src):
                for file_name in os.listdir(static_src):
                    file_src = os.path.join(static_src, file_name)
                    file_dst = os.path.join(self.project_root, file_name)
                    shutil.copy2(file_src, file_dst)
                    logger.info(f"정적 파일 복원 완료: {file_name}")
            
            # 5. 생성된 위젯들 복원
            widgets_src = os.path.join(backup_path, "generated_widgets")
            if os.path.exists(widgets_src):
                for widget_dir in os.listdir(widgets_src):
                    widget_src = os.path.join(widgets_src, widget_dir)
                    widget_dst = os.path.join(self.project_root, "backend", widget_dir)
                    if os.path.exists(widget_dst):
                        shutil.rmtree(widget_dst)
                    shutil.copytree(widget_src, widget_dst)
                    logger.info(f"위젯 디렉토리 복원 완료: {widget_dir}")
            
            logger.info("백업 복원 완료")
            return True
            
        except Exception as e:
            logger.error(f"백업 복원 실패: {e}")
            return False
    
    def cleanup_old_backups(self, keep_count: int = 5):
        """오래된 백업 정리 (최신 5개만 유지)"""
        try:
            backups = self.list_backups()
            
            if len(backups) <= keep_count:
                logger.info("정리할 백업이 없습니다")
                return
            
            # 오래된 백업들 삭제
            for backup in backups[keep_count:]:
                backup_timestamp = backup["backup_timestamp"]
                backup_path = os.path.join(self.backup_dir, f"newsbot_backup_{backup_timestamp}")
                
                if os.path.exists(backup_path):
                    shutil.rmtree(backup_path)
                    logger.info(f"오래된 백업 삭제: {backup_timestamp}")
                
                # ZIP 파일도 삭제
                zip_path = f"{backup_path}.zip"
                if os.path.exists(zip_path):
                    os.remove(zip_path)
                    logger.info(f"오래된 ZIP 파일 삭제: {zip_path}")
            
            logger.info(f"백업 정리 완료: {len(backups) - keep_count}개 삭제")
            
        except Exception as e:
            logger.error(f"백업 정리 실패: {e}")

def main():
    """메인 함수"""
    try:
        # 백업 관리자 초기화
        backup_manager = ProjectBackupManager()
        
        # 백업 디렉토리 생성
        os.makedirs(backup_manager.backup_dir, exist_ok=True)
        
        # 백업 생성
        print("🔄 프로젝트 백업 생성 중...")
        backup_path = backup_manager.create_backup()
        
        if backup_path:
            print(f"✅ 백업 완료: {backup_path}")
            
            # 백업 목록 출력
            print("\n📋 백업 목록:")
            backups = backup_manager.list_backups()
            for i, backup in enumerate(backups[:5]):  # 최신 5개만 표시
                print(f"  {i+1}. {backup['backup_timestamp']} ({backup.get('backup_size', '알 수 없음')})")
            
            # 오래된 백업 정리
            print("\n🧹 오래된 백업 정리 중...")
            backup_manager.cleanup_old_backups()
            
        else:
            print("❌ 백업 생성 실패")
        
    except Exception as e:
        logger.error(f"백업 작업 실패: {e}")

if __name__ == "__main__":
    main()
