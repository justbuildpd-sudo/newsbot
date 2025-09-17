import React, { useState, useEffect } from 'react'

const PoliticianEvaluationWidget = () => {
  const [rankingData, setRankingData] = useState(null)
  const [partyStats, setPartyStats] = useState(null)
  const [scoreDistribution, setScoreDistribution] = useState(null)
  const [selectedPolitician, setSelectedPolitician] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selectedParty, setSelectedParty] = useState('all')

  useEffect(() => {
    fetchEvaluationData()
  }, [selectedParty])

  const fetchEvaluationData = async () => {
    try {
      setLoading(true)
      
      // 랭킹 데이터
      const rankingResponse = await fetch(
        `http://localhost:8000/api/evaluation/ranking?limit=20&party=${selectedParty === 'all' ? '' : selectedParty}`
      )
      const rankingData = await rankingResponse.json()
      setRankingData(rankingData.data)

      // 정당 통계
      const partyResponse = await fetch('http://localhost:8000/api/evaluation/party-stats')
      const partyData = await partyResponse.json()
      setPartyStats(partyData.data)

      // 점수 분포
      const distributionResponse = await fetch('http://localhost:8000/api/evaluation/score-distribution')
      const distributionData = await distributionResponse.json()
      setScoreDistribution(distributionData.data)

    } catch (err) {
      setError('평가 데이터를 불러올 수 없습니다.')
    } finally {
      setLoading(false)
    }
  }

  const fetchPoliticianDetail = async (politicianName) => {
    try {
      const response = await fetch(`http://localhost:8000/api/evaluation/politician/${encodeURIComponent(politicianName)}`)
      const data = await response.json()
      if (data.success) {
        setSelectedPolitician(data.data)
      }
    } catch (err) {
      setError('정치인 상세 정보를 불러올 수 없습니다.')
    }
  }

  const getScoreColor = (score) => {
    if (score >= 8) return 'text-green-500'
    if (score >= 6) return 'text-blue-500'
    if (score >= 4) return 'text-yellow-500'
    if (score >= 2) return 'text-orange-500'
    return 'text-red-500'
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
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
          </svg>
          정치인 종합 평가
        </h2>
        <div className="flex items-center space-x-2">
          <select 
            value={selectedParty} 
            onChange={(e) => setSelectedParty(e.target.value)}
            className="bg-dark-700 text-white px-3 py-1 rounded text-sm"
          >
            <option value="all">전체</option>
            <option value="국민의힘">국민의힘</option>
            <option value="더불어민주당">더불어민주당</option>
            <option value="정의당">정의당</option>
            <option value="개혁신당">개혁신당</option>
          </select>
        </div>
      </div>

      {/* 정당별 통계 */}
      {partyStats && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-white mb-4">정당별 평균 점수</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {partyStats.party_statistics.map((party, index) => (
              <div key={index} className="bg-dark-700 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center">
                    <div className={`w-3 h-3 rounded-full mr-2 ${getPartyColor(party.party)}`}></div>
                    <span className="text-white font-medium">{party.party}</span>
                  </div>
                  <span className="text-sm text-gray-400">{party.count}명</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-400">평균 점수</span>
                  <span className={`text-lg font-bold ${getScoreColor(party.avg_score)}`}>
                    {party.avg_score}
                  </span>
                </div>
                <div className="mt-2">
                  <div className="flex justify-between text-xs text-gray-400">
                    <span>최고: {party.max_score}</span>
                    <span>최저: {party.min_score}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 정치인 랭킹 */}
      {rankingData && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-white mb-4">정치인 랭킹</h3>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {rankingData.politicians.map((politician, index) => (
              <div 
                key={index}
                className="flex items-center justify-between bg-dark-700 rounded-lg p-3 cursor-pointer hover:bg-dark-600 transition-colors"
                onClick={() => fetchPoliticianDetail(politician.name)}
              >
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center text-white font-bold text-sm">
                    {politician.rank}
                  </div>
                  <div>
                    <div className="text-white font-medium">{politician.name}</div>
                    <div className="text-sm text-gray-400">{politician.party} • {politician.district}</div>
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <div className="text-right">
                    <div className={`text-lg font-bold ${getScoreColor(politician.total_score)}`}>
                      {politician.total_score}
                    </div>
                    <div className="text-xs text-gray-400">총점</div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-blue-400">{politician.scores.news.mention}</div>
                    <div className="text-xs text-gray-400">뉴스</div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-green-400">{politician.scores.bill_sponsor.main}</div>
                    <div className="text-xs text-gray-400">의안</div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-purple-400">{politician.scores.connectivity.total}</div>
                    <div className="text-xs text-gray-400">연결</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 점수 분포 */}
      {scoreDistribution && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-white mb-4">점수 분포</h3>
          <div className="space-y-2">
            {scoreDistribution.distribution.map((range, index) => (
              <div key={index} className="flex items-center justify-between">
                <span className="text-white text-sm">{range.range}</span>
                <div className="flex items-center space-x-2">
                  <div className="w-32 bg-dark-700 rounded-full h-2">
                    <div 
                      className="bg-primary-500 h-2 rounded-full"
                      style={{ width: `${(range.count / scoreDistribution.statistics.total_count) * 100}%` }}
                    ></div>
                  </div>
                  <span className="text-gray-400 text-sm w-8">{range.count}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 선택된 정치인 상세 정보 */}
      {selectedPolitician && (
        <div className="mt-6 p-4 bg-dark-700 rounded-lg">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white">
              {selectedPolitician.name} 상세 평가
            </h3>
            <button 
              onClick={() => setSelectedPolitician(null)}
              className="text-gray-400 hover:text-white"
            >
              ✕
            </button>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
            <div className="text-center">
              <div className={`text-2xl font-bold ${getScoreColor(selectedPolitician.total_score)}`}>
                {selectedPolitician.total_score}
              </div>
              <div className="text-sm text-gray-400">총점</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-bold text-blue-400">
                {selectedPolitician.scores.news.mention}
              </div>
              <div className="text-sm text-gray-400">뉴스 언급</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-bold text-green-400">
                {selectedPolitician.scores.bill_sponsor.main}
              </div>
              <div className="text-sm text-gray-400">의안 발의</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-bold text-purple-400">
                {selectedPolitician.scores.connectivity.total}
              </div>
              <div className="text-sm text-gray-400">연결성</div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <h4 className="text-white font-medium mb-2">뉴스 점수</h4>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-400">언급도</span>
                  <span className="text-white">{selectedPolitician.scores.news.mention}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">감정</span>
                  <span className="text-white">{selectedPolitician.scores.news.sentiment}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">트렌드</span>
                  <span className="text-white">{selectedPolitician.scores.news.trend}</span>
                </div>
              </div>
            </div>

            <div>
              <h4 className="text-white font-medium mb-2">의안 점수</h4>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-400">대표발의</span>
                  <span className="text-white">{selectedPolitician.scores.bill_sponsor.main}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">공동발의</span>
                  <span className="text-white">{selectedPolitician.scores.bill_sponsor.co}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">성공률</span>
                  <span className="text-white">{selectedPolitician.scores.bill_sponsor.success_rate}</span>
                </div>
              </div>
            </div>

            <div>
              <h4 className="text-white font-medium mb-2">연결성 점수</h4>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-400">총 연결</span>
                  <span className="text-white">{selectedPolitician.scores.connectivity.total}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">영향력</span>
                  <span className="text-white">{selectedPolitician.scores.connectivity.influence}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">협력도</span>
                  <span className="text-white">{selectedPolitician.scores.connectivity.collaboration}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default PoliticianEvaluationWidget
