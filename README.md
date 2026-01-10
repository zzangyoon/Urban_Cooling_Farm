# 🌳 Urban Cooling Farm

> 시민이 가꾸는 텃밭으로 도시 열섬을 식히고, 탄소를 잡는 기후 케어 플랫폼

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red.svg)](https://streamlit.io)
[![Plotly](https://img.shields.io/badge/Plotly-5.18+-purple.svg)](https://plotly.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📖 프로젝트 소개

Urban Cooling Farm은 **AI 기반 도시 열섬 완화 시스템**입니다. 시민들이 직접 도시 곳곳에 쿨링팜(녹지 공간)을 조성하고, 실시간으로 냉각 효과를 측정하며, **게임화된 미션 시스템**으로 참여를 유도합니다.

### ✨ 주요 기능

#### 🗺️ 열섬 현황 시각화
- **인터랙티브 지도**: 경기도 시군구별 열섬 현황을 Folium 기반 지도로 표시
- **실시간 필터링**: 지역별, 열섬 강도별 데이터 필터링
- **상세 정보**: 각 지점의 온도, 녹지율, 인구밀도 표시

#### 🤖 AI 미션 생성 엔진
- **규칙 기반 AI**: 열섬 데이터를 분석하여 최적의 냉각 지점 추천
- **우선순위 점수**: 열섬 강도, 녹지율, 인구밀도 기반 우선순위 계산
- **5가지 미션 타입**: 나무 심기, 옥상 녹화, 쿨페이브먼트, 수경시설, 그늘막

#### 📊 효과 측정 대시보드
- **Plotly 인터랙티브 차트**: 월별 미션 완료, 지역별 열섬 강도, 미션 타입별 현황
- **통계 페어드 t-검정**: 과학적 효과 검증 (설치 전후 온도 차이)
- **CO2 저감량 계산**: 나무 심기 기반 탄소 흡수량 추정
- **시계열 분석**: 온도 변화 추이 차트

#### 🎮 시민 참여 게임화 시스템

**Phase 1 - 기본 참여 시스템**
- 🔥 **실시간 활동 피드**: 최근 시민들의 미션 완료, 레벨업, 배지 획득 내역
- 🏆 **주간 챌린지**: 나무 심기, 옥상 녹화 등 주간 목표 달성 시 보너스 포인트
- 🥇 **TOP 10 리더보드**: 포인트 기반 랭킹 시스템 (금/은/동 메달)

**Phase 2 - 배지 & 시각화**
- 🏅 **배지 시스템**: 10종 업적 배지 (첫 걸음, 초보/베테랑/전설 활동가, 나무 사랑꾼 등)
- 📈 **인터랙티브 차트**: Plotly 기반 호버 효과, 컬러 그라데이션
- 📊 **미션 진행률 바**: 진행 중인 미션의 실시간 진행 상황 (%)

**Phase 3 - UX 강화**
- 👤 **사용자 프로필 페이지**: 활동 통계, 획득 배지, 레벨 진행도, 최근 활동 내역
- 🔔 **알림 센터**: 미션 완료, 배지 획득, 레벨업, 새 챌린지 알림
- ⏳ **로딩 애니메이션**: 스켈레톤 UI, 커스텀 스피너
- 📱 **모바일 반응형**: 태블릿/모바일 최적화 CSS

## 🏗️ 시스템 구조

```
Urban Cooling Farm
├── FastAPI Backend (REST API)
│   ├── 미션 관리 API
│   ├── 쿨링스팟 API
│   ├── 효과 측정 API
│   ├── AI 미션 생성 Agent
│   ├── 시민 참여 API (NEW)
│   │   ├── 활동 피드
│   │   ├── 주간 챌린지
│   │   ├── 리더보드
│   │   └── 배지 시스템
│   └── 사용자 통계 API
│
├── Streamlit Dashboard (시각화)
│   ├── 📍 열섬 현황 지도 (Folium)
│   ├── 📊 냉각 효과 대시보드 (Plotly)
│   ├── 👥 시민 참여 센터
│   ├── 👤 내 프로필 페이지 (NEW)
│   └── ℹ️ 정보 페이지
│
└── Database (SQLite/PostgreSQL)
    ├── Users (사용자 + 레벨/포인트)
    ├── CoolingSpots (쿨링스팟)
    ├── Missions (미션)
    ├── EffectMeasurements (측정 데이터)
    ├── ActivityFeed (활동 피드) (NEW)
    ├── WeeklyChallenge (주간 챌린지) (NEW)
    ├── Badge (배지 마스터) (NEW)
    └── UserBadge (사용자 배지) (NEW)
```

## 🚀 빠른 시작

### 1️⃣ 필수 요구사항

- Python 3.12 이상
- pip 또는 uv 패키지 매니저

### 2️⃣ 설치

```bash
# 저장소 클론
git clone https://github.com/yourusername/urban-cooling-farm.git
cd urban-cooling-farm

# 가상환경 생성 및 활성화
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

# 의존성 설치
pip install -e .

# 개발 의존성 포함 (테스트 도구)
pip install -e ".[dev]"
```

### 3️⃣ 환경 설정

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 편집
# CLIMATE_API_KEY에 경기기후플랫폼 API 키 입력
```

**`.env` 파일 예시:**
```env
# Database
DATABASE_URL=sqlite:///./urban_cooling.db

# Climate Platform API
CLIMATE_API_BASE_URL=https://climate.gg.go.kr/ols/api/geoserver/wfs
CLIMATE_API_KEY=your_api_key_here

# FastAPI Backend URL (Streamlit에서 사용)
FASTAPI_BASE_URL=http://localhost:8020

# App Settings
APP_NAME=Urban Cooling Farm
DEBUG=True

# Mock Mode (API 키 없이 테스트할 때 True)
USE_MOCK_DATA=True
```

### 4️⃣ 데이터베이스 초기화

```bash
# 시민 참여 더미 데이터 생성 (선택사항)
python app/init_citizen_data.py
```

생성되는 데이터:
- 15명의 사용자 (레벨, 포인트, 통계 포함)
- 30개의 활동 피드 (미션 완료, 레벨업, 배지 획득)
- 3개의 주간 챌린지
- 10개의 배지 마스터 데이터
- 랜덤 배지 할당

### 5️⃣ 실행

**FastAPI 서버 실행:**
```bash
python main.py
```
- 🌐 API 서버: http://localhost:8020
- 📖 API 문서: http://localhost:8020/docs
- 📘 ReDoc: http://localhost:8020/redoc

**Streamlit 대시보드 실행:**
```bash
streamlit run streamlit_app/app.py
```
- 🎨 대시보드: http://localhost:8501

> **💡 Tip**: 두 서버를 동시에 실행해야 모든 기능을 사용할 수 있습니다.

## 📚 사용 가이드

### Streamlit 대시보드 탭 구성

#### 1. 🌡️ 열섬 현황 지도
- 경기도 시군구별 열섬 지도 (Folium)
- 지역/강도 필터링
- 핵심 지표: 모니터링 지점, 평균 온도, 평균 열섬 강도, 심각 지역 수

#### 2. 📊 냉각 효과 대시보드
- **월별 미션 완료 현황**: Plotly 막대 차트
- **지역별 열섬 강도 TOP 10**: 컬러 그라데이션 차트
- **미션 타입별 현황**: 누적 막대 차트 (완료/진행중/대기)
- **효과 측정 결과**: 온도 변화, CO2 저감량, 통계 검정

#### 3. 👥 시민 참여 센터
- **주간 챌린지**: 진행률 바, 보상 포인트
- **배지 컬렉션**: 10종 배지 (획득/미획득 구분)
- **실시간 활동 피드**: 최근 10개 활동
- **TOP 10 리더보드**: 금/은/동 메달, 레벨, 포인트, 냉각 기여도
- **추천 미션**: AI 생성 미션 카드, 진행률 바

#### 4. 👤 내 프로필
- **기본 정보**: 프로필 아이콘, 이름, 이메일, 레벨, VIP 뱃지
- **활동 통계**: 완료 미션, 포인트, 심은 나무, 냉각 기여도
- **획득한 배지**: 5열 그리드 레이아웃
- **최근 활동 내역**: 완료한 미션 5개
- **레벨 진행도**: XP 진행률 바
- **내 순위**: 전체 랭킹

#### 5. ℹ️ 정보
- 프로젝트 소개
- 열섬 현상 설명
- 미션 타입별 냉각 효과

### API 사용 예시

#### 1. 미션 목록 조회
```bash
curl http://localhost:8020/missions
```

#### 2. AI 미션 생성
```bash
curl -X POST http://localhost:8020/agent/generate-mission \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 37.2636,
    "longitude": 127.0286,
    "district": "수원시"
  }'
```

#### 3. 활동 피드 조회
```bash
curl http://localhost:8020/api/citizen/activity-feed?limit=10
```

#### 4. 주간 챌린지 조회
```bash
curl http://localhost:8020/api/citizen/challenges
```

#### 5. 리더보드 조회
```bash
curl http://localhost:8020/api/citizen/leaderboard?limit=10
```

#### 6. 배지 조회 (사용자 획득 여부 포함)
```bash
curl http://localhost:8020/api/citizen/badges?user_id=1
```

## 🎯 주요 컴포넌트

### AI 미션 생성 엔진

```python
from app.services.mission_agent import MissionAgent

agent = MissionAgent()

# 지역 분석
analysis = agent.analyze_area(
    latitude=37.2636,
    longitude=127.0286,
    district="수원시"
)

# 미션 생성
mission = agent.generate_mission(analysis)
print(f"생성된 미션: {mission.title}")
print(f"예상 냉각 효과: {mission.estimated_cooling_effect}°C")
print(f"우선순위: {mission.priority_score}/100")
```

### 미션 타입 및 냉각 효과

| 타입 | 설명 | 예상 효과 (보수적 추정) | 난이도 |
|------|------|-----------|--------|
| 🌳 `TREE_PLANTING` | 나무 심기, 가로수 조성 | 0.2~0.5°C (50m 반경) | ⭐⭐ |
| 🏢 `GREEN_ROOF` | 옥상 녹화, 건물 정원 | 0.3~0.8°C (옥상+주변 10m) | ⭐⭐⭐⭐ |
| 🛣️ `COOL_PAVEMENT` | 쿨페이브먼트 설치 | 0.2~0.5°C (시공 면적 내) | ⭐⭐⭐ |
| ⛲ `WATER_FEATURE` | 분수, 수경시설 조성 | 0.4~0.7°C (주변 30m) | ⭐⭐⭐ |
| ☂️ `SHADE_STRUCTURE` | 그늘막 설치 | 0.2~0.4°C (그늘막 아래 체감온도) | ⭐ |

> **참고**: 냉각 효과는 최적 조건 가정 시 예상값이며, 실제 효과는 설치 규모, 유지관리 상태, 주변 환경에 따라 달라질 수 있습니다. (보수적 추정치 30-40% 낮춤)

### 배지 시스템

| 배지 | 아이콘 | 조건 | 보너스 |
|------|--------|------|--------|
| 첫 걸음 | 🌱 | 미션 1개 완료 | +50P |
| 초보 활동가 | 🏃 | 미션 10개 완료 | +100P |
| 베테랑 활동가 | 🦸 | 미션 50개 완료 | +300P |
| 전설의 활동가 | 👑 | 미션 100개 완료 | +500P |
| 나무 사랑꾼 | 🌳 | 나무 50그루 심기 | +200P |
| 열섬 퇴치자 | ❄️ | 총 10°C 냉각 기여 | +400P |
| 신참 챔피언 | ⭐ | 레벨 5 달성 | +150P |
| 마스터 챔피언 | 💎 | 레벨 10 달성 | +500P |
| 주간 챔피언 | 🏆 | 주간 챌린지 1회 완료 | +100P |
| 옥상 녹화 전문가 | 🏢 | 옥상 녹화 10회 완료 | +250P |

## 🔧 개발 가이드

### 테스트 실행

```bash
# 전체 테스트
pytest

# 상세 출력
pytest -v

# 특정 파일 테스트
pytest tests/test_mission_agent.py

# 비동기 테스트
pytest -v tests/test_routers/
```

### 코드 구조

```
Urban_Cooling_Farm/
├── app/                      # FastAPI 백엔드
│   ├── models/              # SQLAlchemy 모델
│   │   ├── database.py     # DB 설정
│   │   └── models.py       # 테이블 정의 (User, Mission, Badge 등)
│   ├── routers/             # API 라우터
│   │   ├── missions.py     # 미션 API
│   │   ├── climate.py      # 기후 데이터 API
│   │   ├── cooling_spots.py # 쿨링스팟 API
│   │   ├── effects.py      # 효과 측정 API
│   │   ├── agent.py        # AI 에이전트 API
│   │   └── citizen.py      # 시민 참여 API (NEW)
│   ├── services/            # 비즈니스 로직
│   │   ├── mission_agent.py # AI 미션 생성 (규칙 기반)
│   │   ├── climate_service.py # 기후 API 연동
│   │   └── effect_service.py # 효과 측정 (보수적 계산)
│   ├── config.py           # 설정 관리 (Pydantic Settings)
│   ├── main.py             # FastAPI 앱
│   └── init_citizen_data.py # 더미 데이터 생성 스크립트
├── streamlit_app/           # Streamlit 대시보드
│   ├── pages/              # 멀티페이지
│   │   └── 1_effect_dashboard.py
│   └── app.py              # 메인 페이지 (5개 탭)
├── api/                     # Vercel Serverless
│   └── index.py            # 엔트리포인트
├── main.py                  # 실행 스크립트
├── pyproject.toml          # 의존성 관리 (uv, pip)
├── .env.example            # 환경변수 템플릿
├── CLAUDE.md               # Claude Code 가이드
├── PROJECT_REPORT.md       # 프로젝트 보고서
└── README.md               # 이 파일
```

### 주요 의존성

```toml
# Web Framework
fastapi>=0.109.0
uvicorn[standard]>=0.27.0

# Database
sqlalchemy>=2.0.25

# Visualization
streamlit>=1.30.0
folium>=0.15.0
streamlit-folium>=0.18.0
plotly>=5.18.0

# Data Processing
pandas>=2.1.0
scipy>=1.11.0

# Authentication
passlib[bcrypt]>=1.7.4  # 배지 시스템용

# HTTP Client
httpx>=0.26.0

# Settings
pydantic>=2.5.0
pydantic-settings>=2.1.0
python-dotenv>=1.0.0
```

## 🌐 배포

### Vercel 배포

```bash
# Vercel CLI 설치
npm i -g vercel

# 프로젝트 연결
vercel link

# 환경변수 설정
vercel env add CLIMATE_API_KEY
vercel env add DATABASE_URL
vercel env add USE_MOCK_DATA

# 배포
vercel --prod
```

**필수 환경변수 (Vercel Dashboard 설정):**
- `CLIMATE_API_KEY`: 경기기후플랫폼 API 키 (필수)
- `DATABASE_URL`: PostgreSQL 연결 문자열 (프로덕션: PostgreSQL 권장)
- `USE_MOCK_DATA`: `False` (프로덕션)
- `DEBUG`: `False` (프로덕션)

자세한 내용은 [VERCEL_SETUP.md](VERCEL_SETUP.md) 참조

### Docker 배포 (향후 지원 예정)

```bash
# 이미지 빌드
docker build -t urban-cooling-farm .

# 컨테이너 실행
docker run -p 8020:8020 -p 8501:8501 urban-cooling-farm
```

## 📊 데이터 소스

### 경기기후플랫폼 API

- **엔드포인트**: https://climate.gg.go.kr/ols/api/geoserver/wfs
- **프로토콜**: WFS (Web Feature Service) 1.1.0
- **데이터**: 공원, 녹지, 비오톱 정보
- **인증**: API Key 필요
- **응답 형식**: GeoJSON

### Mock 데이터 모드

API 키가 없어도 개발 가능:
- `.env`에서 `USE_MOCK_DATA=True` 설정
- 인구밀도 기반 추정 데이터 자동 생성
- 15개 경기도 시군구 데이터 포함 (수원, 성남, 고양, 용인 등)
- 현실적인 열섬 강도 범위 (0.5~3.0°C)

## 🎨 UI/UX 특징

### CSS 커스터마이징
- **히어로 배너**: 그라데이션 배경, 대형 타이틀
- **큰 메트릭 카드**: 아이콘 + 숫자 + 라벨 (색상별 테두리)
- **미션 카드**: 그림자 효과, 호버 애니메이션
- **배지 카드**: 획득/미획득 구분 (그라데이션/그레이스케일)
- **진행률 바**: 애니메이션 효과, 컬러 그라데이션
- **로딩 스켈레톤**: 물결 효과 애니메이션

### 모바일 반응형
- **태블릿** (max-width: 768px): 폰트/패딩 축소
- **모바일** (max-width: 480px): 더 작은 폰트, 배지 높이 축소

### 접근성
- 시맨틱 HTML 사용
- 명확한 레이블링
- 색상 + 아이콘 병행 (색맹 고려)

## 🔒 보안 고려사항

### 현재 구현된 보안
- ✅ 비밀번호 해싱 (bcrypt)
- ✅ 환경변수 기반 설정
- ✅ SQLAlchemy ORM (SQL Injection 방지)
- ✅ Pydantic 입력 검증

### 프로덕션 배포 시 추가 필요
- ⚠️ CORS 설정 강화 (`allow_origins=["*"]` → 특정 도메인)
- ⚠️ 사용자 인증 시스템 (JWT, OAuth2)
- ⚠️ Rate Limiting
- ⚠️ HTTPS 강제
- ⚠️ 로깅 및 모니터링

## 🤝 기여하기

기여를 환영합니다! 다음 단계를 따라주세요:

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### 코딩 컨벤션

- PEP 8 스타일 가이드 준수
- Type hints 사용 권장
- Docstring 작성 (Google 스타일)
- 한국어 주석 허용 (비즈니스 로직 설명 시)

### 개선 아이디어

**높은 우선순위**:
- [ ] 사용자 인증 시스템 (JWT)
- [ ] 단위 테스트 커버리지 (pytest)
- [ ] 로깅 시스템 (logging 모듈)
- [ ] 중복 코드 제거 (열섬 강도 계산 함수)

**중간 우선순위**:
- [ ] N+1 쿼리 최적화 (SQLAlchemy eager loading)
- [ ] API 응답 캐싱 (Redis)
- [ ] Alembic 마이그레이션 도구
- [ ] 에러 처리 강화

**낮은 우선순위**:
- [ ] 실시간 기상 API 통합
- [ ] PWA (Progressive Web App) 변환
- [ ] i18n (다국어 지원)

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 📞 문의 및 지원

- **이슈 트래커**: [GitHub Issues](https://github.com/yourusername/urban-cooling-farm/issues)
- **이메일**: your.email@example.com
- **문서**:
  - [프로젝트 보고서](PROJECT_REPORT.md)
  - [개발 가이드 (Claude Code)](CLAUDE.md)

## 🙏 감사의 말

- [경기기후플랫폼](https://climate.gg.go.kr) - 공공 데이터 제공
- [FastAPI](https://fastapi.tiangolo.com) - 백엔드 프레임워크
- [Streamlit](https://streamlit.io) - 대시보드 프레임워크
- [Folium](https://python-visualization.github.io/folium) - 지도 시각화
- [Plotly](https://plotly.com) - 인터랙티브 차트

## 📈 개발 타임라인

- **Phase 1** (완료): 기본 시민 참여 시스템
  - 실시간 활동 피드
  - 주간 챌린지
  - TOP 10 리더보드

- **Phase 2** (완료): 게임화 강화
  - 배지 시스템 (10종)
  - Plotly 인터랙티브 차트
  - 미션 진행률 바

- **Phase 3** (완료): UX 개선
  - 사용자 프로필 페이지
  - 알림 센터
  - 로딩 애니메이션
  - 모바일 반응형

- **Phase 4** (계획): 프로덕션 준비
  - 사용자 인증 시스템
  - 테스트 커버리지
  - 보안 강화
  - 성능 최적화

## 🌟 Star History

관심 있으시면 ⭐ Star를 눌러주세요!

---

**Made with ❤️ for a cooler planet 🌍**
