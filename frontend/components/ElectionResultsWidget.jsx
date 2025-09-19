import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  MapPinIcon, 
  UserGroupIcon, 
  ChartBarIcon, 
  TrophyIcon,
  InformationCircleIcon,
  MagnifyingGlassIcon
} from '@heroicons/react/24/outline';
import LocationSelectionModal from './LocationSelectionModal';

const ElectionResultsWidget = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedCandidate, setSelectedCandidate] = useState(null);
  const [cacheStats, setCacheStats] = useState(null);
  const [showLocationSelection, setShowLocationSelection] = useState(false);
  const [locationOptions, setLocationOptions] = useState([]);

  // 실제 정치인/지명 스마트 검색 API 호출
  const smartSearch = async (searchTerm) => {
    setLoading(true);
    try {
      const response = await fetch(`/api/smart/search?term=${encodeURIComponent(searchTerm)}`);
      const data = await response.json();
      
      if (data.success) {
        if (data.type === 'selection_required') {
          // 중복 지명 - 선택 모달 표시
          setLocationOptions(data.options);
          setShowLocationSelection(true);
          setSearchResults(null);
        } else {
          // 정상 검색 결과
          setSearchResults(data);
          // 캐시 통계도 함께 업데이트
          const statsResponse = await fetch('/api/cache/stats');
          const statsData = await statsResponse.json();
          setCacheStats(statsData);
        }
      } else {
        setSearchResults({ 
          error: data.error,
          suggestions: data.suggestions || [],
          available_options: data.available_politicians || data.available_regions || []
        });
      }
    } catch (error) {
      setSearchResults({ error: '검색 중 오류가 발생했습니다.' });
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchTerm.trim()) {
      smartSearch(searchTerm.trim());
    }
  };

  const handleLocationSelect = (selectedOption) => {
    // 선택된 지역으로 다시 검색
    const selectedTerm = selectedOption.key || selectedOption.description;
    setShowLocationSelection(false);
    setLocationOptions([]);
    smartSearch(selectedTerm);
  };

  const ElectionCard = ({ election, type }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-lg shadow-md p-6 mb-4"
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-800 flex items-center">
          <TrophyIcon className="h-5 w-5 mr-2 text-yellow-500" />
          {type} 선거결과
        </h3>
        <span className="text-sm text-gray-500">
          {election.election_date}
        </span>
      </div>

      {/* 당선자 정보 */}
      {election.candidates && election.candidates[0] && (
        <div className="bg-blue-50 rounded-lg p-4 mb-4">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="font-semibold text-blue-800">
                🏆 당선자: {election.candidates[0].name}
              </h4>
              <p className="text-blue-600">
                {election.candidates[0].party} | {election.candidates[0].vote_percentage}% 득표
              </p>
            </div>
            <button
              onClick={() => setSelectedCandidate(election.candidates[0])}
              className="px-3 py-1 bg-blue-600 text-white rounded-md text-sm hover:bg-blue-700"
            >
              상세보기
            </button>
          </div>
        </div>
      )}

      {/* 전체 후보자 목록 */}
      <div className="space-y-2">
        <h5 className="font-medium text-gray-700 flex items-center">
          <UserGroupIcon className="h-4 w-4 mr-2" />
          전체 후보자 ({election.candidates?.length || 0}명)
        </h5>
        
        {election.candidates?.map((candidate, index) => (
          <div 
            key={index}
            className={`flex items-center justify-between p-3 rounded-lg ${
              candidate.elected ? 'bg-green-50 border-l-4 border-green-500' : 'bg-gray-50'
            }`}
          >
            <div className="flex-1">
              <div className="flex items-center">
                <span className={`inline-block w-6 h-6 rounded-full text-xs text-white text-center leading-6 mr-3 ${
                  candidate.elected ? 'bg-green-500' : 'bg-gray-400'
                }`}>
                  {candidate.rank || index + 1}
                </span>
                <div>
                  <p className="font-medium text-gray-800">{candidate.name}</p>
                  <p className="text-sm text-gray-600">{candidate.party}</p>
                </div>
              </div>
            </div>
            
            <div className="text-right">
              <p className="font-semibold text-gray-800">
                {candidate.vote_count?.toLocaleString() || 0}표
              </p>
              <p className="text-sm text-gray-600">
                {candidate.vote_percentage || 0}%
              </p>
            </div>
            
            <button
              onClick={() => setSelectedCandidate(candidate)}
              className="ml-4 px-2 py-1 bg-gray-600 text-white rounded text-xs hover:bg-gray-700"
            >
              정보
            </button>
          </div>
        ))}
      </div>

      {/* 선거 분석 */}
      {election.election_analysis && (
        <div className="mt-4 p-4 bg-gray-50 rounded-lg">
          <h6 className="font-medium text-gray-700 mb-2">📊 선거 분석</h6>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-600">투표율:</span>
              <span className="ml-2 font-semibold">{election.election_analysis.voter_turnout}%</span>
            </div>
            <div>
              <span className="text-gray-600">총 투표수:</span>
              <span className="ml-2 font-semibold">{election.election_analysis.total_votes?.toLocaleString()}</span>
            </div>
          </div>
        </div>
      )}
    </motion.div>
  );

  const CandidateModal = ({ candidate, onClose }) => {
    if (!candidate) return null;

    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          className="bg-white rounded-lg max-w-2xl w-full max-h-[80vh] overflow-y-auto"
          onClick={(e) => e.stopPropagation()}
        >
          <div className="p-6">
            {/* 후보자 헤더 */}
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-2xl font-bold text-gray-800">{candidate.name}</h2>
                <p className="text-lg text-blue-600">{candidate.party}</p>
                {candidate.elected && (
                  <span className="inline-block bg-green-100 text-green-800 px-2 py-1 rounded-full text-sm font-medium mt-2">
                    🏆 당선
                  </span>
                )}
              </div>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-600 text-2xl"
              >
                ×
              </button>
            </div>

            {/* 기본 정보 */}
            <div className="grid grid-cols-2 gap-6 mb-6">
              <div>
                <h3 className="font-semibold text-gray-800 mb-3">📋 기본 정보</h3>
                <div className="space-y-2 text-sm">
                  <div><span className="text-gray-600">나이:</span> <span className="ml-2">{candidate.age}세</span></div>
                  <div><span className="text-gray-600">성별:</span> <span className="ml-2">{candidate.gender}</span></div>
                  <div><span className="text-gray-600">학력:</span> <span className="ml-2">{candidate.education}</span></div>
                  <div><span className="text-gray-600">가족:</span> <span className="ml-2">{candidate.family_info}</span></div>
                </div>
              </div>
              
              <div>
                <h3 className="font-semibold text-gray-800 mb-3">🗳️ 선거 결과</h3>
                <div className="space-y-2 text-sm">
                  <div><span className="text-gray-600">득표수:</span> <span className="ml-2 font-semibold">{candidate.vote_count?.toLocaleString()}</span></div>
                  <div><span className="text-gray-600">득표율:</span> <span className="ml-2 font-semibold">{candidate.vote_percentage}%</span></div>
                  <div><span className="text-gray-600">순위:</span> <span className="ml-2">{candidate.rank}위</span></div>
                  <div><span className="text-gray-600">선거비용:</span> <span className="ml-2">{candidate.campaign_budget?.toLocaleString()}원</span></div>
                </div>
              </div>
            </div>

            {/* 경력 정보 */}
            {candidate.career && candidate.career.length > 0 && (
              <div className="mb-6">
                <h3 className="font-semibold text-gray-800 mb-3">💼 주요 경력</h3>
                <div className="space-y-1">
                  {candidate.career.slice(0, 5).map((career, index) => (
                    <div key={index} className="text-sm text-gray-700 bg-gray-50 p-2 rounded">
                      • {career}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* 공약 정보 */}
            {candidate.promises && candidate.promises.length > 0 && (
              <div className="mb-6">
                <h3 className="font-semibold text-gray-800 mb-3">📜 주요 공약</h3>
                <div className="grid grid-cols-1 gap-2">
                  {candidate.promises.slice(0, 6).map((promise, index) => (
                    <div key={index} className="text-sm text-gray-700 bg-blue-50 p-3 rounded-lg border-l-4 border-blue-400">
                      {index + 1}. {promise}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* 정책 입장 */}
            {candidate.policy_positions && (
              <div className="mb-6">
                <h3 className="font-semibold text-gray-800 mb-3">🎯 정책 입장</h3>
                <div className="grid grid-cols-2 gap-4">
                  {Object.entries(candidate.policy_positions).map(([policy, position], index) => (
                    <div key={index} className="bg-yellow-50 p-3 rounded-lg">
                      <h4 className="font-medium text-yellow-800">{policy}</h4>
                      <p className="text-sm text-yellow-700 mt-1">{position}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* 지지단체 */}
            {candidate.support_groups && candidate.support_groups.length > 0 && (
              <div>
                <h3 className="font-semibold text-gray-800 mb-3">🤝 지지단체</h3>
                <div className="flex flex-wrap gap-2">
                  {candidate.support_groups.map((group, index) => (
                    <span key={index} className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm">
                      {group}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </motion.div>
      </motion.div>
    );
  };

  const CacheStatsPanel = () => {
    if (!cacheStats) return null;

    return (
      <motion.div
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg p-4 mb-6"
      >
        <h3 className="font-semibold text-purple-800 mb-3 flex items-center">
          <ChartBarIcon className="h-5 w-5 mr-2" />
          280MB 캐시 시스템 상태
        </h3>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div className="bg-white rounded-lg p-3">
            <div className="text-purple-600 font-medium">총 용량</div>
            <div className="text-xl font-bold text-purple-800">
              {cacheStats.enhanced_cache_sizes?.total_mb || 0}MB
            </div>
          </div>
          
          <div className="bg-white rounded-lg p-3">
            <div className="text-blue-600 font-medium">사용률</div>
            <div className="text-xl font-bold text-blue-800">
              {cacheStats.enhanced_cache_sizes?.utilization_percentage || 0}%
            </div>
          </div>
          
          <div className="bg-white rounded-lg p-3">
            <div className="text-green-600 font-medium">캐시된 지역</div>
            <div className="text-xl font-bold text-green-800">
              {cacheStats.enhanced_cache_counts?.total_cached_candidates || 0}개
            </div>
          </div>
          
          <div className="bg-white rounded-lg p-3">
            <div className="text-orange-600 font-medium">히트율</div>
            <div className="text-xl font-bold text-orange-800">
              {cacheStats.performance_stats?.hit_rate || 0}%
            </div>
          </div>
        </div>
      </motion.div>
    );
  };

  const DiversityAnalysisPanel = ({ diversityData }) => {
    if (!diversityData) return null;

    const dimensions = Object.keys(diversityData);

    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-6 mb-6"
      >
        <h3 className="font-semibold text-green-800 mb-4 flex items-center">
          <ChartBarIcon className="h-5 w-5 mr-2" />
          96.19% 다양성 시스템 분석 ({dimensions.length}개 차원)
        </h3>
        
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {dimensions.slice(0, 12).map((dimension, index) => {
            const data = diversityData[dimension];
            return (
              <div key={index} className="bg-white rounded-lg p-3 shadow-sm">
                <h4 className="font-medium text-gray-800 text-sm mb-2">{dimension}</h4>
                {data.current_value && (
                  <p className="text-xs text-gray-600 mb-1">
                    현재: {String(data.current_value).slice(0, 20)}...
                  </p>
                )}
                {data.ranking && (
                  <p className="text-xs text-blue-600 font-medium">
                    순위: {data.ranking}
                  </p>
                )}
              </div>
            );
          })}
        </div>
        
        {dimensions.length > 12 && (
          <div className="mt-4 text-center">
            <span className="text-sm text-gray-600">
              +{dimensions.length - 12}개 차원 더 보기
            </span>
          </div>
        )}
      </motion.div>
    );
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      {/* 헤더 */}
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">
          🗳️ 읍면동별 선거결과 검색
        </h1>
        <p className="text-gray-600">
          280MB 캐시 시스템으로 0.3ms 초고속 검색 | 96.19% 다양성 시스템 지원
        </p>
      </div>

      {/* 캐시 통계 패널 */}
      <CacheStatsPanel />

      {/* 검색 폼 */}
      <motion.form
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        onSubmit={handleSearch}
        className="mb-8"
      >
        <div className="flex items-center space-x-4">
          <div className="flex-1 relative">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="정치인 이름 또는 지명을 입력하세요 (예: 이재명, 정자, 강남, 서울)"
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? '검색 중...' : '검색'}
          </button>
        </div>
      </motion.form>

      {/* 검색 결과 */}
      <AnimatePresence>
        {searchResults && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            {searchResults.error ? (
              <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
                <p className="text-red-800">{searchResults.error}</p>
                {searchResults.available_regions && (
                  <div className="mt-4">
                    <p className="text-sm text-red-600 mb-2">사용 가능한 지역 (일부):</p>
                    <div className="flex flex-wrap gap-2 justify-center">
                      {searchResults.available_regions.slice(0, 5).map((region, index) => (
                        <button
                          key={index}
                          onClick={() => setSearchTerm(region.replace('region_', '읍면동_'))}
                          className="px-3 py-1 bg-red-100 text-red-700 rounded-md text-sm hover:bg-red-200"
                        >
                          {region.replace('region_', '읍면동_')}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div>
                {/* 지역 기본 정보 */}
                {searchResults.region_info && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-white rounded-lg shadow-md p-6 mb-6"
                  >
                    <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
                      <MapPinIcon className="h-6 w-6 mr-2 text-blue-500" />
                      {searchResults.region_info.region_name} 지역 정보
                    </h2>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className="bg-blue-50 rounded-lg p-3">
                        <div className="text-blue-600 font-medium text-sm">지역 유형</div>
                        <div className="text-lg font-bold text-blue-800">{searchResults.region_info.region_type}</div>
                      </div>
                      <div className="bg-green-50 rounded-lg p-3">
                        <div className="text-green-600 font-medium text-sm">인구</div>
                        <div className="text-lg font-bold text-green-800">{searchResults.region_info.population?.toLocaleString()}</div>
                      </div>
                      <div className="bg-yellow-50 rounded-lg p-3">
                        <div className="text-yellow-600 font-medium text-sm">면적</div>
                        <div className="text-lg font-bold text-yellow-800">{searchResults.region_info.area}km²</div>
                      </div>
                      <div className="bg-purple-50 rounded-lg p-3">
                        <div className="text-purple-600 font-medium text-sm">지역코드</div>
                        <div className="text-sm font-bold text-purple-800">{searchResults.region_info.region_code}</div>
                      </div>
                    </div>
                  </motion.div>
                )}

                {/* 96.19% 다양성 시스템 분석 */}
                {searchResults.diversity_analysis && (
                  <DiversityAnalysisPanel diversityData={searchResults.diversity_analysis} />
                )}

                {/* 선거 결과 */}
                {searchResults.election_results && (
                  <div>
                    <h2 className="text-xl font-bold text-gray-800 mb-4">🗳️ 선거 결과</h2>
                    
                    {/* 국회의원선거 */}
                    {searchResults.election_results.comprehensive_data?.national_assembly && (
                      <ElectionCard 
                        election={searchResults.election_results.comprehensive_data.national_assembly.election_2024}
                        type="국회의원"
                      />
                    )}

                    {/* 지방선거 */}
                    {searchResults.election_results.comprehensive_data?.local_government && (
                      <ElectionCard 
                        election={searchResults.election_results.comprehensive_data.local_government.mayor_election_2022}
                        type="시장/군수/구청장"
                      />
                    )}

                    {/* 의원선거 */}
                    {searchResults.election_results.comprehensive_data?.council_elections && (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="bg-white rounded-lg shadow-md p-4">
                          <h3 className="font-semibold text-gray-800 mb-3">🏛️ 광역의원선거</h3>
                          <p className="text-sm text-gray-600">
                            상세 선거 데이터가 캐시되어 있습니다.
                          </p>
                        </div>
                        <div className="bg-white rounded-lg shadow-md p-4">
                          <h3 className="font-semibold text-gray-800 mb-3">🏘️ 기초의원선거</h3>
                          <p className="text-sm text-gray-600">
                            상세 선거 데이터가 캐시되어 있습니다.
                          </p>
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* 메타 정보 */}
                {searchResults.meta && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="mt-6 bg-gray-50 rounded-lg p-4"
                  >
                    <h3 className="font-semibold text-gray-700 mb-2 flex items-center">
                      <InformationCircleIcon className="h-4 w-4 mr-2" />
                      검색 정보
                    </h3>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <span className="text-gray-600">응답시간:</span>
                        <span className="ml-2 font-semibold text-green-600">{searchResults.meta.response_time_ms}ms</span>
                      </div>
                      <div>
                        <span className="text-gray-600">데이터 크기:</span>
                        <span className="ml-2 font-semibold text-blue-600">{searchResults.meta.data_size_kb}KB</span>
                      </div>
                      <div>
                        <span className="text-gray-600">완성도:</span>
                        <span className="ml-2 font-semibold text-purple-600">{(searchResults.meta.data_completeness * 100).toFixed(1)}%</span>
                      </div>
                      <div>
                        <span className="text-gray-600">압축:</span>
                        <span className="ml-2 font-semibold text-orange-600">{searchResults.meta.compression}</span>
                      </div>
                    </div>
                  </motion.div>
                )}
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* 지역 선택 모달 */}
      <LocationSelectionModal
        isOpen={showLocationSelection}
        onClose={() => setShowLocationSelection(false)}
        searchTerm={searchTerm}
        options={locationOptions}
        onSelect={handleLocationSelect}
      />

      {/* 후보자 상세 모달 */}
      <AnimatePresence>
        {selectedCandidate && (
          <CandidateModal 
            candidate={selectedCandidate} 
            onClose={() => setSelectedCandidate(null)} 
          />
        )}
      </AnimatePresence>

      {/* 사용 가이드 */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="mt-8 bg-gray-50 rounded-lg p-6"
      >
        <h3 className="font-semibold text-gray-800 mb-4">📖 사용 가이드</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium text-gray-700 mb-2">🔍 검색 방법</h4>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• 읍면동 이름을 입력하세요</li>
              <li>• 예시: "읍면동_0001", "읍면동_0100"</li>
              <li>• 280MB 캐시로 0.3ms 초고속 검색</li>
              <li>• 1,580개 지역 완전 지원</li>
            </ul>
          </div>
          
          <div>
            <h4 className="font-medium text-gray-700 mb-2">📊 제공 정보</h4>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• 6개 선거 유형별 결과</li>
              <li>• 출마 후보 전원 상세 정보</li>
              <li>• 96.19% 다양성 시스템 분석</li>
              <li>• AI 예측 및 정치 동향</li>
            </ul>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default ElectionResultsWidget;
