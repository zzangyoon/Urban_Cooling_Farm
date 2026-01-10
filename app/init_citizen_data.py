"""
시민 참여 데이터 초기화 스크립트
더미 데이터 생성: 활동 피드, 주간 챌린지, 사용자 통계
"""
import sys
import os
from pathlib import Path

# app 디렉토리를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random

from app.models.database import SessionLocal, Base, engine
from app.models.models import User, ActivityFeed, WeeklyChallenge, ActionType, Badge, UserBadge, BadgeType
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_dummy_users(db: Session, count: int = 15):
    """더미 사용자 생성"""
    korean_surnames = ["김", "이", "박", "최", "정", "강", "조", "윤", "장", "임", "한", "오", "서", "신", "권"]
    korean_names = ["민준", "서연", "지우", "하은", "도윤", "예은", "시우", "서현", "주원", "지안"]

    users = []
    for i in range(count):
        username = f"{random.choice(korean_surnames)}{random.choice(korean_names)}{i+1:02d}"
        email = f"user{i+1:03d}@example.com"
        points = random.randint(500, 3000)
        level = min(10, points // 300)
        completed = random.randint(5, 30)
        cooling = round(random.uniform(1.0, 5.5), 1)
        trees = random.randint(10, 100)

        # bcrypt has 72 byte limit, use simple password
        password = "password123"[:72]

        user = User(
            username=username,
            email=email,
            hashed_password=pwd_context.hash(password),
            points=points,
            level=level,
            completed_missions_count=completed,
            cooling_contribution=cooling,
            trees_planted=trees
        )
        users.append(user)

    db.add_all(users)
    db.commit()
    print(f"{len(users)}명의 더미 사용자 생성 완료")
    return users


def create_activity_feed(db: Session, users: list, count: int = 30):
    """활동 피드 더미 데이터 생성"""
    mission_titles = [
        "수원시 가로수 심기",
        "부천시 옥상 녹화",
        "시흥시 쿨페이브먼트",
        "성남시 분수대 설치",
        "안양시 버스정류장 그늘막",
        "광명시 도심 녹지 조성",
        "용인시 공원 나무 심기",
        "고양시 수직정원 설치",
        "평택시 쿨루프 시공"
    ]

    badges = ["첫 나무 심기", "10미션 달성", "열섬 퇴치자", "환경 지킴이", "그린 챔피언"]

    activities = []
    base_time = datetime.now()

    for i in range(count):
        user = random.choice(users)
        action = random.choice([ActionType.MISSION_COMPLETE, ActionType.MISSION_START, ActionType.LEVEL_UP, ActionType.BADGE_EARNED])
        timestamp = base_time - timedelta(minutes=random.randint(5, 1440))

        if action == ActionType.MISSION_COMPLETE:
            activity = ActivityFeed(
                user_id=user.id,
                action_type=action,
                mission_title=random.choice(mission_titles),
                points_earned=random.choice([30, 50, 70, 80, 100]),
                created_at=timestamp
            )
        elif action == ActionType.LEVEL_UP:
            activity = ActivityFeed(
                user_id=user.id,
                action_type=action,
                mission_title=f"레벨 {random.randint(2, 8)} 달성",
                points_earned=0,
                created_at=timestamp
            )
        elif action == ActionType.MISSION_START:
            activity = ActivityFeed(
                user_id=user.id,
                action_type=action,
                mission_title=random.choice(mission_titles),
                points_earned=0,
                created_at=timestamp
            )
        else:  # BADGE_EARNED
            activity = ActivityFeed(
                user_id=user.id,
                action_type=action,
                mission_title=random.choice(badges),
                points_earned=100,
                created_at=timestamp
            )

        activities.append(activity)

    db.add_all(activities)
    db.commit()
    print(f"{len(activities)}개의 활동 피드 생성 완료")


def create_weekly_challenges(db: Session):
    """주간 챌린지 더미 데이터 생성"""
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    week_number = int(today.strftime("%Y%W"))

    challenges = [
        WeeklyChallenge(
            week_number=week_number,
            title="나무 10그루 심기 챌린지",
            description="이번 주 나무 10그루를 심고 100P 보너스를 받으세요!",
            goal_count=10,
            current_progress=random.randint(5, 8),
            reward_points=100,
            start_date=week_start,
            end_date=week_end,
            is_active=True
        ),
        WeeklyChallenge(
            week_number=week_number,
            title="옥상 녹화 5곳 완성",
            description="옥상 녹화 프로젝트 5곳을 완료하면 150P 보상!",
            goal_count=5,
            current_progress=random.randint(2, 4),
            reward_points=150,
            start_date=week_start,
            end_date=week_end,
            is_active=True
        ),
        WeeklyChallenge(
            week_number=week_number,
            title="열섬 퇴치 히어로 되기",
            description="이번 주 총 -5°C 냉각 효과를 달성하세요!",
            goal_count=5,
            current_progress=random.randint(3, 4),
            reward_points=200,
            start_date=week_start,
            end_date=week_end,
            is_active=True
        )
    ]

    db.add_all(challenges)
    db.commit()
    print(f"{len(challenges)}개의 주간 챌린지 생성 완료")


def create_badges(db: Session):
    """배지 마스터 데이터 생성"""
    badges = [
        Badge(
            badge_type=BadgeType.FIRST_MISSION,
            name="첫 걸음",
            description="첫 번째 미션을 완료했습니다!",
            icon="🌱",
            requirement="미션 1개 완료",
            points=50
        ),
        Badge(
            badge_type=BadgeType.MISSIONS_10,
            name="초보 활동가",
            description="10개의 미션을 완료한 열정적인 시민!",
            icon="🏃",
            requirement="미션 10개 완료",
            points=100
        ),
        Badge(
            badge_type=BadgeType.MISSIONS_50,
            name="베테랑 활동가",
            description="50개의 미션을 완료한 경험 많은 환경 지킴이!",
            icon="🦸",
            requirement="미션 50개 완료",
            points=300
        ),
        Badge(
            badge_type=BadgeType.MISSIONS_100,
            name="전설의 활동가",
            description="100개의 미션을 완료한 전설적인 영웅!",
            icon="👑",
            requirement="미션 100개 완료",
            points=500
        ),
        Badge(
            badge_type=BadgeType.TREE_LOVER,
            name="나무 사랑꾼",
            description="50그루 이상의 나무를 심었습니다!",
            icon="🌳",
            requirement="나무 50그루 심기",
            points=200
        ),
        Badge(
            badge_type=BadgeType.COOLING_HERO,
            name="열섬 퇴치자",
            description="총 10°C 이상의 냉각 효과를 달성했습니다!",
            icon="❄️",
            requirement="총 10°C 냉각 기여",
            points=400
        ),
        Badge(
            badge_type=BadgeType.LEVEL_5,
            name="신참 챔피언",
            description="레벨 5에 도달했습니다!",
            icon="⭐",
            requirement="레벨 5 달성",
            points=150
        ),
        Badge(
            badge_type=BadgeType.LEVEL_10,
            name="마스터 챔피언",
            description="레벨 10에 도달한 최고의 활동가!",
            icon="💎",
            requirement="레벨 10 달성",
            points=500
        ),
        Badge(
            badge_type=BadgeType.WEEKLY_CHAMPION,
            name="주간 챔피언",
            description="주간 챌린지를 완료했습니다!",
            icon="🏆",
            requirement="주간 챌린지 1회 완료",
            points=100
        ),
        Badge(
            badge_type=BadgeType.GREEN_ROOF_MASTER,
            name="옥상 녹화 전문가",
            description="옥상 녹화 프로젝트 10개를 완료했습니다!",
            icon="🏢",
            requirement="옥상 녹화 10회 완료",
            points=250
        )
    ]

    db.add_all(badges)
    db.commit()
    print(f"{len(badges)}개의 배지 생성 완료")


def assign_random_badges(db: Session, users: list):
    """사용자에게 랜덤 배지 할당"""
    all_badges = db.query(Badge).all()

    assigned_count = 0
    for user in users:
        # 각 사용자에게 0~5개의 랜덤 배지 할당
        num_badges = random.randint(0, min(5, len(all_badges)))
        selected_badges = random.sample(all_badges, num_badges)

        for badge in selected_badges:
            user_badge = UserBadge(
                user_id=user.id,
                badge_id=badge.id,
                earned_at=datetime.now() - timedelta(days=random.randint(1, 30))
            )
            db.add(user_badge)
            assigned_count += 1

    db.commit()
    print(f"{assigned_count}개의 사용자 배지 할당 완료")


def main():
    """메인 실행 함수"""
    print("Urban Cooling Farm - 시민 참여 데이터 초기화 시작")

    # 데이터베이스 테이블 생성
    print("데이터베이스 테이블 생성 중...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # 기존 데이터 삭제 (옵션)
        print("기존 시민 참여 데이터 삭제 중...")
        db.query(UserBadge).delete()
        db.query(Badge).delete()
        db.query(ActivityFeed).delete()
        db.query(WeeklyChallenge).delete()
        # User는 삭제하지 않고 업데이트만 (기존 미션과의 관계 유지)

        # 더미 데이터 생성
        users = create_dummy_users(db, count=15)
        create_activity_feed(db, users, count=30)
        create_weekly_challenges(db)
        create_badges(db)
        assign_random_badges(db, users)

        print("\n초기화 완료!")
        print("\n생성된 데이터:")
        print(f"  - 사용자: {db.query(User).count()}명")
        print(f"  - 활동 피드: {db.query(ActivityFeed).count()}개")
        print(f"  - 주간 챌린지: {db.query(WeeklyChallenge).count()}개")
        print(f"  - 배지: {db.query(Badge).count()}개")
        print(f"  - 획득한 배지: {db.query(UserBadge).count()}개")

    except Exception as e:
        print(f"에러 발생: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
