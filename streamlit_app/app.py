# streamlit run streamlit_app/app.py
"""
Urban Cooling Farm - Streamlit Dashboard

열섬 현황 지도 시각화 및 대시보드
"""
import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
from datetime import datetime
import httpx
import os
from dotenv import load_dotenv
import plotly.express as px
import plotly.graph_objects as go

# .env 파일 로드
load_dotenv()

# ============== FastAPI Backend Configuration ==============
# Streamlit Cloud 배포 시 Vercel URL 사용, 로컬 개발 시 localhost
FASTAPI_BASE_URL = os.getenv("FASTAPI_BASE_URL", "https://urban-cooling-farm.vercel.app")


# ============== FastAPI 호출 함수 ==============
@st.cache_data(ttl=60)  # 1분 캐시
def fetch_activity_feed(limit: int = 15):
    """활동 피드 조회"""
    try:
        response = httpx.get(f"{FASTAPI_BASE_URL}/api/citizen/activity-feed", params={"limit": limit}, timeout=10.0)
        response.raise_for_status()
        return response.json()
    except Exception:
        # 에러 발생 시 빈 리스트 반환
        return []


@st.cache_data(ttl=300)  # 5분 캐시
def fetch_weekly_challenges():
    """주간 챌린지 조회"""
    try:
        response = httpx.get(f"{FASTAPI_BASE_URL}/api/citizen/challenges", timeout=10.0)
        response.raise_for_status()
        return response.json()
    except Exception:
        # 에러 발생 시 빈 리스트 반환
        return []


@st.cache_data(ttl=300)  # 5분 캐시
def fetch_leaderboard(limit: int = 10):
    """랭킹 조회"""
    try:
        response = httpx.get(f"{FASTAPI_BASE_URL}/api/citizen/leaderboard", params={"limit": limit}, timeout=10.0)
        response.raise_for_status()
        return response.json()
    except Exception:
        # 에러 발생 시 빈 리스트 반환
        return []


@st.cache_data(ttl=600)  # 10분 캐시
def fetch_badges(user_id: int | None = None):
    """배지 조회"""
    try:
        params = {"user_id": user_id} if user_id else {}
        response = httpx.get(f"{FASTAPI_BASE_URL}/api/citizen/badges", params=params, timeout=10.0)
        response.raise_for_status()
        return response.json()
    except Exception:
        # 에러 발생 시 빈 리스트 반환
        return []


