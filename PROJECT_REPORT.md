# Urban Cooling Farm 프로젝트 보고서

## 📋 프로젝트 개요

### 프로젝트명
**Urban Cooling Farm (도시 열섬 완화 쿨링팜 관리 시스템)**

### 프로젝트 목적
시민 참여형 도시 텃밭을 통해 도시 열섬 현상을 완화하고, 탄소 저감을 실현하는 AI 기반 기후 케어 플랫폼

### 개발 기간
2024년 ~ 현재 (지속 개발 중)

### 기술 스택
- **Backend**: Python 3.12+, FastAPI, SQLAlchemy
- **Frontend**: Streamlit, Folium, Plotly
- **Database**: SQLite (개발), PostgreSQL (프로덕션 권장)
- **Deployment**: Vercel (FastAPI), Streamlit Cloud (Dashboard)
- **External API**: 경기기후플랫폼 WFS API
- **데이터 처리**: Pandas, NumPy, SciPy
- **인증**: Passlib (bcrypt)
- **시각화**: Plotly (인터랙티브 차트)

---

## 🎯 프로젝트 목표 및 배경

### 1. 도시 열섬 현상 문제
- 도시 지역의 콘크리트, 아스팔트로 인한 복사열 증가
- 녹지 부족으로 인한 기온 상승 (주변 대비 최대 3°C 이상)
- 기후변화로 인한 도심 온도 상승 추세

### 2. 해결 방안
- **시민 참여형 쿨링팜**: 시민들이 직접 도시 곳곳에 녹지 공간 조성
- **AI 기반 미션 생성**: 열섬 데이터를 분석하여 최적의 냉각 지점 추천
- **효과 측정 및 시각화**: 실시간 온도 변화 추적으로 효과 검증
- **게임화(Gamification)**: 포인트 및 미션 시스템으로 참여 동기 부여

### 3. 기대 효과
- 도시 평균 온도 0.5~3°C 감소
- 연간 탄소 저감량 수천 kg 달성
- 시민 환경 의식 향상
- 지역 커뮤니티 활성화

---

## 🏗️ 시스템 아키텍처

### 전체 구조도

