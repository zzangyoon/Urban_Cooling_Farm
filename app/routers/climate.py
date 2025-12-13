"""기후 데이터 API 라우터"""
from fastapi import APIRouter, Query
from typing import Optional
from datetime import datetime

from app.services.climate_service import ClimateService, HeatIslandData, WeatherData, GreenSpaceData

router = APIRouter(prefix="/climate", tags=["Climate"])

climate_service = ClimateService()


@router.get("/heat-island", response_model=list[HeatIslandData])
async def get_heat_island_data(
    district: Optional[str] = Query(None, description="시군구명 필터"),
    start_date: Optional[datetime] = Query(None, description="조회 시작일"),
    end_date: Optional[datetime] = Query(None, description="조회 종료일")
):
    """열섬 현황 데이터 조회"""
    return await climate_service.get_heat_island_data(district, start_date, end_date)


@router.get("/weather", response_model=WeatherData)
async def get_weather_data(
    latitude: float = Query(..., description="위도"),
    longitude: float = Query(..., description="경도")
):
    """특정 좌표의 기상 데이터 조회"""
    return await climate_service.get_weather_data(latitude, longitude)


@router.get("/green-space", response_model=list[GreenSpaceData])
async def get_green_space_data(
    latitude: float = Query(..., description="중심 위도"),
    longitude: float = Query(..., description="중심 경도"),
    radius_km: float = Query(1.0, description="검색 반경 (km)")
):
    """특정 좌표 주변 녹지 데이터 조회"""
    return await climate_service.get_green_space_data(latitude, longitude, radius_km)


@router.get("/priority-areas", response_model=list[HeatIslandData])
async def get_cooling_priority_areas(
    top_n: int = Query(10, description="상위 N개 지역", ge=1, le=50)
):
    """냉각 우선순위가 높은 지역 조회"""
    return await climate_service.get_cooling_priority_areas(top_n)