# ============== Page Config ==============
st.set_page_config(
    page_title="Urban Cooling Farm",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============== Custom CSS ==============
st.markdown("""
<style>
    /* 헤더 스타일 */
    .main-header {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    .sub-header {
        font-size: 1.3rem;
        color: #555;
        margin-bottom: 2rem;
        text-align: center;
    }

    /* 히어로 배너 */
    .hero-banner {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    .hero-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .hero-subtitle {
        font-size: 1.2rem;
        opacity: 0.95;
    }

    /* 메트릭 카드 */
    .big-metric {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        text-align: center;
        border-left: 5px solid;
        transition: transform 0.2s;
    }
    .big-metric:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .metric-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }

    /* 열섬 강도 색상 */
    .heat-critical { color: #d32f2f; border-color: #d32f2f; }
    .heat-high { color: #f57c00; border-color: #f57c00; }
    .heat-medium { color: #fbc02d; border-color: #fbc02d; }
    .heat-low { color: #388e3c; border-color: #388e3c; }

    /* 사이드바 개선 */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }

    /* 탭 스타일 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f6;
        border-radius: 8px 8px 0 0;
        padding: 12px 24px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #e0e5f0;
        transform: translateY(-2px);
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }

    /* 시민참여 요약 카드 */
    .citizen-summary {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(240, 147, 251, 0.3);
    }
    .citizen-summary-title {
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    .citizen-stats {
        display: flex;
        justify-content: space-around;
        gap: 1rem;
    }
    .citizen-stat-item {
        text-align: center;
    }
    .citizen-stat-value {
        font-size: 2rem;
        font-weight: 700;
    }
    .citizen-stat-label {
        font-size: 0.85rem;
        opacity: 0.9;
    }

    /* 미션 카드 */
    .mission-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border-left: 5px solid #667eea;
        transition: all 0.3s;
    }
    .mission-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    .mission-card-title {
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        color: #333;
    }
    .mission-card-meta {
        display: flex;
        gap: 1rem;
        margin: 1rem 0;
        flex-wrap: wrap;
    }
    .mission-card-tag {
        background: #f0f2f6;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .mission-card-cta {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.8rem 2rem;
        border-radius: 25px;
        font-weight: 700;
        font-size: 1.1rem;
        border: none;
        cursor: pointer;
        transition: all 0.3s;
        width: 100%;
        margin-top: 1rem;
    }
    .mission-card-cta:hover {
        transform: scale(1.05);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }

    /* 챌린지 카드 */
    .challenge-card {
        background: linear-gradient(135deg, #ffeaa7 0%, #fdcb6e 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: #2d3436;
        margin-bottom: 1rem;
        box-shadow: 0 4px 15px rgba(253, 203, 110, 0.3);
    }
    .challenge-title {
        font-size: 1.2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .challenge-desc {
        font-size: 0.9rem;
        opacity: 0.9;
        margin-bottom: 1rem;
    }
    .progress-bar {
        background: rgba(255,255,255,0.3);
        border-radius: 10px;
        height: 20px;
        overflow: hidden;
        margin: 0.5rem 0;
    }
    .progress-fill {
        background: linear-gradient(90deg, #00b894 0%, #00cec9 100%);
        height: 100%;
        transition: width 0.3s;
        border-radius: 10px;
    }

    /* 활동 피드 */
    .activity-feed {
        background: white;
        padding: 0.8rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        border-left: 3px solid #74b9ff;
        font-size: 0.9rem;
        transition: all 0.2s;
    }
    .activity-feed:hover {
        transform: translateX(5px);
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .activity-time {
        color: #999;
        font-size: 0.75rem;
    }

    /* 랭킹 카드 */
    .rank-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        transition: all 0.2s;
    }
    .rank-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .rank-number {
        font-size: 1.5rem;
        font-weight: 700;
        width: 40px;
        text-align: center;
    }
    .rank-gold { color: #f39c12; }
    .rank-silver { color: #95a5a6; }
    .rank-bronze { color: #cd7f32; }

    /* 배지 카드 */
    .badge-card {
        background: white;
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
        transition: all 0.3s;
        border: 2px solid #e0e0e0;
        height: 220px;  /* 고정 높이 */
        display: flex;
        flex-direction: column;
        justify-content: space-between;  /* 상하 균등 배치 */
        align-items: center;
    }
    .badge-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
    }
    .badge-card.earned {
        background: linear-gradient(135deg, #ffeaa7 0%, #fdcb6e 100%);
        border-color: #fdcb6e;
    }
    .badge-card.locked {
        opacity: 0.5;
        filter: grayscale(80%);
    }
    .badge-icon {
        font-size: 2.5rem;  /* 크기 약간 줄임 */
        margin-bottom: 0.3rem;
        line-height: 1;
    }
    .badge-name {
        font-size: 0.9rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
        color: #333;
        line-height: 1.2;
        max-height: 2.4em;  /* 2줄 제한 */
        overflow: hidden;
        text-overflow: ellipsis;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
    }
    .badge-desc {
        font-size: 0.7rem;
        color: #666;
        margin-bottom: 0.2rem;
        line-height: 1.3;
        max-height: 3.9em;  /* 3줄 제한 */
        overflow: hidden;
        text-overflow: ellipsis;
        display: -webkit-box;
        -webkit-line-clamp: 3;
        -webkit-box-orient: vertical;
    }
    .badge-requirement {
        font-size: 0.65rem;
        color: #999;
        font-style: italic;
        line-height: 1.2;
        margin-bottom: 0.3rem;
    }
    .badge-points {
        background: #667eea;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 10px;
        font-size: 0.65rem;
        font-weight: 600;
        margin-top: auto;  /* 하단에 고정 */
        display: inline-block;
    }

    /* 로딩 스켈레톤 */
    .skeleton {
        background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
        background-size: 200% 100%;
        animation: loading 1.5s ease-in-out infinite;
        border-radius: 8px;
    }
    @keyframes loading {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }
    .skeleton-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
    }
    .skeleton-line {
        height: 16px;
        margin-bottom: 10px;
        border-radius: 4px;
    }
    .skeleton-circle {
        width: 50px;
        height: 50px;
        border-radius: 50%;
    }

    /* 커스텀 로딩 스피너 */
    .loading-spinner {
        display: inline-block;
        width: 50px;
        height: 50px;
        border: 4px solid #f3f3f3;
        border-top: 4px solid #667eea;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin: 2rem auto;
    }
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    /* 모바일 반응형 */
    @media (max-width: 768px) {
        .big-metric {
            padding: 1rem;
        }
        .metric-value {
            font-size: 1.5rem;
        }
        .hero-title {
            font-size: 1.5rem;
        }
        .badge-card {
            height: 200px;
        }
        .rank-card, .activity-feed, .challenge-card {
            font-size: 0.85rem;
        }
        .mission-card {
            padding: 1rem;
        }
    }
    @media (max-width: 480px) {
        .big-metric {
            padding: 0.8rem;
        }
        .metric-value {
            font-size: 1.2rem;
        }
        .hero-title {
            font-size: 1.2rem;
        }
        .badge-card {
            height: 180px;
        }
    }
</style>
""", unsafe_allow_html=True)


# ============== 경기도 시군구 정보 ==============
GYEONGGI_DISTRICTS = [
    {"district": "수원시", "lat": 37.2636, "lng": 127.0286, "population_density": 9800},
    {"district": "성남시", "lat": 37.4200, "lng": 127.1265, "population_density": 9200},
    {"district": "고양시", "lat": 37.6584, "lng": 126.8320, "population_density": 7500},
    {"district": "용인시", "lat": 37.2410, "lng": 127.1775, "population_density": 3200},
    {"district": "부천시", "lat": 37.5034, "lng": 126.7660, "population_density": 15800},
    {"district": "안산시", "lat": 37.3219, "lng": 126.8309, "population_density": 8100},
    {"district": "안양시", "lat": 37.3943, "lng": 126.9568, "population_density": 11200},
    {"district": "평택시", "lat": 36.9921, "lng": 127.1128, "population_density": 1800},
    {"district": "시흥시", "lat": 37.3800, "lng": 126.8030, "population_density": 5500},
    {"district": "화성시", "lat": 37.1996, "lng": 126.8312, "population_density": 1500},
    {"district": "광명시", "lat": 37.4786, "lng": 126.8644, "population_density": 17500},
    {"district": "군포시", "lat": 37.3616, "lng": 126.9351, "population_density": 11000},
    {"district": "광주시", "lat": 37.4095, "lng": 127.2550, "population_density": 1800},
    {"district": "김포시", "lat": 37.6152, "lng": 126.7156, "population_density": 2800},
    {"district": "파주시", "lat": 37.7126, "lng": 126.7800, "population_density": 800},
]

DISTRICT_LIST = [d["district"] for d in GYEONGGI_DISTRICTS]


# ============== API 설정 ==============
API_KEY = os.getenv("CLIMATE_API_KEY", "")
API_BASE_URL = os.getenv("CLIMATE_API_BASE_URL", "https://climate.gg.go.kr/ols/api/geoserver/wfs")


# ============== 데이터 로딩 함수 ==============
@st.cache_data(ttl=300)
def fetch_park_data(max_features: int = 200) -> list:
    """경기기후플랫폼에서 공원 데이터 조회"""
    # API 키가 없으면 빈 데이터 반환 (Mock 모드)
    if not API_KEY or API_KEY == "your_api_key_here":
        return []

    try:
        params = {
            "apiKey": API_KEY,
            "service": "WFS",
            "version": "1.1.0",
            "request": "GetFeature",
            "typeName": "park",
            "outputFormat": "application/json",
            "maxFeatures": max_features
        }

        with httpx.Client(timeout=30.0) as client:
            response = client.get(API_BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("features", [])
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 403:
            st.error("⚠️ API 인증 실패: CLIMATE_API_KEY를 .env 파일에 올바르게 설정해주세요.")
        else:
            st.warning(f"API 호출 실패 (HTTP {e.response.status_code}): {e}")
        return []
    except Exception as e:
        st.warning(f"API 호출 실패: {e}")
        return []


@st.cache_data(ttl=300)
def calculate_heat_island_data(district_filter: str = None) -> list:
    """열섬 데이터 계산 (공원 데이터 + 인구밀도 기반)"""

    # 공원 데이터로 시군구별 녹지율 계산
    parks = fetch_park_data(500)

    district_park_area = {}
    for feature in parks:
        props = feature.get("properties", {})
        sgg_nm = props.get("sgg_nm", "")
        area = props.get("biotop_area") or props.get("area") or 10000

        if sgg_nm:
            # 시군구명 정규화 (예: "수원시 팔달구" -> "수원시")
            for d in GYEONGGI_DISTRICTS:
                if d["district"] in sgg_nm or sgg_nm in d["district"]:
                    district_park_area[d["district"]] = district_park_area.get(d["district"], 0) + float(area)
                    break

    # 녹지율 계산 (추정)
    avg_district_area = 40_000_000  # m² (시군구 평균 면적)
    district_green_ratio = {}
    for district, total_area in district_park_area.items():
        green_ratio = (total_area / avg_district_area) * 100
        district_green_ratio[district] = min(max(green_ratio, 5.0), 40.0)

    # 열섬 데이터 생성
    result = []
    base_temp = 28.0

    districts = GYEONGGI_DISTRICTS
    if district_filter:
        districts = [d for d in districts if district_filter in d["district"]]

    for d in districts:
        district_name = d["district"]
        pop_density = d["population_density"]

        # 녹지율 (없으면 인구밀도 기반 추정)
        if district_name in district_green_ratio:
            green_ratio = district_green_ratio[district_name]
        else:
            green_ratio = max(5, 40 - (pop_density / 500))

        # 열섬 강도 계산
        green_factor = (30 - green_ratio) / 30  # 0 ~ 1
        density_factor = min(pop_density / 20000, 1.0)  # 0 ~ 1

        intensity = 0.5 + (green_factor * 1.5) + (density_factor * 1.0)
        intensity = round(min(max(intensity, 0.5), 3.0), 2)

        temperature = base_temp + intensity

        result.append({
            "latitude": d["lat"],
            "longitude": d["lng"],
            "temperature": round(temperature, 1),
            "heat_island_intensity": intensity,
            "timestamp": datetime.now().isoformat(),
            "district": district_name,
            "green_coverage_ratio": round(green_ratio, 1)
        })

    # 강도 높은 순 정렬
    result.sort(key=lambda x: x["heat_island_intensity"], reverse=True)
    return result


# ============== Helper Functions ==============
def get_heat_color(intensity: float) -> str:
    """열섬 강도에 따른 색상 반환"""
    if intensity >= 2.0:
        return "#ff0000"  # 빨강 (심각)
    elif intensity >= 1.5:
        return "#ff6600"  # 주황 (높음)
    elif intensity >= 1.0:
        return "#ffcc00"  # 노랑 (중간)
    else:
        return "#00cc00"  # 녹색 (낮음)


def get_heat_level(intensity: float) -> str:
    """열섬 강도 레벨 텍스트"""
    if intensity >= 2.0:
        return "심각"
    elif intensity >= 1.5:
        return "높음"
    elif intensity >= 1.0:
        return "중간"
    else:
        return "낮음"


def create_heat_island_map(heat_data: list, center: tuple = (37.4, 127.0)) -> folium.Map:
    """열섬 현황 지도 생성"""
    m = folium.Map(
        location=center,
        zoom_start=10,
        tiles="cartodbpositron"
    )

    # 열섬 포인트 추가
    for data in heat_data:
        lat = data["latitude"]
        lng = data["longitude"]
        intensity = data["heat_island_intensity"]
        temp = data["temperature"]
        district = data["district"]
        timestamp = data["timestamp"]
        green_ratio = data.get("green_coverage_ratio")

        color = get_heat_color(intensity)
        level = get_heat_level(intensity)

        # 타임스탬프 포맷팅
        ts_str = timestamp[:16].replace("T", " ") if isinstance(timestamp, str) else timestamp.strftime('%Y-%m-%d %H:%M')

        green_info = f"<p style='margin: 5px 0;'><b>녹지율:</b> {green_ratio:.1f}%</p>" if green_ratio else ""

        popup_html = f"""
        <div style="width: 200px;">
            <h4 style="margin: 0; color: #333;">{district}</h4>
            <hr style="margin: 5px 0;">
            <p style="margin: 5px 0;"><b>현재 온도:</b> {temp}°C</p>
            <p style="margin: 5px 0;"><b>열섬 강도:</b> +{intensity}°C</p>
            <p style="margin: 5px 0;"><b>위험 수준:</b> <span style="color: {color};">{level}</span></p>
            {green_info}
            <p style="margin: 5px 0; font-size: 0.8em; color: #666;">
                측정: {ts_str}
            </p>
        </div>
        """

        # 원형 마커 (열섬 강도에 비례하는 크기)
        folium.CircleMarker(
            location=[lat, lng],
            radius=10 + intensity * 5,
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.6,
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"{district}: +{intensity}°C"
        ).add_to(m)

    # 범례 추가
    legend_html = """
    <div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000;
                background-color: white; padding: 10px; border-radius: 5px;
                border: 2px solid #ccc; font-size: 12px;">
        <b>열섬 강도</b><br>
        <i style="background:#ff0000; width:12px; height:12px; display:inline-block; border-radius:50%;"></i> 심각 (≥2.0°C)<br>
        <i style="background:#ff6600; width:12px; height:12px; display:inline-block; border-radius:50%;"></i> 높음 (1.5-2.0°C)<br>
        <i style="background:#ffcc00; width:12px; height:12px; display:inline-block; border-radius:50%;"></i> 중간 (1.0-1.5°C)<br>
        <i style="background:#00cc00; width:12px; height:12px; display:inline-block; border-radius:50%;"></i> 낮음 (<1.0°C)
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    return m


# ============== Sidebar ==============
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/forest.png", width=80)
    st.title("Urban Cooling Farm")
    st.markdown("---")

    # 필터 옵션
    st.subheader("🔍 필터")
    district_filter = st.selectbox(
        "지역 선택",
        ["전체"] + DISTRICT_LIST
    )

    intensity_filter = st.slider(
        "최소 열섬 강도 (°C)",
        min_value=0.0,
        max_value=3.0,
        value=0.0,
        step=0.1
    )

    st.markdown("---")

    # 알림 센터
    st.subheader("🔔 알림 센터")

    # 알림 더미 데이터
    notifications = [
        {
            "id": 1,
            "type": "success",
            "icon": "🎉",
            "title": "미션 완료!",
            "message": "수원시 가로수 심기 미션을 완료했습니다. +50P",
            "time": "방금 전",
            "read": False
        },
        {
            "id": 2,
            "type": "info",
            "icon": "📢",
            "title": "새로운 챌린지",
            "message": "이번 주 챌린지가 시작되었습니다!",
            "time": "1시간 전",
            "read": False
        },
        {
            "id": 3,
            "type": "badge",
            "icon": "🏅",
            "title": "배지 획득!",
            "message": "초보 활동가 배지를 획득했습니다!",
            "time": "3시간 전",
            "read": True
        },
        {
            "id": 4,
            "type": "level",
            "icon": "⭐",
            "title": "레벨 업!",
            "message": "축하합니다! 레벨 8에 도달했습니다!",
            "time": "어제",
            "read": True
        }
    ]

    # 읽지 않은 알림 개수
    unread_count = sum(1 for n in notifications if not n['read'])
    if unread_count > 0:
        st.markdown(f"**새 알림: {unread_count}개**")

    # 알림 표시
    for notif in notifications[:3]:  # 최근 3개만 표시
        bg_color = "#fff3cd" if not notif['read'] else "#f8f9fa"
        st.markdown(f"""
        <div style='background: {bg_color}; padding: 0.8rem; border-radius: 8px; margin-bottom: 0.5rem;
                    border-left: 3px solid #667eea; font-size: 0.85rem;'>
            <div style='font-weight: 600; margin-bottom: 0.2rem;'>
                {notif['icon']} {notif['title']}
            </div>
            <div style='color: #666; font-size: 0.8rem; margin-bottom: 0.3rem;'>
                {notif['message']}
            </div>
            <div style='color: #999; font-size: 0.75rem;'>
                {notif['time']}
            </div>
        </div>
        """, unsafe_allow_html=True)

    if len(notifications) > 3:
        st.caption(f"외 {len(notifications) - 3}개의 알림 더보기")

    st.markdown("---")

    # 데이터 새로고침 버튼
    if st.button("🔄 데이터 새로고침"):
        st.cache_data.clear()
        st.rerun()

    st.caption(f"마지막 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M')}")


# ============== 시민참여 요약 카드 (전역) ==============
def render_citizen_summary():
    """모든 페이지 상단에 표시되는 시민참여 요약"""
    st.markdown("""
    <div class='citizen-summary'>
        <div class='citizen-summary-title'>👤 내 활동 현황</div>
        <div class='citizen-stats'>
            <div class='citizen-stat-item'>
                <div class='citizen-stat-value'>1,250</div>
                <div class='citizen-stat-label'>획득 포인트</div>
            </div>
            <div class='citizen-stat-item'>
                <div class='citizen-stat-value'>Lv.5</div>
                <div class='citizen-stat-label'>현재 레벨</div>
            </div>
            <div class='citizen-stat-item'>
                <div class='citizen-stat-value'>12</div>
                <div class='citizen-stat-label'>완료 미션</div>
            </div>
            <div class='citizen-stat-item'>
                <div class='citizen-stat-value'>-2.3°C</div>
                <div class='citizen-stat-label'>냉각 기여</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ============== Main Content ==============
# 시민참여 요약 카드 표시
render_citizen_summary()

# 탭 기반 네비게이션
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🌡️ 열섬 현황 지도", "📊 냉각 효과 대시보드", "👥 시민 참여", "👤 내 프로필", "ℹ️ 정보"])

# ============== 탭 1: 열섬 현황 지도 ==============
with tab1:
    # 히어로 배너
    st.markdown("""
    <div class='hero-banner'>
        <div class='hero-title'>🌡️ 경기도 열섬 현황 지도</div>
        <div class='hero-subtitle'>실시간 도시 열섬 모니터링 및 냉각 우선지역 분석</div>
    </div>
    """, unsafe_allow_html=True)

    # 데이터 로드 (캐시됨)
    district_param = None if district_filter == "전체" else district_filter
    heat_data = calculate_heat_island_data(district_param)

    # 강도 필터 적용
    heat_data = [d for d in heat_data if d["heat_island_intensity"] >= intensity_filter]

    # 상단 핵심 지표 (큰 메트릭 카드)
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class='big-metric' style='border-color: #667eea;'>
            <div class='metric-icon'>📍</div>
            <div class='metric-value'>{len(heat_data)}</div>
            <div class='metric-label'>모니터링 지점</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        if heat_data:
            avg_temp = sum(d["temperature"] for d in heat_data) / len(heat_data)
            avg_intensity = sum(d["heat_island_intensity"] for d in heat_data) / len(heat_data)
            heat_class = "heat-critical" if avg_intensity >= 2.0 else "heat-high" if avg_intensity >= 1.5 else "heat-medium"
            st.markdown(f"""
            <div class='big-metric {heat_class}'>
                <div class='metric-icon'>🌡️</div>
                <div class='metric-value'>{avg_temp:.1f}°C</div>
                <div class='metric-label'>평균 온도 (+{avg_intensity:.1f}°C)</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class='big-metric' style='border-color: #ccc;'>
                <div class='metric-icon'>🌡️</div>
                <div class='metric-value'>N/A</div>
                <div class='metric-label'>평균 온도</div>
            </div>
            """, unsafe_allow_html=True)

    with col3:
        if heat_data:
            max_intensity = max(d["heat_island_intensity"] for d in heat_data)
            heat_class = "heat-critical" if max_intensity >= 2.0 else "heat-high"
            st.markdown(f"""
            <div class='big-metric {heat_class}'>
                <div class='metric-icon'>⚠️</div>
                <div class='metric-value'>+{max_intensity:.1f}°C</div>
                <div class='metric-label'>최대 열섬 강도</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class='big-metric' style='border-color: #ccc;'>
                <div class='metric-icon'>⚠️</div>
                <div class='metric-value'>N/A</div>
                <div class='metric-label'>최대 열섬 강도</div>
            </div>
            """, unsafe_allow_html=True)

    with col4:
        critical_count = len([d for d in heat_data if d["heat_island_intensity"] >= 2.0])
        critical_class = "heat-critical" if critical_count > 0 else "heat-low"
        st.markdown(f"""
        <div class='big-metric {critical_class}'>
            <div class='metric-icon'>🚨</div>
            <div class='metric-value'>{critical_count}</div>
            <div class='metric-label'>심각 지역 (≥2.0°C)</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # 지도 표시
    if heat_data:
        # 중심점 계산
        center_lat = sum(d["latitude"] for d in heat_data) / len(heat_data)
        center_lng = sum(d["longitude"] for d in heat_data) / len(heat_data)

        heat_map = create_heat_island_map(heat_data, center=(center_lat, center_lng))

        # returned_objects=[] 로 지도 상호작용으로 인한 rerun 방지
        st_folium(
            heat_map,
            width=None,
            height=500,
            use_container_width=True,
            returned_objects=[]
        )
    else:
        st.warning("선택한 조건에 맞는 데이터가 없습니다.")

    # 데이터 테이블
    st.markdown("### 📋 상세 데이터")

    if heat_data:
        df = pd.DataFrame([
            {
                "지역": d["district"],
                "위도": round(d["latitude"], 4),
                "경도": round(d["longitude"], 4),
                "온도 (°C)": d["temperature"],
                "열섬 강도 (°C)": f"+{d['heat_island_intensity']}",
                "녹지율 (%)": f"{d.get('green_coverage_ratio', 'N/A')}",
                "위험 수준": get_heat_level(d["heat_island_intensity"]),
            }
            for d in heat_data
        ])

        # 열섬 강도 높은 순 정렬
        df = df.sort_values(by="열섬 강도 (°C)", ascending=False)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )


# ============== 탭 2: 냉각 효과 대시보드 ==============
with tab2:
    # 히어로 배너
    st.markdown("""
    <div class='hero-banner'>
        <div class='hero-title'>📊 냉각 효과 대시보드</div>
        <div class='hero-subtitle'>쿨링팜 프로젝트 성과 및 효과 분석</div>
    </div>
    """, unsafe_allow_html=True)

    # Mock 통계 데이터 (큰 메트릭 카드)
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class='big-metric' style='border-color: #4ecdc4;'>
            <div class='metric-icon'>🌳</div>
            <div class='metric-value'>24</div>
            <div class='metric-label'>총 쿨링스팟 (+3)</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class='big-metric' style='border-color: #95e1d3;'>
            <div class='metric-icon'>✅</div>
            <div class='metric-value'>156</div>
            <div class='metric-label'>완료된 미션 (+12)</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class='big-metric heat-low'>
            <div class='metric-icon'>❄️</div>
            <div class='metric-value'>-1.2°C</div>
            <div class='metric-label'>예상 냉각 효과</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class='big-metric' style='border-color: #f38181;'>
            <div class='metric-icon'>👥</div>
            <div class='metric-value'>1,247</div>
            <div class='metric-label'>참여 시민 (+89)</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # 차트 영역
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("📈 월별 미션 완료 현황")
        chart_data = pd.DataFrame({
            "월": ["8월", "9월", "10월", "11월", "12월"],
            "완료 미션": [23, 35, 42, 38, 18]
        })

        # Plotly 인터랙티브 차트
        fig = px.bar(
            chart_data,
            x="월",
            y="완료 미션",
            color="완료 미션",
            color_continuous_scale="Blues",
            labels={"완료 미션": "완료 미션 수"},
            text="완료 미션"
        )
        fig.update_traces(textposition='outside')
        fig.update_layout(
            showlegend=False,
            height=350,
            margin=dict(l=0, r=0, t=0, b=0),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.subheader("🌡️ 지역별 열섬 강도")
        # 캐시된 데이터 사용
        heat_data = calculate_heat_island_data(None)
        intensity_df = pd.DataFrame({
            "지역": [d["district"] for d in heat_data],
            "강도": [d["heat_island_intensity"] for d in heat_data]
        }).sort_values("강도", ascending=False).head(10)  # 상위 10개만

        # Plotly 인터랙티브 차트
        fig = px.bar(
            intensity_df,
            x="지역",
            y="강도",
            color="강도",
            color_continuous_scale="Reds",
            labels={"강도": "열섬 강도 (°C)"},
            text="강도"
        )
        fig.update_traces(texttemplate='%{text:.1f}°C', textposition='outside')
        fig.update_layout(
            showlegend=False,
            height=350,
            margin=dict(l=0, r=0, t=0, b=0),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # 미션 타입별 현황
    st.subheader("🎯 미션 타입별 현황")
    mission_types = pd.DataFrame({
        "미션 타입": ["나무 심기", "옥상 녹화", "쿨페이브먼트", "수경시설", "그늘막 설치"],
        "완료": [45, 28, 32, 21, 30],
        "진행중": [12, 8, 5, 7, 10],
        "대기": [8, 5, 3, 4, 6]
    })

    # Plotly 누적 막대 차트
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='완료',
        x=mission_types["미션 타입"],
        y=mission_types["완료"],
        marker_color='#00b894',
        text=mission_types["완료"],
        textposition='inside'
    ))
    fig.add_trace(go.Bar(
        name='진행중',
        x=mission_types["미션 타입"],
        y=mission_types["진행중"],
        marker_color='#74b9ff',
        text=mission_types["진행중"],
        textposition='inside'
    ))
    fig.add_trace(go.Bar(
        name='대기',
        x=mission_types["미션 타입"],
        y=mission_types["대기"],
        marker_color='#dfe6e9',
        text=mission_types["대기"],
        textposition='inside'
    ))
    fig.update_layout(
        barmode='stack',
        height=400,
        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    st.plotly_chart(fig, use_container_width=True)


# ============== 탭 3: 시민 참여 ==============
with tab3:
    # 히어로 배너
    st.markdown("""
    <div class='hero-banner'>
        <div class='hero-title'>👥 시민 참여 센터</div>
        <div class='hero-subtitle'>함께 만드는 시원한 경기도! 미션에 참여하고 포인트를 모으세요</div>
    </div>
    """, unsafe_allow_html=True)

    # 내 활동 상세 대시보드
    st.markdown("### 🏆 내 활동 상세")
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.markdown("""
        <div class='big-metric' style='border-color: #f093fb;'>
            <div class='metric-icon'>💎</div>
            <div class='metric-value'>1,250</div>
            <div class='metric-label'>총 포인트</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class='big-metric' style='border-color: #feca57;'>
            <div class='metric-icon'>🌟</div>
            <div class='metric-value'>Lv.5</div>
            <div class='metric-label'>현재 레벨</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class='big-metric' style='border-color: #48dbfb;'>
            <div class='metric-icon'>✅</div>
            <div class='metric-value'>12</div>
            <div class='metric-label'>완료 미션</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class='big-metric heat-low'>
            <div class='metric-icon'>❄️</div>
            <div class='metric-value'>-2.3°C</div>
            <div class='metric-label'>냉각 기여</div>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        st.markdown("""
        <div class='big-metric' style='border-color: #1dd1a1;'>
            <div class='metric-icon'>🌳</div>
            <div class='metric-value'>45</div>
            <div class='metric-label'>심은 나무</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # 미션 필터
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox("상태", ["전체", "대기중", "진행중", "완료"])
    with col2:
        type_filter = st.selectbox("미션 타입", ["전체", "나무 심기", "옥상 녹화", "쿨페이브먼트", "수경시설", "그늘막 설치"])
    with col3:
        sort_by = st.selectbox("정렬", ["우선순위", "보상 포인트", "난이도"])

    st.markdown("---")

    # Mock 미션 데이터
    mock_missions = [
        {
            "id": 1,
            "title": "수원시 가로수 심기",
            "type": "나무 심기",
            "status": "대기중",
            "location": "수원시",
            "points": 50,
            "difficulty": 2,
            "cooling_effect": 0.3,
            "ai_reason": "해당 지역은 열섬 강도가 높고 녹지율이 낮습니다. 가로수 식재를 통해 그늘 제공 및 증발산 효과를 기대할 수 있습니다."
        },
        {
            "id": 2,
            "title": "부천시 옥상 녹화 프로젝트",
            "type": "옥상 녹화",
            "status": "진행중",
            "location": "부천시",
            "points": 100,
            "difficulty": 4,
            "cooling_effect": 0.5,
            "progress": 65,  # 진행률 (%)
            "ai_reason": "부천시는 인구 밀집 지역으로 건물 옥상 온도가 주변보다 5°C 이상 높습니다. 옥상 녹화로 건물 냉방 에너지 절감 효과도 기대됩니다."
        },
        {
            "id": 3,
            "title": "시흥시 쿨페이브먼트 시공",
            "type": "쿨페이브먼트",
            "status": "대기중",
            "location": "시흥시",
            "points": 80,
            "difficulty": 3,
            "cooling_effect": 0.4,
            "ai_reason": "시흥시 산업단지 주변 도로의 표면 온도가 60°C를 초과합니다. 차열성 포장재 적용으로 복사열 저감이 필요합니다."
        },
        {
            "id": 4,
            "title": "성남시 분당구 분수대 설치",
            "type": "수경시설",
            "status": "완료",
            "location": "성남시",
            "points": 70,
            "difficulty": 3,
            "cooling_effect": 0.2,
            "ai_reason": "분당 중앙공원 인근의 체감온도가 높아 시민 불편이 접수되었습니다. 수경시설로 국지적 냉각 효과를 제공합니다."
        },
        {
            "id": 5,
            "title": "안양시 버스정류장 그늘막",
            "type": "그늘막 설치",
            "status": "진행중",
            "location": "안양시",
            "points": 30,
            "difficulty": 1,
            "cooling_effect": 0.1,
            "progress": 35,  # 진행률 (%)
            "ai_reason": "안양역 인근 버스정류장의 대기 시민들이 직사광선에 노출되어 있습니다. 그늘막 설치로 체감온도를 3°C 이상 낮출 수 있습니다."
        },
        {
            "id": 6,
            "title": "광명시 도심 녹지 조성",
            "type": "나무 심기",
            "status": "대기중",
            "location": "광명시",
            "points": 80,
            "difficulty": 3,
            "cooling_effect": 0.4,
            "ai_reason": "광명시는 경기도 내 가장 높은 인구밀도를 보이며 녹지율이 부족합니다. 도심 녹지 조성이 시급합니다."
        }
    ]

    # === Phase 1: 주간 챌린지 ===
    st.markdown("### 🏆 이번 주 챌린지")
    challenges = fetch_weekly_challenges()

    if challenges:
        for challenge in challenges:
            progress_pct = challenge['progress_percentage']
            st.markdown(f"""
            <div class='challenge-card'>
                <div class='challenge-title'>{challenge['title']}</div>
                <div class='challenge-desc'>{challenge['description']}</div>
                <div class='progress-bar'>
                    <div class='progress-fill' style='width: {progress_pct}%'></div>
                </div>
                <div style='display: flex; justify-content: space-between; margin-top: 0.5rem;'>
                    <span><strong>{challenge['current_progress']}/{challenge['goal_count']}</strong> 완료</span>
                    <span style='background: rgba(0,0,0,0.1); padding: 0.2rem 0.5rem; border-radius: 5px;'>
                        보상: <strong>{challenge['reward_points']}P</strong>
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("⏳ FastAPI 백엔드를 실행하면 주간 챌린지를 볼 수 있습니다.")

    st.markdown("---")

    # === Phase 2: 배지 컬렉션 ===
    st.markdown("### 🏅 배지 컬렉션")

    # 더미 user_id (실제로는 로그인 시스템에서 가져와야 함)
    current_user_id = 1
    badges = fetch_badges(user_id=current_user_id)

    if badges:
        # 획득/미획득 배지 분류
        earned_badges = [b for b in badges if b['is_earned']]
        locked_badges = [b for b in badges if not b['is_earned']]

        # 상태 표시
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**획득한 배지:** {len(earned_badges)}/{len(badges)}")
        with col2:
            completion_pct = int((len(earned_badges) / len(badges)) * 100) if badges else 0
            st.markdown(f"**달성률:** {completion_pct}%")

        # 배지 그리드 (4열)
        cols_per_row = 5
        all_badges_sorted = earned_badges + locked_badges  # 획득한 배지 먼저 표시

        for i in range(0, len(all_badges_sorted), cols_per_row):
            cols = st.columns(cols_per_row)
            for j, badge in enumerate(all_badges_sorted[i:i+cols_per_row]):
                with cols[j]:
                    card_class = "badge-card earned" if badge['is_earned'] else "badge-card locked"
                    st.markdown(f"""
                    <div class='{card_class}'>
                        <div class='badge-icon'>{badge['icon']}</div>
                        <div class='badge-name'>{badge['name']}</div>
                        <div class='badge-desc'>{badge['description']}</div>
                        <div class='badge-requirement'>{badge['requirement']}</div>
                        <div class='badge-points'>+{badge['points']}P</div>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("⏳ FastAPI 백엔드를 실행하면 배지 컬렉션을 볼 수 있습니다.")

    st.markdown("---")

    # === Phase 1: 2열 레이아웃 (활동 피드 + 랭킹) ===
    col_feed, col_rank = st.columns(2)

    with col_feed:
        st.markdown("### 🔥 실시간 활동 피드")
        activities = fetch_activity_feed(limit=10)

        if activities:
            for activity in activities:
                # 액션 타입에 따른 아이콘
                action_icons = {
                    "mission_complete": "✅",
                    "mission_start": "🚀",
                    "level_up": "⬆️",
                    "badge_earned": "🏅"
                }
                icon = action_icons.get(activity['action_type'], "📌")

                # 시간 포맷팅
                time_str = activity['created_at'][:16].replace("T", " ")

                points_text = f"+{activity['points_earned']}P" if activity['points_earned'] > 0 else ""

                st.markdown(f"""
                <div class='activity-feed'>
                    {icon} <strong>{activity['user_name']}</strong>님이 <strong>{activity['mission_title']}</strong> {points_text}
                    <div class='activity-time'>{time_str}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("⏳ FastAPI 백엔드를 실행하면 실시간 활동을 볼 수 있습니다.")

    with col_rank:
        st.markdown("### 🏆 이번 주 TOP 10")
        leaderboard = fetch_leaderboard(limit=10)

        if leaderboard:
            for entry in leaderboard:
                rank = entry['rank']
                rank_class = "rank-gold" if rank == 1 else "rank-silver" if rank == 2 else "rank-bronze" if rank == 3 else ""

                medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else ""

                st.markdown(f"""
                <div class='rank-card'>
                    <div class='rank-number {rank_class}'>{medal or rank}</div>
                    <div style='flex: 1;'>
                        <strong>{entry['username']}</strong>
                        <div style='font-size: 0.8rem; color: #666;'>
                            Lv.{entry['level']} | {entry['total_points']}P | {entry['cooling_contribution']}°C 기여
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("⏳ FastAPI 백엔드를 실행하면 랭킹을 볼 수 있습니다.")

    st.markdown("---")

    # 추천 미션 섹션
    st.markdown("### 🎯 추천 미션 (지금 참여하세요!)")

    # 미션 카드 표시 (큰 카드 형태)
    for mission in mock_missions:
        # 필터 적용
        if status_filter != "전체" and mission["status"] != status_filter:
            continue
        if type_filter != "전체" and mission["type"] != type_filter:
            continue

        status_emoji = {"대기중": "🟡", "진행중": "🔵", "완료": "🟢"}
        status_badge = f"{status_emoji.get(mission['status'], '⚪')} {mission['status']}"

        # 미션 카드 HTML (진행률 바 포함)
        if mission['status'] == "진행중" and mission.get('progress'):
            progress_pct = mission['progress']
            # 진행률 바가 있는 카드
            st.markdown(f"""
            <div class='mission-card'>
                <div class='mission-card-title'>{mission['title']}</div>
                <div class='mission-card-meta'>
                    <span class='mission-card-tag'>📍 {mission['location']}</span>
                    <span class='mission-card-tag'>{mission['type']}</span>
                    <span class='mission-card-tag'>{status_badge}</span>
                </div>
                <p style='color: #666; margin: 1rem 0;'>
                    <strong>🤖 AI 분석:</strong><br>
                    {mission['ai_reason']}
                </p>
                <div style='margin-top: 1rem;'>
                    <div style='display: flex; justify-content: space-between; margin-bottom: 0.3rem;'>
                        <span style='font-size: 0.9rem; font-weight: 600;'>진행 상황</span>
                        <span style='font-size: 0.9rem; color: #667eea;'><strong>{progress_pct}%</strong></span>
                    </div>
                    <div class='progress-bar'>
                        <div class='progress-fill' style='width: {progress_pct}%; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);'></div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # 진행률 바가 없는 카드
            st.markdown(f"""
            <div class='mission-card'>
                <div class='mission-card-title'>{mission['title']}</div>
                <div class='mission-card-meta'>
                    <span class='mission-card-tag'>📍 {mission['location']}</span>
                    <span class='mission-card-tag'>{mission['type']}</span>
                    <span class='mission-card-tag'>{status_badge}</span>
                </div>
                <p style='color: #666; margin: 1rem 0;'>
                    <strong>🤖 AI 분석:</strong><br>
                    {mission['ai_reason']}
                </p>
            </div>
            """, unsafe_allow_html=True)

        # 메트릭과 CTA 버튼
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("💎 보상", f"{mission['points']}P")
        with col2:
            st.metric("⭐ 난이도", "⭐" * mission['difficulty'])
        with col3:
            st.metric("❄️ 냉각 효과", f"-{mission['cooling_effect']}°C")
        with col4:
            if mission['status'] == "대기중":
                if st.button("✅ 지금 참여하기", key=f"join_{mission['id']}", type="primary", use_container_width=True):
                    st.success("🎉 미션에 참여했습니다! 포인트를 획득했어요!")
            elif mission['status'] == "진행중":
                st.button("🔄 진행 중", key=f"progress_{mission['id']}", disabled=True, use_container_width=True)
            else:
                st.button("🟢 완료됨", key=f"done_{mission['id']}", disabled=True, use_container_width=True)

        st.markdown("---")


# ============== 탭 4: 내 프로필 ==============
with tab4:
    # 히어로 배너
    st.markdown("""
    <div class='hero-banner'>
        <div class='hero-title'>👤 내 프로필</div>
        <div class='hero-subtitle'>활동 내역 및 통계를 확인하세요</div>
    </div>
    """, unsafe_allow_html=True)

    # 더미 사용자 데이터 (실제로는 로그인 시스템에서 가져와야 함)
    current_user_id = 1

    # 사용자 기본 정보 카드
    st.markdown("### 📝 기본 정보")
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        st.markdown("""
        <div style='text-align: center;'>
            <div style='width: 120px; height: 120px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        border-radius: 50%; margin: 0 auto; display: flex; align-items: center; justify-content: center;'>
                <span style='font-size: 4rem; color: white;'>👤</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style='padding: 1rem;'>
            <h2 style='margin: 0; color: #333;'>김민준01</h2>
            <p style='color: #666; margin: 0.5rem 0;'>📧 user001@example.com</p>
            <p style='color: #666; margin: 0.5rem 0;'>📅 가입일: 2026-01-11</p>
            <div style='display: flex; gap: 1rem; margin-top: 1rem;'>
                <span style='background: #667eea; color: white; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.9rem;'>
                    ⭐ Level 8
                </span>
                <span style='background: #fdcb6e; color: white; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.9rem;'>
                    👑 VIP 회원
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        if st.button("✏️ 프로필 수정", use_container_width=True):
            st.info("프로필 수정 기능은 추후 구현 예정입니다.")

    st.markdown("---")

    # 활동 통계
    st.markdown("### 📊 활동 통계")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class='big-metric' style='border-color: #667eea;'>
            <div class='metric-icon'>🎯</div>
            <div class='metric-value'>22</div>
            <div class='metric-label'>완료한 미션</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class='big-metric' style='border-color: #00b894;'>
            <div class='metric-icon'>💎</div>
            <div class='metric-value'>2,538</div>
            <div class='metric-label'>총 포인트</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class='big-metric' style='border-color: #fd79a8;'>
            <div class='metric-icon'>🌳</div>
            <div class='metric-value'>94</div>
            <div class='metric-label'>심은 나무</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class='big-metric' style='border-color: #74b9ff;'>
            <div class='metric-icon'>❄️</div>
            <div class='metric-value'>1.4°C</div>
            <div class='metric-label'>냉각 기여도</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # 획득한 배지
    st.markdown("### 🏅 획득한 배지")
    badges = fetch_badges(user_id=current_user_id)
    earned_badges = [b for b in badges if b['is_earned']] if badges else []

    if earned_badges:
        cols_per_row = 5
        for i in range(0, len(earned_badges), cols_per_row):
            cols = st.columns(cols_per_row)
            for j, badge in enumerate(earned_badges[i:i+cols_per_row]):
                with cols[j]:
                    st.markdown(f"""
                    <div class='badge-card earned'>
                        <div class='badge-icon'>{badge['icon']}</div>
                        <div class='badge-name'>{badge['name']}</div>
                        <div class='badge-desc'>{badge['description']}</div>
                        <div class='badge-requirement'>{badge['requirement']}</div>
                        <div class='badge-points'>+{badge['points']}P</div>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("아직 획득한 배지가 없습니다. 미션을 완료하고 배지를 모아보세요!")

    st.markdown("---")

    # 최근 활동 내역
    st.markdown("### 📜 최근 활동 내역")

    col1, col2 = st.columns([2, 1])

    with col1:
        # 미션 완료 내역 (더미 데이터)
        st.markdown("#### 🎯 완료한 미션")
        recent_missions = [
            {"title": "수원시 가로수 심기", "date": "2026-01-10", "points": 50},
            {"title": "부천시 옥상 녹화 프로젝트", "date": "2026-01-08", "points": 100},
            {"title": "시흥시 쿨페이브먼트 시공", "date": "2026-01-05", "points": 80},
            {"title": "성남시 분당구 분수대 설치", "date": "2026-01-03", "points": 70},
            {"title": "안양시 버스정류장 그늘막", "date": "2025-12-28", "points": 30},
        ]

        for mission in recent_missions:
            st.markdown(f"""
            <div class='activity-feed'>
                ✅ <strong>{mission['title']}</strong> +{mission['points']}P
                <div class='activity-time'>{mission['date']}</div>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        # 레벨 진행도
        st.markdown("#### ⭐ 레벨 진행도")
        current_level = 8
        current_xp = 2538
        next_level_xp = 3000
        progress_pct = int((current_xp / next_level_xp) * 100)

        st.markdown(f"""
        <div style='background: white; padding: 1.5rem; border-radius: 12px;'>
            <div style='text-align: center; margin-bottom: 1rem;'>
                <h2 style='margin: 0; color: #667eea;'>Level {current_level}</h2>
                <p style='color: #666; font-size: 0.9rem; margin: 0.5rem 0;'>다음 레벨까지</p>
                <p style='color: #333; font-weight: 700;'>{next_level_xp - current_xp}P 남음</p>
            </div>
            <div class='progress-bar'>
                <div class='progress-fill' style='width: {progress_pct}%; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);'></div>
            </div>
            <div style='text-align: center; margin-top: 0.5rem; font-size: 0.85rem; color: #666;'>
                {current_xp} / {next_level_xp} XP
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # 랭킹 정보
        st.markdown("#### 🏆 내 순위")
        st.markdown("""
        <div style='background: white; padding: 1.5rem; border-radius: 12px; text-align: center;'>
            <div style='font-size: 3rem; color: #f39c12;'>🥇</div>
            <h2 style='margin: 0.5rem 0; color: #333;'>#1</h2>
            <p style='color: #666; font-size: 0.9rem;'>전체 랭킹</p>
        </div>
        """, unsafe_allow_html=True)


# ============== 탭 5: 정보 ==============
with tab5:
    # 히어로 배너
    st.markdown("""
    <div class='hero-banner'>
        <div class='hero-title'>ℹ️ Urban Cooling Farm 정보</div>
        <div class='hero-subtitle'>시민이 가꾸는 텃밭으로 도시 열섬을 식히는 기후 케어 플랫폼</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    ## 프로젝트 소개

    **Urban Cooling Farm**은 AI 기반 도시 열섬 완화 시스템입니다.

    ### 주요 기능
    - 🌡️ **실시간 열섬 모니터링**: 경기기후플랫폼 API 연동
    - 🤖 **AI 미션 생성**: 냉각 효과 최대화를 위한 자동 미션 생성
    - 🗺️ **지도 시각화**: Folium 기반 열섬 현황 지도
    - 📊 **효과 측정**: 쿨링팜 설치 전후 효과 분석

    ### 열섬 현상이란?
    도시 지역의 기온이 주변 지역보다 높게 나타나는 현상입니다.
    주요 원인:
    - 콘크리트, 아스팔트 등 인공 구조물의 열 흡수
    - 녹지 공간 부족
    - 에어컨 등 인공 열원

    ### 열섬 강도 계산 방식
    본 시스템은 경기기후플랫폼의 **공원 데이터**를 활용하여 열섬 취약 지역을 분석합니다:
    - **녹지율**: 공원 면적 기반 녹지 비율 계산
    - **인구밀도**: 밀집 지역일수록 열섬 강도 증가
    - **열섬 강도** = 기본값 + (녹지 부족 요인) + (인구밀도 요인)

    ### 냉각 솔루션
    | 솔루션 | 냉각 효과 | 설명 |
    |--------|-----------|------|
    | 가로수 식재 | -0.3°C ~ -1.0°C | 그늘 제공 및 증발산 효과 |
    | 옥상 녹화 | -0.5°C ~ -2.0°C | 건물 온도 저감 |
    | 쿨페이브먼트 | -0.2°C ~ -0.5°C | 복사열 반사 |
    | 수경시설 | -0.2°C ~ -0.5°C | 증발 냉각 |
    | 그늘막 | -0.1°C ~ -0.3°C | 직사광선 차단 |

    ---
    ### 기술 스택
    - **Backend**: FastAPI, SQLAlchemy
    - **Frontend**: Streamlit, Folium
    - **Data**: 경기기후플랫폼 WFS API (park 레이어)

    ### 데이터 출처
    - 경기기후플랫폼 (https://climate.gg.go.kr)
    - 공원현황도 레이어 활용
    """)

    st.markdown("---")
    st.caption("© 2024 Urban Cooling Farm Project")
