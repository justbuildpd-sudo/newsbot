#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
의원 발화 마크다운 생성기
옵시디언 호환 마크다운 파일 생성
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import re

class SpeakerMarkdownGenerator:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.speaker_records_dir = os.path.join(data_dir, "speaker_records")
        self.templates_dir = os.path.join(data_dir, "markdown_templates")
        
        # 디렉토리 생성
        os.makedirs(self.speaker_records_dir, exist_ok=True)
        os.makedirs(self.templates_dir, exist_ok=True)
        
        # 템플릿 로드
        self.template = self._load_template()
        
    def _load_template(self) -> str:
        """마크다운 템플릿 로드"""
        template_path = os.path.join(self.templates_dir, "politician_template.md")
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            return self._get_default_template()
    
    def _get_default_template(self) -> str:
        """기본 템플릿 반환"""
        return """# {{politician_name}} {{politician_title}}

**정당**: {{party}}  
**지역구**: {{district}}  
**위원회**: {{committee}}  
**대수**: {{era}}  

---

## 📊 발화 통계

- **총 발화 수**: {{total_speeches}}회
- **활발한 위원회**: {{active_committees}}
- **최근 발화**: {{recent_speech_date}}

---

## 🗣️ 발화 기록

{{speech_records}}

---

## 📅 발화 타임라인

{{timeline_content}}

---

*생성일: {{created_date}}*  
*마지막 업데이트: {{updated_date}}*"""
    
    def generate_speaker_markdown(self, politician: Dict, speeches: List[Dict] = None) -> str:
        """의원별 마크다운 파일 생성"""
        if speeches is None:
            speeches = []
        
        # 템플릿 변수 준비
        template_vars = {
            'politician_name': politician.get('name', ''),
            'politician_title': politician.get('title', '의원'),
            'party': politician.get('party', ''),
            'district': politician.get('district', ''),
            'committee': politician.get('committee', ''),
            'era': politician.get('era', '22대'),
            'birth_date': politician.get('birth_date', ''),
            'education': politician.get('education', ''),
            'career': politician.get('career', ''),
            'total_speeches': len(speeches),
            'active_committees': self._get_active_committees(speeches),
            'recent_speech_date': self._get_recent_speech_date(speeches),
            'speech_records': self._format_speech_records(speeches),
            'timeline_content': self._format_timeline(speeches),
            'created_date': datetime.now().strftime('%Y-%m-%d'),
            'updated_date': datetime.now().strftime('%Y-%m-%d')
        }
        
        # 템플릿 변수 치환
        markdown_content = self.template
        for key, value in template_vars.items():
            markdown_content = markdown_content.replace(f'{{{{{key}}}}}', str(value))
        
        return markdown_content
    
    def _get_active_committees(self, speeches: List[Dict]) -> str:
        """활발한 위원회 목록 반환"""
        if not speeches:
            return "없음"
        
        committee_counts = {}
        for speech in speeches:
            committee = speech.get('committee', '')
            if committee:
                committee_counts[committee] = committee_counts.get(committee, 0) + 1
        
        # 상위 3개 위원회 반환
        sorted_committees = sorted(committee_counts.items(), key=lambda x: x[1], reverse=True)
        return ", ".join([f"{name}({count}회)" for name, count in sorted_committees[:3]])
    
    def _get_recent_speech_date(self, speeches: List[Dict]) -> str:
        """최근 발화 날짜 반환"""
        if not speeches:
            return "없음"
        
        dates = [speech.get('date', '') for speech in speeches if speech.get('date')]
        if dates:
            return max(dates)
        return "없음"
    
    def _format_speech_records(self, speeches: List[Dict]) -> str:
        """발화 기록 포맷팅"""
        if not speeches:
            return "발화 기록이 없습니다."
        
        formatted_records = []
        for speech in speeches:
            meeting_title = speech.get('meeting_title', '')
            meeting_date = speech.get('date', '')
            committee = speech.get('committee', '')
            content = speech.get('content', '')
            meeting_type = speech.get('meeting_type', '')
            
            record = f"""### {meeting_title} ({meeting_date})
- **회의 유형**: {meeting_type}
- **위원회**: {committee}
- **발화 내용**: {content[:200]}{'...' if len(content) > 200 else ''}

"""
            formatted_records.append(record)
        
        return "".join(formatted_records)
    
    def _format_timeline(self, speeches: List[Dict]) -> str:
        """타임라인 포맷팅"""
        if not speeches:
            return "발화 기록이 없습니다."
        
        # 날짜별로 정렬
        sorted_speeches = sorted(speeches, key=lambda x: x.get('date', ''), reverse=True)
        
        timeline_items = []
        for speech in sorted_speeches:
            meeting_title = speech.get('meeting_title', '')
            meeting_date = speech.get('date', '')
            committee = speech.get('committee', '')
            
            timeline_item = f"- **{meeting_date}**: {meeting_title} ({committee})"
            timeline_items.append(timeline_item)
        
        return "\\n".join(timeline_items)
    
    def save_speaker_markdown(self, politician: Dict, speeches: List[Dict] = None) -> str:
        """의원 마크다운 파일 저장"""
        markdown_content = self.generate_speaker_markdown(politician, speeches)
        
        # 파일명 생성 (특수문자 제거)
        safe_name = re.sub(r'[^\w\s-]', '', politician.get('name', 'unknown'))
        safe_name = re.sub(r'[-\s]+', '-', safe_name)
        filename = f"{safe_name}.md"
        
        file_path = os.path.join(self.speaker_records_dir, filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        return file_path
    
    def generate_all_speakers(self, politicians: List[Dict], speeches_data: Dict = None) -> List[str]:
        """모든 의원의 마크다운 파일 생성"""
        generated_files = []
        
        for politician in politicians:
            politician_id = politician.get('id', '')
            politician_speeches = speeches_data.get(politician_id, []) if speeches_data else []
            
            file_path = self.save_speaker_markdown(politician, politician_speeches)
            generated_files.append(file_path)
            
            print(f"✅ {politician.get('name', '')} 마크다운 생성: {file_path}")
        
        return generated_files

def main():
    """메인 실행 함수"""
    generator = SpeakerMarkdownGenerator()
    
    # 의원 데이터 로드
    with open('backend/processed_assembly_members.json', 'r', encoding='utf-8') as f:
        politicians = json.load(f)
    
    print(f"📊 {len(politicians)}명의 의원 데이터 로드 완료")
    
    # 마크다운 파일 생성
    generated_files = generator.generate_all_speakers(politicians)
    
    print(f"\\n🎉 총 {len(generated_files)}개의 마크다운 파일 생성 완료!")
    print(f"📁 저장 위치: {generator.speaker_records_dir}")

if __name__ == "__main__":
    main()
