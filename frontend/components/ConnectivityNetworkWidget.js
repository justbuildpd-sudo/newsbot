import React, { useState, useEffect } from 'react'

const ConnectivityNetworkWidget = () => {
  const [networkData, setNetworkData] = useState(null)
  const [stats, setStats] = useState(null)
  const [selectedPolitician, setSelectedPolitician] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchNetworkData()
    fetchStats()
  }, [])

  const fetchNetworkData = async () => {
    try {
      const response = await fetch('http://localhost:8002/api/connectivity/network?limit=50')
      const data = await response.json()
      if (data.success) {
        setNetworkData(data.data)
      }
    } catch (err) {
      setError('네트워크 데이터를 불러올 수 없습니다.')
    }
  }

  const fetchStats = async () => {
    try {
      const response = await fetch('http://localhost:8002/api/connectivity/stats')
      const data = await response.json()
      if (data.success) {
        setStats(data.data)
      }
    } catch (err) {
      setError('통계 데이터를 불러올 수 없습니다.')
    } finally {
      setLoading(false)
    }
  }

  const fetchPoliticianConnections = async (politicianName) => {
    try {
      const response = await fetch(`http://localhost:8002/api/connectivity/politician/${encodeURIComponent(politicianName)}`)
      const data = await response.json()
      if (data.success) {
        setSelectedPolitician(data.data)
      }
    } catch (err) {
      setError('정치인 연결 정보를 불러올 수 없습니다.')
    }
  }

  const getPartyColor = (party) => {
    const colors = {
      '국민의힘': 'bg-red-500',
      '더불어민주당': 'bg-blue-500',
      '정의당': 'bg-green-500',
      '개혁신당': 'bg-purple-500',
      '정당정보없음': 'bg-gray-500'
    }
    return colors[party] || 'bg-gray-400'
  }

  if (loading) {
    return (
      <div className="widget bg-dark-800 rounded-lg p-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="widget bg-dark-800 rounded-lg p-6">
        <div className="text-center text-red-400">
          <p>{error}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="widget bg-dark-800 rounded-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-white flex items-center">
          <svg className="w-6 h-6 mr-2 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"></path>
          </svg>
          정치인 연결성 네트워크
        </h2>
        <div className="text-sm text-gray-400">
          {stats?.total_connections.toLocaleString()}개 연결
        </div>
      </div>

      {/* 통계 요약 */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-dark-700 rounded-lg p-4">
            <div className="text-2xl font-bold text-white">{stats.total_politicians}</div>
            <div className="text-sm text-gray-400">총 정치인</div>
          </div>
          <div className="bg-dark-700 rounded-lg p-4">
            <div className="text-2xl font-bold text-primary-500">{stats.total_connections.toLocaleString()}</div>
            <div className="text-sm text-gray-400">총 연결</div>
          </div>
          <div className="bg-dark-700 rounded-lg p-4">
            <div className="text-2xl font-bold text-green-500">{stats.connection_types.find(t => t.type === 'party')?.count || 0}</div>
            <div className="text-sm text-gray-400">정당 연결</div>
          </div>
          <div className="bg-dark-700 rounded-lg p-4">
            <div className="text-2xl font-bold text-blue-500">{stats.connection_types.find(t => t.type === 'district')?.count || 0}</div>
            <div className="text-sm text-gray-400">지역구 연결</div>
          </div>
        </div>
      )}

      {/* 정당별 연결성 */}
      {stats?.party_connections && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-white mb-4">정당별 연결성</h3>
          <div className="space-y-3">
            {stats.party_connections.map((party, index) => (
              <div key={index} className="flex items-center justify-between bg-dark-700 rounded-lg p-3">
                <div className="flex items-center">
                  <div className={`w-4 h-4 rounded-full mr-3 ${getPartyColor(party.party)}`}></div>
                  <span className="text-white font-medium">{party.party}</span>
                </div>
                <div className="text-primary-500 font-bold">{party.connections.toLocaleString()}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 가장 연결성이 높은 정치인 */}
      {stats?.top_connected && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-white mb-4">가장 연결성이 높은 정치인</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {stats.top_connected.slice(0, 6).map((politician, index) => (
              <div 
                key={index} 
                className="flex items-center justify-between bg-dark-700 rounded-lg p-3 cursor-pointer hover:bg-dark-600 transition-colors"
                onClick={() => fetchPoliticianConnections(politician.name)}
              >
                <div className="flex items-center">
                  <div className="w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center text-white font-bold text-sm mr-3">
                    {index + 1}
                  </div>
                  <span className="text-white font-medium">{politician.name}</span>
                </div>
                <div className="text-primary-500 font-bold">{politician.connections}개</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 선택된 정치인의 연결 정보 */}
      {selectedPolitician && (
        <div className="mt-6 p-4 bg-dark-700 rounded-lg">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white">
              {selectedPolitician.politician.name}의 연결 정보
            </h3>
            <button 
              onClick={() => setSelectedPolitician(null)}
              className="text-gray-400 hover:text-white"
            >
              ✕
            </button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <div className="text-sm text-gray-400 mb-2">정당</div>
              <div className="text-white">{selectedPolitician.politician.party}</div>
            </div>
            <div>
              <div className="text-sm text-gray-400 mb-2">지역구</div>
              <div className="text-white">{selectedPolitician.politician.district}</div>
            </div>
            <div>
              <div className="text-sm text-gray-400 mb-2">소속 위원회</div>
              <div className="text-white">{selectedPolitician.politician.committee || '정보없음'}</div>
            </div>
            <div>
              <div className="text-sm text-gray-400 mb-2">총 연결 수</div>
              <div className="text-primary-500 font-bold">{selectedPolitician.total_connections}개</div>
            </div>
          </div>
          
          {selectedPolitician.connections.length > 0 && (
            <div className="mt-4">
              <div className="text-sm text-gray-400 mb-2">주요 연결</div>
              <div className="space-y-2 max-h-40 overflow-y-auto">
                {selectedPolitician.connections.slice(0, 10).map((conn, index) => (
                  <div key={index} className="flex items-center justify-between text-sm">
                    <span className="text-white">{conn.name}</span>
                    <div className="flex items-center space-x-2">
                      <span className="text-gray-400">{conn.type}</span>
                      <span className="text-primary-500 font-bold">{conn.strength}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* 패밀리트리 이미지 */}
      <div className="mt-6">
        <h3 className="text-lg font-semibold text-white mb-4">패밀리트리 시각화</h3>
        <div className="bg-dark-700 rounded-lg p-4 text-center">
          <img 
            src="http://localhost:8002/api/connectivity/family-tree" 
            alt="패밀리트리 네트워크"
            className="max-w-full h-auto rounded-lg"
            onError={(e) => {
              e.target.style.display = 'none'
              e.target.nextSibling.style.display = 'block'
            }}
          />
          <div style={{display: 'none'}} className="text-gray-400">
            패밀리트리 이미지를 불러올 수 없습니다.
          </div>
        </div>
      </div>
    </div>
  )
}

export default ConnectivityNetworkWidget