```
┌─────────────────────────────────────────────────────────┐
│                    Urban Cooling Farm                    │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌─────────────────┐         ┌─────────────────┐        │
│  │  FastAPI Backend │         │  Streamlit App  │        │
│  │   (REST API)     │         │  (Dashboard)    │        │
│  │                  │         │                 │        │
│  │  - Mission API   │         │  - Heat Map     │        │
│  │  - Climate API   │         │  - Effect Chart │        │
│  │  - Spot API      │         │  - Statistics   │        │
│  │  - Effect API    │         │                 │        │
│  │  - Agent API     │         │                 │        │
│  └────────┬─────────┘         └────────┬────────┘        │
│           │                            │                 │
│           ▼                            ▼                 │
│  ┌─────────────────┐         ┌─────────────────┐        │
│  │  SQLite/PG DB   │         │  Gyeonggi API   │        │
│  │  (ORM: SQLAlch) │         │  (WFS Protocol) │        │
│  └─────────────────┘         └─────────────────┘        │
│                                                           │
│  ┌────────────────────────────────────────────┐          │
│  │        AI Mission Generation Engine        │          │
│  │  (Rule-based + Data Analysis)              │          │
│  └────────────────────────────────────────────┘          │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

### 주요 컴포넌트

#### 1. FastAPI 백엔드 ([app/](app/))
독립적인 RESTful API 서버로 다음 기능 제공:

**API 엔드포인트:**
- `/missions`: 미션 CRUD 및 조회
- `/climate`: 기후/열섬 데이터 조회
- `/cooling-spots`: 쿨링스팟 관리
- `/effects`: 효과 측정 데이터
- `/agent`: AI 미션 생성

**주요 라우터:**
- `missions.py`: 미션 생성, 조회, 상태 업데이트, 삭제
- `climate.py`: 경기기후플랫폼 API 프록시
- `cooling_spots.py`: 쿨링스팟 위치 관리
- `effects.py`: 온도 측정 및 효과 분석
- `agent.py`: AI 미션 자동 생성

#### 2. Streamlit 대시보드 ([streamlit_app/](streamlit_app/))
독립 실행형 시각화 앱 (FastAPI와 별개):

**5개 탭 구조:**
- **🏠 홈**: 메인 대시보드, 열섬 지도, 주요 지표, 추천 미션
- **🎯 미션**: 미션 목록 및 상세 정보
- **📊 효과 측정**: 쿨링 효과 시계열 차트 및 통계
- **👥 시민 참여**: 활동 피드, 주간 챌린지, TOP 10 랭킹, 배지 컬렉션
- **👤 마이 페이지**: 사용자 프로필, 획득 배지, 최근 활동, 알림

**주요 특징:**
- Folium 기반 인터랙티브 지도
- Plotly 인터랙티브 차트 (hover 효과, 색상 그라디언트)
- 실시간 데이터 갱신 (5분 캐시)
- 경기도 15개 시군구 열섬 분석
- 모바일 반응형 디자인 (CSS Media Query)
- 로딩 스켈레톤 애니메이션

#### 3. AI 미션 생성 엔진 ([app/services/mission_agent.py](app/services/mission_agent.py))

**분석 프로세스:**

1. **지역 분석 (Area Analysis)**
   ```
   입력: 위도, 경도, 시군구명
   ↓
   - 열섬 강도 측정 (Heat Island Intensity)
   - 녹지율 계산 (Green Coverage Ratio)
   - 인구밀도 고려
   - 지역 특성 분류 (주거/상업/산업)
   ↓
   출력: AreaAnalysis 객체
   ```

2. **솔루션 매칭 (Solution Matching)**
   ```
   지역 특성별 최적 미션 타입 추천:

   - 주거지역 → 나무 심기, 옥상 녹화
   - 상업지역 → 그늘막, 쿨페이브먼트
   - 공원 인접 → 수경시설, 나무 심기
   - 산업지역 → 옥상 녹화, 나무 심기
   ```

3. **우선순위 산정 (Priority Scoring)**
   ```python
   priority_score = (
       heat_intensity_weight * 0.4 +      # 열섬 강도 40%
       green_deficit_weight * 0.3 +       # 녹지 부족 30%
       population_density_weight * 0.3    # 인구밀도 30%
   )
   ```

4. **미션 생성 (Mission Generation)**
   - 제목/설명 템플릿 기반 자동 생성
   - 난이도 산정 (1~5단계)
   - 예상 냉각 효과 계산 (0.3~3.0°C)
   - 보상 포인트 책정 (10~200점)

**지원 미션 타입:**
- `TREE_PLANTING`: 나무 심기 (가로수, 도시숲)
- `GREEN_ROOF`: 옥상 녹화 (건물 옥상 정원)
- `COOL_PAVEMENT`: 쿨페이브먼트 (복사열 저감 포장)
- `WATER_FEATURE`: 수경시설 (분수, 연못)
- `SHADE_STRUCTURE`: 그늘막 설치

#### 4. 효과 측정 시스템 ([app/services/effect_service.py](app/services/effect_service.py))

**측정 지표:**
- **온도 변화**: 쿨링스팟 설치 전후 비교
- **냉각 효과**: 주변 지역 대비 온도차
- **시계열 추이**: 일일/주간/월간 온도 변화
- **CO2 저감량**: 녹지 면적 기반 탄소 흡수량 계산

**CO2 저감량 계산 공식:**
```python
# 나무 1그루당 연간 CO2 흡수량: 평균 7kg
trees_co2 = total_trees * 7.0

# 녹지 1m²당 연간 CO2 흡수량: 평균 1.2kg
green_area_co2 = total_green_area_m2 * 1.2

