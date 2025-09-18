import { useState, useEffect } from 'react'
import ConnectivityWidget from './ConnectivityWidget'

export default function MemberDetailWidget({ memberName, onClose }) {
  const [memberBills, setMemberBills] = useState([])
  const [billScores, setBillScores] = useState({})
  const [photoMapping, setPhotoMapping] = useState({})
  const [memberInfo, setMemberInfo] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (memberName) {
      fetchMemberData()
      loadPhotoMapping()
    }
  }, [memberName])

  const loadPhotoMapping = async () => {
    try {
      const response = await fetch('/politician_photos.json')
      const mapping = await response.json()
      setPhotoMapping(mapping)
    } catch (error) {
      console.error('사진 매핑 로드 실패:', error)
    }
  }

  const fetchMemberData = async () => {
    try {
      setLoading(true)
      setError(null)
      
      // 병렬로 데이터 로드
      const [memberResponse, scoresResponse, billsResponse] = await Promise.all([
        fetch(`https://newsbot-backend-6j3p.onrender.com/api/assembly/members/${encodeURIComponent(memberName)}`),
        fetch('https://newsbot-backend-6j3p.onrender.com/api/bills/scores'),
        fetch(`https://newsbot-backend-6j3p.onrender.com/api/bills/politician/${encodeURIComponent(memberName)}`)
      ])
      
      // 의원 기본 정보 처리
      if (memberResponse.ok) {
        const memberData = await memberResponse.json()
        if (memberData.success) {
          setMemberInfo(memberData.data)
          console.log('✅ 의원 정보 로드:', memberData.data.name, memberData.data.party)
        } else {
          console.warn('⚠️ 의원 정보 로드 실패:', memberData.error)
        }
      } else {
        console.warn('⚠️ 의원 API 응답 실패:', memberResponse.status)
      }
      
      // 발의의안 점수 정보 처리
      if (scoresResponse.ok) {
        const scoresData = await scoresResponse.json()
        if (scoresData.success) {
          setBillScores(scoresData.data[memberName] || {})
          console.log('✅ 발의안 점수 로드 완료')
        }
      }
      
      // 특정 의원 발의안 목록 처리
      if (billsResponse.ok) {
        const billsData = await billsResponse.json()
        if (billsData.success) {
          setMemberBills(billsData.data.bills || [])
          console.log('✅ 발의안 목록 로드:', billsData.data.bills?.length || 0, '건')
        }
      }
      
    } catch (err) {
      setError('데이터를 가져올 수 없습니다.')
      console.error('Error fetching member data:', err)
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

  const getRoleColor = (role) => {
    switch (role) {
      case 'main_proposer':
        return 'text-primary-400 bg-primary-900/20'
      case 'co_proposer':
        return 'text-purple-400 bg-purple-900/20'
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
      case '개혁신당':
        return 'text-green-400'
      case '진보당':
        return 'text-pink-400'
      case '새로운미래':
        return 'text-lime-400'
      case '기본소득당':
        return 'text-yellow-400'
      case '사회민주당':
        return 'text-orange-400'
      default:
        return 'text-gray-400'
    }
  }

  const formatElectionCount = (terms) => {
    if (!terms) return '초선'
    
    // 숫자만 추출
    const numMatch = terms.toString().match(/\d+/)
    if (numMatch) {
      const num = parseInt(numMatch[0])
      if (num === 1) return '초선'
      if (num === 2) return '재선'
      if (num >= 3) return `${num}선`
    }
    
    // 텍스트 기반 처리
    const termStr = terms.toString().toLowerCase()
    if (termStr.includes('초선') || termStr === '1') return '초선'
    if (termStr.includes('재선') || termStr === '2') return '재선'
    if (termStr.includes('삼선') || termStr === '3') return '3선'
    if (termStr.includes('4') || termStr.includes('사선')) return '4선'
    if (termStr.includes('5') || termStr.includes('오선')) return '5선'
    if (termStr.includes('6') || termStr.includes('육선')) return '6선'
    
    return '초선' // 기본값
  }

  if (!memberName) return null

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-dark-800 rounded-lg p-6 border border-dark-700 max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-white">{memberName} 의원 상세정보</h2>
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-primary-500"></div>
          </div>
          <div className="space-y-3">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="animate-pulse">
                <div className="h-4 bg-dark-700 rounded mb-2"></div>
                <div className="h-3 bg-dark-700 rounded w-3/4"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-dark-800 rounded-lg p-6 border border-dark-700 max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-white">{memberName} 의원 상세정보</h2>
            <button 
              onClick={onClose}
              className="text-gray-400 hover:text-white transition-colors"
            >
              <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
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
      </div>
    )
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-dark-800 rounded-lg p-6 border border-dark-700 max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-semibold text-white">{memberName} 의원 상세정보</h2>
          <button 
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* 의원 프로필 섹션 */}
        <div className="mb-6 p-6 bg-dark-700 rounded-lg">
          <div className="flex items-start space-x-6">
            {/* 큰 프로필 사진 */}
            <div className="flex-shrink-0">
              <div className="w-32 h-32 rounded-full overflow-hidden bg-gray-600 flex items-center justify-center">
                {photoMapping[memberName] ? (
                  <img 
                    src={photoMapping[memberName]} 
                    alt={memberName}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      e.target.style.display = 'none';
                      e.target.parentElement.innerHTML = `<div class="text-white text-3xl font-bold">${memberName[0]}</div>`;
                    }}
                  />
                ) : (
                  <div className="text-white text-3xl font-bold">{memberName[0]}</div>
                )}
              </div>
            </div>
            
            {/* 의원 정보 */}
            <div className="flex-1">
              <h3 className="text-2xl font-bold text-white mb-4">{memberName}</h3>
              {memberInfo && (
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <div className="text-sm text-gray-400">정당</div>
                    <div className={`text-lg font-semibold ${getPartyColor(memberInfo.party)}`}>
                      {memberInfo.party}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-400">지역구</div>
                    <div className="text-lg text-white">{memberInfo.district || '비례대표'}</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-400">위원회</div>
                    <div className="text-lg text-white">{memberInfo.committee || '정보없음'}</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-400">당선횟수</div>
                    <div className="text-lg text-white">{formatElectionCount(memberInfo.terms)}</div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* 발의의안 통계 */}
        {billScores && Object.keys(billScores).length > 0 && (
          <div className="mb-6 p-4 bg-dark-700 rounded-lg">
            <h3 className="text-lg font-semibold text-white mb-3">발의의안 통계</h3>
            <div className="grid grid-cols-3 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-primary-400">{billScores.main_proposals || 0}</div>
                <div className="text-sm text-gray-400">대표발의</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-400">{billScores.co_proposals || 0}</div>
                <div className="text-sm text-gray-400">공동발의</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-400">{billScores.total_bills || 0}</div>
                <div className="text-sm text-gray-400">총 발의</div>
              </div>
            </div>
          </div>
        )}

        {/* 발의의안 목록 */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-white">발의의안 목록</h3>
          {memberBills.length === 0 ? (
            <div className="text-center py-8">
              <div className="text-gray-400 mb-2">
                <svg className="h-12 w-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <p className="text-gray-400 text-sm">발의한 의안이 없습니다.</p>
            </div>
          ) : (
            memberBills.map((bill, index) => (
              <div key={bill.bill_id || index} className="border border-dark-600 rounded-lg p-4">
                <div className="flex items-start justify-between mb-3">
                  <h4 className="text-lg font-medium text-white flex-1 mr-4">
                    {bill.bill_name}
                  </h4>
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getRoleColor(bill.role)}`}>
                      {bill.role === 'main_proposer' ? '대표발의' : '공동발의'}
                    </span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(bill.status)}`}>
                      {bill.status}
                    </span>
                  </div>
                </div>
                
                <div className="text-sm text-gray-400 mb-3">
                  발의일: {bill.propose_date}
                </div>
                
                {bill.summary && (
                  <p className="text-sm text-gray-300 mb-3">
                    {bill.summary}
                  </p>
                )}
                
                {/* 대표발의자인 경우 공동발의자 표시 */}
                {bill.role === 'main_proposer' && bill.co_proposers && bill.co_proposers.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-dark-600">
                    <div className="text-sm text-gray-400 mb-2">공동발의자:</div>
                    <div className="flex flex-wrap gap-2">
                      {bill.co_proposers.map((co_proposer, idx) => (
                        <span 
                          key={idx}
                          className={`px-2 py-1 rounded-full text-xs font-medium ${getPartyColor(co_proposer.party)} bg-dark-600`}
                        >
                          {co_proposer.name} ({co_proposer.party})
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                
                {/* 공동발의자인 경우 대표발의자 표시 */}
                {bill.role === 'co_proposer' && bill.main_proposer && (
                  <div className="mt-3 pt-3 border-t border-dark-600">
                    <div className="text-sm text-gray-400 mb-2">대표발의자:</div>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPartyColor(bill.main_proposer_party)} bg-dark-600`}>
                      {bill.main_proposer} ({bill.main_proposer_party})
                    </span>
                  </div>
                )}
              </div>
            ))
          )}
        </div>

        {/* 연결성 위젯 */}
        <div className="mt-6">
          <ConnectivityWidget 
            memberName={memberName} 
            memberInfo={memberInfo} 
          />
        </div>

        {/* 개인정보 섹션 (가장 하단) */}
        {memberInfo && (
          <div className="mt-8 p-6 bg-dark-700 rounded-lg border-t-2 border-gray-600">
            <h3 className="text-lg font-semibold text-white mb-4">📞 연락처 정보</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* 이메일 */}
              {(memberInfo.email || memberInfo.email_personal) && (
                <div className="bg-dark-600 p-4 rounded-lg">
                  <div className="text-sm text-gray-400 mb-2">📧 이메일</div>
                  <div className="text-white break-all">
                    {memberInfo.email_personal || memberInfo.email}
                  </div>
                </div>
              )}
              
              {/* 홈페이지 */}
              {memberInfo.homepage && memberInfo.homepage !== 'null' && (
                <div className="bg-dark-600 p-4 rounded-lg">
                  <div className="text-sm text-gray-400 mb-2">🌐 홈페이지</div>
                  <a 
                    href={memberInfo.homepage} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-primary-400 hover:text-primary-300 transition-colors break-all"
                  >
                    {memberInfo.homepage}
                  </a>
                </div>
              )}
              
              {/* 사무실 전화 */}
              {(memberInfo.phone || memberInfo.phone_office) && (
                <div className="bg-dark-600 p-4 rounded-lg">
                  <div className="text-sm text-gray-400 mb-2">📞 사무실 전화</div>
                  <div className="text-white">
                    {memberInfo.phone_office || memberInfo.phone}
                  </div>
                </div>
              )}
              
              {/* 사무실 */}
              {memberInfo.office_room && (
                <div className="bg-dark-600 p-4 rounded-lg">
                  <div className="text-sm text-gray-400 mb-2">🏢 사무실</div>
                  <div className="text-white">
                    {memberInfo.office_room}
                  </div>
                </div>
              )}
            </div>
            
            {/* 개인정보 보호 안내 */}
            <div className="mt-4 pt-4 border-t border-dark-600">
              <p className="text-xs text-gray-500 text-center">
                ℹ️ 위 연락처 정보는 국회 공식 자료에서 제공되는 공개 정보입니다
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
