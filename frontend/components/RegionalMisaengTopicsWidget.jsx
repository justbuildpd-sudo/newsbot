import React, { useState, useEffect, useMemo } from 'react';
import { 
  ChartBarIcon, 
  MapPinIcon, 
  FireIcon, 
  DocumentTextIcon,
  MagnifyingGlassIcon,
  ChevronDownIcon,
  InformationCircleIcon
} from '@heroicons/react/24/outline';

const RegionalMinsaengTopicsWidget = () => {
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

  // 레벨별 아이콘
  const levelIcons = {
    '광역시도': '🏛️',
    '시군구': '🏘️',
    '읍면동': '🏠'
  };

  // 데이터 로드
  useEffect(() => {
    const loadMinsaengData = async () => {
      try {
        setLoading(true);
        
        // 실제 환경에서는 API 엔드포인트에서 로드
        // const response = await fetch('/api/regional-minsaeng-topics');
        // const data = await response.json();
        
        // 개발용 임시 데이터
        const mockData = {
          last_updated: "2025-09-20T01:52:50.686815",
          total_regions: 66,
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
            "서울": {
              region_name: "서울특별시",
              level: "광역시도",
              mention_count: 376,
              dominant_topics: ["경제정책", "주거정책"],
              topic_scores: { "경제정책": 45, "주거정책": 38 },
              interpretation: "서울은 경제정책 분야가 주요 관심사로, 일자리 창출과 경제 활성화에 대한 논의가 활발함. 또한 주거정책 분야도 함께 주목받고 있음",
              promises: ["자전거이동성향상을위한서울지역자전거도로건설", "위한관련인프라조성"],
              confidence_score: 83
            },
            "부산": {
              region_name: "부산광역시",
              level: "광역시도",
              mention_count: 249,
              dominant_topics: ["교통정책", "경제정책"],
              topic_scores: { "교통정책": 32, "경제정책": 28 },
              interpretation: "부산은 교통정책 분야가 주요 관심사로, 교통 인프라 개선과 대중교통 확충에 대한 논의가 활발함",
              promises: ["공항건설", "특별지방자치단체설치"],
              confidence_score: 60
            },
            "성남시": {
              region_name: "성남시",
              level: "시군구",
              mention_count: 45,
              dominant_topics: ["교육정책", "주거정책"],
              topic_scores: { "교육정책": 18, "주거정책": 12 },
              interpretation: "성남시는 교육정책 분야가 주요 관심사로, 교육 환경 개선과 사교육 부담 해소에 대한 논의가 활발함",
              promises: ["교육환경개선사업", "주택공급확대"],
              confidence_score: 30
            },
            "정자동": {
              region_name: "정자동",
              level: "읍면동",
              mention_count: 12,
              dominant_topics: ["교육정책"],
              topic_scores: { "교육정책": 8 },
              interpretation: "정자동은 교육정책 분야가 주요 관심사로, 교육 환경 개선에 대한 논의가 활발함",
              promises: ["학교시설현대화"],
              confidence_score: 8
            }
          }
        };
        
        setMinsaengData(mockData);
      } catch (error) {
        console.error('민생토픽 데이터 로드 실패:', error);
      } finally {
        setLoading(false);
      }
    };

    loadMinsaengData();
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
      regions = regions.filter(([region, data]) => 
        region.toLowerCase().includes(searchTerm.toLowerCase()) ||
        data.region_name.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // 언급 횟수 순으로 정렬
    regions.sort(([_, a], [__, b]) => b.mention_count - a.mention_count);

    return regions;
  }, [minsaengData, selectedLevel, selectedTopic, searchTerm]);

  // 토픽별 통계
  const topicStats = useMemo(() => {
    if (!minsaengData?.regional_data) return {};

    const stats = {};
    Object.values(minsaengData.regional_data).forEach(region => {
      region.dominant_topics.forEach(topic => {
        if (!stats[topic]) {
          stats[topic] = { count: 0, totalScore: 0 };
        }
        stats[topic].count += 1;
        stats[topic].totalScore += region.topic_scores[topic] || 0;
      });
    });

    return stats;
  }, [minsaengData]);

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-4 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (!minsaengData) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="text-center text-gray-500">
          <InformationCircleIcon className="h-12 w-12 mx-auto mb-2" />
          <p>민생토픽 데이터를 불러올 수 없습니다.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      {/* 헤더 */}
      <div className="border-b border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <FireIcon className="h-6 w-6 text-orange-500" />
            <h2 className="text-xl font-bold text-gray-900">지역별 민생토픽 분석</h2>
          </div>
          <div className="text-sm text-gray-500">
            총 {minsaengData.total_regions}개 지역 분석
          </div>
        </div>

        {/* 필터 및 검색 */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* 검색 */}
          <div className="relative">
            <MagnifyingGlassIcon className="h-5 w-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="지역명 검색..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* 레벨 필터 */}
          <select
            value={selectedLevel}
            onChange={(e) => setSelectedLevel(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">모든 레벨</option>
            <option value="광역시도">광역시도</option>
            <option value="시군구">시군구</option>
            <option value="읍면동">읍면동</option>
          </select>

          {/* 토픽 필터 */}
          <select
            value={selectedTopic}
            onChange={(e) => setSelectedTopic(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">모든 토픽</option>
            {Object.keys(minsaengData.minsaeng_topic_categories).map(topic => (
              <option key={topic} value={topic}>{topic}</option>
            ))}
          </select>

          {/* 결과 수 */}
          <div className="flex items-center justify-center px-3 py-2 bg-gray-50 rounded-lg">
            <span className="text-sm text-gray-600">
              {filteredRegions.length}개 지역
            </span>
          </div>
        </div>
      </div>

      {/* 토픽 통계 요약 */}
      <div className="border-b border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-3">주요 민생토픽</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {Object.entries(topicStats)
            .sort(([,a], [,b]) => b.count - a.count)
            .slice(0, 8)
            .map(([topic, stats]) => (
              <div 
                key={topic}
                className={`p-3 rounded-lg border cursor-pointer transition-all ${
                  selectedTopic === topic 
                    ? topicColors[topic] + ' ring-2 ring-offset-1' 
                    : 'bg-gray-50 hover:bg-gray-100 border-gray-200'
                }`}
                onClick={() => setSelectedTopic(selectedTopic === topic ? 'all' : topic)}
              >
                <div className="text-sm font-medium">{topic}</div>
                <div className="text-xs text-gray-600 mt-1">
                  {stats.count}개 지역
                </div>
              </div>
            ))}
        </div>
      </div>

      {/* 지역 목록 */}
      <div className="p-6">
        <div className="space-y-4 max-h-96 overflow-y-auto">
          {filteredRegions.length === 0 ? (
            <div className="text-center text-gray-500 py-8">
              <MapPinIcon className="h-12 w-12 mx-auto mb-2" />
              <p>검색 조건에 맞는 지역이 없습니다.</p>
            </div>
          ) : (
            filteredRegions.map(([regionKey, regionData]) => (
              <div
                key={regionKey}
                className={`p-4 rounded-lg border transition-all cursor-pointer ${
                  selectedRegion === regionKey
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                }`}
                onClick={() => setSelectedRegion(selectedRegion === regionKey ? null : regionKey)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className="text-lg">{levelIcons[regionData.level]}</span>
                      <h4 className="text-lg font-semibold text-gray-900">
                        {regionData.region_name}
                      </h4>
                      <span className="text-sm text-gray-500">
                        ({regionData.level})
                      </span>
                    </div>

                    <div className="flex items-center space-x-4 mb-2">
                      <div className="flex items-center space-x-1">
                        <DocumentTextIcon className="h-4 w-4 text-gray-400" />
                        <span className="text-sm text-gray-600">
                          {regionData.mention_count}회 언급
                        </span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <ChartBarIcon className="h-4 w-4 text-gray-400" />
                        <span className="text-sm text-gray-600">
                          신뢰도 {regionData.confidence_score}
                        </span>
                      </div>
                    </div>

                    <div className="flex flex-wrap gap-2 mb-2">
                      {regionData.dominant_topics.slice(0, 3).map(topic => (
                        <span
                          key={topic}
                          className={`px-2 py-1 text-xs font-medium rounded-full border ${topicColors[topic]}`}
                        >
                          {topic}
                        </span>
                      ))}
                    </div>

                    <p className="text-sm text-gray-700">
                      {regionData.interpretation}
                    </p>
                  </div>

                  <ChevronDownIcon 
                    className={`h-5 w-5 text-gray-400 transition-transform ${
                      selectedRegion === regionKey ? 'transform rotate-180' : ''
                    }`}
                  />
                </div>

                {/* 상세 정보 (펼쳤을 때) */}
                {selectedRegion === regionKey && (
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {/* 토픽 점수 */}
                      <div>
                        <h5 className="text-sm font-medium text-gray-900 mb-2">토픽별 점수</h5>
                        <div className="space-y-2">
                          {Object.entries(regionData.topic_scores)
                            .sort(([,a], [,b]) => b - a)
                            .map(([topic, score]) => (
                              <div key={topic} className="flex items-center justify-between">
                                <span className="text-sm text-gray-600">{topic}</span>
                                <div className="flex items-center space-x-2">
                                  <div className="w-20 bg-gray-200 rounded-full h-2">
                                    <div
                                      className="bg-blue-500 h-2 rounded-full"
                                      style={{ width: `${Math.min(100, (score / 50) * 100)}%` }}
                                    ></div>
                                  </div>
                                  <span className="text-sm font-medium text-gray-900 w-8">
                                    {score}
                                  </span>
                                </div>
                              </div>
                            ))}
                        </div>
                      </div>

                      {/* 주요 공약 */}
                      <div>
                        <h5 className="text-sm font-medium text-gray-900 mb-2">주요 공약</h5>
                        <div className="space-y-1">
                          {regionData.promises.slice(0, 5).map((promise, index) => (
                            <div key={index} className="text-sm text-gray-600">
                              • {promise.length > 50 ? promise.substring(0, 50) + '...' : promise}
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>

      {/* 푸터 */}
      <div className="border-t border-gray-200 px-6 py-3 bg-gray-50">
        <div className="flex items-center justify-between text-sm text-gray-500">
          <span>
            마지막 업데이트: {new Date(minsaengData.last_updated).toLocaleString('ko-KR')}
          </span>
          <span>
            정책선거문화 빅데이터 분석 결과
          </span>
        </div>
      </div>
    </div>
  );
};

export default RegionalMinsaengTopicsWidget;
