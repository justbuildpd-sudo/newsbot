import React, { useState, useEffect } from 'react';
import {
  UserIcon,
  MapPinIcon,
  DocumentTextIcon,
  ChartBarIcon,
  CheckCircleIcon,
  XCircleIcon,
  InformationCircleIcon,
  ArrowRightIcon
} from '@heroicons/react/24/outline';

const TwoStagePoliticianAnalysisWidget = () => {
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
          bill_number: "2024-교육-001",
          proposal_date: "2024-03-15",
          main_content: "사교육비 세액공제 한도를 현행 300만원에서 500만원으로 확대하여 학부모 부담 경감",
          target_topics: ["교육정책"],
          effectiveness_score: 8,
          regional_relevance: 95,
          implementation_possibility: 70
        },
        {
          bill_title: "신혼부부 주거지원 특별법 개정안",
          bill_number: "2024-주거-002",
          proposal_date: "2024-04-20",
          main_content: "신혼부부 전용 임대주택 공급 확대 및 대출 금리 우대 혜택 강화",
          target_topics: ["주거정책"],
          effectiveness_score: 9,
          regional_relevance: 88,
          implementation_possibility: 75
        },
        {
          bill_title: "판교 테크노밸리 확장 및 일자리 창출 특별법",
          bill_number: "2024-경제-003",
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
          { topic: "문화정책", score: 68, priority: "중간" },
          { topic: "관광정책", score: 72, priority: "높음" }
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
          bill_number: "2024-교통-101",
          proposal_date: "2024-02-28",
          main_content: "가덕도 신공항 건설 일정 단축 및 예산 확보를 위한 특별 조치",
          target_topics: ["교통정책", "경제정책"],
          effectiveness_score: 9,
          regional_relevance: 95,
          implementation_possibility: 70
        },
        {
          bill_title: "해양관광 클러스터 조성 특별법",
          bill_number: "2024-문화-102",
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
    '경제정책': 'bg-blue-100 text-blue-800 border-blue-200',
    '주거정책': 'bg-green-100 text-green-800 border-green-200',
    '교육정책': 'bg-purple-100 text-purple-800 border-purple-200',
    '복지정책': 'bg-pink-100 text-pink-800 border-pink-200',
    '환경정책': 'bg-emerald-100 text-emerald-800 border-emerald-200',
    '교통정책': 'bg-orange-100 text-orange-800 border-orange-200',
    '문화정책': 'bg-indigo-100 text-indigo-800 border-indigo-200',
    '안전정책': 'bg-red-100 text-red-800 border-red-200',
    '관광정책': 'bg-cyan-100 text-cyan-800 border-cyan-200'
  };

  // 우선순위 색상
  const priorityColors = {
    '높음': 'text-red-600 bg-red-50',
    '중간': 'text-yellow-600 bg-yellow-50',
    '낮음': 'text-green-600 bg-green-50'
  };

  useEffect(() => {
    setLoading(true);
    // 실제 환경에서는 API 호출
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

  if (!analysisData) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="text-center text-gray-500">
          <InformationCircleIcon className="h-12 w-12 mx-auto mb-2" />
          <p>분석 데이터를 불러올 수 없습니다.</p>
        </div>
      </div>
    );
  }

  const avgEffectiveness = analysisData.performance_analysis.effectiveness_scores.reduce((a, b) => a + b, 0) / analysisData.performance_analysis.effectiveness_scores.length;
  const avgRelevance = analysisData.performance_analysis.regional_relevance_scores.reduce((a, b) => a + b, 0) / analysisData.performance_analysis.regional_relevance_scores.length;
  const avgImplementation = analysisData.performance_analysis.implementation_scores.reduce((a, b) => a + b, 0) / analysisData.performance_analysis.implementation_scores.length;

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      {/* 헤더 */}
      <div className="border-b border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <UserIcon className="h-6 w-6 text-blue-500" />
            <h2 className="text-xl font-bold text-gray-900">2단계 정치인 분석</h2>
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

        {/* 정치인 기본 정보 */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-blue-50 rounded-lg p-4">
            <div className="text-2xl font-bold text-blue-600">{analysisData.politician_info.name}</div>
            <div className="text-sm text-blue-800">{analysisData.politician_info.party}</div>
          </div>
          <div className="bg-green-50 rounded-lg p-4">
            <div className="text-2xl font-bold text-green-600">{analysisData.regional_analysis.region_name}</div>
            <div className="text-sm text-green-800">{analysisData.regional_analysis.population?.toLocaleString()}명</div>
          </div>
          <div className="bg-purple-50 rounded-lg p-4">
            <div className="text-2xl font-bold text-purple-600">{analysisData.politician_info.total_bills}건</div>
            <div className="text-sm text-purple-800">발의 법안</div>
          </div>
          <div className="bg-orange-50 rounded-lg p-4">
            <div className={`text-2xl font-bold ${getScoreColor(analysisData.match_analysis.overall_match_score)}`}>
              {analysisData.match_analysis.overall_match_score}%
            </div>
            <div className="text-sm text-orange-800">매칭 점수</div>
          </div>
        </div>
      </div>

      {/* 1단계: 지역 요구사항 분석 */}
      <div className="border-b border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <MapPinIcon className="h-5 w-5 mr-2 text-green-500" />
          1단계: 지역 요구사항 분석
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          {analysisData.regional_analysis.top_issues.map((issue, index) => (
            <div key={index} className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <span className={`px-2 py-1 rounded-full text-sm font-medium ${topicColors[issue.topic] || 'bg-gray-100 text-gray-800'}`}>
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

        {/* 주요 지역 요구사항 */}
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
      <div className="border-b border-gray-200 p-6">
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
      <div className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <ChartBarIcon className="h-5 w-5 mr-2 text-purple-500" />
          매칭 분석 및 종합 평가
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* 매칭 분석 */}
          <div>
            <div className="bg-gray-50 rounded-lg p-4 mb-4">
              <div className="text-center mb-4">
                <div className={`text-3xl font-bold ${getScoreColor(analysisData.match_analysis.overall_match_score)}`}>
                  {analysisData.match_analysis.overall_match_score}%
                </div>
                <div className="text-sm text-gray-600">
                  {getMatchScoreDescription(analysisData.match_analysis.overall_match_score)}
                </div>
              </div>
            </div>

            <div className="space-y-3">
              <div>
                <h4 className="font-medium text-gray-900 mb-2 flex items-center">
                  <CheckCircleIcon className="h-4 w-4 mr-2 text-green-500" />
                  대응한 토픽
                </h4>
                <div className="flex flex-wrap gap-2">
                  {analysisData.match_analysis.covered_topics.map((topic, index) => (
                    <span key={index} className={`px-2 py-1 rounded-full text-xs font-medium ${topicColors[topic] || 'bg-gray-100 text-gray-800'}`}>
                      {topic}
                    </span>
                  ))}
                </div>
              </div>

              {analysisData.match_analysis.uncovered_high_priority_topics.length > 0 && (
                <div>
                  <h4 className="font-medium text-gray-900 mb-2 flex items-center">
                    <XCircleIcon className="h-4 w-4 mr-2 text-red-500" />
                    미대응 우선순위 토픽
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {analysisData.match_analysis.uncovered_high_priority_topics.map((topic, index) => (
                      <span key={index} className="px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800 border border-red-200">
                        {topic}
                      </span>
                    ))}
                  </div>
                </div>
              )}
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

              {analysisData.match_analysis.uncovered_high_priority_topics.length > 0 && (
                <div className="bg-yellow-50 rounded-lg p-3">
                  <div className="font-medium text-yellow-800">개선 제안</div>
                  <div className="text-sm text-yellow-600">
                    {analysisData.match_analysis.uncovered_high_priority_topics.join(', ')} 분야 법안 발의를 고려해보세요.
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* 푸터 */}
      <div className="border-t border-gray-200 px-6 py-3 bg-gray-50">
        <div className="flex items-center justify-between text-sm text-gray-500">
          <span>2단계 분석: 지역 요구 → 정치인 대응</span>
          <span>마지막 업데이트: {new Date().toLocaleDateString('ko-KR')}</span>
        </div>
      </div>
    </div>
  );
};

export default TwoStagePoliticianAnalysisWidget;
