"""효과 측정 API 라우터"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.models import get_db
from app.services.effect_service import (
    EffectService,
    EffectSummary,
    OverallStats,
    TimeSeriesData,
    ComparisonData,
    RegionalStats
)

router = APIRouter(prefix="/effects", tags=["Effect Measurement"])


@router.get("/stats", response_model=OverallStats)
async def get_overall_stats(
    db: Session = Depends(get_db)
):
    """전체 효과 통계 조회"""
    service = EffectService(db)
    return service.get_overall_stats()


@router.get("/summary/{cooling_spot_id}", response_model=EffectSummary)
async def get_cooling_spot_summary(
    cooling_spot_id: int,
    db: Session = Depends(get_db)
):
    """특정 쿨링스팟의 효과 요약"""
    service = EffectService(db)
    return service.get_cooling_spot_summary(cooling_spot_id)


@router.get("/time-series", response_model=list[TimeSeriesData])
async def get_time_series_data(
    cooling_spot_id: Optional[int] = Query(None, description="쿨링스팟 ID"),
    days: int = Query(30, ge=1, le=365, description="조회 기간 (일)"),
    db: Session = Depends(get_db)
):
    """시계열 데이터 조회"""
    service = EffectService(db)
    return service.get_time_series(cooling_spot_id, days)


@router.get("/comparison/{cooling_spot_id}", response_model=list[ComparisonData])
async def get_before_after_comparison(
    cooling_spot_id: int,
    db: Session = Depends(get_db)
):
    """설치 전후 비교 데이터"""
    service = EffectService(db)
    return service.get_before_after_comparison(cooling_spot_id)


@router.get("/regional", response_model=list[RegionalStats])
async def get_regional_stats(
    db: Session = Depends(get_db)
):
    """지역별 통계"""
    service = EffectService(db)
    return service.get_regional_stats()


@router.get("/mission-types")
async def get_mission_type_effectiveness(
    db: Session = Depends(get_db)
):
    """미션 타입별 효과 분석"""
    service = EffectService(db)
    return service.get_mission_type_effectiveness()


@router.get("/environmental-impact")
async def get_environmental_impact(
    db: Session = Depends(get_db)
):
    """환경 영향 분석"""
    service = EffectService(db)
    return service.calculate_environmental_impact()
