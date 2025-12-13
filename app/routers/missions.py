"""미션 API 라우터"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

from app.models import get_db, Mission, CoolingSpot
from app.models.models import MissionStatus, MissionType

router = APIRouter(prefix="/missions", tags=["Missions"])


# ============== Schemas ==============

class MissionCreate(BaseModel):
    title: str
    description: Optional[str] = None
    mission_type: MissionType
    cooling_spot_id: int
    points_reward: int = 10
    difficulty: int = 1
    estimated_cooling_effect: Optional[float] = None
    ai_reasoning: Optional[str] = None
    priority_score: Optional[float] = None


class MissionResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    mission_type: MissionType
    status: MissionStatus
    points_reward: int
    difficulty: int
    estimated_cooling_effect: Optional[float]
    ai_reasoning: Optional[str]
    priority_score: Optional[float]
    cooling_spot_id: int
    user_id: Optional[int]
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class MissionUpdate(BaseModel):
    status: Optional[MissionStatus] = None
    user_id: Optional[int] = None


# ============== Endpoints ==============

@router.get("/", response_model=list[MissionResponse])
async def list_missions(
    status: Optional[MissionStatus] = Query(None, description="상태 필터"),
    mission_type: Optional[MissionType] = Query(None, description="미션 타입 필터"),
    cooling_spot_id: Optional[int] = Query(None, description="쿨링스팟 ID 필터"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """미션 목록 조회"""
    query = db.query(Mission)

    if status:
        query = query.filter(Mission.status == status)
    if mission_type:
        query = query.filter(Mission.mission_type == mission_type)
    if cooling_spot_id:
        query = query.filter(Mission.cooling_spot_id == cooling_spot_id)

    missions = query.order_by(Mission.priority_score.desc()).offset(skip).limit(limit).all()
    return missions


@router.post("/", response_model=MissionResponse)
async def create_mission(
    mission: MissionCreate,
    db: Session = Depends(get_db)
):
    """새 미션 생성"""
    # 쿨링스팟 존재 확인
    cooling_spot = db.query(CoolingSpot).filter(CoolingSpot.id == mission.cooling_spot_id).first()
    if not cooling_spot:
        raise HTTPException(status_code=404, detail="Cooling spot not found")

    db_mission = Mission(**mission.model_dump())
    db.add(db_mission)
    db.commit()
    db.refresh(db_mission)
    return db_mission


@router.get("/{mission_id}", response_model=MissionResponse)
async def get_mission(
    mission_id: int,
    db: Session = Depends(get_db)
):
    """특정 미션 조회"""
    mission = db.query(Mission).filter(Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    return mission


@router.patch("/{mission_id}", response_model=MissionResponse)
async def update_mission(
    mission_id: int,
    update: MissionUpdate,
    db: Session = Depends(get_db)
):
    """미션 상태 업데이트"""
    mission = db.query(Mission).filter(Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")

    update_data = update.model_dump(exclude_unset=True)

    # 완료 상태로 변경 시 완료 시간 기록
    if update_data.get("status") == MissionStatus.COMPLETED:
        update_data["completed_at"] = datetime.utcnow()

    for field, value in update_data.items():
        setattr(mission, field, value)

    db.commit()
    db.refresh(mission)
    return mission


@router.delete("/{mission_id}")
async def delete_mission(
    mission_id: int,
    db: Session = Depends(get_db)
):
    """미션 삭제"""
    mission = db.query(Mission).filter(Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")

    db.delete(mission)
    db.commit()
    return {"message": "Mission deleted successfully"}