# 총 CO2 저감량
total_co2 = trees_co2 + green_area_co2
```

**통계 산출:**
- 전체 쿨링스팟 수
- 완료된 미션 수
- 평균 냉각 효과
- 총 녹지 면적
- 나무 심기 그루 수
- CO2 저감량

---

## 💾 데이터베이스 설계

### ERD (Entity Relationship Diagram)

```
┌─────────────────┐
│     User        │
├─────────────────┤
│ id (PK)         │
│ username        │
│ email           │
│ hashed_password │
│ points          │
│ created_at      │
│ is_active       │
└────────┬────────┘
         │ 1
         │
         │ N
┌────────▼────────────┐
│     Mission         │
├─────────────────────┤
│ id (PK)             │
│ title               │
│ description         │
│ mission_type        │◄─── Enum: TREE_PLANTING, GREEN_ROOF, etc.
│ status              │◄─── Enum: PENDING, IN_PROGRESS, COMPLETED
│ points_reward       │
│ difficulty          │
│ cooling_effect      │
│ ai_reasoning        │
│ priority_score      │
│ user_id (FK)        │
│ cooling_spot_id(FK) │
│ created_at          │
│ completed_at        │
└────────┬────────────┘
         │ N
         │
         │ 1
┌────────▼────────────┐         ┌───────────────────────┐
│  CoolingSpot        │ 1     N │  EffectMeasurement    │
├─────────────────────┤◄────────┤───────────────────────┤
│ id (PK)             │         │ id (PK)               │
│ name                │         │ cooling_spot_id (FK)  │
│ description         │         │ temperature           │
│ latitude            │         │ humidity              │
│ longitude           │         │ heat_index            │
│ address             │         │ nearby_avg_temp       │
│ heat_intensity      │         │ cooling_effect        │
│ current_temp        │         │ wind_speed            │
│ target_temp         │         │ solar_radiation       │
│ green_coverage      │         │ measured_at           │
│ tree_count          │         └───────────────────────┘
│ created_at          │
│ updated_at          │
└─────────────────────┘
```

### 주요 테이블 설명

#### 1. users (사용자)
- 회원 정보 및 포인트 관리
- **레벨 시스템**: 포인트 기반 자동 레벨업
- **미션 완료 추적**: 총 완료 미션 수 기록
- 배지 획득 기록 연결

#### 2. cooling_spots (쿨링스팟)
- 열섬 완화 지점 위치 정보
- 현재 온도, 목표 온도, 열섬 강도 저장
- 녹지율, 나무 수 추적

#### 3. missions (미션)
- AI가 생성한 냉각 미션
- 사용자 배정 및 상태 추적
- 완료 시간 기록으로 성과 측정

#### 4. effect_measurements (효과 측정)
- 쿨링스팟별 온도/습도 측정 데이터
- 주변 지역과 비교하여 냉각 효과 산출
- 시계열 데이터 축적으로 트렌드 분석

#### 5. badges (배지 마스터 데이터) - **Phase 2 추가**
- 10종 배지 정의 (첫 걸음, 미션 달성, 레벨 업 등)
- 배지별 획득 조건 및 보상 포인트
- 아이콘, 설명 저장

#### 6. user_badges (사용자 배지 획득 기록) - **Phase 2 추가**
- 사용자별 배지 획득 이력
- 획득 시간 기록

#### 7. activity_feeds (활동 피드) - **Phase 1 추가**
- 실시간 사용자 활동 스트림
- 활동 타입: 미션 완료, 레벨업, 배지 획득, 챌린지 달성
- 공개/비공개 설정

#### 8. weekly_challenges (주간 챌린지) - **Phase 1 추가**
- 주간 단위 커뮤니티 챌린지
- 목표 설정 및 진행률 추적
- 완료 시 보상 포인트 지급

---

## 🔌 외부 API 연동

### 경기기후플랫폼 API

**API 정보:**
- **엔드포인트**: `https://climate.gg.go.kr/ols/api/geoserver/wfs`
- **프로토콜**: WFS (Web Feature Service) 1.1.0
- **인증**: API Key (Header)
- **응답 형식**: GeoJSON

**활용 데이터:**
- **공원 데이터**: 경기도 내 공원 위치, 면적
- **녹지 데이터**: 비오톱, 녹지 지역 정보
- **용도**: 시군구별 녹지율 계산, 열섬 취약 지역 식별

