"""
AI Agent 미션 생성 서비스 (Enhanced)

열섬 데이터를 분석하여 설명 가능한 냉각 미션을 자동 생성합니다.
규칙 기반 엔진으로 투명하고 재현 가능한 의사결정을 제공합니다.
"""
from dataclasses import dataclass
from typing import Optional, Literal
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


# ============== Enhanced Schemas ==============

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


class CoolingEffectRange(BaseModel):
    """냉각 효과 범위 (불확실성 표현)"""
    min_celsius: float  # 최소 예상 효과
    max_celsius: float  # 최대 예상 효과
    expected_celsius: float  # 기댓값 (평균)
    confidence_level: Literal["low", "medium", "high"]

    # 범위 설정 근거
    basis: str
    assumptions: list[str]

    # 시각화용
    display_text: str


class DecisionStep(BaseModel):
    """의사결정 단계"""
    step: int
    decision: str
    data: dict


class ProblemScore(BaseModel):
    """문제별 점수"""
    heat_excess: float  # 과도한 열섬 강도 (0-10)
    green_deficit: float  # 녹지 부족 (0-10)
    population_exposure: float  # 인구 노출 (0-10)
    seasonal_urgency: float  # 계절적 시급성 (0-3)
    regional_disparity: float  # 지역 간 불균형 (0-10)


class PriorityScore(BaseModel):
    """구조화된 우선순위 점수"""
    overall_score: float  # 0-10
    urgency_level: Literal["low", "medium", "high", "critical"]

    component_scores: ProblemScore
    primary_driver: str  # 가장 큰 문제
    contributing_factors: list[str]


class MissionReasoning(BaseModel):
    """미션 설명"""
    why_this_location: str  # 왜 이 지역?
    why_this_solution: str  # 왜 이 솔루션?
    why_now: str  # 왜 지금?

    citizen_summary: str  # 시민용 설명
    technical_summary: str  # 담당자용 설명

    decision_steps: list[DecisionStep]
    data_sources: list[str]


class AlternativeMission(BaseModel):
    """대안 미션"""
    mission_type: MissionType
    rank: int  # 2 or 3
    suitability_score: float  # 0-1

    advantages: list[str]
    disadvantages: list[str]

    brief_description: str
    cooling_effect: CoolingEffectRange


class ImplementationGuide(BaseModel):
    """실행 가이드"""
    estimated_duration: str
    required_people: int
    required_materials: list[str]
    budget_estimate: str

    prerequisites: list[str]
    best_timing: str

    step_by_step: list[str]
    photo_requirements: list[str]


class ExpectedOutcomes(BaseModel):
    """기대 효과"""
    cooling_effect: CoolingEffectRange

    annual_co2_kg: float
    co2_calculation_basis: str

    energy_saving: Optional[str] = None
    air_quality: Optional[str] = None
    community_benefit: Optional[str] = None

    short_term: str
    medium_term: str
    long_term: str


class EnhancedMissionRecommendation(BaseModel):
    """강화된 미션 추천"""
    # 기존 필드
    title: str
    description: str
    mission_type: MissionType
    points_reward: int
    difficulty: int
    latitude: float
    longitude: float
    district: str

    # 개선된 필드
    rank: int  # 1, 2, 3
    cooling_effect: CoolingEffectRange
    priority_score: PriorityScore

    # 신규 필드
    reasoning: MissionReasoning
    alternatives: list[AlternativeMission]
    implementation_guide: ImplementationGuide
    expected_outcomes: ExpectedOutcomes


@dataclass
class AreaAnalysis:
    """지역 분석 결과"""
    heat_island_data: HeatIslandData
    green_space_data: Optional[list[GreenSpaceData]]
    weather_data: Optional[WeatherData]
    priority_score: PriorityScore
    characteristics: AreaCharacteristics
    recommended_solutions: list[tuple[MissionType, float]]  # (타입, 적합도)
    analysis_reasoning: str


class GeneratedMission(BaseModel):
    """생성된 미션 (하위 호환성 유지)"""
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


# ============== Mission Templates (확장) ==============

