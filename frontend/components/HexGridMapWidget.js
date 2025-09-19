import { useState, useEffect, useMemo, useCallback } from 'react'

const HexGridMapWidget = ({ onSelectPolitician, politicians = [], onDistrictSelect }) => {
  const [selectedDistrict, setSelectedDistrict] = useState(null)
  const [districtMembers, setDistrictMembers] = useState({})
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])
  const [hoveredDistrict, setHoveredDistrict] = useState(null)

  // 육각형 그리드 데이터 - R에서 생성된 데이터 구조를 기반으로 함
  const hexGridData = useMemo(() => {
    return {
      // 서울특별시 (25개 선거구)
      seoul: [
        { id: 'seoul_01', name: '종로구', x: 150, y: 80, members: [] },
        { id: 'seoul_02', name: '중구·성동구갑', x: 180, y: 80, members: [] },
        { id: 'seoul_03', name: '성동구을', x: 210, y: 80, members: [] },
        { id: 'seoul_04', name: '광진구갑', x: 240, y: 80, members: [] },
        { id: 'seoul_05', name: '광진구을', x: 270, y: 80, members: [] },
        { id: 'seoul_06', name: '동대문구갑', x: 135, y: 110, members: [] },
        { id: 'seoul_07', name: '동대문구을', x: 165, y: 110, members: [] },
        { id: 'seoul_08', name: '성북구갑', x: 195, y: 110, members: [] },
        { id: 'seoul_09', name: '성북구을', x: 225, y: 110, members: [] },
        { id: 'seoul_10', name: '도봉구갑', x: 255, y: 110, members: [] },
        { id: 'seoul_11', name: '도봉구을', x: 285, y: 110, members: [] },
        { id: 'seoul_12', name: '노원구갑', x: 120, y: 140, members: [] },
        { id: 'seoul_13', name: '노원구을', x: 150, y: 140, members: [] },
        { id: 'seoul_14', name: '노원구병', x: 180, y: 140, members: [] },
        { id: 'seoul_15', name: '은평구갑', x: 210, y: 140, members: [] },
        { id: 'seoul_16', name: '은평구을', x: 240, y: 140, members: [] },
        { id: 'seoul_17', name: '서대문구갑', x: 270, y: 140, members: [] },
        { id: 'seoul_18', name: '서대문구을', x: 300, y: 140, members: [] },
        { id: 'seoul_19', name: '마포구갑', x: 135, y: 170, members: [] },
        { id: 'seoul_20', name: '마포구을', x: 165, y: 170, members: [] },
        { id: 'seoul_21', name: '용산구', x: 195, y: 170, members: [] },
        { id: 'seoul_22', name: '성동구병', x: 225, y: 170, members: [] },
        { id: 'seoul_23', name: '강북구갑', x: 255, y: 170, members: [] },
        { id: 'seoul_24', name: '강북구을', x: 285, y: 170, members: [] },
        { id: 'seoul_25', name: '강남구갑', x: 315, y: 170, members: [] }
      ],
      // 부산광역시 (18개 선거구)
      busan: [
        { id: 'busan_01', name: '중구·영도구', x: 450, y: 350, members: [] },
        { id: 'busan_02', name: '서구·동구', x: 480, y: 350, members: [] },
        { id: 'busan_03', name: '부산진구갑', x: 510, y: 350, members: [] },
        { id: 'busan_04', name: '부산진구을', x: 540, y: 350, members: [] },
        { id: 'busan_05', name: '동래구', x: 435, y: 380, members: [] },
        { id: 'busan_06', name: '남구갑', x: 465, y: 380, members: [] },
        { id: 'busan_07', name: '남구을', x: 495, y: 380, members: [] },
        { id: 'busan_08', name: '북구갑', x: 525, y: 380, members: [] },
        { id: 'busan_09', name: '북구을', x: 555, y: 380, members: [] },
        { id: 'busan_10', name: '해운대구갑', x: 420, y: 410, members: [] },
        { id: 'busan_11', name: '해운대구을', x: 450, y: 410, members: [] },
        { id: 'busan_12', name: '사하구갑', x: 480, y: 410, members: [] },
        { id: 'busan_13', name: '사하구을', x: 510, y: 410, members: [] },
        { id: 'busan_14', name: '금정구', x: 540, y: 410, members: [] },
        { id: 'busan_15', name: '연제구', x: 570, y: 410, members: [] },
        { id: 'busan_16', name: '수영구', x: 435, y: 440, members: [] },
        { id: 'busan_17', name: '사상구', x: 465, y: 440, members: [] },
        { id: 'busan_18', name: '기장군', x: 495, y: 440, members: [] }
      ],
      // 경기도 (60개 선거구) - 샘플
      gyeonggi: [
        { id: 'gyeonggi_01', name: '수원시갑', x: 120, y: 200, members: [] },
        { id: 'gyeonggi_02', name: '수원시을', x: 150, y: 200, members: [] },
        { id: 'gyeonggi_03', name: '수원시병', x: 180, y: 200, members: [] },
        { id: 'gyeonggi_04', name: '수원시정', x: 210, y: 200, members: [] },
        { id: 'gyeonggi_05', name: '성남시갑', x: 240, y: 200, members: [] },
        // ... 더 많은 선거구 데이터
      ]
    }
  }, [])

  useEffect(() => {
    if (politicians && politicians.length > 0) {
      processDistrictData()
    }
  }, [politicians])

  const processDistrictData = useCallback(() => {
    setLoading(true)
    
    const districts = {}
    
    politicians.forEach(member => {
      const district = member.district || ''
      const name = member.name
      const party = member.party
      const region = member.region || ''
      
      // 선거구 정보 파싱
      const districtKey = parseDistrictKey(district, region)
      
      if (!districts[districtKey]) {
        districts[districtKey] = []
      }
      
      districts[districtKey].push({
        name,
        party,
        district,
        region,
        phone: member.phone || '',
        email: member.email || '',
        office: member.office || ''
      })
    })

    setDistrictMembers(districts)
    setLoading(false)
    
    console.log('🗺️ 선거구 데이터 처리 완료:', Object.keys(districts).length, '개 선거구')
  }, [politicians])

  const parseDistrictKey = (district, region) => {
    // 지역구 파싱 로직
    if (!district || district === '비례대표') return 'proportional'
    
    // 서울특별시 처리
    if (district.includes('서울')) {
      const match = district.match(/서울특별시\s*(.+)/)
      if (match) {
        return `seoul_${match[1].replace(/\s+/g, '_')}`
      }
    }
    
    // 부산광역시 처리
    if (district.includes('부산')) {
      const match = district.match(/부산광역시\s*(.+)/)
      if (match) {
        return `busan_${match[1].replace(/\s+/g, '_')}`
      }
    }
    
    // 경기도 처리
    if (district.includes('경기')) {
      const match = district.match(/경기도\s*(.+)/)
      if (match) {
        return `gyeonggi_${match[1].replace(/\s+/g, '_')}`
      }
    }
    
    return district.replace(/\s+/g, '_').toLowerCase()
  }

  const searchDistricts = useCallback(async (query) => {
    if (!query.trim()) {
      setSearchResults([])
      return
    }

    try {
      // 로컬 검색 (기존 데이터에서)
      const localResults = Object.keys(districtMembers)
        .filter(key => {
          const members = districtMembers[key]
          return members.some(member => 
            member.name.includes(query) ||
            member.district.includes(query) ||
            member.party.includes(query)
          )
        })
        .map(key => ({
          type: 'district',
          key,
          members: districtMembers[key],
          displayName: districtMembers[key][0]?.district || key
        }))

      // API 검색 (확장 가능)
      const apiResults = await searchPoliticiansAPI(query)
      
      setSearchResults([...localResults, ...apiResults])
    } catch (error) {
      console.error('검색 중 오류:', error)
      setSearchResults([])
    }
  }, [districtMembers])

  const searchPoliticiansAPI = async (query) => {
    // 정치인 검색 API 호출
    try {
      const response = await fetch(`/api/search/politicians?q=${encodeURIComponent(query)}`)
      if (response.ok) {
        const data = await response.json()
        return data.results || []
      }
    } catch (error) {
      console.error('API 검색 오류:', error)
    }
    return []
  }

  const getHexColor = (districtKey) => {
    const memberCount = districtMembers[districtKey]?.length || 0
    if (memberCount === 0) return '#e5e7eb' // gray-200
    if (selectedDistrict === districtKey) return '#1d4ed8' // blue-700
    if (hoveredDistrict === districtKey) return '#3b82f6' // blue-500
    
    // 정당별 색상
    const members = districtMembers[districtKey] || []
    const majorParty = members.reduce((acc, member) => {
      acc[member.party] = (acc[member.party] || 0) + 1
      return acc
    }, {})
    
    const dominantParty = Object.keys(majorParty).reduce((a, b) => 
      majorParty[a] > majorParty[b] ? a : b, ''
    )
    
    // 정당별 색상 매핑
    const partyColors = {
      '국민의힘': '#E53E3E',
      '더불어민주당': '#3182CE',
      '정의당': '#D69E2E',
      '국민의당': '#38A169',
      '개혁신당': '#805AD5'
    }
    
    return partyColors[dominantParty] || '#6B7280' // gray-500
  }

  const handleDistrictClick = (districtKey) => {
    setSelectedDistrict(districtKey === selectedDistrict ? null : districtKey)
    if (onDistrictSelect) {
      onDistrictSelect(districtKey, districtMembers[districtKey])
    }
  }

  const handleMemberClick = (member) => {
    if (onSelectPolitician) {
      onSelectPolitician(member.name, member)
    }
  }

  const renderHexagon = (hex, index) => {
    const { id, name, x, y } = hex
    const color = getHexColor(id)
    const memberCount = districtMembers[id]?.length || 0
    
    // 육각형 SVG 패스
    const hexPath = `M ${x} ${y-15} L ${x+13} ${y-7.5} L ${x+13} ${y+7.5} L ${x} ${y+15} L ${x-13} ${y+7.5} L ${x-13} ${y-7.5} Z`
    
    return (
      <g key={id}>
        <path
          d={hexPath}
          fill={color}
          stroke="#374151"
          strokeWidth="1.5"
          className="cursor-pointer transition-all duration-200"
          onClick={() => handleDistrictClick(id)}
          onMouseEnter={() => setHoveredDistrict(id)}
          onMouseLeave={() => setHoveredDistrict(null)}
        />
        <text
          x={x}
          y={y-2}
          textAnchor="middle"
          className="text-xs font-bold fill-white pointer-events-none"
          style={{ fontSize: '10px' }}
        >
          {name.length > 6 ? name.substring(0, 6) + '...' : name}
        </text>
        <text
          x={x}
          y={y+8}
          textAnchor="middle"
          className="text-xs fill-white pointer-events-none"
          style={{ fontSize: '8px' }}
        >
          {memberCount}명
        </text>
      </g>
    )
  }

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 h-full flex flex-col">
        <h3 className="text-lg font-semibold mb-4">선거구 현황</h3>
        <div className="flex-1 flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6 h-full flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">선거구 현황</h3>
        <div className="text-sm text-gray-500">
          총 {Object.keys(districtMembers).length}개 선거구
        </div>
      </div>

      {/* 검색 바 */}
      <div className="mb-4">
        <div className="relative">
          <input
            type="text"
            placeholder="정치인명, 선거구명, 정당명으로 검색..."
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value)
              searchDistricts(e.target.value)
            }}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <svg
            className="absolute right-3 top-2.5 h-5 w-5 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
        
        {/* 검색 결과 */}
        {searchResults.length > 0 && (
          <div className="mt-2 bg-gray-50 rounded-lg p-2 max-h-32 overflow-y-auto">
            {searchResults.map((result, index) => (
              <div
                key={index}
                className="p-2 hover:bg-blue-50 rounded cursor-pointer text-sm"
                onClick={() => {
                  handleDistrictClick(result.key)
                  setSearchQuery('')
                  setSearchResults([])
                }}
              >
                <div className="font-medium">{result.displayName}</div>
                <div className="text-gray-500">{result.members?.length || 0}명</div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 육각형 그리드 지도 */}
      <div className="relative flex-1 flex flex-col">
        <svg 
          viewBox="0 0 600 500" 
          className="w-full flex-1 border border-gray-200 rounded-lg bg-gray-50"
          style={{ minHeight: '400px' }}
        >
          {/* 서울특별시 */}
          <g>
            <text x="220" y="60" textAnchor="middle" className="text-sm font-bold fill-gray-700">서울특별시</text>
            {hexGridData.seoul.map((hex, index) => renderHexagon(hex, index))}
          </g>
          
          {/* 부산광역시 */}
          <g>
            <text x="500" y="330" textAnchor="middle" className="text-sm font-bold fill-gray-700">부산광역시</text>
            {hexGridData.busan.map((hex, index) => renderHexagon(hex, index))}
          </g>
          
          {/* 경기도 (일부) */}
          <g>
            <text x="180" y="180" textAnchor="middle" className="text-sm font-bold fill-gray-700">경기도</text>
            {hexGridData.gyeonggi.map((hex, index) => renderHexagon(hex, index))}
          </g>
          
          {/* 범례 */}
          <g transform="translate(450, 50)">
            <rect x="0" y="0" width="140" height="100" fill="white" stroke="#ccc" strokeWidth="1" rx="5"/>
            <text x="70" y="15" textAnchor="middle" className="text-xs font-bold">정당별 색상</text>
            <circle cx="15" cy="30" r="6" fill="#E53E3E"/>
            <text x="25" y="35" className="text-xs">국민의힘</text>
            <circle cx="15" cy="45" r="6" fill="#3182CE"/>
            <text x="25" y="50" className="text-xs">더불어민주당</text>
            <circle cx="15" cy="60" r="6" fill="#D69E2E"/>
            <text x="25" y="65" className="text-xs">정의당</text>
            <circle cx="15" cy="75" r="6" fill="#6B7280"/>
            <text x="25" y="80" className="text-xs">기타</text>
          </g>
        </svg>

        {/* 툴팁 */}
        {hoveredDistrict && districtMembers[hoveredDistrict] && (
          <div className="absolute top-4 left-4 bg-black bg-opacity-75 text-white p-2 rounded text-sm pointer-events-none">
            <div className="font-semibold">{districtMembers[hoveredDistrict][0]?.district}</div>
            <div>{districtMembers[hoveredDistrict].length}명 의원</div>
          </div>
        )}
      </div>

      {/* 선택된 선거구의 의원 목록 */}
      {selectedDistrict && districtMembers[selectedDistrict] && (
        <div className="mt-4 p-4 bg-gray-50 rounded-lg">
          <div className="flex items-center justify-between mb-3">
            <h4 className="font-semibold text-gray-800">
              {districtMembers[selectedDistrict][0]?.district} ({districtMembers[selectedDistrict].length}명)
            </h4>
            <button 
              onClick={() => setSelectedDistrict(null)}
              className="text-gray-500 hover:text-gray-700"
            >
              ✕
            </button>
          </div>
          
          <div className="grid grid-cols-1 gap-2 max-h-40 overflow-y-auto">
            {districtMembers[selectedDistrict].map((member, index) => (
              <div 
                key={index}
                className="flex items-center justify-between p-3 bg-white rounded border hover:bg-blue-50 cursor-pointer transition-colors"
                onClick={() => handleMemberClick(member)}
              >
                <div className="flex-1">
                  <div className="font-medium text-gray-800">{member.name}</div>
                  <div className="text-sm text-gray-500">{member.party}</div>
                  {member.phone && (
                    <div className="text-xs text-gray-400">📞 {member.phone}</div>
                  )}
                </div>
                <div className="text-xs text-blue-600">
                  상세보기 →
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default HexGridMapWidget
