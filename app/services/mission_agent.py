"""
AI Agent 미션 생성 서비스

열섬 데이터를 분석하여 최적의 냉각 미션을 자동 생성합니다.
규칙 기반 엔진 + LLM 연동 인터페이스 제공
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from enum import Enum
import random

from pydantic import BaseModel

from app.models.models import MissionType, MissionStatus
from app.services.climate_service import (
    ClimateService,
    HeatIslandData,
    GreenSpaceData,
    WeatherData
)


# ============== Schemas ==============

class AreaCharacteristics(str, Enum):
    """지역 특성"""
    RESIDENTIAL = "residential"          # 주거지역
    COMMERCIAL = "commercial"            # 상업지역
    INDUSTRIAL = "industrial"            # 산업지역
    MIXED = "mixed"                      # 복합지역
    PARK_ADJACENT = "park_adjacent"      # 공원 인접


class MissionDifficulty(int, Enum):
    """미션 난이도"""
    VERY_EASY = 1
    EASY = 2
    MEDIUM = 3
    HARD = 4
    VERY_HARD = 5


@dataclass
class AreaAnalysis:
    """지역 분석 결과"""
    heat_island_data: HeatIslandData
    green_space_data: Optional[list[GreenSpaceData]]
    weather_data: Optional[WeatherData]
    priority_score: float
    characteristics: AreaCharacteristics
    recommended_solutions: list[MissionType]
    analysis_reasoning: str


class GeneratedMission(BaseModel):
    """생성된 미션"""
    title: str
    description: str
    mission_type: MissionType
    points_reward: int
    difficulty: int
    estimated_cooling_effect: float
    priority_score: float
    ai_reasoning: str
    latitude: float
    longitude: float
    district: str


# ============== Mission Templates ==============

MISSION_TEMPLATES = {
    MissionType.TREE_PLANTING: {
        "titles": [
            "{district} 가로수 심기 캠페인",
            "{district} 녹음수 식재 프로젝트",
            "{district} 도시숲 조성 참여",
            "{district} 그늘나무 심기 봉사"
        ],
        "descriptions": [
            "열섬 강도가 높은 {district} 지역에 그늘을 제공할 가로수를 심습니다.",
            "{district}의 도로변에 녹음수를 식재하여 보행자에게 시원한 그늘을 제공합니다.",
            "도시 열섬 완화를 위해 {district}에 소규모 도시숲을 조성합니다."
        ],
        "base_points": 50,
        "base_difficulty": 2,
        "cooling_effect_range": (0.3, 0.8),
        "suitable_for": [AreaCharacteristics.RESIDENTIAL, AreaCharacteristics.COMMERCIAL, AreaCharacteristics.MIXED]
    },
    MissionType.GREEN_ROOF: {
        "titles": [
            "{district} 옥상 녹화 프로젝트",
            "{district} 건물 옥상정원 조성",
            "{district} 그린루프 설치 지원"
        ],
        "descriptions": [
            "건물 밀집 지역인 {district}의 옥상을 녹화하여 건물 온도를 낮춥니다.",
            "{district} 상업시설 옥상에 정원을 조성하여 복사열을 줄입니다.",
            "콘크리트 열섬을 완화하기 위해 {district} 건물에 그린루프를 설치합니다."
        ],
        "base_points": 100,
        "base_difficulty": 4,
        "cooling_effect_range": (0.5, 1.5),
        "suitable_for": [AreaCharacteristics.COMMERCIAL, AreaCharacteristics.INDUSTRIAL, AreaCharacteristics.MIXED]
    },
    MissionType.COOL_PAVEMENT: {
        "titles": [
            "{district} 쿨페이브먼트 시공",
            "{district} 차열 포장재 적용",
            "{district} 도로 온도 저감 프로젝트"
        ],
        "descriptions": [
            "아스팔트 도로의 표면 온도가 높은 {district}에 차열성 포장재를 적용합니다.",
            "{district}의 보행로에 쿨페이브먼트를 시공하여 복사열을 줄입니다.",
            "산업단지 인근 {district} 도로에 열반사 포장재를 적용합니다."
        ],
        "base_points": 80,
        "base_difficulty": 3,
        "cooling_effect_range": (0.2, 0.5),
        "suitable_for": [AreaCharacteristics.INDUSTRIAL, AreaCharacteristics.COMMERCIAL]
    },
    MissionType.WATER_FEATURE: {
        "titles": [
            "{district} 분수대 설치",
            "{district} 수경시설 조성",
            "{district} 미스트 쿨링존 설치"
        ],
        "descriptions": [
            "시민 이용이 많은 {district}에 분수대를 설치하여 증발 냉각 효과를 제공합니다.",
            "{district} 광장에 수경시설을 조성하여 쾌적한 환경을 만듭니다.",
            "무더위 쉼터로 {district}에 미스트 분사 시설을 설치합니다."
        ],
        "base_points": 70,
        "base_difficulty": 3,
        "cooling_effect_range": (0.2, 0.4),
        "suitable_for": [AreaCharacteristics.COMMERCIAL, AreaCharacteristics.PARK_ADJACENT, AreaCharacteristics.RESIDENTIAL]
    },
    MissionType.SHADE_STRUCTURE: {
        "titles": [
            "{district} 그늘막 설치",
            "{district} 쉘터 구조물 설치",
            "{district} 버스정류장 차양 개선"
        ],
        "descriptions": [
            "대중교통 이용객을 위해 {district} 버스정류장에 그늘막을 설치합니다.",
            "{district} 보행로에 쉘터 구조물을 설치하여 직사광선을 차단합니다.",
            "어린이 통학로인 {district}에 차양 시설을 설치합니다."
        ],
        "base_points": 30,
        "base_difficulty": 1,
        "cooling_effect_range": (0.1, 0.3),
        "suitable_for": [AreaCharacteristics.RESIDENTIAL, AreaCharacteristics.COMMERCIAL, AreaCharacteristics.MIXED]
    }
}


# ============== AI Reasoning Templates ==============

REASONING_TEMPLATES = {
    "high_intensity": """
