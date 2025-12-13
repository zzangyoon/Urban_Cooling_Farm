# streamlit run streamlit_app/app.py
"""
효과 측정 대시보드

쿨링팜 설치 효과 분석 및 시각화
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import sys
import os

# 프로젝트 루트를 path에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.services.effect_service import EffectService

# ============== Page Config ==============
st.set_page_config(
    page_title="효과 측정 대시보드 | Urban Cooling Farm",
    page_icon="📊",
    layout="wide"
)

# ============== Custom CSS ==============
st.markdown("""
<style>
    .metric-container {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
    }
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.8;
    }
    .improvement-positive {
        color: #00cc66;
        font-weight: bold;
    }
    .improvement-negative {
        color: #ff4444;
        font-weight: bold;
    }
    .chart-container {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# ============== Initialize Service ==============
effect_service = EffectService()

# ============== Header ==============
st.title("📊 효과 측정 대시보드")
st.markdown("쿨링팜 프로젝트의 도시 냉각 효과를 실시간으로 분석합니다.")
st.markdown("---")

# ============== Overall Stats ==============
st.subheader("🎯 전체 성과 지표")

stats = effect_service.get_overall_stats()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="총 쿨링스팟",
        value=f"{stats.total_cooling_spots}개",
        delta="+3 이번달"
    )

with col2:
    st.metric(
        label="완료 미션",
        value=f"{stats.total_missions_completed}개",
        delta="+12 이번달"
    )

with col3:
    st.metric(
        label="평균 냉각 효과",
        value=f"-{stats.avg_cooling_effect}°C",
        delta="-0.2°C 개선"
    )

with col4:
    st.metric(
        label="CO2 저감",
        value=f"{stats.co2_reduction_kg:,}kg",
        delta="+240kg 이번달"
    )

st.markdown("---")

# ============== Time Series Chart ==============
st.subheader("📈 시계열 온도 변화")

col_chart, col_control = st.columns([3, 1])

with col_control:
    days_range = st.slider("조회 기간 (일)", 7, 90, 30)
    show_humidity = st.checkbox("습도 표시", value=False)

time_series = effect_service.get_time_series(cooling_spot_id=1, days=days_range)

if time_series:
    df_ts = pd.DataFrame([
        {
            "시간": ts.timestamp,
            "온도": ts.temperature,
            "냉각효과": ts.cooling_effect,
            "습도": ts.humidity
        }
        for ts in time_series
    ])

    # 일별 평균으로 리샘플링
    df_ts['날짜'] = pd.to_datetime(df_ts['시간']).dt.date
    df_daily = df_ts.groupby('날짜').agg({
        '온도': 'mean',
        '냉각효과': 'mean',
        '습도': 'mean'
    }).reset_index()

    with col_chart:
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # 온도 라인
        fig.add_trace(
            go.Scatter(
                x=df_daily['날짜'],
                y=df_daily['온도'],
                name="온도 (°C)",
                line=dict(color="#ff6b6b", width=2)
            ),
            secondary_y=False
        )

        # 냉각 효과 바
        fig.add_trace(
            go.Bar(
                x=df_daily['날짜'],
                y=df_daily['냉각효과'],
                name="냉각 효과 (°C)",
                marker_color="#4ecdc4",
                opacity=0.6
            ),
            secondary_y=True
        )

        if show_humidity:
            fig.add_trace(
                go.Scatter(
                    x=df_daily['날짜'],
                    y=df_daily['습도'],
                    name="습도 (%)",
                    line=dict(color="#95afc0", width=1, dash='dot')
                ),
                secondary_y=False
            )

        fig.update_layout(
            title="일별 온도 및 냉각 효과 추이",
            height=400,
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02)
        )
        fig.update_yaxes(title_text="온도 (°C)", secondary_y=False)
        fig.update_yaxes(title_text="냉각 효과 (°C)", secondary_y=True)

        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ============== Before/After Comparison ==============
st.subheader("📉 설치 전후 비교")

