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
import sys
import os

# 프로젝트 루트를 path에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.climate_service import ClimateService, MOCK_HEAT_ISLAND_LOCATIONS

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


# ============== Initialize Services ==============
@st.cache_resource
def get_climate_service():
    return ClimateService()


climate_service = get_climate_service()


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
        color = get_heat_color(data.heat_island_intensity)
        level = get_heat_level(data.heat_island_intensity)

        popup_html = f"""
        <div style="width: 200px;">
            <h4 style="margin: 0; color: #333;">{data.district}</h4>
            <hr style="margin: 5px 0;">
            <p style="margin: 5px 0;"><b>현재 온도:</b> {data.temperature}°C</p>
            <p style="margin: 5px 0;"><b>열섬 강도:</b> +{data.heat_island_intensity}°C</p>
            <p style="margin: 5px 0;"><b>위험 수준:</b> <span style="color: {color};">{level}</span></p>
            <p style="margin: 5px 0; font-size: 0.8em; color: #666;">
                측정: {data.timestamp.strftime('%Y-%m-%d %H:%M')}
            </p>
        </div>
        """

        # 원형 마커 (열섬 강도에 비례하는 크기)
        folium.CircleMarker(
            location=[data.latitude, data.longitude],
            radius=10 + data.heat_island_intensity * 5,
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.6,
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"{data.district}: +{data.heat_island_intensity}°C"
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
        ["전체"] + [loc["district"] for loc in MOCK_HEAT_ISLAND_LOCATIONS]
    )

    intensity_filter = st.slider(
        "최소 열섬 강도 (°C)",
        min_value=0.0,
        max_value=3.0,
        value=0.0,
        step=0.1
    )

    st.markdown("---")
    st.caption(f"마지막 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M')}")


# ============== Main Content ==============
if page == "🗺️ 열섬 현황 지도":
    st.markdown('<p class="main-header">🌡️ 경기도 열섬 현황 지도</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">실시간 도시 열섬 모니터링 및 냉각 우선지역 분석</p>', unsafe_allow_html=True)

    # 데이터 로드
    district_param = None if district_filter == "전체" else district_filter

    # 동기 함수로 Mock 데이터 직접 호출
    if district_param:
        heat_data = climate_service._generate_mock_heat_island_data(district_param)
    else:
        heat_data = climate_service._generate_mock_heat_island_data(None)

    # 강도 필터 적용
    heat_data = [d for d in heat_data if d.heat_island_intensity >= intensity_filter]

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
            avg_temp = sum(d.temperature for d in heat_data) / len(heat_data)
            st.metric(
                label="평균 온도",
                value=f"{avg_temp:.1f}°C",
                delta=f"+{sum(d.heat_island_intensity for d in heat_data) / len(heat_data):.1f}°C"
            )
        else:
            st.metric(label="평균 온도", value="N/A")

    with col3:
        if heat_data:
            max_intensity = max(d.heat_island_intensity for d in heat_data)
            st.metric(
                label="최대 열섬 강도",
                value=f"+{max_intensity:.1f}°C",
                delta="심각" if max_intensity >= 2.0 else "주의"
            )
        else:
            st.metric(label="최대 열섬 강도", value="N/A")

    with col4:
        critical_count = len([d for d in heat_data if d.heat_island_intensity >= 2.0])
        st.metric(
            label="심각 지역",
            value=f"{critical_count}개",
            delta="즉시 조치 필요" if critical_count > 0 else "양호"
        )

    st.markdown("---")

    # 지도 표시
    if heat_data:
        # 중심점 계산
        center_lat = sum(d.latitude for d in heat_data) / len(heat_data)
        center_lng = sum(d.longitude for d in heat_data) / len(heat_data)

        heat_map = create_heat_island_map(heat_data, center=(center_lat, center_lng))
        st_folium(heat_map, width=None, height=500, use_container_width=True)
    else:
        st.warning("선택한 조건에 맞는 데이터가 없습니다.")

    # 데이터 테이블
    st.markdown("### 📋 상세 데이터")

    if heat_data:
        df = pd.DataFrame([
            {
                "지역": d.district,
                "위도": round(d.latitude, 4),
                "경도": round(d.longitude, 4),
                "온도 (°C)": d.temperature,
                "열섬 강도 (°C)": f"+{d.heat_island_intensity}",
                "위험 수준": get_heat_level(d.heat_island_intensity),
                "측정 시간": d.timestamp.strftime('%H:%M')
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
        heat_data = climate_service._generate_mock_heat_island_data(None)
        intensity_df = pd.DataFrame({
            "지역": [d.district.split()[0] for d in heat_data],
            "강도": [d.heat_island_intensity for d in heat_data]
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
            "title": "수원시 팔달구 가로수 심기",
            "type": "나무 심기",
            "status": "대기중",
            "location": "수원시 팔달구",
            "points": 50,
            "difficulty": 2,
            "cooling_effect": 0.3,
            "ai_reason": "해당 지역은 열섬 강도 2.5°C로 경기도 내 최고 수준입니다. 가로수 식재를 통해 그늘 제공 및 증발산 효과를 기대할 수 있습니다."
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
            "location": "성남시 분당구",
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
            "location": "안양시 만안구",
            "points": 30,
            "difficulty": 1,
            "cooling_effect": 0.1,
            "ai_reason": "안양역 인근 버스정류장의 대기 시민들이 직사광선에 노출되어 있습니다. 그늘막 설치로 체감온도를 3°C 이상 낮출 수 있습니다."
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
    - 🌡️ **실시간 열섬 모니터링**: 경기기후플랫폼 연동
    - 🤖 **AI 미션 생성**: 냉각 효과 최대화를 위한 자동 미션 생성
    - 🗺️ **지도 시각화**: Folium 기반 열섬 현황 지도
    - 📊 **효과 측정**: 쿨링팜 설치 전후 효과 분석

    ### 열섬 현상이란?
    도시 지역의 기온이 주변 지역보다 높게 나타나는 현상입니다.
    주요 원인:
    - 콘크리트, 아스팔트 등 인공 구조물의 열 흡수
    - 녹지 공간 부족
    - 에어컨 등 인공 열원

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
    - **Data**: 경기기후플랫폼 API
    """)

    st.markdown("---")
    st.caption("© 2024 Urban Cooling Farm Project")
