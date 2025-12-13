# python main.py
"""
Urban Cooling Farm - FastAPI Application

도시 열섬 완화를 위한 쿨링팜 관리 시스템
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import get_settings
from app.models.database import Base, engine
from app.routers import climate_router, missions_router, cooling_spots_router, agent_router, effects_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작/종료 시 실행되는 이벤트"""
    # 시작 시: 테이블 생성
    Base.metadata.create_all(bind=engine)
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
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인만 허용
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