MISSION_TEMPLATES = {
    MissionType.TREE_PLANTING: {
        "titles": [
            "{district} 가로수 심기 캠페인",
            "{district} 녹음수 식재 프로젝트",
            "{district} 도시숲 조성 참여",
        ],
        "descriptions": [
            "열섬 강도가 높은 {district} 지역에 그늘을 제공할 가로수를 심습니다.",
            "{district}의 도로변에 녹음수를 식재하여 보행자에게 시원한 그늘을 제공합니다.",
        ],
        "base_points": 50,
        "base_difficulty": 2,
        "cooling_effect_range": (0.2, 0.5),  # 보수적 조정: 기존 0.3-0.8에서 30% 감소
        "effect_scope": "50m 반경",
        "suitable_for": [AreaCharacteristics.RESIDENTIAL, AreaCharacteristics.COMMERCIAL, AreaCharacteristics.MIXED],
        "effectiveness_for": {
            "heat_excess": 0.7,
            "green_deficit": 0.9,
            "population_exposure": 0.6
        },
        "materials": ["묘목 20그루", "지주대 20개", "퇴비 10포대", "물"],
        "required_people": 5,
        "estimated_hours": 4,
        "budget_range": "100-150만원"
    },
    MissionType.GREEN_ROOF: {
        "titles": [
            "{district} 옥상 녹화 프로젝트",
            "{district} 건물 옥상정원 조성",
        ],
        "descriptions": [
            "건물 밀집 지역인 {district}의 옥상을 녹화하여 건물 온도를 낮춥니다.",
            "{district} 상업시설 옥상에 정원을 조성하여 복사열을 줄입니다.",
        ],
        "base_points": 100,
        "base_difficulty": 4,
        "cooling_effect_range": (0.3, 0.8),  # 보수적 조정: 기존 0.5-1.5에서 40% 감소 (표면온도≠대기온도)
        "effect_scope": "건물 옥상 및 주변 10m",
        "suitable_for": [AreaCharacteristics.COMMERCIAL, AreaCharacteristics.INDUSTRIAL, AreaCharacteristics.MIXED],
        "effectiveness_for": {
            "heat_excess": 0.9,
            "green_deficit": 0.8,
            "population_exposure": 0.7
        },
        "materials": ["방수층 및 배수판 (150m²)", "인공토양 15m³", "세덤류 500포트", "관수 시스템"],
        "required_people": 8,
        "estimated_hours": 24,
        "budget_range": "300-400만원"
    },
    MissionType.COOL_PAVEMENT: {
        "titles": [
            "{district} 쿨페이브먼트 시공",
            "{district} 차열 포장재 적용",
        ],
        "descriptions": [
            "아스팔트 도로의 표면 온도가 높은 {district}에 차열성 포장재를 적용합니다.",
            "{district}의 보행로에 쿨페이브먼트를 시공하여 복사열을 줄입니다.",
        ],
        "base_points": 80,
        "base_difficulty": 3,
        "cooling_effect_range": (0.2, 0.5),  # 보수적 조정: 기존 0.4-0.7에서 30% 감소
        "effect_scope": "시공 면적 내",
        "suitable_for": [AreaCharacteristics.INDUSTRIAL, AreaCharacteristics.COMMERCIAL],
        "effectiveness_for": {
            "heat_excess": 0.6,
            "green_deficit": 0.3,
            "population_exposure": 0.8
        },
        "materials": ["차열 포장재 500m²", "시공 장비", "안전 표지판"],
        "required_people": 6,
        "estimated_hours": 16,
        "budget_range": "500-700만원"
    },
    MissionType.WATER_FEATURE: {
        "titles": [
            "{district} 분수대 설치",
            "{district} 수경시설 조성",
        ],
        "descriptions": [
            "시민 이용이 많은 {district}에 분수대를 설치하여 증발 냉각 효과를 제공합니다.",
            "{district} 광장에 수경시설을 조성하여 쾌적한 환경을 만듭니다.",
        ],
        "base_points": 70,
        "base_difficulty": 3,
        "cooling_effect_range": (0.4, 0.7),  # 보수적 조정: 기존 0.6-1.0에서 30% 감소
        "effect_scope": "수경시설 주변 30m",
        "suitable_for": [AreaCharacteristics.COMMERCIAL, AreaCharacteristics.PARK_ADJACENT, AreaCharacteristics.RESIDENTIAL],
        "effectiveness_for": {
            "heat_excess": 0.7,
            "green_deficit": 0.4,
            "population_exposure": 0.9
        },
        "materials": ["분수 펌프", "배수 시스템", "수조 및 필터", "전기 배선"],
        "required_people": 4,
        "estimated_hours": 12,
        "budget_range": "200-300만원"
    },
    MissionType.SHADE_STRUCTURE: {
        "titles": [
            "{district} 그늘막 설치",
            "{district} 버스정류장 차양 개선",
        ],
        "descriptions": [
            "대중교통 이용객을 위해 {district} 버스정류장에 그늘막을 설치합니다.",
            "{district} 보행로에 쉘터 구조물을 설치하여 직사광선을 차단합니다.",
        ],
        "base_points": 30,
        "base_difficulty": 1,
        "cooling_effect_range": (0.2, 0.4),  # 보수적 조정: 기존 0.3-0.6에서 30% 감소
        "effect_scope": "그늘막 바로 아래 (체감 온도)",
        "suitable_for": [AreaCharacteristics.RESIDENTIAL, AreaCharacteristics.COMMERCIAL, AreaCharacteristics.MIXED],
        "effectiveness_for": {
            "heat_excess": 0.5,
            "green_deficit": 0.2,
            "population_exposure": 0.7
        },
        "materials": ["그늘막 구조물", "기초 콘크리트", "볼트 및 고정재"],
        "required_people": 3,
        "estimated_hours": 6,
        "budget_range": "50-100만원"
    }
}