**요청 예시:**
```python
params = {
    "apiKey": "YOUR_API_KEY",
    "service": "WFS",
    "version": "1.1.0",
    "request": "GetFeature",
    "typeName": "park",
    "outputFormat": "application/json",
    "maxFeatures": 500
}
response = httpx.get(API_BASE_URL, params=params)
data = response.json()
```

**응답 처리:**
```python
for feature in data.get("features", []):
    properties = feature.get("properties", {})
    district = properties.get("sgg_nm")  # 시군구명
    area = properties.get("biotop_area")  # 면적
    geometry = feature.get("geometry")   # 좌표
```

---

## 🎮 주요 기능 상세

### Phase 1: 시민 참여 시스템 (완료)

#### 1.1 실시간 활동 피드
**위치**: [app/routers/citizen.py](app/routers/citizen.py), 시민 참여 탭

**기능:**
- 사용자들의 최근 활동 실시간 표시
- 활동 타입: 미션 완료, 레벨업, 배지 획득, 챌린지 달성
- 사용자 아바타 및 시간 표시
- 공개/비공개 설정 지원

**API 엔드포인트:**
```
GET /api/citizen/activities?limit=20
```

#### 1.2 주간 챌린지
**위치**: [app/routers/citizen.py](app/routers/citizen.py), 시민 참여 탭

**기능:**
- 주간 단위 커뮤니티 목표 설정
- 실시간 진행률 표시 (예: 85/100 완료)
- 챌린지 타입: 나무 심기, 미션 완료, CO2 저감
- 완료 시 보너스 포인트 지급

**API 엔드포인트:**
```
GET /api/citizen/challenges/weekly
```

#### 1.3 TOP 10 리더보드
**위치**: 시민 참여 탭

**기능:**
- 포인트 기준 상위 10명 랭킹
- 실시간 순위 업데이트
- 사용자 레벨, 완료 미션 수 표시
- 메달 아이콘 (1위 🥇, 2위 🥈, 3위 🥉)

**API 엔드포인트:**
```
GET /api/citizen/leaderboard?limit=10
```

### Phase 2: 게임화 강화 (완료)

#### 2.1 배지 시스템
**위치**: [app/models/models.py](app/models/models.py:170-212), 시민 참여 탭

**10종 배지:**
| 배지 | 조건 | 포인트 |
|------|------|--------|
| 🌱 첫 걸음 | 미션 1개 완료 | 50 |
| 🎯 미션 마스터 10 | 미션 10개 완료 | 100 |
| 🏆 미션 챔피언 50 | 미션 50개 완료 | 300 |
| 🌟 미션 레전드 100 | 미션 100개 완료 | 500 |
| 🌳 나무 사랑꾼 | 나무 심기 10회 | 100 |
| ❄️ 쿨링 히어로 | 3°C 이상 냉각 달성 | 200 |
| 🥉 레벨 5 달성 | 레벨 5 도달 | 80 |
| 🥇 레벨 10 달성 | 레벨 10 도달 | 150 |
| 👑 주간 챔피언 | 주간 챌린지 1위 | 200 |
| 🏠 옥상정원 마스터 | 옥상 녹화 5회 | 150 |

**기능:**
- 자동 배지 획득 체크
- 획득/미획득 상태 표시
- 획득 날짜 기록
- 배지 컬렉션 UI (카드 그리드)

**API 엔드포인트:**
```
GET /api/citizen/badges
GET /api/citizen/badges/user/{user_id}
```

#### 2.2 Plotly 인터랙티브 차트
**위치**: [streamlit_app/app.py](streamlit_app/app.py), 홈 탭

**차트 종류:**
1. **월별 미션 완료 추이** (Bar Chart)
   - 색상 그라디언트 (Blues)
   - Hover 효과로 정확한 수치 표시
   - 텍스트 레이블 외부 배치