## 분석 결과

**지역**: {district}
**열섬 강도**: +{intensity}°C (심각 수준)
**현재 온도**: {temperature}°C

### 문제점
{district} 지역은 주변 대비 {intensity}°C 높은 열섬 현상이 관측되고 있습니다.
이는 경기도 평균 열섬 강도({avg_intensity}°C)보다 {diff}°C 높은 수치입니다.

### 권장 솔루션: {solution_name}
{solution_reason}

### 예상 효과
- 냉각 효과: -{cooling_effect}°C
- 체감온도 개선: 약 {feel_temp_improvement}°C 감소
- 주변 지역 파급 효과 기대
""",
    "medium_intensity": """
## 분석 결과

**지역**: {district}
**열섬 강도**: +{intensity}°C (주의 수준)
**현재 온도**: {temperature}°C

### 현황
{district} 지역은 중간 수준의 열섬 현상이 나타나고 있습니다.
녹지율이 {green_ratio}%로 추가적인 녹화 사업이 효과적입니다.

### 권장 솔루션: {solution_name}
{solution_reason}

### 예상 효과
- 냉각 효과: -{cooling_effect}°C
- 예방적 조치로 열섬 악화 방지
""",
    "low_intensity": """
## 분석 결과

**지역**: {district}
**열섬 강도**: +{intensity}°C (양호)
**현재 온도**: {temperature}°C

### 현황
{district} 지역은 상대적으로 양호한 열환경을 보이고 있습니다.
현재 상태를 유지하고 개선하기 위한 예방적 조치를 권장합니다.

### 권장 솔루션: {solution_name}
{solution_reason}

