"""
시민 참여 관련 API 라우터
활동 피드, 주간 챌린지, 랭킹 등
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List
from datetime import datetime, timedelta

from app.models.database import get_db
from app.models.models import ActivityFeed, WeeklyChallenge, User, ActionType, Badge, UserBadge, BadgeType
from pydantic import BaseModel


router = APIRouter(prefix="/api/citizen", tags=["citizen"])


# ============== Pydantic 스키마 ==============
class ActivityFeedResponse(BaseModel):
    id: int
    user_name: str
    action_type: str
    mission_title: str | None
    points_earned: int
    created_at: datetime

    class Config:
        from_attributes = True


class WeeklyChallengeResponse(BaseModel):
    id: int
    title: str
    description: str | None
    goal_count: int
    current_progress: int
    reward_points: int
    progress_percentage: float

    class Config:
        from_attributes = True


class LeaderboardEntry(BaseModel):
    rank: int
    user_id: int
    username: str
    total_points: int
    level: int
    completed_missions: int
    cooling_contribution: float
    trees_planted: int


class BadgeResponse(BaseModel):
    id: int
    badge_type: str
    name: str
    description: str | None
    icon: str | None
    requirement: str | None
    points: int
    is_earned: bool = False
    earned_at: datetime | None = None

    class Config:
        from_attributes = True


# ============== API 엔드포인트 ==============

@router.get("/activity-feed", response_model=List[ActivityFeedResponse])
async def get_activity_feed(
    limit: int = 15,
    db: Session = Depends(get_db)
):
    """최근 활동 피드 조회"""
    activities = db.query(ActivityFeed).join(User).order_by(
        desc(ActivityFeed.created_at)
    ).limit(limit).all()

    return [
        ActivityFeedResponse(
            id=activity.id,
            user_name=_mask_username(activity.user.username),
            action_type=activity.action_type.value,
            mission_title=activity.mission_title,
            points_earned=activity.points_earned,
            created_at=activity.created_at
        )
        for activity in activities
    ]


@router.get("/challenges", response_model=List[WeeklyChallengeResponse])
async def get_weekly_challenges(
    db: Session = Depends(get_db)
):
    """활성 주간 챌린지 조회"""
    challenges = db.query(WeeklyChallenge).filter(
        WeeklyChallenge.is_active == True
    ).all()

    return [
        WeeklyChallengeResponse(
            id=challenge.id,
            title=challenge.title,
            description=challenge.description,
            goal_count=challenge.goal_count,
            current_progress=challenge.current_progress,
            reward_points=challenge.reward_points,
            progress_percentage=round(
                (challenge.current_progress / challenge.goal_count * 100) if challenge.goal_count > 0 else 0,
                1
            )
        )
        for challenge in challenges
    ]


@router.get("/leaderboard", response_model=List[LeaderboardEntry])
async def get_leaderboard(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """랭킹 조회 (TOP N)"""
    users = db.query(User).filter(
        User.is_active == True
    ).order_by(
        desc(User.points)
    ).limit(limit).all()

    return [
        LeaderboardEntry(
            rank=idx + 1,
            user_id=user.id,
            username=_mask_username(user.username),
            total_points=user.points,
            level=user.level,
            completed_missions=user.completed_missions_count,
            cooling_contribution=user.cooling_contribution,
            trees_planted=user.trees_planted
        )
        for idx, user in enumerate(users)
    ]


@router.get("/user-stats/{user_id}")
async def get_user_stats(
    user_id: int,
    db: Session = Depends(get_db)
):
    """특정 사용자 통계 조회"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "user_id": user.id,
        "username": user.username,
        "points": user.points,
        "level": user.level,
        "completed_missions": user.completed_missions_count,
        "cooling_contribution": user.cooling_contribution,
        "trees_planted": user.trees_planted,
        "created_at": user.created_at
    }


@router.get("/badges", response_model=List[BadgeResponse])
async def get_all_badges(
    user_id: int | None = None,
    db: Session = Depends(get_db)
):
    """모든 배지 조회 (특정 사용자 획득 여부 포함)"""
    badges = db.query(Badge).all()

    # 사용자가 획득한 배지 조회
    user_badge_map = {}
    if user_id:
        user_badges = db.query(UserBadge).filter(UserBadge.user_id == user_id).all()
        user_badge_map = {ub.badge_id: ub.earned_at for ub in user_badges}

    return [
        BadgeResponse(
            id=badge.id,
            badge_type=badge.badge_type.value,
            name=badge.name,
            description=badge.description,
            icon=badge.icon,
            requirement=badge.requirement,
            points=badge.points,
            is_earned=badge.id in user_badge_map,
            earned_at=user_badge_map.get(badge.id)
        )
        for badge in badges
    ]


@router.get("/badges/user/{user_id}", response_model=List[BadgeResponse])
async def get_user_badges(
    user_id: int,
    db: Session = Depends(get_db)
):
    """특정 사용자가 획득한 배지만 조회"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_badges = db.query(UserBadge).filter(UserBadge.user_id == user_id).all()

    return [
        BadgeResponse(
            id=ub.badge.id,
            badge_type=ub.badge.badge_type.value,
            name=ub.badge.name,
            description=ub.badge.description,
            icon=ub.badge.icon,
            requirement=ub.badge.requirement,
            points=ub.badge.points,
            is_earned=True,
            earned_at=ub.earned_at
        )
        for ub in user_badges
    ]


# ============== Helper Functions ==============
def _mask_username(username: str) -> str:
    """사용자 이름 마스킹 (개인정보 보호)"""
    if len(username) <= 2:
        return username[0] + "*"
    return username[0] + "*" + username[-1]