comparison_data = effect_service.get_before_after_comparison(cooling_spot_id=1)

col1, col2 = st.columns(2)

with col1:
    df_comp = pd.DataFrame([
        {
            "기간": c.period,
            "설치 전": c.before_avg_temp,
            "설치 후": c.after_avg_temp,
            "냉각효과": c.cooling_effect
        }
        for c in comparison_data
    ])

    fig_comp = go.Figure()

    fig_comp.add_trace(go.Bar(
        name='설치 전',
        x=df_comp['기간'],
        y=df_comp['설치 전'],
        marker_color='#ff6b6b'
    ))

    fig_comp.add_trace(go.Bar(
        name='설치 후',
        x=df_comp['기간'],
        y=df_comp['설치 후'],
        marker_color='#4ecdc4'
    ))

    fig_comp.update_layout(
        title="주별 평균 온도 비교",
        barmode='group',
        height=350,
        yaxis_title="온도 (°C)"
    )

    st.plotly_chart(fig_comp, use_container_width=True)

with col2:
    # 개선율 게이지
    avg_improvement = sum(c.improvement_percent for c in comparison_data) / len(comparison_data)

    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=avg_improvement,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "평균 개선율 (%)"},
        delta={'reference': 3.0, 'increasing': {'color': "#4ecdc4"}},
        gauge={
            'axis': {'range': [None, 10], 'tickwidth': 1},
            'bar': {'color': "#4ecdc4"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 3], 'color': '#ffcccc'},
                {'range': [3, 6], 'color': '#ffffcc'},
                {'range': [6, 10], 'color': '#ccffcc'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 5
            }
        }
    ))

    fig_gauge.update_layout(height=350)
    st.plotly_chart(fig_gauge, use_container_width=True)

st.markdown("---")

# ============== Regional Stats ==============
st.subheader("🗺️ 지역별 효과 분석")

regional_stats = effect_service.get_regional_stats()

col1, col2 = st.columns(2)

with col1:
    df_regional = pd.DataFrame([
        {
            "지역": r.district,
            "쿨링스팟": r.cooling_spots_count,
            "완료미션": r.missions_completed,
            "냉각효과": r.avg_cooling_effect,
            "열섬감소": r.heat_island_reduction
        }
        for r in regional_stats
    ])

    fig_regional = px.bar(
        df_regional,
        x='지역',
        y='냉각효과',
        color='열섬감소',
        color_continuous_scale='Blues',
        title="지역별 평균 냉각 효과"
    )
    fig_regional.update_layout(height=400)
    st.plotly_chart(fig_regional, use_container_width=True)

with col2:
    # 지역별 상세 테이블
    st.markdown("##### 지역별 상세 현황")
    st.dataframe(
        df_regional.sort_values('냉각효과', ascending=False),
        use_container_width=True,
        hide_index=True
    )

st.markdown("---")

# ============== Mission Type Effectiveness ==============
st.subheader("🎯 미션 타입별 효과 분석")

mission_effectiveness = effect_service.get_mission_type_effectiveness()

col1, col2 = st.columns(2)

with col1:
    # 레이더 차트
    categories = []
    effectiveness_scores = []

    for key, data in mission_effectiveness.items():
        categories.append(data['name'])
        effectiveness_scores.append(data['effectiveness_score'])

    fig_radar = go.Figure()

    fig_radar.add_trace(go.Scatterpolar(
        r=effectiveness_scores,
        theta=categories,
        fill='toself',
        name='효과 점수',
        line_color='#4ecdc4'
    ))

    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        title="미션 타입별 효과 점수",
        height=400
    )

    st.plotly_chart(fig_radar, use_container_width=True)