### 예상 효과
- 현재의 양호한 열환경 유지
- 추가 냉각 효과: -{cooling_effect}°C
"""
}

SOLUTION_REASONS = {
    MissionType.TREE_PLANTING: "가로수는 그늘 제공과 증발산 작용을 통해 주변 온도를 효과적으로 낮춥니다. 장기적으로 가장 지속 가능한 솔루션입니다.",
    MissionType.GREEN_ROOF: "건물 옥상 녹화는 건물의 열 흡수를 줄이고, 증발산을 통해 주변 공기를 냉각합니다. 건물 에너지 비용 절감 효과도 있습니다.",
    MissionType.COOL_PAVEMENT: "차열성 포장재는 태양열 반사율을 높여 도로 표면 온도를 낮춥니다. 특히 아스팔트 도로가 많은 지역에 효과적입니다.",
    MissionType.WATER_FEATURE: "수경시설은 물의 증발 과정에서 주변 열을 흡수하여 국지적 냉각 효과를 제공합니다. 시민들에게 심리적 쾌적감도 제공합니다.",
    MissionType.SHADE_STRUCTURE: "그늘막은 직사광선을 차단하여 즉각적인 체감온도 저감 효과를 제공합니다. 설치가 간편하고 비용 효율적입니다."
}


class MissionAgent:
    """AI 기반 미션 생성 에이전트"""

    def __init__(self, use_llm: bool = False, llm_api_key: Optional[str] = None):
        """
        Args:
            use_llm: LLM API 사용 여부 (False면 규칙 기반)
            llm_api_key: LLM API 키 (OpenAI, Claude 등)
        """
        self.climate_service = ClimateService()
        self.use_llm = use_llm
        self.llm_api_key = llm_api_key

    async def analyze_area(self, heat_data: HeatIslandData) -> AreaAnalysis:
        """
        특정 지역의 열섬 상황을 분석

        Args:
            heat_data: 열섬 데이터

        Returns:
            지역 분석 결과
        """
        # 녹지 데이터 조회
        green_data = await self.climate_service.get_green_space_data(
            heat_data.latitude,
            heat_data.longitude
        )

        # 기상 데이터 조회
        weather_data = await self.climate_service.get_weather_data(
            heat_data.latitude,
            heat_data.longitude
        )

        # 우선순위 점수 계산
        priority_score = self._calculate_priority_score(
            heat_data, green_data, weather_data
        )

        # 지역 특성 추정
        characteristics = self._estimate_area_characteristics(
            heat_data, green_data
        )

        # 추천 솔루션 결정
        recommended_solutions = self._recommend_solutions(
            heat_data, characteristics, green_data
        )

        # 분석 근거 생성
        reasoning = self._generate_analysis_reasoning(
            heat_data, green_data, weather_data, priority_score
        )

        return AreaAnalysis(
            heat_island_data=heat_data,
            green_space_data=green_data,
            weather_data=weather_data,
            priority_score=priority_score,
            characteristics=characteristics,
            recommended_solutions=recommended_solutions,
            analysis_reasoning=reasoning
        )

    def _calculate_priority_score(
        self,
        heat_data: HeatIslandData,
        green_data: Optional[list[GreenSpaceData]],
        weather_data: Optional[WeatherData]
    ) -> float:
        """
        우선순위 점수 계산 (0-100)

        높을수록 미션 생성 우선순위가 높음
        """
        score = 0.0

        # 1. 열섬 강도 (최대 40점)
        intensity_score = min(heat_data.heat_island_intensity * 16, 40)
        score += intensity_score

        # 2. 현재 온도 (최대 20점)
        if heat_data.temperature >= 35:
            score += 20
        elif heat_data.temperature >= 32:
            score += 15
        elif heat_data.temperature >= 30:
            score += 10
        elif heat_data.temperature >= 28:
            score += 5

        # 3. 녹지율 역점수 (낮을수록 높은 점수, 최대 20점)
        if green_data:
            avg_green_ratio = sum(g.green_coverage_ratio for g in green_data) / len(green_data)
            green_score = max(0, 20 - (avg_green_ratio * 0.5))
            score += green_score
        else:
            score += 15  # 데이터 없으면 중간 점수

        # 4. 기상 조건 (최대 20점)
        if weather_data:
            # 습도 높으면 체감온도 상승
            if weather_data.humidity >= 70:
                score += 10
            elif weather_data.humidity >= 60:
                score += 5

            # 바람 약하면 열 분산 어려움
            if weather_data.wind_speed < 1.0:
                score += 10
            elif weather_data.wind_speed < 2.0:
                score += 5

        return min(score, 100)

    def _estimate_area_characteristics(
        self,
        heat_data: HeatIslandData,
        green_data: Optional[list[GreenSpaceData]]
    ) -> AreaCharacteristics:
        """지역 특성 추정"""
        district = heat_data.district

        # 키워드 기반 추정 (실제로는 API 또는 DB에서 조회)
        if any(kw in district for kw in ["산업", "공단", "단지"]):
            return AreaCharacteristics.INDUSTRIAL
        elif any(kw in district for kw in ["상업", "역", "시장", "백화점"]):
            return AreaCharacteristics.COMMERCIAL
        elif green_data and any(g.park_area > 5000 for g in green_data):
            return AreaCharacteristics.PARK_ADJACENT

        # 녹지율 기반 추정
        if green_data:
            avg_green = sum(g.green_coverage_ratio for g in green_data) / len(green_data)
            if avg_green > 30:
                return AreaCharacteristics.RESIDENTIAL

        return AreaCharacteristics.MIXED

    def _recommend_solutions(
        self,
        heat_data: HeatIslandData,
        characteristics: AreaCharacteristics,
        green_data: Optional[list[GreenSpaceData]]
    ) -> list[MissionType]:
        """
        지역 특성에 맞는 솔루션 추천

        Returns:
            추천 솔루션 리스트 (우선순위 순)
        """
        recommendations = []

        # 각 솔루션의 적합도 점수 계산
        solution_scores: dict[MissionType, float] = {}

        for mission_type, template in MISSION_TEMPLATES.items():
            score = 0.0

            # 지역 특성 적합도
            if characteristics in template["suitable_for"]:
                score += 30

            # 열섬 강도에 따른 가중치
            if heat_data.heat_island_intensity >= 2.0:
                # 심각: 효과 큰 솔루션 선호
                if mission_type in [MissionType.GREEN_ROOF, MissionType.TREE_PLANTING]:
                    score += 25
            elif heat_data.heat_island_intensity >= 1.5:
                # 높음: 중간 효과 솔루션
                if mission_type in [MissionType.COOL_PAVEMENT, MissionType.TREE_PLANTING]:
                    score += 20
            else:
                # 낮음: 간단한 솔루션
                if mission_type in [MissionType.SHADE_STRUCTURE, MissionType.WATER_FEATURE]:
                    score += 15

            # 녹지율에 따른 가중치
            if green_data:
                avg_green = sum(g.green_coverage_ratio for g in green_data) / len(green_data)
                if avg_green < 15 and mission_type == MissionType.TREE_PLANTING:
                    score += 20  # 녹지율 낮으면 나무 심기 우선
                elif avg_green < 10 and mission_type == MissionType.GREEN_ROOF:
                    score += 15

            solution_scores[mission_type] = score

        # 점수 순으로 정렬
        sorted_solutions = sorted(
            solution_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return [sol[0] for sol in sorted_solutions[:3]]

    def _generate_analysis_reasoning(
        self,
        heat_data: HeatIslandData,
        green_data: Optional[list[GreenSpaceData]],
        weather_data: Optional[WeatherData],
        priority_score: float
    ) -> str:
        """분석 근거 텍스트 생성"""
        intensity = heat_data.heat_island_intensity

        if intensity >= 2.0:
            template_key = "high_intensity"
        elif intensity >= 1.5:
            template_key = "medium_intensity"
        else:
            template_key = "low_intensity"

        avg_green = 15.0
        if green_data:
            avg_green = sum(g.green_coverage_ratio for g in green_data) / len(green_data)

        return f"""
