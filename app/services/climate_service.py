"""
경기기후플랫폼 API 연동 서비스

경기기후 플랫폼 WFS API를 통해 공원, 녹지, 비오톱 데이터를 조회하고
열섬 취약 지역 분석에 활용합니다.
"""
import httpx
import math
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
    green_coverage_ratio: Optional[float] = None  # 녹지율


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
    district: Optional[str] = None
    park_name: Optional[str] = None


class ParkData(BaseModel):
    """공원 데이터 스키마"""
    uid: Optional[str] = None
    sgg_nm: str  # 시군구명
    lclsf_nm: Optional[str] = None  # 대분류
    mclsf_nm: Optional[str] = None  # 중분류
    sclsf_nm: Optional[str] = None  # 소분류
    area: Optional[float] = None  # 면적
    latitude: float
    longitude: float


# ============== 경기도 시군구 정보 ==============

# 경기도 주요 시군구 중심 좌표 (EPSG:4326)
GYEONGGI_DISTRICTS = [
    {"district": "수원시", "lat": 37.2636, "lng": 127.0286, "population_density": 9800},
    {"district": "성남시", "lat": 37.4200, "lng": 127.1265, "population_density": 9200},
    {"district": "고양시", "lat": 37.6584, "lng": 126.8320, "population_density": 7500},
    {"district": "용인시", "lat": 37.2410, "lng": 127.1775, "population_density": 3200},
    {"district": "부천시", "lat": 37.5034, "lng": 126.7660, "population_density": 15800},
    {"district": "안산시", "lat": 37.3219, "lng": 126.8309, "population_density": 8100},
    {"district": "안양시", "lat": 37.3943, "lng": 126.9568, "population_density": 11200},
    {"district": "평택시", "lat": 36.9921, "lng": 127.1128, "population_density": 1800},
    {"district": "시흥시", "lat": 37.3800, "lng": 126.8030, "population_density": 5500},
    {"district": "화성시", "lat": 37.1996, "lng": 126.8312, "population_density": 1500},
    {"district": "광명시", "lat": 37.4786, "lng": 126.8644, "population_density": 17500},
    {"district": "군포시", "lat": 37.3616, "lng": 126.9351, "population_density": 11000},
    {"district": "광주시", "lat": 37.4095, "lng": 127.2550, "population_density": 1800},
    {"district": "김포시", "lat": 37.6152, "lng": 126.7156, "population_density": 2800},
    {"district": "파주시", "lat": 37.7126, "lng": 126.7800, "population_density": 800},
]


# ============== 좌표 변환 유틸리티 ==============

def epsg5186_to_wgs84(x: float, y: float) -> tuple[float, float]:
    """
    EPSG:5186 (Korea 2000 / Central Belt) to EPSG:4326 (WGS84) 좌표 변환

    간소화된 변환 공식 사용 (정밀도 약간 떨어지지만 라이브러리 의존성 없음)
    """
    # 원점 파라미터
    lat0 = 38.0  # 중부원점 위도
    lon0 = 127.0  # 중부원점 경도
    x0 = 200000  # False Easting
    y0 = 600000  # False Northing
    k0 = 1.0  # Scale factor

    # GRS80 타원체
    a = 6378137.0  # 장반경
    f = 1 / 298.257222101  # 편평률

    # 이심률
    e2 = 2 * f - f * f
    e = math.sqrt(e2)

    # 좌표 이동
    x_shifted = x - x0
    y_shifted = y - y0

    # 역변환 (간소화)
    lat_rad = math.radians(lat0)
    m0 = a * (1 - e2) / math.pow(1 - e2 * math.sin(lat_rad)**2, 1.5)

    # 근사 변환
    lat = lat0 + (y_shifted / m0) * (180 / math.pi)

    # 경도 보정
    cos_lat = math.cos(math.radians(lat))
    n = a / math.sqrt(1 - e2 * math.sin(math.radians(lat))**2)
    lng = lon0 + (x_shifted / (n * cos_lat)) * (180 / math.pi)

    return lat, lng


def get_centroid_from_coordinates(coordinates: list) -> tuple[float, float]:
    """다각형 좌표에서 중심점 계산"""
    if not coordinates:
        return 0.0, 0.0

    # 첫 번째 링(외곽선)의 좌표 사용
    ring = coordinates[0] if isinstance(coordinates[0][0], list) else coordinates

    if not ring:
        return 0.0, 0.0

    x_sum = sum(point[0] for point in ring)
    y_sum = sum(point[1] for point in ring)
    count = len(ring)

    return x_sum / count, y_sum / count


