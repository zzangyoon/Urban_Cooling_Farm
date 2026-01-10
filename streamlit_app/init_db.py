"""
Streamlit App Database Initialization
시민 참여 기능을 위한 DB 스키마 및 더미 데이터 생성
"""
import sqlite3
from datetime import datetime, timedelta
import random
import os

# 현재 파일의 디렉토리 기준 DB 경로
DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "citizen_data.db")


def init_database():
    """데이터베이스 초기화 및 테이블 생성"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. 시민 활동 피드 테이블
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS activity_feed (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_name TEXT NOT NULL,
        action_type TEXT NOT NULL,
        mission_title TEXT,
        points INTEGER,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 2. 주간 챌린지 테이블
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS weekly_challenge (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        week_number INTEGER NOT NULL,
        challenge_title TEXT NOT NULL,
        challenge_description TEXT,
        goal_count INTEGER,
        current_progress INTEGER DEFAULT 0,
        reward_points INTEGER,
        start_date DATE,
        end_date DATE,
        is_active BOOLEAN DEFAULT 1
    )
    """)

    # 3. 사용자 통계 테이블 (확장용)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT UNIQUE NOT NULL,
        total_points INTEGER DEFAULT 0,
        level INTEGER DEFAULT 1,
        completed_missions INTEGER DEFAULT 0,
        cooling_contribution REAL DEFAULT 0.0,
        trees_planted INTEGER DEFAULT 0,
        last_active DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 4. 랭킹 뷰 (빠른 조회용)
    cursor.execute("""
    CREATE VIEW IF NOT EXISTS leaderboard AS
    SELECT
        user_id,
        total_points,
        level,
        completed_missions,
        cooling_contribution,
        trees_planted,
        RANK() OVER (ORDER BY total_points DESC) as rank
    FROM user_stats
    ORDER BY total_points DESC
    LIMIT 10
    """)

    conn.commit()
    conn.close()
    print("✅ 데이터베이스 초기화 완료")