### 지역 분석: {heat_data.district}

**열섬 강도**: +{intensity}°C
**우선순위 점수**: {priority_score:.1f}/100
**녹지율**: {avg_green:.1f}%

열섬 강도가 {'심각' if intensity >= 2.0 else '주의' if intensity >= 1.5 else '양호'} 수준입니다.
{'즉각적인 조치가 필요합니다.' if intensity >= 2.0 else '예방적 조치를 권장합니다.' if intensity >= 1.5 else '현재 상태 유지를 위한 관리가 필요합니다.'}
"""

    async def generate_mission(
        self,
        heat_data: HeatIslandData,
        mission_type: Optional[MissionType] = None
    ) -> GeneratedMission:
        """
        특정 지역에 대한 미션 생성

        Args:
            heat_data: 열섬 데이터
            mission_type: 미션 타입 (없으면 자동 추천)

        Returns:
            생성된 미션
        """
        # 지역 분석
        analysis = await self.analyze_area(heat_data)

        # 미션 타입 결정
        if mission_type is None:
            mission_type = analysis.recommended_solutions[0]

        template = MISSION_TEMPLATES[mission_type]

        # 미션 제목/설명 생성
        title = random.choice(template["titles"]).format(district=heat_data.district)
        description = random.choice(template["descriptions"]).format(district=heat_data.district)

        # 냉각 효과 계산
        min_effect, max_effect = template["cooling_effect_range"]
        cooling_effect = round(
            min_effect + (analysis.priority_score / 100) * (max_effect - min_effect),
            2
        )

        # 포인트 계산 (우선순위/난이도 반영)
        base_points = template["base_points"]
        points_reward = int(base_points * (1 + analysis.priority_score / 200))

        # AI 추론 생성
        ai_reasoning = self._generate_mission_reasoning(
            heat_data, analysis, mission_type, cooling_effect
        )

        return GeneratedMission(
            title=title,
            description=description,
            mission_type=mission_type,
            points_reward=points_reward,
            difficulty=template["base_difficulty"],
            estimated_cooling_effect=cooling_effect,
            priority_score=analysis.priority_score,
            ai_reasoning=ai_reasoning,
            latitude=heat_data.latitude,
            longitude=heat_data.longitude,
            district=heat_data.district
        )

    def _generate_mission_reasoning(
        self,
        heat_data: HeatIslandData,
        analysis: AreaAnalysis,
        mission_type: MissionType,
        cooling_effect: float
    ) -> str:
        """미션 생성 근거 생성"""
        solution_name = {
            MissionType.TREE_PLANTING: "가로수 식재",
            MissionType.GREEN_ROOF: "옥상 녹화",
            MissionType.COOL_PAVEMENT: "쿨페이브먼트",
            MissionType.WATER_FEATURE: "수경시설",
            MissionType.SHADE_STRUCTURE: "그늘막 설치"
        }[mission_type]

        intensity = heat_data.heat_island_intensity
        avg_intensity = 1.8  # 경기도 평균 (Mock)

        reasoning = f"""## AI 미션 생성 분석

