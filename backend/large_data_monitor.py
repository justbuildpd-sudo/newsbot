#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
대용량 데이터 처리 모니터링 시스템
5,318명 기초의회의원 데이터 처리 진행 상황을 실시간으로 모니터링합니다.
"""

import time
import json
import os
from datetime import datetime, timedelta
import subprocess

def get_system_resources():
    """시스템 자원 사용량을 확인합니다."""
    try:
        # 디스크 사용량
        disk_result = subprocess.run(['df', '-h', '.'], capture_output=True, text=True)
        disk_info = disk_result.stdout.split('\n')[1].split()
        disk_available = disk_info[3]
        disk_usage = disk_info[4]
        
        # 메모리 사용량 (macOS)
        vm_result = subprocess.run(['vm_stat'], capture_output=True, text=True)
        vm_lines = vm_result.stdout.split('\n')
        
        return {
            'disk_available': disk_available,
            'disk_usage': disk_usage,
            'vm_stat': vm_lines[:3]
        }
    except:
        return {'error': 'Unable to get system resources'}

def monitor_large_data_processing():
    """대용량 데이터 처리를 모니터링합니다."""
    
    print("🔄 대용량 데이터 처리 모니터링 시작")
    print("=" * 80)
    
    start_time = datetime.now()
    total_candidates = 5318
    
    while True:
        try:
            # 로그 파일에서 진행 상황 확인
            if os.path.exists("basic_council_processing.log"):
                with open("basic_council_processing.log", "r", encoding="utf-8") as f:
                    lines = f.readlines()
                
                # 최근 진행 상황 추출
                progress_lines = [line for line in lines[-10:] if "처리 중:" in line]
                success_lines = [line for line in lines if "✅ 성공:" in line]
                failed_lines = [line for line in lines if "❌" in line or "실패" in line]
                
                if progress_lines:
                    latest_progress = progress_lines[-1].strip()
                    
                    # 진행률 추출
                    if "/" in latest_progress:
                        parts = latest_progress.split()
                        for part in parts:
                            if "/" in part and part.replace("/", "").replace("5318", "").isdigit():
                                current, total = part.split("/")
                                current_num = int(current)
                                progress_percent = (current_num / total_candidates) * 100
                                
                                elapsed = datetime.now() - start_time
                                if current_num > 0:
                                    estimated_total = elapsed * (total_candidates / current_num)
                                    remaining = estimated_total - elapsed
                                    eta = start_time + estimated_total
                                else:
                                    remaining = "계산 중..."
                                    eta = "계산 중..."
                                
                                # 시스템 자원 확인
                                resources = get_system_resources()
                                
                                print(f"\r🚀 진행률: {progress_percent:.1f}% ({current}/{total_candidates}) | "
                                      f"성공: {len(success_lines):,}명 | "
                                      f"실패: {len(failed_lines)}명 | "
                                      f"경과: {str(elapsed).split('.')[0]} | "
                                      f"남은시간: {str(remaining).split('.')[0] if remaining != '계산 중...' else remaining} | "
                                      f"디스크: {resources.get('disk_available', 'N/A')}", end="")
                                
                                # 주요 진행 단계에서 상세 정보 출력
                                if current_num % 100 == 0:
                                    print(f"\n📊 {current_num}명 처리 완료 - {datetime.now().strftime('%H:%M:%S')}")
                                    print(f"   평균 처리 속도: {current_num / elapsed.total_seconds() * 60:.1f}명/분")
                                    if eta != "계산 중...":
                                        print(f"   예상 완료: {eta.strftime('%H:%M:%S')}")
                                break
                
                # 완료 확인
                completion_lines = [line for line in lines if "전체 수집:" in line and "성공" in line]
                if completion_lines:
                    final_time = datetime.now()
                    total_duration = final_time - start_time
                    
                    print(f"\n\n🎉 대용량 데이터 처리 완료!")
                    print(f"⏰ 총 소요시간: {total_duration}")
                    print(f"📊 처리 속도: {total_candidates / total_duration.total_seconds() * 60:.1f}명/분")
                    
                    # 결과 파일 확인
                    if os.path.exists("basic_council_election_full.json"):
                        file_size = os.path.getsize("basic_council_election_full.json") / (1024 * 1024)
                        print(f"📁 결과 파일 크기: {file_size:.1f}MB")
                        
                        with open("basic_council_election_full.json", "r", encoding="utf-8") as f:
                            result_data = json.load(f)
                            print(f"✅ 수집 성공: {result_data['statistics']['processed_candidates']:,}명")
                            print(f"❌ 수집 실패: {result_data['statistics']['failed_candidates']:,}명")
                            print(f"📊 성공률: {result_data['statistics']['success_rate']:.1f}%")
                    
                    # 시스템 자원 최종 확인
                    final_resources = get_system_resources()
                    print(f"💾 최종 디스크 여유공간: {final_resources.get('disk_available', 'N/A')}")
                    
                    break
                    
            else:
                print("📋 로그 파일 대기 중...")
            
            time.sleep(10)  # 10초마다 업데이트
            
        except KeyboardInterrupt:
            print(f"\n\n⏹️ 모니터링 중단")
            break
        except Exception as e:
            print(f"\n❌ 모니터링 오류: {e}")
            time.sleep(10)
            continue

if __name__ == "__main__":
    monitor_large_data_processing()

