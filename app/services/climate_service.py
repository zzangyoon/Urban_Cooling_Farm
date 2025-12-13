"""
경기기후플랫폼 API 연동 서비스

실제 API 문서 확인 후 구현 예정.
현재는 Mock 데이터로 테스트 가능하도록 구현.
"""
import httpx
from typing import Optional
from datetime import datetime
import random

from pydantic import BaseModel
from app.config import get_settings


# ============== Schemas ==============

class HeatIslandData(BaseModel):
    """열섬 데이터 스키마"""
    latitude: float
    longitude: float
    temperature: float
    heat_island_intensity: float  # 주변 대비 온도차
    timestamp: datetime
    district: str  # 시군구


class WeatherData(BaseModel):
    """기상 데이터 스키마"""
    temperature: float
    humidity: float
    wind_speed: float
    solar_radiation: Optional[float] = None
    timestamp: datetime


class GreenSpaceData(BaseModel):
    """녹지 데이터 스키마"""
    latitude: float
    longitude: float
    green_coverage_ratio: float  # 녹지율 (%)
    tree_density: float  # 나무 밀도 (그루/ha)
    park_area: float  # 공원 면적 (m²)


# ============== Mock Data ==============

# 경기도 주요 지역 좌표 (열섬 발생 지점 시뮬레이션)
MOCK_HEAT_ISLAND_LOCATIONS = [
    {"district": "수원시 팔달구", "lat": 37.2851, "lng": 127.0106, "base_intensity": 2.5},
    {"district": "성남시 분당구", "lat": 37.3825, "lng": 127.1155, "base_intensity": 2.1},
    {"district": "고양시 일산동구", "lat": 37.6584, "lng": 126.7749, "base_intensity": 1.8},
    {"district": "용인시 수지구", "lat": 37.3219, "lng": 127.0965, "base_intensity": 1.5},
    {"district": "부천시", "lat": 37.5034, "lng": 126.7660, "base_intensity": 2.3},
    {"district": "안양시 만안구", "lat": 37.4319, "lng": 126.9022, "base_intensity": 2.0},
    {"district": "평택시", "lat": 36.9921, "lng": 127.1128, "base_intensity": 1.7},
    {"district": "안산시 단원구", "lat": 37.3180, "lng": 126.8309, "base_intensity": 1.9},
    {"district": "화성시", "lat": 37.1996, "lng": 126.8312, "base_intensity": 1.4},
    {"district": "시흥시", "lat": 37.3800, "lng": 126.8030, "base_intensity": 2.2},
]


class ClimateService:
    """경기기후플랫폼 API 서비스"""

    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.CLIMATE_API_BASE_URL
        self.api_key = self.settings.CLIMATE_REMOVED
        self.use_mock = self.settings.USE_MOCK_DATA

    async def _request(self, endpoint: str, params: Optional[dict] = None) -> dict:
        """API 요청 공통 메서드"""
        if self.use_mock:
            return self._get_mock_response(endpoint, params)

        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = await client.get(
                f"{self.base_url}/{endpoint}",
                params=params,
                headers=headers
            )
            response.raise_for_status()
            return response.json()

    def _get_mock_response(self, endpoint: str, params: Optional[dict] = None) -> dict:
        """Mock 응답 생성"""
        # 실제 API 응답 구조에 맞게 수정 필요
        return {"status": "success", "data": []}

    async def get_heat_island_data(
        self,
        district: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> list[HeatIslandData]:
        """
        열섬 현황 데이터 조회

        Args:
            district: 시군구명 (없으면 전체)
            start_date: 조회 시작일
            end_date: 조회 종료일

        Returns:
            열섬 데이터 리스트
        """
        if self.use_mock:
            return self._generate_mock_heat_island_data(district)

        params = {}
        if district:
            params["district"] = district
        if start_date:
            params["start_date"] = start_date.isoformat()
        if end_date:
            params["end_date"] = end_date.isoformat()

        response = await self._request("heat-island", params)
        return [HeatIslandData(**item) for item in response.get("data", [])]

    def _generate_mock_heat_island_data(
        self,
        district: Optional[str] = None
    ) -> list[HeatIslandData]:
        """Mock 열섬 데이터 생성"""
        locations = MOCK_HEAT_ISLAND_LOCATIONS
        if district:
            locations = [loc for loc in locations if district in loc["district"]]

        result = []
        base_temp = 28.0  # 기본 기온

        for loc in locations:
            # 약간의 랜덤성 추가
            intensity = loc["base_intensity"] + random.uniform(-0.3, 0.3)
            temp = base_temp + intensity + random.uniform(-1, 1)

            result.append(HeatIslandData(
                latitude=loc["lat"] + random.uniform(-0.005, 0.005),
                longitude=loc["lng"] + random.uniform(-0.005, 0.005),
                temperature=round(temp, 1),
                heat_island_intensity=round(intensity, 2),
                timestamp=datetime.now(),
                district=loc["district"]
            ))

        return result

    async def get_weather_data(
        self,
        latitude: float,
        longitude: float
    ) -> WeatherData:
        """
        특정 좌표의 기상 데이터 조회

        Args:
            latitude: 위도
            longitude: 경도

        Returns:
            기상 데이터
        """
        if self.use_mock:
            return self._generate_mock_weather_data()

        params = {"lat": latitude, "lng": longitude}
        response = await self._request("weather", params)
        return WeatherData(**response.get("data", {}))

    def _generate_mock_weather_data(self) -> WeatherData:
        """Mock 기상 데이터 생성"""
        return WeatherData(
            temperature=round(28 + random.uniform(-3, 5), 1),
            humidity=round(60 + random.uniform(-20, 20), 1),
            wind_speed=round(random.uniform(0.5, 5), 1),
            solar_radiation=round(random.uniform(200, 800), 1),
            timestamp=datetime.now()
        )

    async def get_green_space_data(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 1.0
    ) -> list[GreenSpaceData]:
        """
        특정 좌표 주변 녹지 데이터 조회

        Args:
            latitude: 중심 위도
            longitude: 중심 경도
            radius_km: 검색 반경 (km)

        Returns:
            녹지 데이터 리스트
        """
        if self.use_mock:
            return self._generate_mock_green_space_data(latitude, longitude)

        params = {
            "lat": latitude,
            "lng": longitude,
            "radius": radius_km
        }
        response = await self._request("green-space", params)
        return [GreenSpaceData(**item) for item in response.get("data", [])]

    def _generate_mock_green_space_data(
        self,
        latitude: float,
        longitude: float
    ) -> list[GreenSpaceData]:
        """Mock 녹지 데이터 생성"""
        # 주변에 3-5개의 녹지 포인트 생성
        count = random.randint(3, 5)
        result = []

        for _ in range(count):
            result.append(GreenSpaceData(
                latitude=latitude + random.uniform(-0.01, 0.01),
                longitude=longitude + random.uniform(-0.01, 0.01),
                green_coverage_ratio=round(random.uniform(5, 40), 1),
                tree_density=round(random.uniform(10, 100), 1),
                park_area=round(random.uniform(100, 10000), 1)
            ))

        return result

    async def get_cooling_priority_areas(
        self,
        top_n: int = 10
    ) -> list[HeatIslandData]:
        """
        냉각 우선순위가 높은 지역 조회
        (열섬 강도가 높은 순)

        Args:
            top_n: 상위 N개 지역

        Returns:
            열섬 데이터 리스트 (강도 높은 순)
        """
        heat_data = await self.get_heat_island_data()
        sorted_data = sorted(
            heat_data,
            key=lambda x: x.heat_island_intensity,
            reverse=True
        )
        return sorted_data[:top_n]