def generate_dummy_data():
    """더미 데이터 생성"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 기존 데이터 삭제 (재생성 시)
    cursor.execute("DELETE FROM activity_feed")
    cursor.execute("DELETE FROM weekly_challenge")
    cursor.execute("DELETE FROM user_stats")

    # === 1. 활동 피드 더미 데이터 ===
    activity_templates = [
        {"action": "mission_complete", "missions": [
            "수원시 가로수 심기", "부천시 옥상 녹화", "시흥시 쿨페이브먼트",
            "성남시 분수대 설치", "안양시 그늘막 설치", "광명시 도심 녹지 조성"
        ]},
        {"action": "level_up", "levels": [2, 3, 4, 5, 6]},
        {"action": "mission_start", "missions": [
            "용인시 공원 조성", "고양시 수직정원", "평택시 쿨루프 시공"
        ]},
        {"action": "badge_earned", "badges": [
            "첫 나무 심기", "10미션 달성", "열섬 퇴치자", "환경 지킴이"
        ]}
    ]

    korean_surnames = ["김", "이", "박", "최", "정", "강", "조", "윤", "장", "임", "한", "오", "서", "신"]

    activities = []
    base_time = datetime.now()

    for i in range(30):  # 30개의 활동 피드
        surname = random.choice(korean_surnames)
        name_hidden = f"{surname}*{random.choice(['민', '수', '영', '현', '지', '서', '우'])}"

        action_type = random.choice(["mission_complete", "level_up", "mission_start", "badge_earned"])
        timestamp = base_time - timedelta(minutes=random.randint(5, 1440))  # 최근 24시간

        if action_type == "mission_complete":
            mission = random.choice(activity_templates[0]["missions"])
            points = random.choice([30, 50, 70, 80, 100])
            activities.append((name_hidden, action_type, mission, points, timestamp))
        elif action_type == "level_up":
            level = random.choice(activity_templates[1]["levels"])
            activities.append((name_hidden, action_type, f"레벨 {level} 달성", 0, timestamp))
        elif action_type == "mission_start":
            mission = random.choice(activity_templates[2]["missions"])
            activities.append((name_hidden, action_type, mission, 0, timestamp))
        else:  # badge_earned
            badge = random.choice(activity_templates[3]["badges"])
            activities.append((name_hidden, action_type, badge, 100, timestamp))

    cursor.executemany("""
        INSERT INTO activity_feed (user_name, action_type, mission_title, points, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, activities)

    # === 2. 주간 챌린지 더미 데이터 ===
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)

    challenges = [
        (1, "나무 10그루 심기 챌린지", "이번 주 나무 10그루를 심고 100P 보너스를 받으세요!",
         10, random.randint(5, 8), 100, week_start, week_end, 1),
        (2, "옥상 녹화 5곳 완성", "옥상 녹화 프로젝트 5곳을 완료하면 150P 보상!",
         5, random.randint(2, 4), 150, week_start, week_end, 1),
        (3, "열섬 퇴치 히어로 되기", "이번 주 총 -5°C 냉각 효과를 달성하세요!",
         5, random.randint(3, 4), 200, week_start, week_end, 1),
    ]

    cursor.executemany("""
        INSERT INTO weekly_challenge (week_number, challenge_title, challenge_description,
                                      goal_count, current_progress, reward_points,
                                      start_date, end_date, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, challenges)

    # === 3. 사용자 통계 더미 데이터 (TOP 10) ===
    users = []
    for i in range(15):  # 15명의 가상 사용자
        surname = random.choice(korean_surnames)
        user_id = f"user_{i+1:03d}"
        total_points = random.randint(500, 3000)
        level = min(10, total_points // 300)
        completed_missions = random.randint(5, 30)
        cooling_contribution = round(random.uniform(1.0, 5.5), 1)
        trees_planted = random.randint(10, 100)
        last_active = datetime.now() - timedelta(hours=random.randint(1, 48))

        users.append((user_id, total_points, level, completed_missions,
                     cooling_contribution, trees_planted, last_active))

    cursor.executemany("""
        INSERT INTO user_stats (user_id, total_points, level, completed_missions,
                               cooling_contribution, trees_planted, last_active)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, users)

    conn.commit()
    conn.close()
    print(f"✅ 더미 데이터 생성 완료:")
    print(f"   - 활동 피드: {len(activities)}개")
    print(f"   - 주간 챌린지: {len(challenges)}개")
    print(f"   - 사용자: {len(users)}명")


def get_recent_activities(limit=10):
    """최근 활동 피드 조회"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT user_name, action_type, mission_title, points, timestamp
        FROM activity_feed
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,))

    results = cursor.fetchall()
    conn.close()
    return results


def get_active_challenges():
    """활성 주간 챌린지 조회"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT challenge_title, challenge_description, goal_count,
               current_progress, reward_points
        FROM weekly_challenge
        WHERE is_active = 1
        ORDER BY id
    """)

    results = cursor.fetchall()
    conn.close()
    return results


def get_leaderboard(limit=10):
    """랭킹 조회"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT user_id, total_points, level, completed_missions,
               cooling_contribution, trees_planted
        FROM user_stats
        ORDER BY total_points DESC
        LIMIT ?
    """, (limit,))

    results = cursor.fetchall()
    conn.close()
    return results


if __name__ == "__main__":
    print("🚀 Urban Cooling Farm - DB 초기화 시작")
    init_database()
    generate_dummy_data()

    print("\n📊 데이터 확인:")
    print("\n=== 최근 활동 피드 ===")
    for activity in get_recent_activities(5):
        print(f"  {activity[0]}: {activity[2]} (+{activity[3]}P)")

    print("\n=== 주간 챌린지 ===")
    for challenge in get_active_challenges():
        print(f"  {challenge[0]}: {challenge[2]}/{challenge[3]} 완료")

    print("\n=== TOP 5 랭킹 ===")
    for idx, user in enumerate(get_leaderboard(5), 1):
        print(f"  {idx}. {user[0]}: {user[1]}P (Lv.{user[2]})")

    print("\n✨ 초기화 완료!")
