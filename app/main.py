# python main.py
"""
Urban Cooling Farm - FastAPI Application

도시 열섬 완화를 위한 쿨링팜 관리 시스템
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import get_settings
from app.models.database import Base, engine, SessionLocal
from app.routers import climate_router, missions_router, cooling_spots_router, agent_router, effects_router
from app.routers.citizen import router as citizen_router
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작/종료 시 실행되는 이벤트"""
    # 시작 시: 테이블 생성
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully")

        # Vercel 환경에서는 초기 데이터 자동 생성
        if os.getenv("VERCEL"):
            print("Vercel environment detected - initializing data...")
            from app.init_citizen_data import (
                create_dummy_users, create_activity_feed,
                create_weekly_challenges, create_badges, assign_random_badges
            )
            db = SessionLocal()
            try:
                users = create_dummy_users(db, count=15)
                create_activity_feed(db, users, count=30)
                create_weekly_challenges(db)
                create_badges(db)
                assign_random_badges(db, users)
                print("Initial data created successfully")
            except Exception as init_error:
                print(f"Warning: Data initialization failed: {init_error}")
                db.rollback()
            finally:
                db.close()

    except Exception as e:
        # 데이터베이스 초기화 실패 시 경고 출력
        print(f"Warning: Database initialization failed: {e}")
        print("App will continue with USE_MOCK_DATA mode")
    yield
    # 종료 시: 정리 작업 (필요시)


settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    description="도시 열섬 완화를 위한 AI 기반 쿨링팜 관리 시스템",
    version="0.1.0",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://urbancoolingfarm.streamlit.app",  # Streamlit Cloud
        "http://localhost:8501",  # 로컬 개발
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(climate_router)
app.include_router(missions_router)
app.include_router(cooling_spots_router)
app.include_router(agent_router)
app.include_router(effects_router)
app.include_router(citizen_router)


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "name": settings.APP_NAME,
        "version": "0.1.0",
        "description": "도시 열섬 완화를 위한 AI 기반 쿨링팜 관리 시스템",
        "docs_url": "/docs"
    }


@app.get("/health")
async def health_check():
    """헬스체크 엔드포인트"""
    return {"status": "healthy"}