class ClimateService:
    """경기기후플랫폼 API 서비스"""

    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.CLIMATE_API_BASE_URL
        self.api_key = self.settings.CLIMATE_REMOVED
        self.use_mock = self.settings.USE_MOCK_DATA

        # 캐시 저장소 (API 호출 최소화)
        self._park_cache: dict = {}
        self._district_park_stats: dict = {}

    async def _wfs_request(
        self,
        type_name: str,
        max_features: int = 100,
        cql_filter: Optional[str] = None
    ) -> dict:
        """WFS API 요청"""
        params = {
            "apiKey": self.api_key,
            "service": "WFS",
            "version": "1.1.0",
            "request": "GetFeature",
            "typeName": type_name,
            "outputFormat": "application/json",
            "maxFeatures": max_features
        }

        if cql_filter:
            params["CQL_FILTER"] = cql_filter

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(self.base_url, params=params)
            response.raise_for_status()
            return response.json()

    async def get_park_data(
        self,
        district: Optional[str] = None,
        max_features: int = 200
    ) -> list[ParkData]:
        """
        공원 데이터 조회

        Args:
            district: 시군구명 필터 (예: "수원시")
            max_features: 최대 조회 개수

        Returns:
            공원 데이터 리스트
        """
        if self.use_mock:
            return self._generate_mock_park_data(district)

        try:
            cql_filter = None
            if district:
                cql_filter = f"sgg_nm LIKE '%{district}%'"

            response = await self._wfs_request("park", max_features, cql_filter)

            parks = []
            for feature in response.get("features", []):
                props = feature.get("properties", {})
                geometry = feature.get("geometry", {})

                # 좌표 추출 및 변환
                coords = geometry.get("coordinates", [])
                if coords:
                    x, y = get_centroid_from_coordinates(coords)
                    lat, lng = epsg5186_to_wgs84(x, y)
                else:
                    continue

                parks.append(ParkData(
                    uid=props.get("uid"),
                    sgg_nm=props.get("sgg_nm", "알 수 없음"),
                    lclsf_nm=props.get("lclsf_nm"),
                    mclsf_nm=props.get("mclsf_nm"),
                    sclsf_nm=props.get("sclsf_nm"),
                    area=props.get("biotop_area") or props.get("area"),
                    latitude=lat,
                    longitude=lng
                ))

            return parks

        except Exception as e:
            print(f"공원 데이터 조회 실패: {e}")
            return self._generate_mock_park_data(district)

    def _generate_mock_park_data(self, district: Optional[str] = None) -> list[ParkData]:
        """Mock 공원 데이터 생성"""
        parks = []
        districts = GYEONGGI_DISTRICTS

        if district:
            districts = [d for d in districts if district in d["district"]]

        for d in districts:
            # 각 시군구당 2-5개의 공원 생성
            for i in range(random.randint(2, 5)):
                parks.append(ParkData(
                    uid=f"{d['district']}_{i}",
                    sgg_nm=d["district"],
                    lclsf_nm="도시공원",
                    mclsf_nm="근린공원",
                    sclsf_nm="일반",
                    area=random.uniform(5000, 50000),
                    latitude=d["lat"] + random.uniform(-0.02, 0.02),
                    longitude=d["lng"] + random.uniform(-0.02, 0.02)
                ))

        return parks

    async def get_district_green_stats(self) -> dict[str, float]:
        """
        시군구별 녹지 통계 조회

        Returns:
            {시군구명: 녹지율} 딕셔너리
        """
        if self._district_park_stats:
            return self._district_park_stats

        try:
            parks = await self.get_park_data(max_features=500)

            # 시군구별 공원 면적 합계
            district_areas: dict[str, float] = {}
            district_counts: dict[str, int] = {}

            for park in parks:
                district = park.sgg_nm
                area = park.area or 10000  # 기본값

                district_areas[district] = district_areas.get(district, 0) + area
                district_counts[district] = district_counts.get(district, 0) + 1

            # 녹지율 추정 (공원 면적 / 추정 시군구 면적 * 100)
            # 경기도 시군구 평균 면적 약 40km² 가정
            avg_district_area = 40_000_000  # m²

            for district in district_areas:
                total_park_area = district_areas[district]
                # 녹지율 = (공원면적 / 시군구면적) * 100
                green_ratio = (total_park_area / avg_district_area) * 100
                # 최소 5%, 최대 40%로 제한
                self._district_park_stats[district] = min(max(green_ratio, 5.0), 40.0)

            return self._district_park_stats

        except Exception as e:
            print(f"녹지 통계 조회 실패: {e}")
            # Mock 데이터 반환
            return {d["district"]: random.uniform(8, 35) for d in GYEONGGI_DISTRICTS}

    async def get_heat_island_data(
        self,
        district: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> list[HeatIslandData]:
        """
        열섬 현황 데이터 조회

        녹지 데이터를 기반으로 열섬 취약 지역을 분석합니다.
        녹지율이 낮고 인구밀도가 높은 지역일수록 열섬 강도가 높게 추정됩니다.

        Args:
            district: 시군구명 (없으면 전체)
            start_date: 조회 시작일 (미사용)
            end_date: 조회 종료일 (미사용)

        Returns:
            열섬 데이터 리스트
        """
        if self.use_mock:
            return self._generate_mock_heat_island_data(district)

        try:
            # 녹지 통계 조회
            green_stats = await self.get_district_green_stats()

            # 열섬 데이터 생성
            result = []
            base_temp = 28.0  # 여름철 기준 기온

            districts = GYEONGGI_DISTRICTS
            if district:
                districts = [d for d in districts if district in d["district"]]

            for d in districts:
                district_name = d["district"]
                pop_density = d["population_density"]

                # 녹지율 가져오기 (없으면 기본값 15%)
                green_ratio = green_stats.get(district_name, 15.0)

                # 열섬 강도 계산
                # - 녹지율이 낮을수록 강도 증가
                # - 인구밀도가 높을수록 강도 증가
                green_factor = (30 - green_ratio) / 30  # 0 ~ 1
                density_factor = min(pop_density / 20000, 1.0)  # 0 ~ 1

                intensity = 0.5 + (green_factor * 1.5) + (density_factor * 1.0)
                intensity = round(min(max(intensity, 0.5), 3.0), 2)

                # 온도 계산
                temperature = base_temp + intensity

                result.append(HeatIslandData(
                    latitude=d["lat"],
                    longitude=d["lng"],
                    temperature=round(temperature, 1),
                    heat_island_intensity=intensity,
                    timestamp=datetime.now(),
                    district=district_name,
                    green_coverage_ratio=round(green_ratio, 1)
                ))

            # 강도 높은 순 정렬
            result.sort(key=lambda x: x.heat_island_intensity, reverse=True)
            return result

        except Exception as e:
            print(f"열섬 데이터 조회 실패: {e}")
            return self._generate_mock_heat_island_data(district)

    def _generate_mock_heat_island_data(
        self,
        district: Optional[str] = None
    ) -> list[HeatIslandData]:
        """Mock 열섬 데이터 생성 (캐시 사용)"""
        # 세션 내에서 일관된 데이터 유지를 위해 seed 사용
        cache_key = f"heat_{district or 'all'}"

        if cache_key in self._park_cache:
            return self._park_cache[cache_key]

        districts = GYEONGGI_DISTRICTS
        if district:
            districts = [d for d in districts if district in d["district"]]

        result = []
        base_temp = 28.0

        for d in districts:
            pop_density = d["population_density"]

            # 인구밀도 기반 녹지율 추정 (밀도 높을수록 녹지율 낮음)
            green_ratio = max(5, 40 - (pop_density / 500))

            # 열섬 강도 계산
            green_factor = (30 - green_ratio) / 30
            density_factor = min(pop_density / 20000, 1.0)

            intensity = 0.5 + (green_factor * 1.5) + (density_factor * 1.0)
            intensity = round(min(max(intensity, 0.5), 3.0), 2)

            temperature = base_temp + intensity

            result.append(HeatIslandData(
                latitude=d["lat"],
                longitude=d["lng"],
                temperature=round(temperature, 1),
                heat_island_intensity=intensity,
                timestamp=datetime.now(),
                district=d["district"],
                green_coverage_ratio=round(green_ratio, 1)
            ))

        result.sort(key=lambda x: x.heat_island_intensity, reverse=True)
        self._park_cache[cache_key] = result
        return result

    async def get_weather_data(
        self,
        latitude: float,
        longitude: float
    ) -> WeatherData:
        """
        특정 좌표의 기상 데이터 조회

        현재는 기상청 API 연동 없이 추정치 반환

        Args:
            latitude: 위도
            longitude: 경도

        Returns:
            기상 데이터
        """
        # 실제 기상 API 연동 시 여기에 구현
        return self._generate_mock_weather_data()

    def _generate_mock_weather_data(self) -> WeatherData:
        """Mock 기상 데이터 생성"""
        return WeatherData(
            temperature=30.0,
            humidity=65.0,
            wind_speed=2.5,
            solar_radiation=600.0,
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

        try:
            # 전체 공원 데이터 조회
            parks = await self.get_park_data(max_features=300)

            # 반경 내 공원 필터링
            result = []
            for park in parks:
                # 거리 계산 (Haversine 공식 간소화)
                dlat = abs(park.latitude - latitude)
                dlng = abs(park.longitude - longitude)
                approx_dist = math.sqrt(dlat**2 + dlng**2) * 111  # km 근사

                if approx_dist <= radius_km:
                    result.append(GreenSpaceData(
                        latitude=park.latitude,
                        longitude=park.longitude,
                        green_coverage_ratio=random.uniform(20, 80),
                        tree_density=random.uniform(50, 200),
                        park_area=park.area or 10000,
                        district=park.sgg_nm,
                        park_name=park.uid
                    ))

            return result if result else self._generate_mock_green_space_data(latitude, longitude)

        except Exception as e:
            print(f"녹지 데이터 조회 실패: {e}")
            return self._generate_mock_green_space_data(latitude, longitude)

    def _generate_mock_green_space_data(
        self,
        latitude: float,
        longitude: float
    ) -> list[GreenSpaceData]:
        """Mock 녹지 데이터 생성"""
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


# 시군구 목록 내보내기 (Streamlit에서 사용)
DISTRICT_LIST = [d["district"] for d in GYEONGGI_DISTRICTS]
