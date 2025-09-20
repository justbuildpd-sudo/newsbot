import React, { useState, useEffect, useMemo } from 'react';
import {
  FireIcon,
  MagnifyingGlassIcon,
  ChevronDownIcon,
  InformationCircleIcon
} from '@heroicons/react/24/outline';

const StaticRegionalMinsaengTopicsWidget = () => {
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
        
        // 정적 데이터 (실제 API 대신 사용)
        const staticData = {
          last_updated: new Date().toISOString(),
          total_regions: 207,
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
            "강동구": {
              region_name: "강동구",
              parent_government: "서울특별시",
              level: "시군구",
              dominant_topics: ["주거정책", "경제정책", "교통정책"],
              topic_scores: { "주거정책": 75, "경제정책": 42, "교통정책": 38 },
              interpretation: "강동구는 주거정책과 경제정책에 상당한 관심을 보이며, 관련 정책 개발이 활발히 진행되고 있음",
              promises: ["주택공급확대", "경제지원", "교통인프라개선"],
              confidence_score: 8
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
            },
            "성남시": {
              region_name: "성남시",
              parent_government: "경기도",
              level: "시군구",
              dominant_topics: ["교육정책", "주거정책", "경제정책"],
              topic_scores: { "교육정책": 58, "주거정책": 42, "경제정책": 38 },
              interpretation: "성남시는 교육정책 분야가 주요 관심사로, 교육 환경 개선과 사교육 부담 해소에 대한 논의가 활발함",
              promises: ["교육환경개선사업", "주택공급확대", "경제지원"],
              confidence_score: 6
            },
            "대구수성구": {
              region_name: "수성구",
              parent_government: "대구광역시",
              level: "시군구",
              dominant_topics: ["주거정책", "환경정책", "문화정책"],
              topic_scores: { "주거정책": 52, "환경정책": 38, "문화정책": 28 },
              interpretation: "수성구는 주거정책 분야에서 상당한 관심을 보이며, 관련 정책 개발이 활발히 진행되고 있음",
              promises: ["주택공급", "환경개선", "문화시설건설"],
              confidence_score: 7
            },
            "인천연수구": {
              region_name: "연수구",
              parent_government: "인천광역시",
              level: "시군구",
              dominant_topics: ["경제정책", "교통정책", "주거정책"],
              topic_scores: { "경제정책": 65, "교통정책": 45, "주거정책": 35 },
              interpretation: "연수구는 경제정책 분야에서 강한 관심을 보이며, 이는 해당 지역의 주요 정책 이슈임",
              promises: ["경제활성화", "교통인프라개선", "주택공급"],
              confidence_score: 8
            },
            "광주광산구": {
              region_name: "광산구",
              parent_government: "광주광역시",
              level: "시군구",
              dominant_topics: ["경제정책", "주거정책", "환경정책"],
              topic_scores: { "경제정책": 58, "주거정책": 42, "환경정책": 28 },
              interpretation: "광산구는 경제정책 분야에서 상당한 관심을 보이며, 관련 정책 개발이 활발히 진행되고 있음",
              promises: ["경제지원", "주택공급", "환경개선"],
              confidence_score: 6
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

    // 언급 횟수 순으로 정렬
    regions.sort(([_, a], [__, b]) => (b.mention_count || 0) - (a.mention_count || 0));

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
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="space-y-3">
            <div className="h-4 bg-gray-200 rounded"></div>
            <div className="h-4 bg-gray-200 rounded w-5/6"></div>
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
            <h2 className="text-xl font-bold text-gray-900">시군구별 민생토픽 분석</h2>
          </div>
          <div className="text-sm text-gray-500">
            총 {minsaengData.total_regions}개 시군구 분석
          </div>
        </div>

        {/* 필터 및 검색 */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* 검색 */}
          <div className="relative">
            <MagnifyingGlassIcon className="h-5 w-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="시군구명 검색 (예: 강남구, 수원시, 부산진구...)"
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
              {filteredRegions.length}개 시군구
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
              <div key={topic} className={`p-3 rounded-lg border ${topicColors[topic] || 'bg-gray-100 text-gray-800 border-gray-200'}`}>
                <div className="font-medium text-sm">{topic}</div>
                <div className="text-xs mt-1">{stats.count}개 지역</div>
              </div>
            ))}
        </div>
      </div>

      {/* 지역별 결과 */}
      <div className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">지역별 분석 결과</h3>
        <div className="space-y-4">
          {filteredRegions.map(([regionName, regionData]) => (
            <div
              key={regionName}
              className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
              onClick={() => setSelectedRegion(selectedRegion === regionName ? null : regionName)}
            >
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-2">
                  <span className="text-lg">{levelIcons[regionData.level] || '🏘️'}</span>
                  <div>
                    <h4 className="font-semibold text-gray-900">{regionData.region_name}</h4>
                    <p className="text-sm text-gray-500">{regionData.parent_government}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                    신뢰도 {regionData.confidence_score}/10
                  </span>
                  <ChevronDownIcon 
                    className={`h-4 w-4 text-gray-400 transition-transform ${
                      selectedRegion === regionName ? 'rotate-180' : ''
                    }`} 
                  />
                </div>
              </div>

              <div className="mb-3">
                <div className="flex flex-wrap gap-2">
                  {regionData.dominant_topics.map(topic => (
                    <span
                      key={topic}
                      className={`px-2 py-1 rounded-full text-xs font-medium ${topicColors[topic] || 'bg-gray-100 text-gray-800'}`}
                    >
                      {topic}
                    </span>
                  ))}
                </div>
              </div>

              <p className="text-sm text-gray-600 mb-3">
                {regionData.interpretation}
              </p>

              {selectedRegion === regionName && (
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <h5 className="font-medium text-gray-900 mb-2">정책 공약</h5>
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
          <div className="text-center text-gray-500 py-8">
            <InformationCircleIcon className="h-12 w-12 mx-auto mb-2" />
            <p>검색 조건에 맞는 지역이 없습니다.</p>
          </div>
        )}
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

export default StaticRegionalMinsaengTopicsWidget;
