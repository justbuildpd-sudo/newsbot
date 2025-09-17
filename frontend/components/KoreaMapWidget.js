import { useState, useEffect, useMemo } from 'react'

const KoreaMapWidget = ({ onSelectPolitician, politicians = [] }) => {
  const [selectedRegion, setSelectedRegion] = useState(null)
  const [regionMembers, setRegionMembers] = useState({})
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (politicians && politicians.length > 0) {
      processRegionData()
    }
  }, [politicians])

  const processRegionData = () => {
    setLoading(true)
    
    const regions = {}
    const proportional = []

    politicians.forEach(member => {
      const district = member.district || ''
      const name = member.name
      const party = member.party

      if (district === '비례대표' || !district) {
        proportional.push({ name, party, district: '비례대표' })
        return
      }

      // 지역구 분류
      let region = '기타'
      if (district.startsWith('서울')) region = '서울특별시'
      else if (district.startsWith('부산')) region = '부산광역시'
      else if (district.startsWith('대구')) region = '대구광역시'
      else if (district.startsWith('인천')) region = '인천광역시'
      else if (district.startsWith('광주')) region = '광주광역시'
      else if (district.startsWith('대전')) region = '대전광역시'
      else if (district.startsWith('울산')) region = '울산광역시'
      else if (district.startsWith('세종')) region = '세종특별자치시'
      else if (district.startsWith('경기')) region = '경기도'
      else if (district.startsWith('강원')) region = '강원특별자치도'
      else if (district.startsWith('충북') || district.startsWith('충청북도')) region = '충청북도'
      else if (district.startsWith('충남') || district.startsWith('충청남도')) region = '충청남도'
      else if (district.startsWith('전북') || district.startsWith('전라북도')) region = '전북특별자치도'
      else if (district.startsWith('전남') || district.startsWith('전라남도')) region = '전라남도'
      else if (district.startsWith('경북') || district.startsWith('경상북도')) region = '경상북도'
      else if (district.startsWith('경남') || district.startsWith('경상남도')) region = '경상남도'
      else if (district.startsWith('제주')) region = '제주특별자치도'

      if (!regions[region]) regions[region] = []
      regions[region].push({ name, party, district, region })
    })

    regions['비례대표'] = proportional
    setRegionMembers(regions)
    setLoading(false)

    console.log('🗺️ 지역구 데이터 처리 완료:', Object.keys(regions).map(r => `${r}(${regions[r].length}명)`))
  }

  const getRegionColor = (regionName) => {
    const count = regionMembers[regionName]?.length || 0
    if (count === 0) return '#e5e7eb' // gray-200
    if (count <= 5) return '#dbeafe' // blue-100
    if (count <= 15) return '#bfdbfe' // blue-200
    if (count <= 30) return '#93c5fd' // blue-300
    if (count <= 50) return '#60a5fa' // blue-400
    return '#3b82f6' // blue-500
  }

  const handleRegionClick = (regionName) => {
    setSelectedRegion(regionName === selectedRegion ? null : regionName)
  }

  const handleMemberClick = (memberName) => {
    if (onSelectPolitician) {
      onSelectPolitician(memberName)
    }
  }

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 h-full flex flex-col">
        <h3 className="text-lg font-semibold mb-4">지역구 현황</h3>
        <div className="flex-1 flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6 h-full flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">지역구 현황</h3>
        <div className="text-sm text-gray-500">
          총 {Object.keys(regionMembers).length - 1}개 광역시/도
        </div>
      </div>

      {/* 남한 지도 SVG - flex-1로 남은 공간 모두 사용 */}
      <div className="relative flex-1 flex flex-col">
        <svg 
          viewBox="0 0 400 500" 
          className="w-full flex-1 border border-gray-200 rounded-lg"
          style={{ minHeight: '300px' }}
        >
          {/* 서울특별시 */}
          <rect 
            x="150" y="120" width="30" height="25" 
            fill={getRegionColor('서울특별시')}
            stroke="#374151" strokeWidth="2"
            className="cursor-pointer hover:opacity-80 transition-opacity"
            onClick={() => handleRegionClick('서울특별시')}
          />
          <text x="165" y="135" textAnchor="middle" className="text-xs font-bold fill-gray-800">서울</text>
          
          {/* 인천광역시 */}
          <rect 
            x="120" y="130" width="25" height="20" 
            fill={getRegionColor('인천광역시')}
            stroke="#374151" strokeWidth="2"
            className="cursor-pointer hover:opacity-80 transition-opacity"
            onClick={() => handleRegionClick('인천광역시')}
          />
          <text x="132" y="142" textAnchor="middle" className="text-xs font-bold fill-gray-800">인천</text>

          {/* 경기도 */}
          <path 
            d="M 100 100 L 200 100 L 200 160 L 100 160 Z" 
            fill={getRegionColor('경기도')}
            stroke="#374151" strokeWidth="2"
            className="cursor-pointer hover:opacity-80 transition-opacity"
            onClick={() => handleRegionClick('경기도')}
          />
          <text x="150" y="105" textAnchor="middle" className="text-xs font-bold fill-gray-800">경기도</text>

          {/* 강원특별자치도 */}
          <path 
            d="M 200 80 L 300 80 L 300 160 L 200 160 Z" 
            fill={getRegionColor('강원특별자치도')}
            stroke="#374151" strokeWidth="2"
            className="cursor-pointer hover:opacity-80 transition-opacity"
            onClick={() => handleRegionClick('강원특별자치도')}
          />
          <text x="250" y="125" textAnchor="middle" className="text-xs font-bold fill-gray-800">강원도</text>

          {/* 충청북도 */}
          <rect 
            x="150" y="160" width="70" height="40" 
            fill={getRegionColor('충청북도')}
            stroke="#374151" strokeWidth="2"
            className="cursor-pointer hover:opacity-80 transition-opacity"
            onClick={() => handleRegionClick('충청북도')}
          />
          <text x="185" y="182" textAnchor="middle" className="text-xs font-bold fill-gray-800">충북</text>

          {/* 충청남도 */}
          <rect 
            x="80" y="160" width="70" height="40" 
            fill={getRegionColor('충청남도')}
            stroke="#374151" strokeWidth="2"
            className="cursor-pointer hover:opacity-80 transition-opacity"
            onClick={() => handleRegionClick('충청남도')}
          />
          <text x="115" y="182" textAnchor="middle" className="text-xs font-bold fill-gray-800">충남</text>

          {/* 세종특별자치시 */}
          <circle 
            cx="130" cy="180" r="8" 
            fill={getRegionColor('세종특별자치시')}
            stroke="#374151" strokeWidth="2"
            className="cursor-pointer hover:opacity-80 transition-opacity"
            onClick={() => handleRegionClick('세종특별자치시')}
          />
          <text x="130" y="185" textAnchor="middle" className="text-xs font-bold fill-gray-800">세종</text>

          {/* 대전광역시 */}
          <circle 
            cx="150" cy="200" r="10" 
            fill={getRegionColor('대전광역시')}
            stroke="#374151" strokeWidth="2"
            className="cursor-pointer hover:opacity-80 transition-opacity"
            onClick={() => handleRegionClick('대전광역시')}
          />
          <text x="150" y="205" textAnchor="middle" className="text-xs font-bold fill-gray-800">대전</text>

          {/* 전북특별자치도 */}
          <rect 
            x="80" y="200" width="60" height="50" 
            fill={getRegionColor('전북특별자치도')}
            stroke="#374151" strokeWidth="2"
            className="cursor-pointer hover:opacity-80 transition-opacity"
            onClick={() => handleRegionClick('전북특별자치도')}
          />
          <text x="110" y="227" textAnchor="middle" className="text-xs font-bold fill-gray-800">전북</text>

          {/* 전라남도 */}
          <rect 
            x="60" y="250" width="80" height="60" 
            fill={getRegionColor('전라남도')}
            stroke="#374151" strokeWidth="2"
            className="cursor-pointer hover:opacity-80 transition-opacity"
            onClick={() => handleRegionClick('전라남도')}
          />
          <text x="100" y="282" textAnchor="middle" className="text-xs font-bold fill-gray-800">전남</text>

          {/* 광주광역시 */}
          <circle 
            cx="90" cy="270" r="10" 
            fill={getRegionColor('광주광역시')}
            stroke="#374151" strokeWidth="2"
            className="cursor-pointer hover:opacity-80 transition-opacity"
            onClick={() => handleRegionClick('광주광역시')}
          />
          <text x="90" y="275" textAnchor="middle" className="text-xs font-bold fill-gray-800">광주</text>

          {/* 경상북도 */}
          <rect 
            x="220" y="160" width="80" height="80" 
            fill={getRegionColor('경상북도')}
            stroke="#374151" strokeWidth="2"
            className="cursor-pointer hover:opacity-80 transition-opacity"
            onClick={() => handleRegionClick('경상북도')}
          />
          <text x="260" y="202" textAnchor="middle" className="text-xs font-bold fill-gray-800">경북</text>

          {/* 대구광역시 */}
          <circle 
            cx="240" cy="220" r="12" 
            fill={getRegionColor('대구광역시')}
            stroke="#374151" strokeWidth="2"
            className="cursor-pointer hover:opacity-80 transition-opacity"
            onClick={() => handleRegionClick('대구광역시')}
          />
          <text x="240" y="225" textAnchor="middle" className="text-xs font-bold fill-gray-800">대구</text>

          {/* 경상남도 */}
          <rect 
            x="140" y="250" width="80" height="60" 
            fill={getRegionColor('경상남도')}
            stroke="#374151" strokeWidth="2"
            className="cursor-pointer hover:opacity-80 transition-opacity"
            onClick={() => handleRegionClick('경상남도')}
          />
          <text x="180" y="282" textAnchor="middle" className="text-xs font-bold fill-gray-800">경남</text>

          {/* 부산광역시 */}
          <circle 
            cx="220" cy="280" r="12" 
            fill={getRegionColor('부산광역시')}
            stroke="#374151" strokeWidth="2"
            className="cursor-pointer hover:opacity-80 transition-opacity"
            onClick={() => handleRegionClick('부산광역시')}
          />
          <text x="220" y="285" textAnchor="middle" className="text-xs font-bold fill-gray-800">부산</text>

          {/* 울산광역시 */}
          <circle 
            cx="280" cy="240" r="10" 
            fill={getRegionColor('울산광역시')}
            stroke="#374151" strokeWidth="2"
            className="cursor-pointer hover:opacity-80 transition-opacity"
            onClick={() => handleRegionClick('울산광역시')}
          />
          <text x="280" y="245" textAnchor="middle" className="text-xs font-bold fill-gray-800">울산</text>

          {/* 제주특별자치도 */}
          <ellipse 
            cx="120" cy="350" rx="25" ry="15" 
            fill={getRegionColor('제주특별자치도')}
            stroke="#374151" strokeWidth="2"
            className="cursor-pointer hover:opacity-80 transition-opacity"
            onClick={() => handleRegionClick('제주특별자치도')}
          />
          <text x="120" y="355" textAnchor="middle" className="text-xs font-bold fill-gray-800">제주도</text>

          {/* 비례대표 (우측 상단) */}
          <rect 
            x="320" y="40" width="60" height="30" 
            fill={getRegionColor('비례대표')}
            stroke="#374151" strokeWidth="2"
            className="cursor-pointer hover:opacity-80 transition-opacity"
            onClick={() => handleRegionClick('비례대표')}
          />
          <text x="350" y="57" textAnchor="middle" className="text-xs font-bold fill-gray-800">비례대표</text>
        </svg>

        {/* 범례 - 압축된 형태 */}
        <div className="mt-2 flex flex-col space-y-1 text-xs text-gray-600">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="flex items-center space-x-1">
                <div className="w-2 h-2 bg-gray-200 border border-gray-400"></div>
                <span>0</span>
              </div>
              <div className="flex items-center space-x-1">
                <div className="w-2 h-2 bg-blue-100 border border-gray-400"></div>
                <span>1-5</span>
              </div>
              <div className="flex items-center space-x-1">
                <div className="w-2 h-2 bg-blue-300 border border-gray-400"></div>
                <span>15-30</span>
              </div>
              <div className="flex items-center space-x-1">
                <div className="w-2 h-2 bg-blue-500 border border-gray-400"></div>
                <span>50+</span>
              </div>
            </div>
          </div>
          <div className="text-center text-gray-500">
            클릭하여 해당 지역 의원 보기
          </div>
        </div>
      </div>

      {/* 선택된 지역의 의원 목록 - 컴팩트 버전 */}
      {selectedRegion && regionMembers[selectedRegion] && (
        <div className="mt-4 p-3 bg-gray-50 rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <h4 className="font-semibold text-sm text-gray-800">
              {selectedRegion} ({regionMembers[selectedRegion].length}명)
            </h4>
            <button 
              onClick={() => setSelectedRegion(null)}
              className="text-gray-500 hover:text-gray-700 text-sm"
            >
              ✕
            </button>
          </div>
          
          <div className="grid grid-cols-1 gap-1 max-h-32 overflow-y-auto">
            {regionMembers[selectedRegion].map((member, index) => (
              <div 
                key={index}
                className="flex items-center justify-between p-2 bg-white rounded border hover:bg-blue-50 cursor-pointer transition-colors"
                onClick={() => handleMemberClick(member.name)}
              >
                <div className="flex-1 min-w-0">
                  <div className="font-medium text-xs text-gray-800 truncate">{member.name}</div>
                  <div className="text-xs text-gray-500 truncate">{member.party}</div>
                </div>
                <div className="text-xs text-gray-400 ml-2">
                  {member.district !== '비례대표' ? member.district.replace(selectedRegion.split('특별시')[0].split('광역시')[0].split('도')[0], '').trim() : '비례'}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default KoreaMapWidget
