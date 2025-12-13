"""쿨링 스팟 API 라우터"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

from app.models import get_db, CoolingSpot, EffectMeasurement

router = APIRouter(prefix="/cooling-spots", tags=["Cooling Spots"])


# ============== Schemas ==============

class CoolingSpotCreate(BaseModel):
    name: str
    description: Optional[str] = None
    latitude: float
    longitude: float
    address: Optional[str] = None
    heat_island_intensity: Optional[float] = None
    current_temperature: Optional[float] = None
    target_temperature: Optional[float] = None
    green_coverage_ratio: float = 0.0
    tree_count: int = 0


class CoolingSpotResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    latitude: float
    longitude: float
    address: Optional[str]
    heat_island_intensity: Optional[float]
    current_temperature: Optional[float]
    target_temperature: Optional[float]
    green_coverage_ratio: float
    tree_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CoolingSpotUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    heat_island_intensity: Optional[float] = None
    current_temperature: Optional[float] = None
    target_temperature: Optional[float] = None
    green_coverage_ratio: Optional[float] = None
    tree_count: Optional[int] = None


class MeasurementCreate(BaseModel):
    temperature: float
    humidity: Optional[float] = None
    heat_index: Optional[float] = None
    nearby_avg_temperature: Optional[float] = None
    cooling_effect: Optional[float] = None
    wind_speed: Optional[float] = None
    solar_radiation: Optional[float] = None


class MeasurementResponse(BaseModel):
    id: int
    cooling_spot_id: int
    temperature: float
    humidity: Optional[float]
    heat_index: Optional[float]
    nearby_avg_temperature: Optional[float]
    cooling_effect: Optional[float]
    wind_speed: Optional[float]
    solar_radiation: Optional[float]
    measured_at: datetime

    class Config:
        from_attributes = True


# ============== Cooling Spots Endpoints ==============

@router.get("/", response_model=list[CoolingSpotResponse])
async def list_cooling_spots(
    min_intensity: Optional[float] = Query(None, description="최소 열섬 강도"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """쿨링 스팟 목록 조회"""
    query = db.query(CoolingSpot)

    if min_intensity is not None:
        query = query.filter(CoolingSpot.heat_island_intensity >= min_intensity)

    spots = query.order_by(CoolingSpot.heat_island_intensity.desc()).offset(skip).limit(limit).all()
    return spots


@router.post("/", response_model=CoolingSpotResponse)
async def create_cooling_spot(
    spot: CoolingSpotCreate,
    db: Session = Depends(get_db)
):
    """새 쿨링 스팟 생성"""
    db_spot = CoolingSpot(**spot.model_dump())
    db.add(db_spot)
    db.commit()
    db.refresh(db_spot)
    return db_spot


@router.get("/{spot_id}", response_model=CoolingSpotResponse)
async def get_cooling_spot(
    spot_id: int,
    db: Session = Depends(get_db)
):
    """특정 쿨링 스팟 조회"""
    spot = db.query(CoolingSpot).filter(CoolingSpot.id == spot_id).first()
    if not spot:
        raise HTTPException(status_code=404, detail="Cooling spot not found")
    return spot


@router.patch("/{spot_id}", response_model=CoolingSpotResponse)
async def update_cooling_spot(
    spot_id: int,
    update: CoolingSpotUpdate,
    db: Session = Depends(get_db)
):
    """쿨링 스팟 정보 업데이트"""
    spot = db.query(CoolingSpot).filter(CoolingSpot.id == spot_id).first()
    if not spot:
        raise HTTPException(status_code=404, detail="Cooling spot not found")

    update_data = update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(spot, field, value)

    db.commit()
    db.refresh(spot)
    return spot


@router.delete("/{spot_id}")
async def delete_cooling_spot(
    spot_id: int,
    db: Session = Depends(get_db)
):
    """쿨링 스팟 삭제"""
    spot = db.query(CoolingSpot).filter(CoolingSpot.id == spot_id).first()
    if not spot:
        raise HTTPException(status_code=404, detail="Cooling spot not found")

    db.delete(spot)
    db.commit()
    return {"message": "Cooling spot deleted successfully"}


# ============== Measurements Endpoints ==============

@router.get("/{spot_id}/measurements", response_model=list[MeasurementResponse])
async def list_measurements(
    spot_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """특정 쿨링 스팟의 측정 데이터 조회"""
    spot = db.query(CoolingSpot).filter(CoolingSpot.id == spot_id).first()
    if not spot:
        raise HTTPException(status_code=404, detail="Cooling spot not found")

    measurements = db.query(EffectMeasurement).filter(
        EffectMeasurement.cooling_spot_id == spot_id
    ).order_by(EffectMeasurement.measured_at.desc()).offset(skip).limit(limit).all()

    return measurements


@router.post("/{spot_id}/measurements", response_model=MeasurementResponse)
async def create_measurement(
    spot_id: int,
    measurement: MeasurementCreate,
    db: Session = Depends(get_db)
):
    """새 측정 데이터 추가"""
    spot = db.query(CoolingSpot).filter(CoolingSpot.id == spot_id).first()
    if not spot:
        raise HTTPException(status_code=404, detail="Cooling spot not found")

    db_measurement = EffectMeasurement(
        cooling_spot_id=spot_id,
        **measurement.model_dump()
    )
    db.add(db_measurement)
    db.commit()
    db.refresh(db_measurement)
    return db_measurement
