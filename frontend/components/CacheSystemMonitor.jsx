import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  CpuChipIcon, 
  CircleStackIcon, 
  ClockIcon, 
  ChartBarIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';

const CacheSystemMonitor = () => {
  const [cacheStats, setCacheStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(null);

  const fetchCacheStats = async () => {
    try {
      const response = await fetch('/api/cache/stats');
      const data = await response.json();
      
      if (data.success) {
        setCacheStats(data.cache_statistics);
        setLastUpdate(new Date());
      }
    } catch (error) {
      console.error('캐시 통계 조회 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCacheStats();
    
    // 30초마다 자동 업데이트
    const interval = setInterval(fetchCacheStats, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="space-y-3">
            <div className="h-3 bg-gray-200 rounded"></div>
            <div className="h-3 bg-gray-200 rounded w-5/6"></div>
          </div>
        </div>
      </div>
    );
  }

  if (!cacheStats) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex items-center">
          <ExclamationTriangleIcon className="h-5 w-5 text-red-500 mr-2" />
          <span className="text-red-800">캐시 시스템 통계를 불러올 수 없습니다</span>
        </div>
      </div>
    );
  }

  const achievement = cacheStats.final_cache_achievement || {};
  const breakdown = cacheStats.cache_breakdown || {};
  const density = cacheStats.data_density || {};
  const performance = cacheStats.performance_metrics || {};

  const getUtilizationColor = (percentage) => {
    if (percentage >= 90) return 'text-green-600 bg-green-100';
    if (percentage >= 70) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getUtilizationIcon = (percentage) => {
    if (percentage >= 90) return <CheckCircleIcon className="h-5 w-5" />;
    return <ExclamationTriangleIcon className="h-5 w-5" />;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-lg shadow-md p-6"
    >
      {/* 헤더 */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-gray-800 flex items-center">
          <CpuChipIcon className="h-6 w-6 mr-2 text-blue-500" />
          280MB 캐시 시스템 모니터
        </h2>
        {lastUpdate && (
          <span className="text-sm text-gray-500 flex items-center">
            <ClockIcon className="h-4 w-4 mr-1" />
            {lastUpdate.toLocaleTimeString()}
          </span>
        )}
      </div>

      {/* 주요 지표 */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <motion.div
          whileHover={{ scale: 1.05 }}
          className="bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg p-4"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-600 font-medium text-sm">총 사용량</p>
              <p className="text-2xl font-bold text-blue-800">
                {achievement.total_mb || 0}MB
              </p>
            </div>
            <CircleStackIcon className="h-8 w-8 text-blue-500" />
          </div>
          <div className="mt-2">
            <div className="w-full bg-blue-200 rounded-full h-2">
              <div 
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${Math.min(achievement.utilization_percentage || 0, 100)}%` }}
              ></div>
            </div>
            <p className="text-xs text-blue-600 mt-1">
              목표: {achievement.target_mb || 280}MB
            </p>
          </div>
        </motion.div>

        <motion.div
          whileHover={{ scale: 1.05 }}
          className={`rounded-lg p-4 ${getUtilizationColor(achievement.utilization_percentage || 0)}`}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-sm">사용률</p>
              <p className="text-2xl font-bold">
                {achievement.utilization_percentage?.toFixed(1) || 0}%
              </p>
            </div>
            {getUtilizationIcon(achievement.utilization_percentage || 0)}
          </div>
          <p className="text-xs mt-2">
            {achievement.target_achieved ? '✅ 목표 달성' : '⚠️ 목표 미달'}
          </p>
        </motion.div>

        <motion.div
          whileHover={{ scale: 1.05 }}
          className="bg-gradient-to-r from-green-50 to-green-100 rounded-lg p-4"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-600 font-medium text-sm">캐시된 지역</p>
              <p className="text-2xl font-bold text-green-800">
                {density.regions_cached || 0}개
              </p>
            </div>
            <ChartBarIcon className="h-8 w-8 text-green-500" />
          </div>
          <p className="text-xs text-green-600 mt-2">
            평균 {density.avg_size_per_region_kb || 0}KB/지역
          </p>
        </motion.div>

        <motion.div
          whileHover={{ scale: 1.05 }}
          className="bg-gradient-to-r from-purple-50 to-purple-100 rounded-lg p-4"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-600 font-medium text-sm">히트율</p>
              <p className="text-2xl font-bold text-purple-800">
                {performance.hit_rate?.toFixed(1) || 0}%
              </p>
            </div>
            <ClockIcon className="h-8 w-8 text-purple-500" />
          </div>
          <p className="text-xs text-purple-600 mt-2">
            총 {performance.total_requests || 0}회 요청
          </p>
        </motion.div>
      </div>

      {/* 상세 통계 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* 캐시 구성 */}
        <div>
          <h3 className="font-semibold text-gray-800 mb-3">📊 캐시 구성</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <span className="text-gray-700">지역 데이터</span>
              <span className="font-semibold text-blue-600">
                {breakdown.regional_data_mb || 0}MB
              </span>
            </div>
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <span className="text-gray-700">후보자 데이터</span>
              <span className="font-semibold text-green-600">
                {breakdown.candidate_data_mb || 0}MB
              </span>
            </div>
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <span className="text-gray-700">선거 데이터</span>
              <span className="font-semibold text-purple-600">
                {breakdown.election_data_mb || 0}MB
              </span>
            </div>
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <span className="text-gray-700">메타데이터</span>
              <span className="font-semibold text-orange-600">
                {breakdown.metadata_mb || 0}MB
              </span>
            </div>
          </div>
        </div>

        {/* 시스템 기능 */}
        <div>
          <h3 className="font-semibold text-gray-800 mb-3">⚡ 시스템 기능</h3>
          <div className="space-y-3">
            <div className="flex items-center p-3 bg-green-50 rounded-lg">
              <CheckCircleIcon className="h-5 w-5 text-green-500 mr-3" />
              <div>
                <p className="font-medium text-green-800">읍면동별 선거결과</p>
                <p className="text-sm text-green-600">6개 선거 유형 완전 지원</p>
              </div>
            </div>
            <div className="flex items-center p-3 bg-blue-50 rounded-lg">
              <CheckCircleIcon className="h-5 w-5 text-blue-500 mr-3" />
              <div>
                <p className="font-medium text-blue-800">출마 후보 상세 정보</p>
                <p className="text-sm text-blue-600">공약, 경력, 정책 입장 포함</p>
              </div>
            </div>
            <div className="flex items-center p-3 bg-purple-50 rounded-lg">
              <CheckCircleIcon className="h-5 w-5 text-purple-500 mr-3" />
              <div>
                <p className="font-medium text-purple-800">96.19% 다양성 시스템</p>
                <p className="text-sm text-purple-600">19차원 완전 분석</p>
              </div>
            </div>
            <div className="flex items-center p-3 bg-yellow-50 rounded-lg">
              <CheckCircleIcon className="h-5 w-5 text-yellow-500 mr-3" />
              <div>
                <p className="font-medium text-yellow-800">0.3ms 초고속 검색</p>
                <p className="text-sm text-yellow-600">Raw JSON 직접 제공</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 새로고침 버튼 */}
      <div className="mt-6 text-center">
        <button
          onClick={fetchCacheStats}
          className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 text-sm"
        >
          🔄 통계 새로고침
        </button>
      </div>
    </motion.div>
  );
};

export default CacheSystemMonitor;
