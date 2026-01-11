import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import get_settings

settings = get_settings()

# Vercel 등 서버리스 환경 감지
def get_database_url() -> str:
    """환경에 맞는 데이터베이스 URL 반환"""
    # Vercel 환경 변수로 감지
    if os.getenv("VERCEL"):
        # 서버리스 환경에서는 in-memory SQLite 사용
        return "sqlite:///:memory:"
    return settings.DATABASE_URL

engine = create_engine(
    get_database_url(),
    connect_args={"check_same_thread": False}  # SQLite용
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI Dependency로 사용할 DB 세션 생성기"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
