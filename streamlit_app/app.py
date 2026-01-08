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

# .env 파일 로드
load_dotenv()

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
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
    }
    .heat-high { color: #ff4444; font-weight: bold; }
    .heat-medium { color: #ffaa00; font-weight: bold; }
    .heat-low { color: #44aa44; font-weight: bold; }
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

    # 페이지 선택
    page = st.radio(
        "메뉴",
        ["🗺️ 열섬 현황 지도", "📊 대시보드", "🎯 미션 현황", "ℹ️ 정보"],
        index=0
    )

    st.markdown("---")

    # 필터 옵션
    st.subheader("필터")
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

    # 데이터 새로고침 버튼
    if st.button("🔄 데이터 새로고침"):
        st.cache_data.clear()
        st.rerun()

    st.caption(f"마지막 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M')}")


# ============== Main Content ==============
if page == "🗺️ 열섬 현황 지도":
    st.markdown('<p class="main-header">🌡️ 경기도 열섬 현황 지도</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">실시간 도시 열섬 모니터링 및 냉각 우선지역 분석</p>', unsafe_allow_html=True)

    # 데이터 로드 (캐시됨)
    district_param = None if district_filter == "전체" else district_filter
    heat_data = calculate_heat_island_data(district_param)

    # 강도 필터 적용
    heat_data = [d for d in heat_data if d["heat_island_intensity"] >= intensity_filter]

    # 상단 메트릭
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="모니터링 지점",
            value=f"{len(heat_data)}개",
            delta=None
        )

    with col2:
        if heat_data:
            avg_temp = sum(d["temperature"] for d in heat_data) / len(heat_data)
            avg_intensity = sum(d["heat_island_intensity"] for d in heat_data) / len(heat_data)
            st.metric(
                label="평균 온도",
                value=f"{avg_temp:.1f}°C",
                delta=f"+{avg_intensity:.1f}°C"
            )
        else:
            st.metric(label="평균 온도", value="N/A")

    with col3:
        if heat_data:
            max_intensity = max(d["heat_island_intensity"] for d in heat_data)
            st.metric(
                label="최대 열섬 강도",
                value=f"+{max_intensity:.1f}°C",
                delta="심각" if max_intensity >= 2.0 else "주의"
            )
        else:
            st.metric(label="최대 열섬 강도", value="N/A")

    with col4:
        critical_count = len([d for d in heat_data if d["heat_island_intensity"] >= 2.0])
        st.metric(
            label="심각 지역",
            value=f"{critical_count}개",
            delta="즉시 조치 필요" if critical_count > 0 else "양호"
        )

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


elif page == "📊 대시보드":
    st.markdown('<p class="main-header">📊 냉각 효과 대시보드</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">쿨링팜 프로젝트 성과 및 효과 분석</p>', unsafe_allow_html=True)

    # Mock 통계 데이터
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("총 쿨링스팟", "24개", "+3")
    with col2:
        st.metric("완료된 미션", "156개", "+12")
    with col3:
        st.metric("예상 냉각 효과", "-1.2°C", "-0.3°C")
    with col4:
        st.metric("참여 시민", "1,247명", "+89")

    st.markdown("---")

    # 차트 영역
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("📈 월별 미션 완료 현황")
        chart_data = pd.DataFrame({
            "월": ["8월", "9월", "10월", "11월", "12월"],
            "완료 미션": [23, 35, 42, 38, 18]
        })
        st.bar_chart(chart_data.set_index("월"))

    with col_right:
        st.subheader("🌡️ 지역별 열섬 강도")
        # 캐시된 데이터 사용
        heat_data = calculate_heat_island_data(None)
        intensity_df = pd.DataFrame({
            "지역": [d["district"] for d in heat_data],
            "강도": [d["heat_island_intensity"] for d in heat_data]
        })
        st.bar_chart(intensity_df.set_index("지역"))

    st.markdown("---")

    # 미션 타입별 현황
    st.subheader("🎯 미션 타입별 현황")
    mission_types = pd.DataFrame({
        "미션 타입": ["나무 심기", "옥상 녹화", "쿨페이브먼트", "수경시설", "그늘막 설치"],
        "완료": [45, 28, 32, 21, 30],
        "진행중": [12, 8, 5, 7, 10],
        "대기": [8, 5, 3, 4, 6]
    })
    st.dataframe(mission_types, use_container_width=True, hide_index=True)


elif page == "🎯 미션 현황":
    st.markdown('<p class="main-header">🎯 AI 생성 미션 현황</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">도시 냉각을 위한 시민 참여 미션</p>', unsafe_allow_html=True)

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

    # 미션 카드 표시
    for mission in mock_missions:
        # 필터 적용
        if status_filter != "전체" and mission["status"] != status_filter:
            continue
        if type_filter != "전체" and mission["type"] != type_filter:
            continue

        status_color = {"대기중": "🟡", "진행중": "🔵", "완료": "🟢"}

        with st.expander(f"{status_color.get(mission['status'], '⚪')} {mission['title']}", expanded=False):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown(f"**위치:** {mission['location']}")
                st.markdown(f"**타입:** {mission['type']}")
                st.markdown(f"**상태:** {mission['status']}")
                st.markdown("---")
                st.markdown("**🤖 AI 분석:**")
                st.info(mission['ai_reason'])

            with col2:
                st.metric("보상 포인트", f"{mission['points']}P")
                st.metric("난이도", "⭐" * mission['difficulty'])
                st.metric("예상 냉각 효과", f"-{mission['cooling_effect']}°C")

                if mission['status'] == "대기중":
                    if st.button("미션 참여", key=f"join_{mission['id']}"):
                        st.success("미션에 참여했습니다!")


elif page == "ℹ️ 정보":
    st.markdown('<p class="main-header">ℹ️ Urban Cooling Farm 정보</p>', unsafe_allow_html=True)

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
