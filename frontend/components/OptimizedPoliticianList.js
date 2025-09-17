import { useState, useEffect, useMemo } from 'react'
import useOptimizedData from '../hooks/useOptimizedData'

const OptimizedPoliticianList = ({ onSelectPolitician }) => {
  const [currentPage, setCurrentPage] = useState(0)
  const [photoMapping, setPhotoMapping] = useState({})
  const itemsPerPage = 20

  // 최적화된 데이터 훅 사용
  const { 
    data: { politicians, billScores }, 
    loading, 
    errors, 
    isLoading,
    refreshData,
    cacheStats
  } = useOptimizedData()

  useEffect(() => {
    loadPhotoMapping()
  }, [])

  const loadPhotoMapping = async () => {
    try {
      const response = await fetch('/politician_photos.json')
      const mapping = await response.json()
      setPhotoMapping(mapping)
      console.log('✅ 사진 매핑 로드:', Object.keys(mapping).length + '명')
    } catch (error) {
      console.error('사진 매핑 로드 실패:', error)
    }
  }

  // 페이징된 정치인 목록 (메모이제이션)
  const paginatedPoliticians = useMemo(() => {
    if (!politicians || politicians.length === 0) return []
    
    const startIdx = currentPage * itemsPerPage
    const endIdx = startIdx + itemsPerPage
    return politicians.slice(startIdx, endIdx)
  }, [politicians, currentPage, itemsPerPage])

  // 발의안 점수 가져오기 (메모이제이션)
  const getBillScore = useMemo(() => {
    return (memberName) => {
      return billScores[memberName] || { main_proposals: 0, co_proposals: 0, total_bills: 0 }
    }
  }, [billScores])

  const getPartyColor = (party) => {
    const colors = {
      '더불어민주당': 'bg-blue-500 text-white',
      '국민의힘': 'bg-red-500 text-white', 
      '조국혁신당': 'bg-purple-500 text-white',
      '개혁신당': 'bg-green-500 text-white',
      '진보당': 'bg-pink-500 text-white',
      '국민의미래': 'bg-teal-500 text-white',
      '더불어민주연합': 'bg-cyan-500 text-white',
      '새로운미래': 'bg-lime-500 text-white'
    }
    return colors[party] || 'bg-gray-500 text-white'
  }

  const handleLoadMore = () => {
    setCurrentPage(prev => prev + 1)
  }

  const hasMore = politicians && (currentPage + 1) * itemsPerPage < politicians.length

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">국회의원 현황</h2>
          <div className="flex items-center space-x-2 text-sm text-gray-500">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
            <span>최적화된 로딩 중...</span>
          </div>
        </div>
        
        <div className="space-y-3">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="animate-pulse">
              <div className="flex items-center space-x-4 p-3">
                <div className="w-12 h-12 bg-gray-200 rounded-full"></div>
                <div className="flex-1">
                  <div className="h-4 bg-gray-200 rounded mb-2"></div>
                  <div className="h-3 bg-gray-200 rounded w-3/4"></div>
                </div>
                <div className="w-20 h-8 bg-gray-200 rounded"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (errors.politicians) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold mb-4">국회의원 현황</h2>
        <div className="text-center py-8">
          <div className="text-red-500 mb-2">
            <svg className="h-12 w-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <p className="text-red-500 text-sm">{errors.politicians}</p>
          <button 
            onClick={() => refreshData('politicians')}
            className="mt-2 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            다시 시도
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold">국회의원 현황</h2>
        <div className="flex items-center space-x-4">
          {/* 캐시 상태 표시 */}
          <div className="text-xs text-green-600">
            ⚡ 캐시 최적화 ({cacheStats.size}개 항목)
          </div>
          <div className="text-sm text-gray-500">
            총 {politicians?.length || 0}명
          </div>
          <button 
            onClick={() => refreshData('politicians')}
            className="text-blue-600 hover:text-blue-800 text-sm"
          >
            🔄 새로고침
          </button>
        </div>
      </div>

      {/* 정치인 목록 */}
      <div className="space-y-3">
        {paginatedPoliticians.map((politician, index) => {
          const billScore = getBillScore(politician.name)
          
          return (
            <div
              key={`${politician.name}-${index}`}
              className="flex items-center space-x-4 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors cursor-pointer"
              onClick={() => onSelectPolitician && onSelectPolitician(politician.name)}
            >
              {/* 프로필 영역 */}
              <div className="flex-shrink-0">
                <div className={`w-12 h-12 rounded-full overflow-hidden flex items-center justify-center text-sm font-bold ${getPartyColor(politician.party)}`}>
                  {photoMapping[politician.name] ? (
                    <img 
                      src={photoMapping[politician.name]} 
                      alt={politician.name}
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        e.target.style.display = 'none'
                        e.target.parentElement.textContent = politician.name[0]
                      }}
                    />
                  ) : (
                    politician.name[0]
                  )}
                </div>
              </div>
              
              {/* 정보 영역 */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-2 mb-1">
                  <h3 className="font-semibold text-gray-900 truncate">{politician.name}</h3>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getPartyColor(politician.party)}`}>
                    {politician.party}
                  </span>
                </div>
                <div className="text-sm text-gray-600">
                  <p className="truncate">{politician.district || '비례대표'}</p>
                  {politician.committee && (
                    <p className="truncate text-xs">{politician.committee}</p>
                  )}
                </div>
              </div>

              {/* 발의의안 점수 영역 */}
              <div className="flex-shrink-0 text-right">
                <div className="text-xs text-gray-500 mb-1">발의의안</div>
                <div className="flex items-center space-x-2">
                  <div className="text-center">
                    <div className="text-sm font-bold text-blue-600">{billScore.main_proposals}</div>
                    <div className="text-xs text-gray-400">대표</div>
                  </div>
                  <div className="text-center">
                    <div className="text-sm font-bold text-purple-600">{billScore.co_proposals}</div>
                    <div className="text-xs text-gray-400">공동</div>
                  </div>
                  <div className="text-center">
                    <div className="text-sm font-bold text-green-600">{billScore.total_bills}</div>
                    <div className="text-xs text-gray-400">총계</div>
                  </div>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* 더 보기 버튼 */}
      {hasMore && (
        <div className="mt-6 text-center">
          <button
            onClick={handleLoadMore}
            disabled={isLoadingMore}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoadingMore ? (
              <div className="flex items-center space-x-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                <span>로딩 중...</span>
              </div>
            ) : (
              `더 보기 (${politicians?.length - (currentPage + 1) * itemsPerPage}명 남음)`
            )}
          </button>
        </div>
      )}

      {/* 성능 정보 (개발 모드) */}
      {process.env.NODE_ENV === 'development' && (
        <div className="mt-4 p-2 bg-gray-100 rounded text-xs text-gray-600">
          ⚡ 성능 정보: 캐시 {cacheStats.size}개 | 
          로딩 상태: {Object.entries(loading).filter(([_, isLoading]) => isLoading).map(([key]) => key).join(', ') || '없음'}
        </div>
      )}
    </div>
  )
}

export default OptimizedPoliticianList
