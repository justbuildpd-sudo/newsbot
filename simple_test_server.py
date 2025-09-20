#!/usr/bin/env python3
"""
간단한 테스트 서버 - 프론트엔드 파일을 직접 서빙
Node.js 없이도 브라우저에서 확인 가능
"""

import os
import json
import mimetypes
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import time

class CustomHTTPRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="/Users/hopidaay/newsbot-kr/frontend", **kwargs)
    
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # API 엔드포인트 처리
        if path.startswith('/api/'):
            self.handle_api_request(path, parsed_path.query)
            return
        
        # 정적 파일 처리
        if path == '/':
            path = '/index.html'
        elif path == '/regional-minsaeng-topics':
            path = '/regional-minsaeng-topics.html'
        
        # 파일 확장자가 없으면 .html 추가
        if '.' not in os.path.basename(path):
            path += '.html'
        
        # JSX 파일을 JS로 처리
        if path.endswith('.jsx'):
            path = path.replace('.jsx', '.js')
        
        try:
            # 실제 파일 경로
            file_path = os.path.join(self.directory, path.lstrip('/'))
            
            # 특별 처리: regional-minsaeng-topics.html 생성
            if path.endswith('regional-minsaeng-topics.html'):
                self.serve_regional_topics_html()
                return
            
            # 특별 처리: politician-analysis.html 생성
            if path.endswith('politician-analysis.html'):
                self.serve_politician_analysis_html()
                return
            
            # 일반 파일 서빙
            super().do_GET()
            
        except Exception as e:
            print(f"파일 서빙 오류: {e}")
            self.send_error(404, f"File not found: {path}")
    
    def handle_api_request(self, path, query):
        """API 요청 처리"""
        try:
            # 샘플 API 응답
            if path == '/api/regional-minsaeng-topics':
                query_params = parse_qs(query)
                limit = int(query_params.get('limit', [50])[0])
                
                # 샘플 데이터
                sample_data = {
                    "success": True,
                    "data": {
                        "강남구": {
                            "region_name": "강남구",
                            "parent_government": "서울특별시",
                            "level": "시군구",
                            "dominant_topics": ["주거정책", "문화정책", "교통정책"],
                            "topic_scores": {"주거정책": 85, "문화정책": 51, "교통정책": 63},
                            "interpretation": "강남구는 주거정책 분야에서 매우 강한 관심을 보이며, 이는 해당 지역의 핵심 정책 이슈로 판단됨",
                            "promises": ["주택공급", "문화시설건설", "교통개선"],
                            "confidence_score": 6
                        },
                        "수원시": {
                            "region_name": "수원시",
                            "parent_government": "경기도",
                            "level": "시군구",
                            "dominant_topics": ["교육정책", "경제정책", "주거정책"],
                            "topic_scores": {"교육정책": 68, "경제정책": 55, "주거정책": 45},
                            "interpretation": "수원시는 교육정책 분야에서 강한 관심을 보이며, 이는 해당 지역의 주요 정책 이슈임",
                            "promises": ["교육시설확충", "일자리창출", "주택공급"],
                            "confidence_score": 7
                        }
                    },
                    "metadata": {
                        "total_regions": 2,
                        "level_filter": "all",
                        "topic_filter": "all",
                        "search_term": "",
                        "limit": limit
                    }
                }
                
                self.send_json_response(sample_data)
            else:
                self.send_error(404, "API endpoint not found")
                
        except Exception as e:
            print(f"API 처리 오류: {e}")
            self.send_error(500, f"API error: {str(e)}")
    
    def serve_regional_topics_html(self):
        """민생토픽 페이지 HTML 생성 및 서빙"""
        html_content = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>시군구별 민생토픽 분석 | NewsBot 정세분석</title>
    <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .topic-경제정책 { @apply bg-blue-100 text-blue-800 border-blue-200; }
        .topic-주거정책 { @apply bg-green-100 text-green-800 border-green-200; }
        .topic-교육정책 { @apply bg-purple-100 text-purple-800 border-purple-200; }
        .topic-복지정책 { @apply bg-pink-100 text-pink-800 border-pink-200; }
        .topic-환경정책 { @apply bg-emerald-100 text-emerald-800 border-emerald-200; }
        .topic-교통정책 { @apply bg-orange-100 text-orange-800 border-orange-200; }
        .topic-문화정책 { @apply bg-indigo-100 text-indigo-800 border-indigo-200; }
        .topic-안전정책 { @apply bg-red-100 text-red-800 border-red-200; }
    </style>