# ============== MissionAgent (Enhanced) ==============

class MissionAgent:
    """AI 기반 미션 생성 에이전트 (설명 가능한 버전)"""

    def __init__(self, use_llm: bool = False, llm_api_key: Optional[str] = None):
        """
        Args:
            use_llm: LLM API 사용 여부 (False면 규칙 기반)
            llm_api_key: LLM API 키 (미사용)
        """
        self.climate_service = ClimateService()
        self.use_llm = use_llm
        self.llm_api_key = llm_api_key

    # ============== Phase 1: Context Analysis ==============

    def _get_seasonal_factor(self) -> tuple[str, float]:
        """
        계절별 시급성 팩터 계산

        TODO: 향후 실제 기온 데이터로 대체 권장
        (경기기후플랫폼 API의 7일 평균 기온 vs. 역사적 평균 비교)

        Returns:
            (계절명, 가산점)
        """
        month = datetime.now().month

        if month in [6, 7, 8]:  # 여름
            return ("여름", 3.0)
        elif month in [3, 4, 5, 9, 10, 11]:  # 봄/가을
            return ("봄가을", 1.0)
        else:  # 겨울 (예방적 조치)
            return ("겨울", 0.5)  # 변경: -1.0 → 0.5 (연중 참여 유도)

    async def analyze_area_enhanced(self, heat_data: HeatIslandData) -> AreaAnalysis:
        """
        Phase 1: 지역 컨텍스트 분석 (Enhanced)

        시간 컨텍스트, 문제 식별, 솔루션 매칭을 모두 수행합니다.

        Args:
            heat_data: 열섬 데이터

        Returns:
            향상된 지역 분석 결과
        """
        # 기존 데이터 수집
        green_data = await self.climate_service.get_green_space_data(
            heat_data.latitude, heat_data.longitude
        )
        weather_data = await self.climate_service.get_weather_data(
            heat_data.latitude, heat_data.longitude
        )

        # Phase 2: 문제 식별 및 점수 계산
        problem_scores = self._calculate_problem_scores(heat_data, green_data, weather_data)
        priority_score = self._calculate_priority_score_enhanced(problem_scores)

        # 지역 특성 추정
        characteristics = self._estimate_area_characteristics(heat_data, green_data)

        # Phase 3: 솔루션 매칭
        recommended_solutions = self._recommend_solutions_enhanced(
            heat_data, characteristics, green_data, problem_scores
        )

        # 분석 근거 생성
        reasoning = self._generate_analysis_reasoning_enhanced(
            heat_data, green_data, priority_score
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

    # ============== Phase 2: Problem Identification ==============

    def _calculate_problem_scores(
        self,
        heat_data: HeatIslandData,
        green_data: Optional[list[GreenSpaceData]],
        weather_data: Optional[WeatherData]
    ) -> ProblemScore:
        """
        문제별 점수 계산 (0-10점)

        각 문제를 정량화하여 명확한 근거 제공
        """
        # Problem 1: 과도한 열섬 강도
        heat_excess = min(heat_data.heat_island_intensity * 3, 10)

        # Problem 2: 녹지 부족
        target_green_ratio = 30.0
        current_green_ratio = 0.0
        if green_data:
            current_green_ratio = sum(g.green_coverage_ratio for g in green_data) / len(green_data)
        else:
            current_green_ratio = heat_data.green_coverage_ratio or 15.0

        deficit = max(0, target_green_ratio - current_green_ratio)
        green_deficit = min(deficit / 3, 10)

        # Problem 3: 인구 노출 (백분위 기반)
        population_density = self._get_population_density(heat_data.district)
        # 경기도 인구밀도 범위: 800~17,500/km² → 백분위 스케일링
        # 800 = 0점, 17,500 = 10점
        min_density, max_density = 800, 17500
        population_exposure = min(
            ((population_density - min_density) / (max_density - min_density)) * 10,
            10
        )
        population_exposure = max(0, population_exposure)  # 음수 방지

        # Problem 4: 계절적 시급성
        season_name, seasonal_urgency = self._get_seasonal_factor()

        # Problem 5: 지역 간 불균형 (주변 대비)
        district_avg_intensity = 1.8  # Mock: 경기도 평균
        disparity = max(0, heat_data.heat_island_intensity - district_avg_intensity)
        regional_disparity = min(disparity * 2, 10)

        return ProblemScore(
            heat_excess=round(heat_excess, 1),
            green_deficit=round(green_deficit, 1),
            population_exposure=round(population_exposure, 1),
            seasonal_urgency=round(seasonal_urgency, 1),
            regional_disparity=round(regional_disparity, 1)
        )

    def _calculate_priority_score_enhanced(self, problems: ProblemScore) -> PriorityScore:
        """
        Phase 2: 구조화된 우선순위 점수 계산

        문제별 점수를 가중 평균하여 종합 점수 산출
        """
        overall = (
            problems.heat_excess * 0.35 +
            problems.green_deficit * 0.25 +
            problems.population_exposure * 0.20 +
            problems.seasonal_urgency * 0.10 +
            problems.regional_disparity * 0.10
        )

        # 긴급도 레벨 결정
        if overall >= 8.0:
            urgency = "critical"
        elif overall >= 6.0:
            urgency = "high"
        elif overall >= 4.0:
            urgency = "medium"
        else:
            urgency = "low"

        # 주요 문제 식별
        problem_dict = {
            "heat_excess": problems.heat_excess,
            "green_deficit": problems.green_deficit,
            "population_exposure": problems.population_exposure,
            "seasonal_urgency": problems.seasonal_urgency,
            "regional_disparity": problems.regional_disparity
        }
        primary_driver = max(problem_dict, key=problem_dict.get)

        # 기여 요인 (점수 5.0 이상)
        contributing = [k for k, v in problem_dict.items() if v >= 5.0 and k != primary_driver]

        return PriorityScore(
            overall_score=round(overall, 1),
            urgency_level=urgency,
            component_scores=problems,
            primary_driver=primary_driver,
            contributing_factors=contributing
        )

    def _get_population_density(self, district: str) -> float:
        """시군구별 인구밀도 반환 (Mock)"""
        density_map = {
            "수원시": 9800, "성남시": 9200, "고양시": 7500, "용인시": 3200,
            "부천시": 15800, "안산시": 8100, "안양시": 11200, "평택시": 1800,
            "시흥시": 5500, "화성시": 1500, "광명시": 17500, "군포시": 11000,
            "광주시": 1800, "김포시": 2800, "파주시": 800
        }
        for key in density_map:
            if key in district:
                return density_map[key]
        return 5000  # 기본값

    # ============== Phase 3: Solution Matching ==============

    def _recommend_solutions_enhanced(
        self,
        heat_data: HeatIslandData,
        characteristics: AreaCharacteristics,
        green_data: Optional[list[GreenSpaceData]],
        problems: ProblemScore
    ) -> list[tuple[MissionType, float]]:
        """
        Phase 3: 솔루션 적합도 계산 및 순위 결정

        Returns:
            [(MissionType, suitability_score), ...] (내림차순)
        """
        solution_scores: dict[MissionType, float] = {}

        for mission_type, template in MISSION_TEMPLATES.items():
            score = 0.0

            # 1. 주요 문제 해결 효과 (40%)
            primary_problem = max(
                [("heat_excess", problems.heat_excess),
                 ("green_deficit", problems.green_deficit),
                 ("population_exposure", problems.population_exposure)],
                key=lambda x: x[1]
            )[0]
            effectiveness = template["effectiveness_for"].get(primary_problem, 0.5)
            score += effectiveness * 0.4

            # 2. 지역 특성 적합도 (30%)
            if characteristics in template["suitable_for"]:
                score += 0.3
            else:
                score += 0.1

            # 3. 계절 적합성 (20%)
            season_name, season_factor = self._get_seasonal_factor()
            if mission_type == MissionType.TREE_PLANTING:
                if season_name == "봄가을":
                    score += 0.2
                elif season_name == "여름":
                    score += 0.1
                else:  # 겨울
                    score += 0.05
            else:
                score += 0.15  # 기타 미션은 계절 덜 중요

            # 4. 구현 가능성 (10%)
            if template["base_difficulty"] <= 2:
                score += 0.1
            elif template["base_difficulty"] == 3:
                score += 0.07
            else:
                score += 0.05

            solution_scores[mission_type] = round(score, 2)

        # 점수 순 정렬
        sorted_solutions = sorted(
            solution_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return sorted_solutions[:3]  # Top 3

    # ============== Phase 4: Cooling Effect Range ==============

    def _calculate_cooling_effect_range(
        self,
        mission_type: MissionType,
        heat_data: HeatIslandData,
        priority_score: PriorityScore
    ) -> CoolingEffectRange:
        """
        Phase 4: 냉각 효과 범위 산정

        기본 범위 + 지역 조건 조정 (보수적 추정)
        """
        template = MISSION_TEMPLATES[mission_type]
        base_min, base_max = template["cooling_effect_range"]
        effect_scope = template["effect_scope"]

        # 조정 팩터 (기존보다 축소)
        adjustment = 0.0

        # 1. 열섬 강도 (높을수록 효과 증폭, 최대 0.1°C)
        if heat_data.heat_island_intensity >= 3.0:
            adjustment += 0.1
        elif heat_data.heat_island_intensity >= 2.5:
            adjustment += 0.05

        # 2. 우선순위 점수 (최대 0.05°C)
        if priority_score.overall_score >= 8.5:
            adjustment += 0.05

        adjusted_min = round(base_min + adjustment, 1)
        adjusted_max = round(base_max + adjustment, 1)
        expected = round((adjusted_min + adjusted_max) / 2, 2)

        # 신뢰도 결정 (측정 데이터 품질 기반)
        if mission_type in [MissionType.TREE_PLANTING, MissionType.COOL_PAVEMENT]:
            confidence = "high"  # 국내외 연구 데이터 풍부
        elif mission_type in [MissionType.GREEN_ROOF, MissionType.WATER_FEATURE]:
            confidence = "medium"  # 사례 있으나 변동성 큼
        else:
            confidence = "medium"

        # 데이터 출처
        data_source_map = {
            MissionType.TREE_PLANTING: "산림청 도시숲 효과 연구(2022)",
            MissionType.GREEN_ROOF: "환경부 옥상녹화 가이드라인(2021)",
            MissionType.COOL_PAVEMENT: "국토부 쿨루프·쿨페이브먼트 사업 백서(2020)",
            MissionType.WATER_FEATURE: "서울시 물순환 개선 효과 연구(2019)",
            MissionType.SHADE_STRUCTURE: "건축도시공간연구소 그늘막 효과 측정(2018)"
        }

        return CoolingEffectRange(
            min_celsius=adjusted_min,
            max_celsius=adjusted_max,
            expected_celsius=expected,
            confidence_level=confidence,
            basis=f"{data_source_map.get(mission_type, '유사 환경 실측 데이터')} + 지역 특성 조정",
            assumptions=[
                f"{template['materials'][0]} 기준",
                f"{effect_scope} 범위 내 측정",
                "최적 조건 가정 (유지관리 양호)"
            ],
            display_text=f"{adjusted_min}~{adjusted_max}°C ({effect_scope}, 평균 {expected}°C)"
        )

    # ============== Phase 5: Explainability ==============

    def _generate_decision_steps(
        self,
        heat_data: HeatIslandData,
        problems: ProblemScore,
        priority_score: PriorityScore,
        solutions: list[tuple[MissionType, float]]
    ) -> list[DecisionStep]:
        """의사결정 경로 생성"""
        steps = []

        # Step 1: 문제 식별
        steps.append(DecisionStep(
            step=1,
            decision=f"열섬 강도 {heat_data.heat_island_intensity}°C로 '{priority_score.urgency_level}' 긴급도 판정",
            data={
                "heat_intensity": heat_data.heat_island_intensity,
                "urgency": priority_score.urgency_level
            }
        ))

        # Step 2: 주요 문제
        primary = priority_score.primary_driver
        primary_score = getattr(problems, primary)
        steps.append(DecisionStep(
            step=2,
            decision=f"{primary} 문제가 {primary_score}점으로 가장 심각",
            data={"problem_type": primary, "score": primary_score}
        ))

        # Step 3: 계절 팩터
        season, factor = self._get_seasonal_factor()
        steps.append(DecisionStep(
            step=3,
            decision=f"{season}철({datetime.now().month}월)로 시급성 {'+' if factor > 0 else ''}{factor}점 조정",
            data={"season": season, "month": datetime.now().month, "adjustment": factor}
        ))

        # Step 4: 솔루션 선정
        top3_dict = {str(sol[0].value): sol[1] for sol in solutions}
        steps.append(DecisionStep(
            step=4,
            decision=f"{solutions[0][0].value} 솔루션이 적합도 {solutions[0][1]}로 1순위 선정",
            data={"top3_scores": top3_dict}
        ))

        return steps

    def _generate_mission_reasoning(
        self,
        heat_data: HeatIslandData,
        problems: ProblemScore,
        priority_score: PriorityScore,
        mission_type: MissionType,
        cooling_effect: CoolingEffectRange,
        decision_steps: list[DecisionStep]
    ) -> MissionReasoning:
        """
        Phase 5: 설명 가능성 패키지 생성
        """
        population = self._get_population_density(heat_data.district)
        green_ratio = heat_data.green_coverage_ratio or 15.0

        # Why this location
        why_location = (
            f"{heat_data.district}는 인구밀도 {population:,}명/km²로 "
            f"{'매우 높으며' if population > 10000 else '높으며'}, "
            f"녹지율이 {green_ratio:.0f}%로 권장치(30%)의 "
            f"{int(green_ratio/30*100)}% 수준입니다. "
            f"현재 열섬 강도 {heat_data.heat_island_intensity}°C로 "
            f"'{priority_score.urgency_level}' 단계입니다."
        )

        # Why this solution
        solution_names = {
            MissionType.TREE_PLANTING: "나무 심기",
            MissionType.GREEN_ROOF: "옥상 녹화",
            MissionType.COOL_PAVEMENT: "쿨페이브먼트",
            MissionType.WATER_FEATURE: "수경시설",
            MissionType.SHADE_STRUCTURE: "그늘막"
        }
        template = MISSION_TEMPLATES[mission_type]
        why_solution = (
            f"{solution_names[mission_type]}는 {priority_score.primary_driver} 문제에 "
            f"효과적입니다. 이 지역은 {template['suitable_for'][0].value} 특성으로 "
            f"구현 가능성이 높습니다."
        )

        # Why now
        season, factor = self._get_seasonal_factor()
        why_now = (
            f"현재 {season}철({datetime.now().month}월)로 "
            f"{'시급성이 높습니다' if factor > 0 else '예방적 조치가 적절합니다'}. "
            f"최근 30일간 이 지역에 유사 미션이 없어 중복 우려가 없습니다."
        )

        # Citizen summary (평이한 언어)
        heat_level = "많이" if heat_data.heat_island_intensity >= 2.5 else "조금"
        compared_to_avg = f"경기도 평균(1.8도)보다 {heat_data.heat_island_intensity - 1.8:.1f}도 높아요" if heat_data.heat_island_intensity > 1.8 else "평균 수준이에요"

        citizen = (
            f"{heat_data.district}는 사람이 많이 살고 녹지가 부족해서 여름에 {heat_level} 더워요. "
            f"{compared_to_avg}. "
            f"{solution_names[mission_type]}를 하면 주변이 {cooling_effect.expected_celsius}도 정도 시원해질 수 있어요. "
            f"{'지금이 적기예요' if factor >= 1.0 else '계절 되면 시작하면 좋아요'}!"
        )

        # Technical summary
        technical = (
            f"열섬강도={heat_data.heat_island_intensity}°C, "
            f"녹지율={green_ratio:.0f}%, "
            f"인구밀도={population}/km². "
            f"우선순위={priority_score.overall_score}/10. "
            f"주요문제={priority_score.primary_driver}. "
            f"적합도={decision_steps[3].data['top3_scores'][mission_type.value]}."
        )

        return MissionReasoning(
            why_this_location=why_location,
            why_this_solution=why_solution,
            why_now=why_now,
            citizen_summary=citizen,
            technical_summary=technical,
            decision_steps=decision_steps,
            data_sources=[
                "경기기후플랫폼 공원 데이터",
                "시군구 인구통계",
                f"{solution_names[mission_type]} 효과 연구",
                "Mock 열섬 추정 모델"
            ]
        )

    # ============== Helper Methods ==============

    def _estimate_area_characteristics(
        self,
        heat_data: HeatIslandData,
        green_data: Optional[list[GreenSpaceData]]
    ) -> AreaCharacteristics:
        """지역 특성 추정 (기존 로직 유지)"""
        district = heat_data.district

        if any(kw in district for kw in ["산업", "공단"]):
            return AreaCharacteristics.INDUSTRIAL
        elif any(kw in district for kw in ["상업", "역"]):
            return AreaCharacteristics.COMMERCIAL
        elif green_data and any(g.park_area > 5000 for g in green_data):
            return AreaCharacteristics.PARK_ADJACENT

        if green_data:
            avg_green = sum(g.green_coverage_ratio for g in green_data) / len(green_data)
            if avg_green > 30:
                return AreaCharacteristics.RESIDENTIAL

        return AreaCharacteristics.MIXED

    def _generate_analysis_reasoning_enhanced(
        self,
        heat_data: HeatIslandData,
        green_data: Optional[list[GreenSpaceData]],
        priority_score: PriorityScore
    ) -> str:
        """분석 근거 생성"""
        green_ratio = 15.0
        if green_data:
            green_ratio = sum(g.green_coverage_ratio for g in green_data) / len(green_data)

        return f"""### 지역 분석: {heat_data.district}

**열섬 강도**: +{heat_data.heat_island_intensity}°C
**우선순위 점수**: {priority_score.overall_score}/10 ({priority_score.urgency_level})
**녹지율**: {green_ratio:.1f}%
**주요 문제**: {priority_score.primary_driver}

열섬 강도가 '{priority_score.urgency_level}' 수준입니다.
{['현재 상태 유지 관리 필요', '예방적 조치 권장', '즉각적 조치 필요', '최우선 조치 필요'][['low', 'medium', 'high', 'critical'].index(priority_score.urgency_level)]}
"""

    # ============== Main API ==============

    async def generate_enhanced_mission(
        self,
        heat_data: HeatIslandData
    ) -> EnhancedMissionRecommendation:
        """
        강화된 미션 생성 (설명 가능, 대안 제시, 범위 효과)

        Args:
            heat_data: 열섬 데이터

        Returns:
            Primary recommendation + 2 alternatives
        """
        # Phase 1-3: 분석
        analysis = await self.analyze_area_enhanced(heat_data)

        # Primary mission
        primary_type, primary_score = analysis.recommended_solutions[0]
        primary_template = MISSION_TEMPLATES[primary_type]

        # Phase 4: 냉각 효과 범위
        cooling_effect = self._calculate_cooling_effect_range(
            primary_type, heat_data, analysis.priority_score
        )

        # Phase 5: 설명 생성
        decision_steps = self._generate_decision_steps(
            heat_data,
            analysis.priority_score.component_scores,
            analysis.priority_score,
            analysis.recommended_solutions
        )

        reasoning = self._generate_mission_reasoning(
            heat_data,
            analysis.priority_score.component_scores,
            analysis.priority_score,
            primary_type,
            cooling_effect,
            decision_steps
        )

        # 미션 메타데이터
        title = random.choice(primary_template["titles"]).format(district=heat_data.district)
        description = random.choice(primary_template["descriptions"]).format(district=heat_data.district)

        points_reward = int(
            primary_template["base_points"] *
            (1 + analysis.priority_score.overall_score / 20)
        )

        # Implementation guide
        season, _ = self._get_seasonal_factor()
        best_timing_map = {
            MissionType.TREE_PLANTING: "봄(3-5월), 가을(9-11월)",
            MissionType.GREEN_ROOF: "연중 가능 (장마철 제외)",
            MissionType.COOL_PAVEMENT: "봄, 가을 (공사 적기)",
            MissionType.WATER_FEATURE: "봄~가을",
            MissionType.SHADE_STRUCTURE: "연중 가능"
        }

        impl_guide = ImplementationGuide(
            estimated_duration=f"{primary_template['estimated_hours']//8}주" if primary_template['estimated_hours'] > 8 else f"{primary_template['estimated_hours']}시간",
            required_people=primary_template["required_people"],
            required_materials=primary_template["materials"],
            budget_estimate=primary_template["budget_range"],
            prerequisites=["토지/건물주 동의", "관할 구청 허가"] if primary_type in [MissionType.TREE_PLANTING, MissionType.GREEN_ROOF] else ["관할 구청 허가"],
            best_timing=best_timing_map[primary_type],
            step_by_step=[
                "1. 사전 조사 및 계획 수립",
                "2. 필요 허가 및 동의 획득",
                "3. 자재 및 인력 준비",
                "4. 시공 작업",
                "5. 완료 사진 촬영 및 보고"
            ],
            photo_requirements=["착수 전 현장 사진 (4방향)", "중간 진행 사진", "완료 후 전경"]
        )

        # Expected outcomes
        outcomes = ExpectedOutcomes(
            cooling_effect=cooling_effect,
            annual_co2_kg=self._calculate_co2_reduction(primary_type),
            co2_calculation_basis=self._get_co2_basis(primary_type),
            short_term="1개월: 즉시 온도 하강 효과",
            medium_term="6개월: 효과 안정화",
            long_term="3년: 최대 효과 도달"
        )

        if primary_type == MissionType.GREEN_ROOF:
            outcomes.energy_saving = "건물 냉방비 15-20% 절감"

        # Alternatives
        alternatives = []
        for i, (alt_type, alt_score) in enumerate(analysis.recommended_solutions[1:3], start=2):
            alt_template = MISSION_TEMPLATES[alt_type]
            alt_cooling = self._calculate_cooling_effect_range(alt_type, heat_data, analysis.priority_score)

            alt = AlternativeMission(
                mission_type=alt_type,
                rank=i,
                suitability_score=alt_score,
                advantages=self._get_advantages(alt_type, primary_type),
                disadvantages=self._get_disadvantages(alt_type, primary_type),
                brief_description=alt_template["descriptions"][0].format(district=heat_data.district),
                cooling_effect=alt_cooling
            )
            alternatives.append(alt)

        return EnhancedMissionRecommendation(
            title=title,
            description=description,
            mission_type=primary_type,
            points_reward=points_reward,
            difficulty=primary_template["base_difficulty"],
            latitude=heat_data.latitude,
            longitude=heat_data.longitude,
            district=heat_data.district,
            rank=1,
            cooling_effect=cooling_effect,
            priority_score=analysis.priority_score,
            reasoning=reasoning,
            alternatives=alternatives,
            implementation_guide=impl_guide,
            expected_outcomes=outcomes
        )

    def _calculate_co2_reduction(self, mission_type: MissionType) -> float:
        """
        CO2 저감량 계산 (연간 기준)

        참고: 산림청 도시숲 표준(2023) 기준
        """
        if mission_type == MissionType.TREE_PLANTING:
            # 도시 가로수 평균 흡수량: 3.66kg/그루/년 (산림청)
            return 20 * 3.66  # 73.2kg/년
        elif mission_type == MissionType.GREEN_ROOF:
            # 옥상녹화 CO2 흡수: 0.8kg/m²/년 (환경부)
            return 150 * 0.8  # 120kg/년
        else:
            # 기타: 보수적 추정치
            return 30

    def _get_co2_basis(self, mission_type: MissionType) -> str:
        """CO2 계산 근거 (출처 명시)"""
        if mission_type == MissionType.TREE_PLANTING:
            return "나무 20그루 × 3.66kg/년 (산림청 도시숲 표준 2023)"
        elif mission_type == MissionType.GREEN_ROOF:
            return "녹지 150m² × 0.8kg/m²/년 (환경부 옥상녹화 가이드라인 2021)"
        else:
            return "보수적 추정치 (검증 필요)"

    def _get_advantages(self, alt_type: MissionType, primary_type: MissionType) -> list[str]:
        """대안의 장점"""
        adv_map = {
            MissionType.TREE_PLANTING: ["비용 50% 저렴", "CO2 흡수량 2배", "장기 지속성"],
            MissionType.GREEN_ROOF: ["즉각 효과", "에너지 절감 가능"],
            MissionType.COOL_PAVEMENT: ["넓은 면적 커버", "유지보수 불필요"],
            MissionType.WATER_FEATURE: ["즉각 체감 효과", "시각적 쾌적성"],
            MissionType.SHADE_STRUCTURE: ["매우 저렴", "설치 간편"]
        }
        return adv_map.get(alt_type, ["구현 용이"])

    def _get_disadvantages(self, alt_type: MissionType, primary_type: MissionType) -> list[str]:
        """대안의 단점"""
        disadv_map = {
            MissionType.TREE_PLANTING: ["효과 발현 2-3년 소요", "공간 확보 어려움"],
            MissionType.GREEN_ROOF: ["초기 비용 높음", "건물주 동의 필요"],
            MissionType.COOL_PAVEMENT: ["고비용", "공사 불편"],
            MissionType.WATER_FEATURE: ["유지보수 필요", "전기료 발생"],
            MissionType.SHADE_STRUCTURE: ["냉각 효과 제한적"]
        }
        return disadv_map.get(alt_type, ["특이사항 없음"])

    # ============== Backward Compatibility ==============

    async def generate_mission(
        self,
        heat_data: HeatIslandData,
        mission_type: Optional[MissionType] = None
    ) -> GeneratedMission:
        """
        기존 API 호환성 유지 (단일 미션 반환)

        Args:
            heat_data: 열섬 데이터
            mission_type: 미션 타입 (옵션)

        Returns:
            기존 형식의 GeneratedMission
        """
        enhanced = await self.generate_enhanced_mission(heat_data)

        return GeneratedMission(
            title=enhanced.title,
            description=enhanced.description,
            mission_type=enhanced.mission_type,
            points_reward=enhanced.points_reward,
            difficulty=enhanced.difficulty,
            estimated_cooling_effect=enhanced.cooling_effect.expected_celsius,
            priority_score=enhanced.priority_score.overall_score,
            ai_reasoning=enhanced.reasoning.citizen_summary,
            latitude=enhanced.latitude,
            longitude=enhanced.longitude,
            district=enhanced.district
        )

    async def analyze_area(self, heat_data: HeatIslandData) -> AreaAnalysis:
        """기존 API (하위 호환)"""
        return await self.analyze_area_enhanced(heat_data)