with col2:
    # 미션 타입별 상세
    mission_df = pd.DataFrame([
        {
            "미션 타입": data['name'],
            "평균 냉각효과": f"-{data['avg_cooling_effect']}°C",
            "완료 수": data['missions_completed'],
            "효과 점수": data['effectiveness_score']
        }
        for data in mission_effectiveness.values()
    ])

    st.markdown("##### 미션 타입별 성과")
    st.dataframe(
        mission_df.sort_values('효과 점수', ascending=False),
        use_container_width=True,
        hide_index=True
    )

    # 가장 효과적인 미션
    best_mission = max(mission_effectiveness.values(), key=lambda x: x['effectiveness_score'])
    st.success(f"🏆 가장 효과적인 미션: **{best_mission['name']}** (효과 점수: {best_mission['effectiveness_score']})")

st.markdown("---")

# ============== Environmental Impact ==============
st.subheader("🌍 환경 영향 분석")

env_impact = effect_service.calculate_environmental_impact()

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("##### 🌱 CO2 저감")
    st.metric(
        label="연간 CO2 저감량",
        value=f"{env_impact['co2_reduction']['value']:,} kg"
    )
    st.caption(env_impact['co2_reduction']['equivalent'])

with col2:
    st.markdown("##### ⚡ 에너지 절감")
    st.metric(
        label="연간 에너지 절감",
        value=f"{env_impact['energy_saving']['value']:,} kWh"
    )
    st.caption(env_impact['energy_saving']['equivalent'])

with col3:
    st.markdown("##### 💧 우수 저류")
    st.metric(
        label="연간 빗물 저류",
        value=f"{env_impact['water_retention']['value']:,.0f} 톤"
    )
    st.caption(env_impact['water_retention']['equivalent'])

# 추가 환경 지표
st.markdown("##### 🌿 추가 환경 효과")

env_col1, env_col2 = st.columns(2)

with env_col1:
    st.info(f"""
    **미세먼지 저감**
    - PM2.5 저감량: {env_impact['air_quality']['pm25_reduction']:.1f} kg/년
    - 대기질 개선 효과
    """)

with env_col2:
    st.info(f"""
    **생태 다양성**
    - 서식지 면적: {env_impact['biodiversity']['habitat_area']:,} m²
    - 지원 가능 종 수: 약 {env_impact['biodiversity']['species_supported']}종
    """)

st.markdown("---")

# ============== Summary Report ==============
st.subheader("📋 요약 리포트")

with st.expander("📄 상세 리포트 보기", expanded=False):
    st.markdown(f"""
    ## Urban Cooling Farm 효과 측정 리포트

    **생성일시**: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}

    ### 1. 프로젝트 현황
    - 총 쿨링스팟: **{stats.total_cooling_spots}개**
    - 완료된 미션: **{stats.total_missions_completed}건**
    - 총 측정 횟수: **{stats.total_measurements:,}회**

    ### 2. 냉각 효과
    - 평균 냉각 효과: **-{stats.avg_cooling_effect}°C**
    - 총 예상 냉각 효과: **-{stats.total_estimated_cooling}°C**
    - 식재된 나무: **{stats.total_trees_planted}그루**
    - 녹화 면적: **{stats.total_green_area_m2:,}m²**

    ### 3. 환경 영향
    - CO2 저감: **{env_impact['co2_reduction']['value']:,}kg/년**
    - 에너지 절감: **{env_impact['energy_saving']['value']:,}kWh/년**
    - 미세먼지 저감: **{env_impact['air_quality']['pm25_reduction']:.1f}kg/년**

    ### 4. 권장사항
    1. **옥상 녹화** 프로젝트 확대 (최고 효과 점수)
    2. 열섬 강도가 높은 **수원시, 부천시** 지역 집중 투자
    3. 시민 참여 미션 확대를 통한 녹지율 향상

    ---
    *이 리포트는 자동으로 생성되었습니다.*
    """)

    # 다운로드 버튼
    report_text = f"Urban Cooling Farm 효과 측정 리포트\n생성일: {datetime.now()}\n..."
    st.download_button(
        label="📥 리포트 다운로드 (TXT)",
        data=report_text,
        file_name=f"cooling_farm_report_{datetime.now().strftime('%Y%m%d')}.txt",
        mime="text/plain"
    )
