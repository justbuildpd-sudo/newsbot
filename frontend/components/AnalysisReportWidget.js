import { useState, useEffect } from 'react'

const AnalysisReportWidget = () => {
  const [reportData, setReportData] = useState({})
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // 분석 리포트 데이터 로딩 시뮬레이션
    const mockReportData = {
      date: '2024-01-15',
      period: '일간',
      insights: [
        {
          title: '예산안 논의가 핫이슈로 부상',
          description: '국회 예산안 심의와 관련된 언급이 15% 증가했습니다.',
          impact: 'high',
          trend: 'up'
        },
        {
          title: '국방정책 관련 긍정적 반응 증가',
          description: '국방정책에 대한 긍정적 언급이 전주 대비 8% 증가했습니다.',
          impact: 'medium',
          trend: 'up'
        },
        {
          title: '교육개혁 논의 감소',
          description: '교육개혁 관련 언급이 전주 대비 3% 감소했습니다.',
          impact: 'low',
          trend: 'down'
        }
      ],
      predictions: [
        '예산안 논의가 다음 주까지 지속될 것으로 예상됩니다.',
        '국방정책 관련 긍정적 여론이 계속될 가능성이 높습니다.',
        '교육개혁 이슈는 새로운 정책 발표 시 다시 부상할 것으로 예상됩니다.'
      ],
      statistics: {
        totalNews: 1250,
        totalMentions: 3450,
        avgSentiment: 0.2,
        topKeyword: '예산안',
        topPolitician: '윤석열'
      }
    }

    setTimeout(() => {
      setReportData(mockReportData)
      setIsLoading(false)
    }, 1000)
  }, [])

  const getImpactColor = (impact) => {
    switch (impact) {
      case 'high':
        return 'text-red-500'
      case 'medium':
        return 'text-yellow-500'
      case 'low':
        return 'text-green-500'
      default:
        return 'text-gray-500'
    }
  }

  const getImpactLabel = (impact) => {
    switch (impact) {
      case 'high':
        return '높음'
      case 'medium':
        return '보통'
      case 'low':
        return '낮음'
      default:
        return '알 수 없음'
    }
  }

  const getTrendIcon = (trend) => {
    switch (trend) {
      case 'up':
        return (
          <svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 17l9.2-9.2M17 17V7H7" />
          </svg>
        )
      case 'down':
        return (
          <svg className="w-4 h-4 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 7l-9.2 9.2M7 7v10h10" />
          </svg>
        )
      default:
        return (
          <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
          </svg>
        )
    }
  }

  if (isLoading) {
    return (
      <div className="bg-dark-800 rounded-lg p-6 border border-dark-700">
        <div className="animate-pulse">
          <div className="h-6 bg-dark-700 rounded mb-4"></div>
          <div className="space-y-3">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="space-y-2">
                <div className="h-4 bg-dark-700 rounded"></div>
                <div className="h-3 bg-dark-700 rounded w-3/4"></div>
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
          <svg className="w-5 h-5 mr-2 text-orange-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          분석 리포트
        </h2>
        <span className="text-sm text-dark-400">{reportData.period}</span>
      </div>
      
      <div className="space-y-4">
        {/* 주요 인사이트 */}
        <div>
          <h3 className="text-sm font-semibold text-white mb-3">주요 인사이트</h3>
          <div className="space-y-3">
            {reportData.insights?.map((insight, index) => (
              <div key={index} className="bg-dark-700 rounded-lg p-3">
                <div className="flex items-start justify-between mb-2">
                  <h4 className="text-sm font-medium text-white line-clamp-1">
                    {insight.title}
                  </h4>
                  <div className="flex items-center space-x-1">
                    {getTrendIcon(insight.trend)}
                    <span className={`text-xs font-medium ${getImpactColor(insight.impact)}`}>
                      {getImpactLabel(insight.impact)}
                    </span>
                  </div>
                </div>
                <p className="text-xs text-dark-300 line-clamp-2">
                  {insight.description}
                </p>
              </div>
            ))}
          </div>
        </div>
        
        {/* 예측 분석 */}
        <div>
          <h3 className="text-sm font-semibold text-white mb-3">예측 분석</h3>
          <div className="bg-dark-700 rounded-lg p-3">
            <ul className="space-y-2">
              {reportData.predictions?.map((prediction, index) => (
                <li key={index} className="flex items-start space-x-2">
                  <div className="w-1.5 h-1.5 bg-orange-500 rounded-full mt-2 flex-shrink-0"></div>
                  <span className="text-xs text-dark-300">
                    {prediction}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        </div>
        
        {/* 통계 요약 */}
        <div>
          <h3 className="text-sm font-semibold text-white mb-3">통계 요약</h3>
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-dark-700 rounded-lg p-3">
              <p className="text-xs text-dark-400 mb-1">총 뉴스</p>
              <p className="text-lg font-semibold text-white">
                {reportData.statistics?.totalNews?.toLocaleString()}
              </p>
            </div>
            <div className="bg-dark-700 rounded-lg p-3">
              <p className="text-xs text-dark-400 mb-1">총 언급</p>
              <p className="text-lg font-semibold text-white">
                {reportData.statistics?.totalMentions?.toLocaleString()}
              </p>
            </div>
            <div className="bg-dark-700 rounded-lg p-3">
              <p className="text-xs text-dark-400 mb-1">평균 감정</p>
              <p className="text-lg font-semibold text-white">
                {reportData.statistics?.avgSentiment?.toFixed(2)}
              </p>
            </div>
            <div className="bg-dark-700 rounded-lg p-3">
              <p className="text-xs text-dark-400 mb-1">핫 키워드</p>
              <p className="text-lg font-semibold text-white">
                {reportData.statistics?.topKeyword}
              </p>
            </div>
          </div>
        </div>
      </div>
      
      <div className="mt-4 pt-4 border-t border-dark-700">
        <div className="flex space-x-2">
          <button className="flex-1 text-center text-sm text-orange-500 hover:text-orange-400 transition-colors">
            PDF 다운로드
          </button>
          <button className="flex-1 text-center text-sm text-orange-500 hover:text-orange-400 transition-colors">
            상세 보기
          </button>
        </div>
      </div>
    </div>
  )
}

export default AnalysisReportWidget