### 대상 지역
- **위치**: {heat_data.district}
- **좌표**: ({heat_data.latitude:.4f}, {heat_data.longitude:.4f})
- **현재 온도**: {heat_data.temperature}°C
- **열섬 강도**: +{intensity}°C

### 우선순위 분석
- **우선순위 점수**: {analysis.priority_score:.1f}/100
- **경기도 평균 대비**: {'+' if intensity > avg_intensity else ''}{intensity - avg_intensity:.1f}°C

### 권장 솔루션: {solution_name}

{SOLUTION_REASONS[mission_type]}

### 예상 효과
- **냉각 효과**: -{cooling_effect}°C
- **체감온도 개선**: 약 {cooling_effect * 1.5:.1f}°C 감소
- **영향 범위**: 반경 약 {50 + int(cooling_effect * 100)}m

### 생성 시각
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return reasoning

    async def generate_missions_batch(
        self,
        top_n: int = 5
    ) -> list[GeneratedMission]:
        """
        우선순위 높은 지역들에 대한 미션 일괄 생성

        Args:
            top_n: 생성할 미션 수

        Returns:
            생성된 미션 리스트
        """
        # 우선순위 높은 열섬 지역 조회
        priority_areas = await self.climate_service.get_cooling_priority_areas(top_n)

        missions = []
        for heat_data in priority_areas:
            mission = await self.generate_mission(heat_data)
            missions.append(mission)

        # 우선순위 점수순 정렬
        missions.sort(key=lambda m: m.priority_score, reverse=True)

        return missions

    async def suggest_mission_for_location(
        self,
        latitude: float,
        longitude: float
    ) -> list[GeneratedMission]:
        """
        특정 좌표에 대한 미션 제안

        Args:
            latitude: 위도
            longitude: 경도

        Returns:
            제안된 미션 리스트 (타입별)
        """
        # 해당 좌표의 기상 데이터로 가상의 열섬 데이터 생성
        weather = await self.climate_service.get_weather_data(latitude, longitude)

        # 간단한 열섬 강도 추정
        estimated_intensity = 1.5 + (weather.temperature - 28) * 0.1

        heat_data = HeatIslandData(
            latitude=latitude,
            longitude=longitude,
            temperature=weather.temperature,
            heat_island_intensity=max(0.5, estimated_intensity),
            timestamp=datetime.now(),
            district="지정 위치"
        )

        # 각 미션 타입별로 미션 생성
        missions = []
        for mission_type in MissionType:
            mission = await self.generate_mission(heat_data, mission_type)
            missions.append(mission)

        return missions
