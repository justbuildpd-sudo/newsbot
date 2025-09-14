import { useState, useEffect } from 'react'

const PoliticianProfileWidget = () => {
  const [politicians, setPoliticians] = useState([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // 정치인 데이터 로딩 시뮬레이션
    const mockPoliticians = [
      {
        id: 1,
        name: "윤석열",
        party: "국민의힘",
        position: "대통령",
        mentionCount: 1250,
        sentiment: 0.3,
        recentStatement: "경제 회복을 위한 정책을 추진하겠습니다."
      },
      {
        id: 2,
        name: "이재명",
        party: "더불어민주당",
        position: "대표",
        mentionCount: 980,
        sentiment: -0.1,
        recentStatement: "정부의 정책에 대해 우려를 표명합니다."
      },
      {
        id: 3,
        name: "안철수",
        party: "국민의당",
        position: "대표",
        mentionCount: 720,
        sentiment: 0.1,
        recentStatement: "새로운 정치를 제안합니다."
      },
      {
        id: 4,
        name: "조국",
        party: "더불어민주당",
        position: "의원",
        mentionCount: 650,
        sentiment: -0.2,
        recentStatement: "법무정책 개혁이 필요합니다."
      }
    ]

    setTimeout(() => {
      setPoliticians(mockPoliticians)
      setIsLoading(false)
    }, 1000)
  }, [])

  const getSentimentColor = (sentiment) => {
    if (sentiment > 0.2) return 'text-green-500'
    if (sentiment < -0.2) return 'text-red-500'
    return 'text-yellow-500'
  }

  const getSentimentLabel = (sentiment) => {
    if (sentiment > 0.2) return '긍정'
    if (sentiment < -0.2) return '부정'
    return '중립'
  }

  const getPartyColor = (party) => {
    const colors = {
      '국민의힘': 'bg-red-100 text-red-800',
      '더불어민주당': 'bg-blue-100 text-blue-800',
      '국민의당': 'bg-yellow-100 text-yellow-800',
      '정의당': 'bg-green-100 text-green-800'
    }
    return colors[party] || 'bg-gray-100 text-gray-800'
  }

  if (isLoading) {
    return (
      <div className="bg-dark-800 rounded-lg p-6 border border-dark-700">
        <div className="animate-pulse">
          <div className="h-6 bg-dark-700 rounded mb-4"></div>
          <div className="space-y-3">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-dark-700 rounded-full"></div>
                <div className="flex-1 space-y-2">
                  <div className="h-4 bg-dark-700 rounded"></div>
                  <div className="h-3 bg-dark-700 rounded w-2/3"></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-dark-800 rounded-lg p-6 border border-dark-700">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-white flex items-center">
          <svg className="w-5 h-5 mr-2 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
          정치인 프로필
        </h2>
        <span className="text-sm text-dark-400">실시간</span>
      </div>
      
      <div className="space-y-4">
        {politicians.map((politician) => (
          <div key={politician.id} className="bg-dark-700 rounded-lg p-4 hover:bg-dark-600 transition-colors cursor-pointer">
            <div className="flex items-start space-x-3">
              {/* 프로필 이미지 */}
              <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-primary-700 rounded-full flex items-center justify-center text-white font-bold text-lg">
                {politician.name.charAt(0)}
              </div>
              
              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-2 mb-1">
                  <h3 className="text-sm font-semibold text-white truncate">
                    {politician.name}
                  </h3>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPartyColor(politician.party)}`}>
                    {politician.party}
                  </span>
                </div>
                
                <p className="text-xs text-dark-400 mb-2">
                  {politician.position}
                </p>
                
                <p className="text-xs text-dark-300 line-clamp-2 mb-3">
                  "{politician.recentStatement}"
                </p>
                
                <div className="flex items-center justify-between text-xs">
                  <div className="flex items-center space-x-4">
                    <span className="text-dark-400">
                      언급 {politician.mentionCount.toLocaleString()}회
                    </span>
                    <span className={`font-medium ${getSentimentColor(politician.sentiment)}`}>
                      {getSentimentLabel(politician.sentiment)}
                    </span>
                  </div>
                  <button className="text-primary-500 hover:text-primary-400 transition-colors">
                    자세히 →
                  </button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
      
      <div className="mt-4 pt-4 border-t border-dark-700">
        <button className="w-full text-center text-sm text-blue-500 hover:text-blue-400 transition-colors">
          모든 정치인 보기
        </button>
      </div>
    </div>
  )
}

export default PoliticianProfileWidget