2. **지역별 열섬 강도 TOP 10** (Bar Chart)
   - 색상 그라디언트 (Reds)
   - 내림차순 정렬
   - 단위: °C

3. **미션 타입별 현황** (Stacked Bar Chart)
   - 3개 상태: 완료(녹색), 진행중(주황), 대기(회색)
   - 적층 막대로 전체 현황 한눈에 파악

**기술 스택:**
- Plotly Express (간단한 차트)
- Plotly Graph Objects (복잡한 적층 차트)

#### 2.3 미션 진행률 바
**위치**: [streamlit_app/app.py](streamlit_app/app.py), 추천 미션 섹션

**기능:**
- 진행중 미션에만 표시
- 퍼센트 및 비주얼 바 (그라디언트)
- CSS 애니메이션 효과

**구현:**
```html
<div class='progress-bar'>
    <div class='progress-fill' style='width: 65%;'></div>
</div>
```

### Phase 3: UX 개선 (완료)

#### 3.1 사용자 프로필 페이지
**위치**: 마이 페이지 탭

**섹션:**
- **프로필 헤더**: 레벨, 포인트, 경험치 바
- **통계**: 완료 미션, 획득 배지, 총 활동일
- **획득 배지 컬렉션**: 카드 그리드 (3열)
- **최근 활동**: 최근 10개 활동 타임라인
- **알림 센터**: 7개 더미 알림 (배지, 레벨업, 챌린지)

**UI 특징:**
- 그라디언트 배경
- 애니메이션 효과
- 반응형 그리드

#### 3.2 로딩 애니메이션
**위치**: 전역 CSS

**스켈레톤 로딩:**
```css
.skeleton {
    background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
    background-size: 200% 100%;
    animation: loading 1.5s ease-in-out infinite;
}
```

**적용 위치:**
- 데이터 로딩 중 카드 컴포넌트
- 차트 렌더링 전

#### 3.3 모바일 반응형 디자인
**위치**: 전역 CSS

**Breakpoints:**
```css
/* 태블릿 (max-width: 768px) */
- 폰트 크기 축소
- 패딩 조정
- 메트릭 카드 1열 배치

/* 모바일 (max-width: 480px) */
- 더 작은 폰트
- 배지 카드 높이 축소
- 터치 친화적 버튼 크기
```

**반응형 요소:**
- 메트릭 카드 그리드 (4열 → 2열 → 1열)
- 배지 컬렉션 (3열 → 2열 → 1열)
- 차트 너비 자동 조정

### 기존 핵심 기능

#### 1. 열섬 지도 시각화
**위치**: [streamlit_app/app.py](streamlit_app/app.py)

**기능:**
- Folium 기반 인터랙티브 지도
- 경기도 15개 시군구 열섬 강도 표시
- 색상 코드로 위험도 시각화:
  - 빨강 (3°C 이상): 심각
  - 주황 (2~3°C): 높음
  - 노랑 (1~2°C): 중간
  - 녹색 (1°C 미만): 낮음
- 마커 클릭 시 상세 정보 팝업
- 시군구 필터링 기능

**데이터 소스:**
- 실제 API 연동 시: 경기기후플랫폼 공원 데이터
- Mock 모드: 인구밀도 기반 추정 데이터

### 2. AI 미션 자동 생성
**위치**: [app/routers/agent.py](app/routers/agent.py), [app/services/mission_agent.py](app/services/mission_agent.py)

**엔드포인트:**
```
POST /agent/generate-mission
Body: {
  "latitude": 37.2636,
  "longitude": 127.0286,
  "district": "수원시"
}
```

**응답 예시:**
```json
{
  "title": "수원시 가로수 심기 캠페인",
  "description": "열섬 강도가 높은 수원시 지역에 그늘을 제공할 가로수를 심습니다.",
  "mission_type": "tree_planting",
  "points_reward": 50,
  "difficulty": 2,
  "estimated_cooling_effect": 0.5,
  "priority_score": 8.5,
  "ai_reasoning": "높은 인구밀도(9800명/km²)와 낮은 녹지율(15%)로 인해...",
  "latitude": 37.2636,
  "longitude": 127.0286,
  "district": "수원시"
}
```

