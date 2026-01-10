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


class ActionType(str, enum.Enum):
    """활동 피드 액션 타입"""
    MISSION_COMPLETE = "mission_complete"
    MISSION_START = "mission_start"
    LEVEL_UP = "level_up"
    BADGE_EARNED = "badge_earned"


class User(Base):
    """사용자 모델"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    points = Column(Integer, default=0)  # 미션 완료 포인트
    level = Column(Integer, default=1)  # 사용자 레벨
    completed_missions_count = Column(Integer, default=0)  # 완료한 미션 수
    cooling_contribution = Column(Float, default=0.0)  # 총 냉각 기여도 (°C)
    trees_planted = Column(Integer, default=0)  # 심은 나무 수
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationships
    missions = relationship("Mission", back_populates="user")
    activity_feeds = relationship("ActivityFeed", back_populates="user")


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


class ActivityFeed(Base):
    """시민 활동 피드 모델"""
    __tablename__ = "activity_feeds"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action_type = Column(Enum(ActionType), nullable=False)
    mission_title = Column(String(200), nullable=True)  # 미션 관련일 경우
    points_earned = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User", back_populates="activity_feeds")


class WeeklyChallenge(Base):
    """주간 챌린지 모델"""
    __tablename__ = "weekly_challenges"

    id = Column(Integer, primary_key=True, index=True)
    week_number = Column(Integer, nullable=False, index=True)  # 주차 (년도 + 주)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    goal_count = Column(Integer, nullable=False)  # 목표 수량
    current_progress = Column(Integer, default=0)  # 현재 진행도
    reward_points = Column(Integer, default=0)  # 보상 포인트
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class BadgeType(str, enum.Enum):
    """배지 타입"""
    FIRST_MISSION = "first_mission"  # 첫 미션 완료
    MISSIONS_10 = "missions_10"  # 10개 미션 완료
    MISSIONS_50 = "missions_50"  # 50개 미션 완료
    MISSIONS_100 = "missions_100"  # 100개 미션 완료
    TREE_LOVER = "tree_lover"  # 나무 50그루 심기
    COOLING_HERO = "cooling_hero"  # 총 10°C 냉각 기여
    LEVEL_5 = "level_5"  # 레벨 5 달성
    LEVEL_10 = "level_10"  # 레벨 10 달성
    WEEKLY_CHAMPION = "weekly_champion"  # 주간 챌린지 완료
    GREEN_ROOF_MASTER = "green_roof_master"  # 옥상녹화 전문가


class Badge(Base):
    """배지 마스터 데이터"""
    __tablename__ = "badges"

    id = Column(Integer, primary_key=True, index=True)
    badge_type = Column(Enum(BadgeType), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    icon = Column(String(10))  # 이모지
    requirement = Column(String(200))  # 획득 조건 설명
    points = Column(Integer, default=0)  # 배지 획득 시 보너스 포인트
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user_badges = relationship("UserBadge", back_populates="badge")


class UserBadge(Base):
    """사용자가 획득한 배지"""
    __tablename__ = "user_badges"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    badge_id = Column(Integer, ForeignKey("badges.id"), nullable=False)
    earned_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", backref="badges")
    badge = relationship("Badge", back_populates="user_badges")
