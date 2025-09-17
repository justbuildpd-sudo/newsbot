"""
디버깅용 회의록 처리기
"""
import re
import os

def extract_meeting_info_from_filename(file_path: str):
    filename = os.path.basename(file_path)
    print(f"Processing filename: {repr(filename)}")
    
    pattern = r'제(\d+)대 국회 제(\d+)회 제(\d+)차 (.+?)(\d{4}-\d{2}-\d{2})\.xlsx'
    match = re.search(pattern, filename)
    print(f"Pattern match: {match}")
    
    if match:
        dae_num, session_num, meeting_num, committee_name, meeting_date = match.groups()
        print(f"Groups: {match.groups()}")
        return {
            'dae_num': int(dae_num),
            'session_num': int(session_num),
            'meeting_num': int(meeting_num),
            'committee_name': committee_name,
            'meeting_date': meeting_date,
            'file_name': filename
        }
    
    print("No match found, using default values")
    return {
        'dae_num': 22,
        'session_num': 1,
        'meeting_num': 1,
        'committee_name': '기타위원회',
        'meeting_date': '2025-09-15',
        'file_name': filename
    }

# 테스트
data_directory = "/Users/hopidaay/InsightForge/qa_service/data/processed_meetings"
files = [f for f in os.listdir(data_directory) if f.endswith('.xlsx')]
if files:
    first_file = os.path.join(data_directory, files[0])
    result = extract_meeting_info_from_filename(first_file)
    print(f"Result: {result}")
