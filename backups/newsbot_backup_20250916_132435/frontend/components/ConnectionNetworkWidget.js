import { useState, useEffect } from 'react'

const ConnectionNetworkWidget = () => {
  const [networkData, setNetworkData] = useState({ nodes: [], links: [] })
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // 네트워크 데이터 로딩 시뮬레이션
    const mockNetworkData = {
      nodes: [
        { id: '윤석열', group: 'politician', size: 20, color: '#ef4444' },
        { id: '이재명', group: 'politician', size: 18, color: '#3b82f6' },
        { id: '안철수', group: 'politician', size: 15, color: '#eab308' },
        { id: '예산안', group: 'issue', size: 12, color: '#8b5cf6' },
        { id: '국방정책', group: 'issue', size: 10, color: '#06b6d4' },
        { id: '교육개혁', group: 'issue', size: 8, color: '#10b981' }
      ],
      links: [
        { source: '윤석열', target: '예산안', strength: 0.8 },
        { source: '이재명', target: '예산안', strength: 0.6 },
        { source: '안철수', target: '교육개혁', strength: 0.7 },
        { source: '윤석열', target: '국방정책', strength: 0.5 },
        { source: '이재명', target: '국방정책', strength: 0.4 }
      ]
    }

    setTimeout(() => {
      setNetworkData(mockNetworkData)
      setIsLoading(false)
    }, 1000)
  }, [])

  const getNodeColor = (group) => {
    switch (group) {
      case 'politician':
        return 'bg-red-500'
      case 'issue':
        return 'bg-blue-500'
      default:
        return 'bg-gray-500'
    }
  }

  const getNodeSize = (size) => {
    return Math.max(8, size * 2)
  }

  if (isLoading) {
    return (
      <div className="bg-dark-800 rounded-lg p-6 border border-dark-700">
        <div className="animate-pulse">
          <div className="h-6 bg-dark-700 rounded mb-4"></div>
          <div className="h-32 bg-dark-700 rounded"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-dark-800 rounded-lg p-6 border border-dark-700">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-white flex items-center">
          <svg className="w-5 h-5 mr-2 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
          </svg>
          연결성 네트워크
        </h2>
        <span className="text-sm text-dark-400">실시간</span>
      </div>
      
      <div className="space-y-4">
        {/* 간단한 네트워크 시각화 */}
        <div className="h-32 bg-dark-700 rounded-lg p-4 relative overflow-hidden">
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="grid grid-cols-3 gap-4 w-full h-full">
              {networkData.nodes.map((node, index) => (
                <div
                  key={node.id}
                  className="flex flex-col items-center justify-center"
                  style={{ gridColumn: index % 3 + 1, gridRow: Math.floor(index / 3) + 1 }}
                >
                  <div
                    className={`w-6 h-6 rounded-full ${getNodeColor(node.group)} flex items-center justify-center text-white text-xs font-bold`}
                    style={{ width: getNodeSize(node.size), height: getNodeSize(node.size) }}
                  >
                    {node.id.charAt(0)}
                  </div>
                  <span className="text-xs text-dark-300 mt-1 text-center">
                    {node.id}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
        
        {/* 연결성 통계 */}
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-dark-700 rounded-lg p-3">
            <p className="text-xs text-dark-400 mb-1">총 노드 수</p>
            <p className="text-lg font-semibold text-white">
              {networkData.nodes.length}
            </p>
          </div>
          <div className="bg-dark-700 rounded-lg p-3">
            <p className="text-xs text-dark-400 mb-1">총 연결 수</p>
            <p className="text-lg font-semibold text-white">
              {networkData.links.length}
            </p>
          </div>
        </div>
        
        {/* 노드 유형별 분포 */}
        <div className="bg-dark-700 rounded-lg p-3">
          <p className="text-xs text-dark-400 mb-2">노드 유형</p>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                <span className="text-sm text-white">정치인</span>
              </div>
              <span className="text-sm text-dark-400">
                {networkData.nodes.filter(n => n.group === 'politician').length}개
              </span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                <span className="text-sm text-white">이슈</span>
              </div>
              <span className="text-sm text-dark-400">
                {networkData.nodes.filter(n => n.group === 'issue').length}개
              </span>
            </div>
          </div>
        </div>
        
        {/* 최근 연결성 변화 */}
        <div className="bg-dark-700 rounded-lg p-3">
          <p className="text-xs text-dark-400 mb-2">최근 변화</p>
          <div className="flex items-center space-x-2">
            <svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 17l9.2-9.2M17 17V7H7" />
            </svg>
            <span className="text-sm text-white">
              새로운 연결 3개 발견
            </span>
          </div>
        </div>
      </div>
      
      <div className="mt-4 pt-4 border-t border-dark-700">
        <button className="w-full text-center text-sm text-purple-500 hover:text-purple-400 transition-colors">
          네트워크 확대 보기
        </button>
      </div>
    </div>
  )
}

export default ConnectionNetworkWidget
