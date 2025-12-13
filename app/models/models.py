from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from .database import Base


class MissionStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class MissionType(str, enum.Enum):
    TREE_PLANTING = "tree_planting"          # 나무 심기
    GREEN_ROOF = "green_roof"                # 옥상 녹화
    COOL_PAVEMENT = "cool_pavement"          # 쿨페이브먼트
    WATER_FEATURE = "water_feature"          # 수경시설
    SHADE_STRUCTURE = "shade_structure"      # 그늘막 설치


class User(Base):
    """사용자 모델"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    points = Column(Integer, default=0)  # 미션 완료 포인트
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationships
    missions = relationship("Mission", back_populates="user")


class CoolingSpot(Base):
    """쿨링 스팟 (열섬 완화 지점) 모델"""
    __tablename__ = "cooling_spots"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(String(255))

    # 열섬 관련 데이터
    heat_island_intensity = Column(Float)  # 열섬 강도 (주변 대비 온도차)
    current_temperature = Column(Float)    # 현재 온도
    target_temperature = Column(Float)     # 목표 온도

    # 녹지 정보
    green_coverage_ratio = Column(Float, default=0.0)  # 녹지율 (0-100)
    tree_count = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    missions = relationship("Mission", back_populates="cooling_spot")
    measurements = relationship("EffectMeasurement", back_populates="cooling_spot")


class Mission(Base):
    """AI Agent가 생성하는 미션 모델"""
    __tablename__ = "missions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    mission_type = Column(Enum(MissionType), nullable=False)
    status = Column(Enum(MissionStatus), default=MissionStatus.PENDING)

    # 미션 상세
    points_reward = Column(Integer, default=10)  # 완료 시 보상 포인트
    difficulty = Column(Integer, default=1)       # 난이도 (1-5)
    estimated_cooling_effect = Column(Float)      # 예상 냉각 효과 (도)

    # AI 생성 관련
    ai_reasoning = Column(Text)  # AI가 미션을 생성한 이유
    priority_score = Column(Float)  # 우선순위 점수

    # 관계
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    cooling_spot_id = Column(Integer, ForeignKey("cooling_spots.id"), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="missions")
    cooling_spot = relationship("CoolingSpot", back_populates="missions")


class EffectMeasurement(Base):
    """효과 측정 데이터 모델"""
    __tablename__ = "effect_measurements"

    id = Column(Integer, primary_key=True, index=True)
    cooling_spot_id = Column(Integer, ForeignKey("cooling_spots.id"), nullable=False)

    # 측정 데이터
    temperature = Column(Float, nullable=False)
    humidity = Column(Float)
    heat_index = Column(Float)  # 체감온도

    # 비교 데이터
    nearby_avg_temperature = Column(Float)  # 주변 평균 온도
    cooling_effect = Column(Float)          # 냉각 효과 (주변 대비)

    # 환경 데이터
    wind_speed = Column(Float)
    solar_radiation = Column(Float)

    measured_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    cooling_spot = relationship("CoolingSpot", back_populates="measurements")
