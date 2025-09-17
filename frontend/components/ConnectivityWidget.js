import React, { useState, useEffect } from 'react';

const ConnectivityWidget = ({ memberName, memberInfo }) => {
  const [connections, setConnections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [photoMapping, setPhotoMapping] = useState({});

  useEffect(() => {
    if (memberName && memberInfo) {
      loadPhotoMapping();
      loadConnections();
    }
  }, [memberName, memberInfo]);

  const loadPhotoMapping = async () => {
    try {
      const response = await fetch('/politician_photos.json');
      if (response.ok) {
        const photos = await response.json();
        setPhotoMapping(photos);
      }
    } catch (err) {
      console.warn('사진 매핑 로드 실패:', err);
    }
  };

  const loadConnections = async () => {
    try {
      setLoading(true);
      setError(null);

      // 연결성 분석 API 호출
      const response = await fetch(`https://newsbot-backend-6j3p.onrender.com/api/connectivity/${encodeURIComponent(memberName)}`);
      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          setConnections(result.data);
        } else {
          throw new Error(result.error || '연결성 데이터 로드 실패');
        }
      } else {
        // 백엔드 API가 실패하면 로컬 계산 사용
        console.warn('백엔드 연결성 API 실패, 로컬 계산 사용');
        const membersResponse = await fetch('https://newsbot-backend-6j3p.onrender.com/api/assembly/members');
        if (membersResponse.ok) {
          const membersResult = await membersResponse.json();
          if (membersResult.success) {
            const connectivityData = calculateConnectivity(memberInfo, membersResult.data);
            setConnections(connectivityData);
          } else {
            throw new Error('의원 데이터 로드 실패');
          }
        } else {
          throw new Error(`API 오류: ${response.status}`);
        }
      }
    } catch (err) {
      setError('연결성 데이터를 불러올 수 없습니다: ' + err.message);
      console.error('연결성 데이터 로드 오류:', err);
      
      // 폴백 데이터
      setConnections(generateFallbackConnections(memberInfo));
    } finally {
      setLoading(false);
    }
  };

  const calculateConnectivity = (currentMember, allMembers) => {
    if (!currentMember || !allMembers) return [];

    const currentCommittee = currentMember.committee;
    const currentParty = currentMember.party;

    if (!currentCommittee) return [];

    // 같은 상임위원회 소속 의원들 필터링
    const committeeMembers = allMembers.filter(member => 
      member.committee === currentCommittee && 
      member.name !== currentMember.name
    );

    // 연결성 점수 계산 및 정렬
    const connectivityScores = committeeMembers.map(member => {
      const isSameParty = member.party === currentParty;
      const baseScore = 70; // 기본 위원회 연결 점수
      
      // 같은 정당이면 +20, 다른 정당이면 +10
      const partyBonus = isSameParty ? 20 : 10;
      
      // 지역구 유사성 보너스 (간단한 지역 매칭)
      const regionBonus = calculateRegionBonus(currentMember.district, member.district);
      
      const totalScore = Math.min(100, baseScore + partyBonus + regionBonus);
      
      return {
        ...member,
        connectivityScore: totalScore,
        isSameParty,
        connectionType: 'committee',
        connectionReason: `${currentCommittee} 동료`
      };
    });

    // 점수순으로 정렬하고 상위 8명만 반환
    return connectivityScores
      .sort((a, b) => b.connectivityScore - a.connectivityScore)
      .slice(0, 8);
  };

  const calculateRegionBonus = (district1, district2) => {
    if (!district1 || !district2) return 0;
    
    const region1 = district1.split(' ')[0]; // 첫 번째 단어 (시/도)
    const region2 = district2.split(' ')[0];
    
    return region1 === region2 ? 10 : 0;
  };

  const generateFallbackConnections = (memberInfo) => {
    const fallbackMembers = [
      { name: '김영배', party: '더불어민주당', district: '서울 강남구갑', committee: memberInfo.committee },
      { name: '박진', party: '국민의힘', district: '서울 종로구', committee: memberInfo.committee },
      { name: '정청래', party: '더불어민주당', district: '서울 마포구을', committee: memberInfo.committee },
      { name: '조국', party: '조국혁신당', district: '서울 종로구', committee: memberInfo.committee },
      { name: '한동훈', party: '국민의힘', district: '서울 동작구갑', committee: memberInfo.committee },
      { name: '김기현', party: '국민의힘', district: '울산 북구', committee: memberInfo.committee }
    ];

    return fallbackMembers.map((member, index) => ({
      ...member,
      connectivityScore: 85 - (index * 5),
      isSameParty: member.party === memberInfo.party,
      connectionType: 'committee',
      connectionReason: `${memberInfo.committee} 동료`
    }));
  };

  const getPartyColor = (party, isSameParty) => {
    if (isSameParty) {
      // 같은 정당 - 진한 색상
      switch (party) {
        case '더불어민주당':
          return 'from-blue-500 to-blue-600';
        case '국민의힘':
          return 'from-red-500 to-red-600';
        case '조국혁신당':
          return 'from-purple-500 to-purple-600';
        case '개혁신당':
          return 'from-green-500 to-green-600';
        case '진보당':
          return 'from-pink-500 to-pink-600';
        case '새로운미래':
          return 'from-lime-500 to-lime-600';
        case '기본소득당':
          return 'from-yellow-500 to-yellow-600';
        case '사회민주당':
          return 'from-orange-500 to-orange-600';
        default:
          return 'from-gray-500 to-gray-600';
      }
    } else {
      // 다른 정당 - 연한 색상
      switch (party) {
        case '더불어민주당':
          return 'from-blue-300 to-blue-400';
        case '국민의힘':
          return 'from-red-300 to-red-400';
        case '조국혁신당':
          return 'from-purple-300 to-purple-400';
        case '개혁신당':
          return 'from-green-300 to-green-400';
        case '진보당':
          return 'from-pink-300 to-pink-400';
        case '새로운미래':
          return 'from-lime-300 to-lime-400';
        case '기본소득당':
          return 'from-yellow-300 to-yellow-400';
        case '사회민주당':
          return 'from-orange-300 to-orange-400';
        default:
          return 'from-gray-300 to-gray-400';
      }
    }
  };

  const getConnectionStrength = (score) => {
    if (score >= 90) return { width: '100%', opacity: 1.0, label: '매우 강함' };
    if (score >= 80) return { width: '80%', opacity: 0.9, label: '강함' };
    if (score >= 70) return { width: '60%', opacity: 0.8, label: '보통' };
    if (score >= 60) return { width: '40%', opacity: 0.7, label: '약함' };
    return { width: '20%', opacity: 0.6, label: '매우 약함' };
  };

  const renderMemberCard = (member) => {
    const partyColor = getPartyColor(member.party, member.isSameParty);
    const strength = getConnectionStrength(member.connectivityScore);
    const photoUrl = photoMapping[member.name];

    return (
      <div
        key={member.name}
        className={`relative bg-gradient-to-r ${partyColor} rounded-xl p-4 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105`}
        style={{ opacity: strength.opacity }}
      >
        {/* 연결 강도 표시 바 */}
        <div className="absolute top-0 left-0 right-0 h-1 bg-black bg-opacity-20 rounded-t-xl">
          <div
            className="h-full bg-white bg-opacity-60 rounded-t-xl transition-all duration-500"
            style={{ width: strength.width }}
          />
        </div>

        {/* 멤버 정보 */}
        <div className="flex items-center space-x-3">
          {/* 프로필 사진 */}
          <div className="flex-shrink-0">
            {photoUrl ? (
              <img
                src={photoUrl}
                alt={member.name}
                className="w-12 h-12 rounded-full border-2 border-white shadow-md object-cover"
              />
            ) : (
              <div className="w-12 h-12 rounded-full border-2 border-white shadow-md bg-white bg-opacity-20 flex items-center justify-center">
                <span className="text-white font-bold text-sm">
                  {member.name.substring(0, 2)}
                </span>
              </div>
            )}
          </div>

          {/* 이름 및 정보 */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center space-x-2">
              <h4 className="text-white font-bold text-sm truncate">
                {member.name}
              </h4>
              {member.isSameParty && (
                <span className="inline-block w-2 h-2 bg-white rounded-full opacity-80" />
              )}
            </div>
            <p className="text-white text-xs opacity-90 truncate">
              {member.district}
            </p>
            <div className="flex items-center justify-between mt-1">
              <span className="text-white text-xs opacity-75">
                {member.party}
              </span>
              <span className="text-white text-xs font-medium">
                {member.connectivityScore}%
              </span>
            </div>
          </div>
        </div>

        {/* 연결 이유 */}
        <div className="mt-2 pt-2 border-t border-white border-opacity-20">
          <p className="text-white text-xs opacity-80 truncate">
            📋 {member.connectionReason}
          </p>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="bg-gray-800 rounded-lg p-6">
        <div className="flex items-center space-x-2 mb-4">
          <div className="w-6 h-6 bg-blue-500 rounded animate-pulse" />
          <h3 className="text-lg font-semibold text-white">연결성 분석</h3>
        </div>
        <div className="grid grid-cols-2 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="bg-gray-700 rounded-lg p-4 animate-pulse">
              <div className="flex items-center space-x-3">
                <div className="w-12 h-12 bg-gray-600 rounded-full" />
                <div className="flex-1">
                  <div className="h-4 bg-gray-600 rounded mb-2" />
                  <div className="h-3 bg-gray-600 rounded w-2/3" />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-gray-800 rounded-lg p-6">
        <div className="flex items-center space-x-2 mb-4">
          <div className="w-6 h-6 bg-red-500 rounded" />
          <h3 className="text-lg font-semibold text-white">연결성 분석</h3>
        </div>
        <div className="text-center py-8">
          <p className="text-red-400 mb-4">⚠️ {error}</p>
          <button
            onClick={loadConnections}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
          >
            다시 시도
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-lg p-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-2">
          <div className="w-6 h-6 bg-gradient-to-r from-blue-500 to-purple-500 rounded" />
          <h3 className="text-lg font-semibold text-white">연결성 분석</h3>
        </div>
        <div className="text-sm text-gray-400">
          {memberInfo?.committee || '상임위원회'} 기준
        </div>
      </div>

      {/* 연결성 범례 */}
      <div className="mb-4 p-3 bg-gray-700 rounded-lg">
        <div className="flex items-center justify-between text-xs text-gray-300">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-white rounded-full opacity-80" />
            <span>동일 정당</span>
          </div>
          <div className="flex items-center space-x-4">
            <span>연결 강도:</span>
            <div className="flex items-center space-x-1">
              <div className="w-4 h-1 bg-white opacity-100 rounded" />
              <div className="w-4 h-1 bg-white opacity-80 rounded" />
              <div className="w-4 h-1 bg-white opacity-60 rounded" />
            </div>
          </div>
        </div>
      </div>

      {/* 연결된 의원들 */}
      {connections.length > 0 ? (
        <div className="grid grid-cols-2 gap-4">
          {connections.map(renderMemberCard)}
        </div>
      ) : (
        <div className="text-center py-8 text-gray-400">
          <p>📭 연결된 의원 정보가 없습니다</p>
          <p className="text-sm mt-2">상임위원회 정보를 확인해주세요</p>
        </div>
      )}

      {/* 하단 정보 */}
      <div className="mt-4 pt-4 border-t border-gray-700">
        <p className="text-xs text-gray-400 text-center">
          💡 상임위원회 동료 의원들과의 연결성을 정당별로 구분하여 표시
        </p>
      </div>
    </div>
  );
};

export default ConnectivityWidget;