### 3. 효과 측정 대시보드
**위치**: [streamlit_app/pages/1_effect_dashboard.py](streamlit_app/pages/1_effect_dashboard.py)

**주요 차트:**
- **전체 성과 지표**: 쿨링스팟 수, 완료 미션, 평균 냉각 효과, CO2 저감량
- **시계열 온도 변화**: 일별/주별 온도 및 냉각 효과 추이
- **냉각 효과 비교**: 설치 전후 온도 비교
- **지역별 통계**: 시군구별 쿨링스팟 분포 및 효과

**인터랙티브 기능:**
- 조회 기간 조절 (7~90일)
- 습도 표시 on/off
- 지역별 필터링

### 4. 미션 관리 시스템
**위치**: [app/routers/missions.py](app/routers/missions.py)

**미션 상태 흐름:**
```
PENDING (대기)
    ↓ 사용자 수락
IN_PROGRESS (진행중)
    ↓ 완료 보고
COMPLETED (완료) → 포인트 지급
    또는
FAILED (실패)
```

**주요 API:**
- `GET /missions`: 미션 목록 조회 (필터링, 페이지네이션)
- `POST /missions`: 새 미션 생성
- `GET /missions/{id}`: 미션 상세 조회
- `PATCH /missions/{id}`: 상태 업데이트
- `DELETE /missions/{id}`: 미션 삭제

---

## 🔧 개발 환경 설정

### 1. 필수 요구사항
- Python 3.12 이상
- pip 또는 uv 패키지 매니저

### 2. 설치 및 실행
```bash
# 1. 가상환경 생성
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# 2. 의존성 설치
pip install -e .
# 또는 개발 의존성 포함
pip install -e ".[dev]"

# 3. 환경변수 설정
cp .env.example .env
# .env 파일 편집하여 CLIMATE_API_KEY 입력

# 4. FastAPI 서버 실행 (http://localhost:8020)
python main.py

# 5. Streamlit 대시보드 실행 (http://localhost:8501)
streamlit run streamlit_app/app.py
```

### 3. Mock 데이터 모드
API 키 없이 개발하려면 `.env` 파일에서:
```bash
USE_MOCK_DATA=True
```

Mock 모드에서는 인구밀도 기반 추정 데이터 사용

---

## 🚀 배포 전략

### Vercel Serverless 배포

