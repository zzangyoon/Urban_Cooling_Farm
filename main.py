"""
Urban Cooling Farm - Entry Point

Usage:
    python main.py [--reload]  : FastAPI 서버 실행
    streamlit run streamlit_app/app.py : Streamlit 대시보드 실행
"""
import uvicorn


def main():
    """FastAPI 서버 실행"""
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8020,
        reload=True
    )


if __name__ == "__main__":
    main()
