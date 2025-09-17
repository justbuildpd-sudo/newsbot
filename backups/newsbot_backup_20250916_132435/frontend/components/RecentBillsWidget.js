import { useState, useEffect } from 'react'

export default function RecentBillsWidget() {
  const [bills, setBills] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchRecentBills()
  }, [])

  const fetchRecentBills = async () => {
    try {
      setLoading(true)
      const response = await fetch('http://localhost:8001/api/bills/recent')
      const data = await response.json()
      
      if (data.success) {
        setBills(data.data)
      } else {
        setError('의안발의 데이터를 가져올 수 없습니다.')
      }
    } catch (err) {
      setError('서버 연결 오류가 발생했습니다.')
      console.error('Error fetching bills:', err)
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case '본회의 통과':
        return 'text-green-400 bg-green-900/20'
      case '위원회 심사':
        return 'text-yellow-400 bg-yellow-900/20'
      case '정부 제출':
        return 'text-blue-400 bg-blue-900/20'
      default:
        return 'text-gray-400 bg-gray-900/20'
    }
  }

  const getPartyColor = (party) => {
    switch (party) {
      case '더불어민주당':
        return 'text-blue-400'
      case '국민의힘':
        return 'text-red-400'
      case '조국혁신당':
        return 'text-purple-400'
      default:
        return 'text-gray-400'
    }
  }

  if (loading) {
    return (
      <div className="bg-dark-800 rounded-lg p-6 border border-dark-700">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-white">최근 입법</h2>
          <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-primary-500"></div>
        </div>
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="animate-pulse">
              <div className="h-4 bg-dark-700 rounded mb-2"></div>
              <div className="h-3 bg-dark-700 rounded w-3/4"></div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-dark-800 rounded-lg p-6 border border-dark-700">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-white">최근 입법</h2>
          <button 
            onClick={fetchRecentBills}
            className="text-primary-500 hover:text-primary-400 transition-colors"
          >
            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
        </div>
        <div className="text-center py-8">
          <div className="text-red-400 mb-2">
            <svg className="h-12 w-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <p className="text-red-400 text-sm">{error}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-dark-800 rounded-lg p-6 border border-dark-700">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-white">최근 입법</h2>
        <button 
          onClick={fetchRecentBills}
          className="text-primary-500 hover:text-primary-400 transition-colors"
        >
          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
      </div>

      <div className="space-y-4">
        {bills.length === 0 ? (
          <div className="text-center py-8">
            <div className="text-gray-400 mb-2">
              <svg className="h-12 w-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <p className="text-gray-400 text-sm">최근 입법 데이터가 없습니다.</p>
          </div>
        ) : (
          bills.map((bill, index) => (
            <div key={bill.bill_id || index} className="border-b border-dark-700 pb-4 last:border-b-0">
              <div className="flex items-start justify-between mb-2">
                <h3 className="text-sm font-medium text-white line-clamp-2 flex-1 mr-2">
                  {bill.bill_name}
                </h3>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(bill.status)}`}>
                  {bill.status}
                </span>
              </div>
              
              <div className="flex items-center justify-between text-xs text-gray-400">
                <div className="flex items-center space-x-2">
                  <span className={`font-medium ${getPartyColor(bill.proposer_party)}`}>
                    {bill.proposer}
                  </span>
                  <span className="text-gray-500">•</span>
                  <span className="text-gray-400">{bill.proposer_party}</span>
                </div>
                <span>{bill.propose_date}</span>
              </div>
              
              {bill.summary && (
                <p className="text-xs text-gray-400 mt-2 line-clamp-2">
                  {bill.summary}
                </p>
              )}
            </div>
          ))
        )}
      </div>

      {bills.length > 0 && (
        <div className="mt-4 pt-4 border-t border-dark-700">
          <button className="w-full text-center text-primary-500 hover:text-primary-400 text-sm font-medium transition-colors">
            모든 입법 보기 →
          </button>
        </div>
      )}
    </div>
  )
}