**설정 파일**: [vercel.json](vercel.json)

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ]
}
```

**배포 단계:**
1. Vercel CLI 설치: `npm i -g vercel`
2. 프로젝트 연결: `vercel link`
3. 환경변수 설정: `vercel env add CLIMATE_API_KEY`
4. 배포: `vercel --prod`

**필수 환경변수 (Vercel Dashboard):**
- `CLIMATE_API_KEY`: 경기기후플랫폼 API 키
- `DATABASE_URL`: PostgreSQL 연결 문자열 (권장)
- `USE_MOCK_DATA`: False (프로덕션)

---

## 📊 성과 및 기대 효과

### 정량적 성과 (예상)
- **온도 저감**: 쿨링스팟당 평균 1~3°C 감소
- **CO2 흡수**: 나무 1그루당 연간 7kg, 녹지 1m²당 1.2kg
- **참여자 수**: 월 100명 이상 (목표)
- **쿨링스팟**: 연간 20개 이상 조성 (목표)

### 정성적 효과
- **환경 인식 개선**: 시민들의 기후변화 대응 의식 향상
- **커뮤니티 활성화**: 지역 주민 간 협력 및 소통 증진
- **도시 미관 개선**: 녹지 공간 확대로 도시 경관 향상
- **생물 다양성**: 도시 내 생태계 복원 기여

### 사회적 가치
- **기후정의**: 취약 지역 우선 지원으로 환경 불평등 해소
- **시민과학**: 주민이 직접 데이터 수집하고 효과 검증
- **교육적 가치**: 기후변화 교육의 살아있는 교재

---

## 🔮 향후 발전 방향

### 개발 완료 (Phase 1-3)
- ✅ **시민 참여 시스템**: 활동 피드, 주간 챌린지, 리더보드
- ✅ **배지 시스템**: 10종 배지 및 획득 기록
- ✅ **Plotly 인터랙티브 차트**: 월별/지역별/타입별 차트
- ✅ **사용자 프로필 페이지**: 마이 페이지, 알림 센터
- ✅ **모바일 반응형 디자인**: CSS Media Query
- ✅ **배포 환경 구성**: Vercel/Streamlit Cloud 설정 완료

### 단기 계획 (3개월)
1. **사용자 인증 시스템 구축**
   - JWT 기반 로그인/회원가입
   - 소셜 로그인 연동 (카카오, 네이버)
   - 하드코딩된 user_id 제거

2. **실시간 센서 연동**
   - IoT 온습도 센서 데이터 수집
   - 자동화된 효과 측정

3. **코드 품질 개선**
   - 단위 테스트 추가 (pytest)
   - 중복 코드 제거 (열섬 강도 계산 함수 통합)
   - N+1 쿼리 최적화 (SQLAlchemy eager loading)
   - 에러 처리 강화

### 중기 계획 (6개월)
1. **머신러닝 모델 도입**
   - 열섬 예측 모델 (XGBoost, LSTM)
   - 최적 위치 추천 알고리즘

2. **커뮤니티 기능 강화**
   - 미션 후기, 사진 공유
   - 댓글, 좋아요 기능
   - 그룹/팀 미션

3. **데이터베이스 마이그레이션**
   - SQLite → PostgreSQL
   - Alembic 마이그레이션 도구 도입

### 장기 계획 (1년)
1. **전국 확대**
   - 서울, 부산 등 타 지역 데이터 통합
   - 지자체별 맞춤 대시보드

2. **기업 ESG 연계**
   - 기업 스폰서십 프로그램
   - ESG 리포트 자동 생성

3. **탄소배출권 거래**
   - CO2 저감량 크레딧화
   - 블록체인 기반 인증 시스템

---

## 🐛 알려진 이슈 및 제한사항

### 현재 제한사항
1. **데이터 정확도**
   - Mock 모드에서는 추정 데이터 사용
   - 실제 센서 데이터 필요

2. **확장성**
   - SQLite는 개발용, 프로덕션에서는 PostgreSQL 권장
   - 동시 접속자 증가 시 성능 최적화 필요

3. **API 의존성**
   - 경기기후플랫폼 API 가용성에 의존
   - API 요청 제한(Rate Limit) 고려 필요

### 해결 예정
- [ ] 사용자 인증 시스템 미구현
- [ ] 이미지 업로드 기능 없음 (미션 완료 인증)
- [ ] 푸시 알림 미지원
- [ ] 다국어 지원 없음 (현재 한국어만)

---

## 📚 참고 자료

### 관련 연구
- 환경부, "도시 열섬 완화를 위한 정책 방안"
- 서울시, "기후변화 적응대책 세부시행계획"
- IPCC, "기후변화 완화 보고서"

### 기술 문서
- FastAPI 공식 문서: https://fastapi.tiangolo.com
- Streamlit 공식 문서: https://docs.streamlit.io
- Folium 공식 문서: https://python-visualization.github.io/folium
- 경기기후플랫폼: https://climate.gg.go.kr

### 오픈소스 라이선스
- 본 프로젝트는 MIT License 하에 배포 (예정)

---

## 👥 팀 및 기여

### 프로젝트 팀
- **개발자**: [팀원 이름]
- **데이터 분석**: [팀원 이름]
- **UI/UX 디자인**: [팀원 이름]

### 기여 방법
1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📞 문의

프로젝트 관련 문의사항은 다음으로 연락 주세요:
- **Email**: [이메일 주소]
- **GitHub Issues**: [GitHub 저장소 URL]

---

**작성일**: 2026년 1월 11일
**버전**: 0.3.0 (Phase 1-3 완료)
**상태**: 배포 준비 완료
