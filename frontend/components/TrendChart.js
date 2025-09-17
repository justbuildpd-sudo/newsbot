import { useState, useEffect } from 'react'
import { Line } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'

// Chart.js 등록
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
)

const TrendChart = () => {
  const [chartData, setChartData] = useState(null)
  const [ranking, setRanking] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    loadTrendData()
  }, [])

  const loadTrendData = async () => {
    try {
      setLoading(true)
      setError(null)
      
      // 병렬로 트렌드 데이터 로드
      const [chartResponse, rankingResponse] = await Promise.all([
        fetch('https://newsbot-backend-6j3p.onrender.com/api/trends/chart'),
        fetch('https://newsbot-backend-6j3p.onrender.com/api/trends/ranking')
      ])
      
      // 차트 데이터 처리
      if (chartResponse.ok) {
        const chartResult = await chartResponse.json()
        if (chartResult.success) {
          setChartData(chartResult.data)
          console.log('✅ 트렌드 차트 데이터 로드 완료')
        } else {
          throw new Error('차트 데이터 로드 실패')
        }
      } else {
        throw new Error(`차트 API 오류: ${chartResponse.status}`)
      }
      
      // 랭킹 데이터 처리
      if (rankingResponse.ok) {
        const rankingResult = await rankingResponse.json()
        if (rankingResult.success) {
          setRanking(rankingResult.data.ranking || [])
          console.log('✅ 트렌드 랭킹 데이터 로드 완료')
        }
      }
      
    } catch (err) {
      setError('트렌드 데이터를 불러올 수 없습니다: ' + err.message)
      console.error('Error loading trend data:', err)
      
      // 폴백 데이터
      setChartData({
        labels: ['8월 18일', '8월 25일', '9월 1일', '9월 8일', '9월 15일'],
        datasets: [
          {
            label: '이재명',
            data: [45, 52, 38, 42, 35],
            borderColor: '#3B82F6',
            backgroundColor: '#3B82F620'
          },
          {
            label: '한동훈', 
            data: [25, 28, 22, 30, 27],
            borderColor: '#EF4444',
            backgroundColor: '#EF444420'
          },
          {
            label: '조국',
            data: [15, 20, 18, 25, 22],
            borderColor: '#8B5CF6',
            backgroundColor: '#8B5CF620'
          }
        ]
      })
      
      setRanking([
        {rank: 1, politician: '이재명', party: '더불어민주당', average_search: 42.4, trend_direction: 'falling'},
        {rank: 2, politician: '한동훈', party: '국민의힘', average_search: 26.4, trend_direction: 'stable'},
        {rank: 3, politician: '조국', party: '조국혁신당', average_search: 20.0, trend_direction: 'rising'}
      ])
      
    } finally {
      setLoading(false)
    }
  }

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: '정치인 검색량 트렌드 (최근 30일)',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: '검색량 지수'
        }
      },
      x: {
        title: {
          display: true,
          text: '날짜'
        }
      }
    },
    interaction: {
      mode: 'index',
      intersect: false,
    },
    elements: {
      point: {
        radius: 4,
        hoverRadius: 6
      }
    }
  }

  const getTrendIcon = (direction) => {
    switch (direction) {
      case 'rising':
        return '📈'
      case 'falling':
        return '📉'
      default:
        return '➡️'
    }
  }

  const getTrendColor = (direction) => {
    switch (direction) {
      case 'rising':
        return 'text-green-600'
      case 'falling':
        return 'text-red-600'
      default:
        return 'text-gray-600'
    }
  }

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold mb-4">트렌드 차트</h2>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold mb-4">트렌드 차트</h2>
        <div className="text-center py-8">
          <div className="text-red-500 mb-2">
            <svg className="h-12 w-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <p className="text-red-500 text-sm">{error}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold">트렌드 차트</h2>
        <div className="flex items-center space-x-2 text-sm text-gray-500">
          <span>📊 네이버 데이터랩</span>
          <span>•</span>
          <span>실시간</span>
        </div>
      </div>

      {/* 차트 영역 */}
      {chartData && (
        <div className="mb-6">
          <div className="h-64">
            <Line data={chartData} options={chartOptions} />
          </div>
        </div>
      )}

      {/* 트렌드 랭킹 */}
      {ranking.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold mb-4">🏆 검색량 랭킹</h3>
          <div className="space-y-3">
            {ranking.map((item, index) => (
              <div key={item.politician} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-sm font-bold text-blue-600">
                    {item.rank}
                  </div>
                  <div>
                    <div className="font-medium">{item.politician}</div>
                    <div className="text-sm text-gray-500">{item.party}</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-semibold">{item.average_search?.toFixed(2) || '0.00'}</div>
                  <div className={`text-sm ${getTrendColor(item.trend_direction)}`}>
                    {getTrendIcon(item.trend_direction)} {item.trend_direction}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 데이터 소스 표시 */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <p className="text-xs text-gray-500 text-center">
          데이터 제공: 네이버 뉴스 API + 네이버 데이터랩 검색어 트렌드
        </p>
      </div>
    </div>
  )
}

export default TrendChart