</head>
<body>
    <div id="root"></div>
    
    <script type="text/babel">
        const { useState, useEffect, useMemo } = React;
        
        const RegionalMinsaengTopicsPage = () => {
            const [minsaengData, setMinsaengData] = useState(null);
            const [loading, setLoading] = useState(true);
            const [selectedLevel, setSelectedLevel] = useState('all');
            const [selectedTopic, setSelectedTopic] = useState('all');
            const [searchTerm, setSearchTerm] = useState('');
            const [selectedRegion, setSelectedRegion] = useState(null);

            // 민생토픽 카테고리 색상 매핑
            const topicColors = {
                '경제정책': 'bg-blue-100 text-blue-800 border-blue-200',
                '주거정책': 'bg-green-100 text-green-800 border-green-200',
                '교육정책': 'bg-purple-100 text-purple-800 border-purple-200',
                '복지정책': 'bg-pink-100 text-pink-800 border-pink-200',
                '환경정책': 'bg-emerald-100 text-emerald-800 border-emerald-200',
                '교통정책': 'bg-orange-100 text-orange-800 border-orange-200',
                '문화정책': 'bg-indigo-100 text-indigo-800 border-indigo-200',
                '안전정책': 'bg-red-100 text-red-800 border-red-200'
            };

            // 레벨별 아이콘 매핑
            const levelIcons = {
                '광역시도': '🏛️',
                '시군구': '🏘️',
                '읍면동': '🏠'
            };

            // 정적 데이터 로드
            useEffect(() => {
                const loadStaticData = async () => {
                    try {
                        setLoading(true);
                        
                        // 정적 데이터
                        const staticData = {
                            last_updated: new Date().toISOString(),
                            total_regions: 8,
                            minsaeng_topic_categories: {
                                "경제정책": {
                                    keywords: ["일자리", "취업", "창업", "경제성장", "소득", "임금"],
                                    description: "일자리 창출, 경제 활성화, 소득 증대"
                                },
                                "주거정책": {
                                    keywords: ["주택", "부동산", "임대", "전세", "월세", "아파트"],
                                    description: "주택 공급, 부동산 안정화, 주거 복지"
                                },
                                "교육정책": {
                                    keywords: ["교육", "학교", "대학", "입시", "사교육", "교육비"],
                                    description: "교육 환경 개선, 사교육 부담 해소"
                                },
                                "복지정책": {
                                    keywords: ["복지", "의료", "건강보험", "연금", "육아", "보육"],
                                    description: "사회복지 확충, 의료 서비스 개선"
                                },
                                "환경정책": {
                                    keywords: ["환경", "기후", "에너지", "미세먼지", "재생에너지"],
                                    description: "환경 보호, 지속가능한 발전"
                                },
                                "교통정책": {
                                    keywords: ["교통", "대중교통", "지하철", "버스", "도로"],
                                    description: "교통 인프라 개선, 대중교통 확충"
                                },
                                "문화정책": {
                                    keywords: ["문화", "예술", "체육", "관광", "축제"],
                                    description: "문화 시설 확충, 관광 산업 발전"
                                },
                                "안전정책": {
                                    keywords: ["안전", "치안", "재해", "방범", "소방"],
                                    description: "안전한 생활 환경 조성"
                                }
                            },
                            regional_data: {
                                "강남구": {
                                    region_name: "강남구",
                                    parent_government: "서울특별시",
                                    level: "시군구",
                                    dominant_topics: ["주거정책", "문화정책", "교통정책"],
                                    topic_scores: { "주거정책": 85, "문화정책": 51, "교통정책": 63 },
                                    interpretation: "강남구는 주거정책 분야에서 매우 강한 관심을 보이며, 이는 해당 지역의 핵심 정책 이슈로 판단됨",
                                    promises: ["주택공급", "문화시설건설", "교통개선"],
                                    confidence_score: 6
                                },
                                "수원시": {
                                    region_name: "수원시",
                                    parent_government: "경기도",
                                    level: "시군구",
                                    dominant_topics: ["교육정책", "경제정책", "주거정책"],
                                    topic_scores: { "교육정책": 68, "경제정책": 55, "주거정책": 45 },
                                    interpretation: "수원시는 교육정책 분야에서 강한 관심을 보이며, 이는 해당 지역의 주요 정책 이슈임",
                                    promises: ["교육시설확충", "일자리창출", "주택공급"],
                                    confidence_score: 7
                                },
                                "부산진구": {
                                    region_name: "부산진구",
                                    parent_government: "부산광역시",
                                    level: "시군구",
                                    dominant_topics: ["경제정책", "교통정책", "문화정책"],
                                    topic_scores: { "경제정책": 72, "교통정책": 48, "문화정책": 35 },
                                    interpretation: "부산진구는 경제정책 분야에서 매우 강한 관심을 보이며, 이는 해당 지역의 핵심 정책 이슈로 판단됨",
                                    promises: ["경제활성화", "교통개선", "문화시설건설"],
                                    confidence_score: 8
                                }
                            }
                        };
                        
                        setMinsaengData(staticData);
                    } catch (error) {
                        console.error('민생토픽 데이터 로드 실패:', error);
                    } finally {
                        setLoading(false);
                    }
                };

                loadStaticData();
            }, []);

            // 필터링된 지역 데이터
            const filteredRegions = useMemo(() => {
                if (!minsaengData?.regional_data) return [];

                let regions = Object.entries(minsaengData.regional_data);

                // 레벨 필터
                if (selectedLevel !== 'all') {
                    regions = regions.filter(([_, data]) => data.level === selectedLevel);
                }

                // 토픽 필터
                if (selectedTopic !== 'all') {
                    regions = regions.filter(([_, data]) => 
                        data.dominant_topics.includes(selectedTopic)
                    );
                }

                // 검색 필터
                if (searchTerm) {
                    regions = regions.filter(([name, data]) => 
                        name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                        data.parent_government.toLowerCase().includes(searchTerm.toLowerCase())
                    );
                }

                return regions;
            }, [minsaengData, selectedLevel, selectedTopic, searchTerm]);

            if (loading) {
                return (
                    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                        <div className="text-center">
                            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                            <p className="text-gray-600">민생토픽 데이터 로드 중...</p>
                        </div>
                    </div>
                );
            }

            return (
                <div className="min-h-screen bg-gray-50">
                    {/* 네비게이션 헤더 */}
                    <header className="bg-white shadow-sm border-b border-gray-200">
                        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                            <div className="flex justify-between items-center py-4">
                                <div className="flex items-center space-x-4">
                                    <h1 className="text-xl font-bold text-gray-800">
                                        📊 NewsBot 정세분석
                                    </h1>
                                    <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
                                        시군구별 민생토픽
                                    </span>
                                </div>
                                <div className="text-sm text-gray-500">
                                    {minsaengData?.total_regions}개 시군구 분석
                                </div>
                            </div>
                        </div>
                    </header>

                    {/* 메인 컨텐츠 */}
                    <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                        {/* 페이지 제목 */}
                        <div className="text-center mb-8">
                            <h1 className="text-3xl font-bold text-gray-900 mb-4">
                                시군구별 민생토픽 분석
                            </h1>
                            <p className="text-lg text-gray-600 mb-6 max-w-3xl mx-auto">
                                정책선거문화 확산을 위한 빅데이터 분석으로 각 지역의 주요 민생토픽을 파악합니다.
                            </p>
                        </div>

                        {/* 검색 및 필터 */}
                        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
                            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                                {/* 검색 */}
                                <div className="relative">
                                    <input
                                        type="text"
                                        placeholder="시군구명 검색..."
                                        value={searchTerm}
                                        onChange={(e) => setSearchTerm(e.target.value)}
                                        className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                    />
                                    <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400">🔍</span>
                                </div>

                                {/* 레벨 필터 */}
                                <select
                                    value={selectedLevel}
                                    onChange={(e) => setSelectedLevel(e.target.value)}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                >
                                    <option value="all">모든 레벨</option>
                                    <option value="시군구">시군구</option>
                                </select>

                                {/* 토픽 필터 */}
                                <select
                                    value={selectedTopic}
                                    onChange={(e) => setSelectedTopic(e.target.value)}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                >
                                    <option value="all">모든 토픽</option>
                                    {Object.keys(minsaengData?.minsaeng_topic_categories || {}).map(topic => (
                                        <option key={topic} value={topic}>{topic}</option>
                                    ))}
                                </select>

                                {/* 결과 수 */}
                                <div className="flex items-center justify-center px-3 py-2 bg-gray-50 rounded-lg">
                                    <span className="text-sm text-gray-600">
                                        {filteredRegions.length}개 시군구
                                    </span>
                                </div>
                            </div>
                        </div>

                        {/* 지역별 결과 */}
                        <div className="space-y-4">
                            {filteredRegions.map(([regionName, regionData]) => (
                                <div
                                    key={regionName}
                                    className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow cursor-pointer"
                                    onClick={() => setSelectedRegion(selectedRegion === regionName ? null : regionName)}
                                >
                                    <div className="flex items-center justify-between mb-4">
                                        <div className="flex items-center space-x-3">
                                            <span className="text-2xl">{levelIcons[regionData.level] || '🏘️'}</span>
                                            <div>
                                                <h3 className="text-xl font-bold text-gray-900">{regionData.region_name}</h3>
                                                <p className="text-sm text-gray-500">{regionData.parent_government}</p>
                                            </div>
                                        </div>
                                        <div className="flex items-center space-x-2">
                                            <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                                                신뢰도 {regionData.confidence_score}/10
                                            </span>
                                        </div>
                                    </div>

                                    <div className="mb-4">
                                        <div className="flex flex-wrap gap-2">
                                            {regionData.dominant_topics.map(topic => (
                                                <span
                                                    key={topic}
                                                    className={`px-3 py-1 rounded-full text-sm font-medium ${topicColors[topic] || 'bg-gray-100 text-gray-800'}`}
                                                >
                                                    {topic}
                                                </span>
                                            ))}
                                        </div>
                                    </div>

                                    <p className="text-gray-600 mb-4">
                                        {regionData.interpretation}
                                    </p>

                                    {selectedRegion === regionName && (
                                        <div className="mt-4 pt-4 border-t border-gray-200">
                                            <h4 className="font-semibold text-gray-900 mb-3">정책 공약</h4>
                                            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                                                {regionData.promises.map((promise, index) => (
                                                    <div key={index} className="text-sm text-gray-600 bg-gray-50 px-3 py-2 rounded">
                                                        {promise}
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>

                        {filteredRegions.length === 0 && (
                            <div className="text-center text-gray-500 py-12">
                                <p className="text-lg">검색 조건에 맞는 지역이 없습니다.</p>
                            </div>
                        )}
                    </main>

                    {/* 푸터 */}
                    <footer className="bg-white border-t border-gray-200 mt-12">
                        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                            <div className="text-center text-sm text-gray-500">
                                <p>© 2024 NewsBot 정세분석 시스템. 정책선거문화 확산을 위한 빅데이터 분석 플랫폼.</p>
                            </div>
                        </div>
                    </footer>
                </div>
            );
        };

        ReactDOM.render(<RegionalMinsaengTopicsPage />, document.getElementById('root'));
    </script>
</body>
</html>
        """
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(html_content.encode('utf-8'))))
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
    
    def serve_politician_analysis_html(self):
        """2단계 정치인 분석 페이지 HTML 생성 및 서빙"""
        html_content = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>2단계 정치인 분석 | NewsBot 정세분석</title>
    <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
    <div id="root"></div>
    
    <script type="text/babel">
        const { useState, useEffect } = React;
        
        // Heroicons 컴포넌트들 (간단한 버전)
        const UserIcon = ({ className }) => (
            <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
        );
        
        const MapPinIcon = ({ className }) => (
            <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
        );
        
        const DocumentTextIcon = ({ className }) => (
            <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
        );
        
        const ChartBarIcon = ({ className }) => (
            <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
        );
        
        const CheckCircleIcon = ({ className }) => (
            <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
        );
        
        const ArrowRightIcon = ({ className }) => (
            <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
            </svg>
        );

        const TwoStagePoliticianAnalysisPage = () => {
            const [selectedPolitician, setSelectedPolitician] = useState('이재명');
            const [analysisData, setAnalysisData] = useState(null);
            const [loading, setLoading] = useState(false);

            // 샘플 분석 데이터
            const sampleAnalysisData = {
                "이재명": {
                    politician_info: {
                        name: "이재명",
                        constituency: "성남시 분당구 갑",
                        party: "더불어민주당",
                        total_bills: 5
                    },
                    regional_analysis: {
                        region_name: "성남시",
                        population: 948757,
                        top_issues: [
                            { topic: "교육정책", score: 85, priority: "높음" },
                            { topic: "주거정책", score: 78, priority: "높음" },
                            { topic: "경제정책", score: 72, priority: "높음" },
                            { topic: "교통정책", score: 68, priority: "중간" }
                        ]
                    },
                    performance_analysis: {
                        effectiveness_scores: [8, 9, 9, 7, 8],
                        regional_relevance_scores: [95, 88, 92, 85, 78],
                        implementation_scores: [70, 75, 80, 65, 85]
                    },
                    match_analysis: {
                        covered_topics: ["경제정책", "교육정책", "교통정책", "주거정책"],
                        uncovered_high_priority_topics: [],
                        overall_match_score: 100.0
                    },
                    detailed_bills: [
                        {
                            bill_title: "교육비 부담 완화를 위한 사교육비 세액공제 확대법",
                            proposal_date: "2024-03-15",
                            main_content: "사교육비 세액공제 한도를 현행 300만원에서 500만원으로 확대하여 학부모 부담 경감",
                            target_topics: ["교육정책"],
                            effectiveness_score: 8,
                            regional_relevance: 95,
                            implementation_possibility: 70
                        },
                        {
                            bill_title: "신혼부부 주거지원 특별법 개정안",
                            proposal_date: "2024-04-20",
                            main_content: "신혼부부 전용 임대주택 공급 확대 및 대출 금리 우대 혜택 강화",
                            target_topics: ["주거정책"],
                            effectiveness_score: 9,
                            regional_relevance: 88,
                            implementation_possibility: 75
                        },
                        {
                            bill_title: "판교 테크노밸리 확장 및 일자리 창출 특별법",
                            proposal_date: "2024-05-10",
                            main_content: "판교 테크노밸리 2단계 조성 및 스타트업 지원 확대를 통한 지역 일자리 창출",
                            target_topics: ["경제정책"],
                            effectiveness_score: 9,
                            regional_relevance: 92,
                            implementation_possibility: 80
                        }
                    ],
                    citizen_demands: [
                        "사교육비 경감을 위한 공교육 강화",
                        "신혼부부·청년 주거 지원 확대",
                        "판교 외 지역 일자리 창출",
                        "대중교통 인프라 확충"
                    ]
                },
                "김기현": {
                    politician_info: {
                        name: "김기현",
                        constituency: "부산 해운대구 을",
                        party: "국민의힘",
                        total_bills: 2
                    },
                    regional_analysis: {
                        region_name: "부산 해운대구",
                        population: 410000,
                        top_issues: [
                            { topic: "교통정책", score: 88, priority: "높음" },
                            { topic: "경제정책", score: 75, priority: "높음" },
                            { topic: "문화정책", score: 68, priority: "중간" }
                        ]
                    },
                    performance_analysis: {
                        effectiveness_scores: [9, 8],
                        regional_relevance_scores: [95, 82],
                        implementation_scores: [70, 75]
                    },
                    match_analysis: {
                        covered_topics: ["교통정책", "경제정책", "문화정책"],
                        uncovered_high_priority_topics: [],
                        overall_match_score: 85.0
                    },
                    detailed_bills: [
                        {
                            bill_title: "부산 가덕도 신공항 건설 촉진법",
                            proposal_date: "2024-02-28",
                            main_content: "가덕도 신공항 건설 일정 단축 및 예산 확보를 위한 특별 조치",
                            target_topics: ["교통정책", "경제정책"],
                            effectiveness_score: 9,
                            regional_relevance: 95,
                            implementation_possibility: 70
                        },
                        {
                            bill_title: "해양관광 클러스터 조성 특별법",
                            proposal_date: "2024-04-15",
                            main_content: "부산 해운대 일대 해양관광 클러스터 조성을 통한 관광산업 활성화",
                            target_topics: ["문화정책", "경제정책"],
                            effectiveness_score: 8,
                            regional_relevance: 82,
                            implementation_possibility: 75
                        }
                    ],
                    citizen_demands: [
                        "가덕도 신공항 조기 완공",
                        "해양관광 인프라 확충",
                        "지역 일자리 창출",
                        "교통 접근성 개선"
                    ]
                }
            };

            // 토픽 색상 매핑
            const topicColors = {
                '경제정책': 'bg-blue-100 text-blue-800',
                '주거정책': 'bg-green-100 text-green-800',
                '교육정책': 'bg-purple-100 text-purple-800',
                '복지정책': 'bg-pink-100 text-pink-800',
                '환경정책': 'bg-emerald-100 text-emerald-800',
                '교통정책': 'bg-orange-100 text-orange-800',
                '문화정책': 'bg-indigo-100 text-indigo-800',
                '안전정책': 'bg-red-100 text-red-800'
            };

            // 우선순위 색상
            const priorityColors = {
                '높음': 'text-red-600 bg-red-50',
                '중간': 'text-yellow-600 bg-yellow-50',
                '낮음': 'text-green-600 bg-green-50'
            };

            useEffect(() => {
                setLoading(true);
                setTimeout(() => {
                    setAnalysisData(sampleAnalysisData[selectedPolitician]);
                    setLoading(false);
                }, 500);
            }, [selectedPolitician]);

            const getScoreColor = (score) => {
                if (score >= 80) return 'text-green-600';
                if (score >= 60) return 'text-yellow-600';
                return 'text-red-600';
            };

            const getMatchScoreDescription = (score) => {
                if (score >= 80) return '🌟 매우 우수';
                if (score >= 60) return '👍 양호';
                if (score >= 40) return '⚠️ 보통';
                return '❌ 개선 필요';
            };

            if (loading || !analysisData) {
                return (
                    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                        <div className="text-center">
                            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                            <p className="text-gray-600">분석 데이터 로드 중...</p>
                        </div>
                    </div>
                );
            }

            const avgEffectiveness = analysisData.performance_analysis.effectiveness_scores.reduce((a, b) => a + b, 0) / analysisData.performance_analysis.effectiveness_scores.length;
            const avgRelevance = analysisData.performance_analysis.regional_relevance_scores.reduce((a, b) => a + b, 0) / analysisData.performance_analysis.regional_relevance_scores.length;
            const avgImplementation = analysisData.performance_analysis.implementation_scores.reduce((a, b) => a + b, 0) / analysisData.performance_analysis.implementation_scores.length;

            return (
                <div className="min-h-screen bg-gray-50">
                    {/* 네비게이션 헤더 */}
                    <header className="bg-white shadow-sm border-b border-gray-200">
                        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                            <div className="flex justify-between items-center py-4">
                                <div className="flex items-center space-x-4">
                                    <h1 className="text-xl font-bold text-gray-800">
                                        🎯 NewsBot 2단계 정치인 분석
                                    </h1>
                                </div>
                                <select
                                    value={selectedPolitician}
                                    onChange={(e) => setSelectedPolitician(e.target.value)}
                                    className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                >
                                    <option value="이재명">이재명 (성남시 분당구 갑)</option>
                                    <option value="김기현">김기현 (부산 해운대구 을)</option>
                                </select>
                            </div>
                        </div>
                    </header>

                    {/* 메인 컨텐츠 */}
                    <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                        {/* 정치인 기본 정보 */}
                        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
                            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                                <div className="bg-blue-50 rounded-lg p-4 text-center">
                                    <div className="text-2xl font-bold text-blue-600">{analysisData.politician_info.name}</div>
                                    <div className="text-sm text-blue-800">{analysisData.politician_info.party}</div>
                                </div>
                                <div className="bg-green-50 rounded-lg p-4 text-center">
                                    <div className="text-2xl font-bold text-green-600">{analysisData.regional_analysis.region_name}</div>
                                    <div className="text-sm text-green-800">{analysisData.regional_analysis.population?.toLocaleString()}명</div>
                                </div>
                                <div className="bg-purple-50 rounded-lg p-4 text-center">
                                    <div className="text-2xl font-bold text-purple-600">{analysisData.politician_info.total_bills}건</div>
                                    <div className="text-sm text-purple-800">발의 법안</div>
                                </div>
                                <div className="bg-orange-50 rounded-lg p-4 text-center">
                                    <div className={`text-2xl font-bold ${getScoreColor(analysisData.match_analysis.overall_match_score)}`}>
                                        {analysisData.match_analysis.overall_match_score}%
                                    </div>
                                    <div className="text-sm text-orange-800">매칭 점수</div>
                                </div>
                            </div>
                        </div>

                        {/* 1단계: 지역 요구사항 분석 */}
                        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
                            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                                <MapPinIcon className="h-5 w-5 mr-2 text-green-500" />
                                1단계: 지역 요구사항 분석
                            </h3>
                            
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                                {analysisData.regional_analysis.top_issues.map((issue, index) => (
                                    <div key={index} className="border border-gray-200 rounded-lg p-4">
                                        <div className="flex items-center justify-between mb-2">
                                            <span className={`px-3 py-1 rounded-full text-sm font-medium ${topicColors[issue.topic] || 'bg-gray-100 text-gray-800'}`}>
                                                {issue.topic}
                                            </span>
                                            <span className={`px-2 py-1 rounded text-xs font-medium ${priorityColors[issue.priority]}`}>
                                                {issue.priority} 우선순위
                                            </span>
                                        </div>
                                        <div className="text-2xl font-bold text-gray-900">{issue.score}점</div>
                                    </div>
                                ))}
                            </div>

                            <div className="bg-gray-50 rounded-lg p-4">
                                <h4 className="font-semibold text-gray-900 mb-3">🏘️ 주요 지역 요구사항</h4>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                                    {analysisData.citizen_demands?.map((demand, index) => (
                                        <div key={index} className="flex items-center text-sm text-gray-600">
                                            <ArrowRightIcon className="h-4 w-4 mr-2 text-gray-400" />
                                            {demand}
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>

                        {/* 2단계: 정치인 대응 분석 */}
                        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
                            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                                <DocumentTextIcon className="h-5 w-5 mr-2 text-blue-500" />
                                2단계: 정치인 대응 분석
                            </h3>

                            {/* 성과 지표 */}
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                                <div className="bg-blue-50 rounded-lg p-4 text-center">
                                    <div className="text-2xl font-bold text-blue-600">{avgEffectiveness.toFixed(1)}/10</div>
                                    <div className="text-sm text-blue-800">평균 효과성</div>
                                </div>
                                <div className="bg-green-50 rounded-lg p-4 text-center">
                                    <div className="text-2xl font-bold text-green-600">{avgRelevance.toFixed(1)}/100</div>
                                    <div className="text-sm text-green-800">평균 지역 연관성</div>
                                </div>
                                <div className="bg-purple-50 rounded-lg p-4 text-center">
                                    <div className="text-2xl font-bold text-purple-600">{avgImplementation.toFixed(1)}/100</div>
                                    <div className="text-sm text-purple-800">평균 실현 가능성</div>
                                </div>
                            </div>

                            {/* 주요 법안 */}
                            <h4 className="font-semibold text-gray-900 mb-3">📜 주요 발의 법안</h4>
                            <div className="space-y-4">
                                {analysisData.detailed_bills.map((bill, index) => (
                                    <div key={index} className="border border-gray-200 rounded-lg p-4">
                                        <div className="flex items-start justify-between mb-2">
                                            <h5 className="font-medium text-gray-900 flex-1">{bill.bill_title}</h5>
                                            <span className="text-xs text-gray-500 ml-4">{bill.proposal_date}</span>
                                        </div>
                                        
                                        <div className="flex flex-wrap gap-2 mb-2">
                                            {bill.target_topics.map((topic, topicIndex) => (
                                                <span key={topicIndex} className={`px-2 py-1 rounded-full text-xs font-medium ${topicColors[topic] || 'bg-gray-100 text-gray-800'}`}>
                                                    {topic}
                                                </span>
                                            ))}
                                        </div>
                                        
                                        <p className="text-sm text-gray-600 mb-3">{bill.main_content}</p>
                                        
                                        <div className="grid grid-cols-3 gap-4 text-center">
                                            <div>
                                                <div className="text-lg font-semibold text-blue-600">{bill.effectiveness_score}/10</div>
                                                <div className="text-xs text-gray-500">효과성</div>
                                            </div>
                                            <div>
                                                <div className="text-lg font-semibold text-green-600">{bill.regional_relevance}/100</div>
                                                <div className="text-xs text-gray-500">지역 연관성</div>
                                            </div>
                                            <div>
                                                <div className="text-lg font-semibold text-purple-600">{bill.implementation_possibility}/100</div>
                                                <div className="text-xs text-gray-500">실현 가능성</div>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* 매칭 분석 및 평가 */}
                        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                                <ChartBarIcon className="h-5 w-5 mr-2 text-purple-500" />
                                매칭 분석 및 종합 평가
                            </h3>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                {/* 매칭 분석 */}
                                <div>
                                    <div className="bg-gray-50 rounded-lg p-4 mb-4 text-center">
                                        <div className={`text-3xl font-bold ${getScoreColor(analysisData.match_analysis.overall_match_score)}`}>
                                            {analysisData.match_analysis.overall_match_score}%
                                        </div>
                                        <div className="text-sm text-gray-600">
                                            {getMatchScoreDescription(analysisData.match_analysis.overall_match_score)}
                                        </div>
                                    </div>

                                    <div>
                                        <h4 className="font-medium text-gray-900 mb-2 flex items-center">
                                            <CheckCircleIcon className="h-4 w-4 mr-2 text-green-500" />
                                            대응한 토픽
                                        </h4>
                                        <div className="flex flex-wrap gap-2">
                                            {analysisData.match_analysis.covered_topics.map((topic, index) => (
                                                <span key={index} className={`px-3 py-1 rounded-full text-sm font-medium ${topicColors[topic] || 'bg-gray-100 text-gray-800'}`}>
                                                    {topic}
                                                </span>
                                            ))}
                                        </div>
                                    </div>
                                </div>

                                {/* 종합 평가 */}
                                <div>
                                    <h4 className="font-medium text-gray-900 mb-3">💡 종합 평가</h4>
                                    <div className="space-y-3">
                                        <div className="bg-blue-50 rounded-lg p-3">
                                            <div className="font-medium text-blue-800">지역 요구사항 반영도</div>
                                            <div className="text-sm text-blue-600">
                                                {analysisData.match_analysis.overall_match_score >= 80 ? 
                                                    '매우 잘 반영하고 있습니다.' :
                                                    analysisData.match_analysis.overall_match_score >= 60 ?
                                                    '적절히 반영하고 있습니다.' :
                                                    '반영도를 높일 필요가 있습니다.'
                                                }
                                            </div>
                                        </div>

                                        <div className="bg-green-50 rounded-lg p-3">
                                            <div className="font-medium text-green-800">법안 효과성</div>
                                            <div className="text-sm text-green-600">
                                                {avgEffectiveness >= 8 ?
                                                    '법안의 효과성이 매우 높습니다.' :
                                                    avgEffectiveness >= 6 ?
                                                    '법안의 효과성이 적절합니다.' :
                                                    '법안의 효과성 개선이 필요합니다.'
                                                }
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </main>

                    {/* 푸터 */}
                    <footer className="bg-white border-t border-gray-200 mt-12">
                        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                            <div className="text-center text-sm text-gray-500">
                                <p>© 2024 NewsBot 2단계 정치인 분석 시스템. 지역 요구 → 정치인 대응 분석 플랫폼.</p>
                            </div>
                        </div>
                    </footer>
                </div>
            );
        };

        ReactDOM.render(<TwoStagePoliticianAnalysisPage />, document.getElementById('root'));
    </script>
</body>
</html>
        """
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(html_content.encode('utf-8'))))
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
    
    def send_json_response(self, data):
        """JSON 응답 전송"""
        json_data = json.dumps(data, ensure_ascii=False, indent=2)
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(json_data.encode('utf-8'))))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json_data.encode('utf-8'))
    
    def log_message(self, format, *args):
        """로그 메시지 출력"""
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {format % args}")

def run_test_server(port=3000):
    """테스트 서버 실행"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, CustomHTTPRequestHandler)
    
    print(f"🚀 NewsBot 민생토픽 테스트 서버 시작!")
    print(f"📍 주소: http://localhost:{port}")
    print(f"🔗 민생토픽 페이지: http://localhost:{port}/regional-minsaeng-topics")
    print(f"⏹️  종료하려면 Ctrl+C를 누르세요")
    print("=" * 60)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print(f"\n🛑 테스트 서버 종료")
        httpd.server_close()

if __name__ == "__main__":
    run_test_server()
