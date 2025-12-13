"""AI Agent API 라우터"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel

from app.models import get_db, Mission, CoolingSpot
from app.models.models import MissionType
from app.services.mission_agent import MissionAgent, GeneratedMission

router = APIRouter(prefix="/agent", tags=["AI Agent"])

# Agent 인스턴스
mission_agent = MissionAgent(use_llm=False)


# ============== Schemas ==============

class MissionGenerateRequest(BaseModel):
    district: Optional[str] = None
    mission_type: Optional[MissionType] = None
    top_n: int = 5


class LocationMissionRequest(BaseModel):
    latitude: float
    longitude: float


class SaveMissionRequest(BaseModel):
    mission: GeneratedMission
    cooling_spot_id: Optional[int] = None


# ============== Endpoints ==============

@router.post("/generate", response_model=list[GeneratedMission])
async def generate_missions(
    request: MissionGenerateRequest
):
    """
    AI가 우선순위 높은 지역에 미션을 자동 생성

    - district: 특정 지역만 대상 (없으면 전체)
    - mission_type: 특정 미션 타입만 생성 (없으면 최적 타입 자동 선택)
    - top_n: 생성할 미션 수
    """
    missions = await mission_agent.generate_missions_batch(top_n=request.top_n)

    # 지역 필터 적용
    if request.district:
        missions = [m for m in missions if request.district in m.district]

    # 미션 타입 필터 적용
    if request.mission_type:
        missions = [m for m in missions if m.mission_type == request.mission_type]

    return missions


@router.post("/suggest", response_model=list[GeneratedMission])
async def suggest_missions_for_location(
    request: LocationMissionRequest
):
    """
    특정 좌표에 대한 모든 타입의 미션 제안

    - latitude: 위도
    - longitude: 경도

    해당 위치에 적용 가능한 5가지 미션 타입별 제안을 반환합니다.
    """
    missions = await mission_agent.suggest_mission_for_location(
        latitude=request.latitude,
        longitude=request.longitude
    )
    return missions


@router.get("/analyze/{district}")
async def analyze_district(
    district: str
):
    """
    특정 지역의 열섬 상황 분석

    AI가 해당 지역의 열섬 데이터를 분석하고
    우선순위 점수, 권장 솔루션 등을 반환합니다.
    """
    from app.services.climate_service import ClimateService

    climate_service = ClimateService()
    heat_data_list = climate_service._generate_mock_heat_island_data(district)

    if not heat_data_list:
        raise HTTPException(status_code=404, detail=f"District '{district}' not found")

    heat_data = heat_data_list[0]
    analysis = await mission_agent.analyze_area(heat_data)

    return {
        "district": district,
        "heat_island_intensity": heat_data.heat_island_intensity,
        "temperature": heat_data.temperature,
        "priority_score": analysis.priority_score,
        "characteristics": analysis.characteristics.value,
        "recommended_solutions": [s.value for s in analysis.recommended_solutions],
        "analysis": analysis.analysis_reasoning
    }


@router.post("/save", response_model=dict)
async def save_generated_mission(
    request: SaveMissionRequest,
    db: Session = Depends(get_db)
):
    """
    AI가 생성한 미션을 DB에 저장

    cooling_spot_id가 없으면 자동으로 CoolingSpot도 생성합니다.
    """
    mission_data = request.mission

    # CoolingSpot 확인 또는 생성
    if request.cooling_spot_id:
        cooling_spot = db.query(CoolingSpot).filter(
            CoolingSpot.id == request.cooling_spot_id
        ).first()
        if not cooling_spot:
            raise HTTPException(status_code=404, detail="Cooling spot not found")
    else:
        # 좌표로 기존 CoolingSpot 검색
        cooling_spot = db.query(CoolingSpot).filter(
            CoolingSpot.latitude == mission_data.latitude,
            CoolingSpot.longitude == mission_data.longitude
        ).first()

        # 없으면 새로 생성
        if not cooling_spot:
            cooling_spot = CoolingSpot(
                name=f"{mission_data.district} 쿨링스팟",
                latitude=mission_data.latitude,
                longitude=mission_data.longitude,
                address=mission_data.district,
                heat_island_intensity=2.0  # 기본값
            )
            db.add(cooling_spot)
            db.commit()
            db.refresh(cooling_spot)

    # Mission 생성
    db_mission = Mission(
        title=mission_data.title,
        description=mission_data.description,
        mission_type=mission_data.mission_type,
        points_reward=mission_data.points_reward,
        difficulty=mission_data.difficulty,
        estimated_cooling_effect=mission_data.estimated_cooling_effect,
        priority_score=mission_data.priority_score,
        ai_reasoning=mission_data.ai_reasoning,
        cooling_spot_id=cooling_spot.id
    )
    db.add(db_mission)
    db.commit()
    db.refresh(db_mission)

    return {
        "message": "Mission saved successfully",
        "mission_id": db_mission.id,
        "cooling_spot_id": cooling_spot.id
    }


@router.post("/auto-generate")
async def auto_generate_and_save(
    top_n: int = Query(5, ge=1, le=20, description="생성할 미션 수"),
    db: Session = Depends(get_db)
):
    """
    AI가 미션을 자동 생성하고 DB에 저장

    우선순위 높은 지역부터 자동으로 미션을 생성하고 저장합니다.
    """
    missions = await mission_agent.generate_missions_batch(top_n=top_n)

    saved_missions = []
    for mission_data in missions:
        # CoolingSpot 생성/조회
        cooling_spot = db.query(CoolingSpot).filter(
            CoolingSpot.latitude == mission_data.latitude,
            CoolingSpot.longitude == mission_data.longitude
        ).first()

        if not cooling_spot:
            cooling_spot = CoolingSpot(
                name=f"{mission_data.district} 쿨링스팟",
                latitude=mission_data.latitude,
                longitude=mission_data.longitude,
                address=mission_data.district,
                heat_island_intensity=2.0
            )
            db.add(cooling_spot)
            db.commit()
            db.refresh(cooling_spot)

        # Mission 생성
        db_mission = Mission(
            title=mission_data.title,
            description=mission_data.description,
            mission_type=mission_data.mission_type,
            points_reward=mission_data.points_reward,
            difficulty=mission_data.difficulty,
            estimated_cooling_effect=mission_data.estimated_cooling_effect,
            priority_score=mission_data.priority_score,
            ai_reasoning=mission_data.ai_reasoning,
            cooling_spot_id=cooling_spot.id
        )
        db.add(db_mission)
        db.commit()
        db.refresh(db_mission)

        saved_missions.append({
            "mission_id": db_mission.id,
            "title": db_mission.title,
            "cooling_spot_id": cooling_spot.id,
            "priority_score": mission_data.priority_score
        })

    return {
        "message": f"Successfully generated and saved {len(saved_missions)} missions",
        "missions": saved_missions
    }
