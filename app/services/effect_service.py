"""
효과 측정 서비스

쿨링스팟 설치 전후 효과 분석 및 통계 제공
"""
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional
import random

from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.models import CoolingSpot, Mission, EffectMeasurement, MissionStatus, MissionType


# ============== Schemas ==============

class EffectSummary(BaseModel):
    """효과 요약"""
    cooling_spot_id: int
    cooling_spot_name: str
    total_measurements: int
    avg_temperature: float
    avg_cooling_effect: float
    max_cooling_effect: float
    trend: str  # "improving", "stable", "declining"


class OverallStats(BaseModel):
    """전체 통계"""
    total_cooling_spots: int
    total_missions_completed: int
    total_measurements: int
    avg_cooling_effect: float
    total_estimated_cooling: float
    total_trees_planted: int
    total_green_area_m2: float
    co2_reduction_kg: float


class TimeSeriesData(BaseModel):
    """시계열 데이터"""
    timestamp: datetime
    temperature: float
    cooling_effect: float
    humidity: Optional[float] = None


class ComparisonData(BaseModel):
    """비교 데이터"""
    period: str
    before_avg_temp: float
    after_avg_temp: float
    cooling_effect: float
    improvement_percent: float


class RegionalStats(BaseModel):
    """지역별 통계"""
    district: str
    cooling_spots_count: int
    missions_completed: int
    avg_cooling_effect: float
    heat_island_reduction: float


# ============== Mock Data Generator ==============

def generate_mock_measurements(
    cooling_spot_id: int,
    days: int = 30,
    base_temp: float = 30.0,
    cooling_trend: float = -0.02  # 일일 냉각 트렌드
) -> list[dict]:
    """Mock 측정 데이터 생성"""
    measurements = []
    current_date = datetime.now() - timedelta(days=days)

    for day in range(days):
        # 하루 3회 측정 (아침, 점심, 저녁)
        for hour in [9, 14, 19]:
            timestamp = current_date + timedelta(days=day, hours=hour)

            # 시간대별 기온 변화
            hour_factor = 0 if hour == 9 else (3 if hour == 14 else 1)

            # 일별 냉각 효과 증가 (쿨링스팟 효과)
            daily_cooling = day * cooling_trend

            # 랜덤 변동
            random_var = random.uniform(-1, 1)

            temp = base_temp + hour_factor + daily_cooling + random_var
            nearby_temp = temp + random.uniform(1.5, 3.0)  # 주변은 더 높음
            cooling_effect = nearby_temp - temp

            measurements.append({
                "cooling_spot_id": cooling_spot_id,
                "temperature": round(temp, 1),
                "humidity": round(60 + random.uniform(-15, 15), 1),
                "heat_index": round(temp + random.uniform(2, 5), 1),
                "nearby_avg_temperature": round(nearby_temp, 1),
                "cooling_effect": round(cooling_effect, 2),
                "wind_speed": round(random.uniform(0.5, 4), 1),
                "solar_radiation": round(random.uniform(200, 800), 1),
                "measured_at": timestamp
            })

    return measurements


class EffectService:
    """효과 측정 서비스"""

    def __init__(self, db: Optional[Session] = None):
        self.db = db

    def get_cooling_spot_summary(
        self,
        cooling_spot_id: int
    ) -> EffectSummary:
        """특정 쿨링스팟의 효과 요약"""
        if self.db:
            spot = self.db.query(CoolingSpot).filter(
                CoolingSpot.id == cooling_spot_id
            ).first()

            if not spot:
                raise ValueError(f"Cooling spot {cooling_spot_id} not found")

            measurements = self.db.query(EffectMeasurement).filter(
                EffectMeasurement.cooling_spot_id == cooling_spot_id
            ).all()

            if measurements:
                avg_temp = sum(m.temperature for m in measurements) / len(measurements)
                avg_effect = sum(m.cooling_effect or 0 for m in measurements) / len(measurements)
                max_effect = max(m.cooling_effect or 0 for m in measurements)
            else:
                avg_temp = 28.0
                avg_effect = 0.0
                max_effect = 0.0

            return EffectSummary(
                cooling_spot_id=cooling_spot_id,
                cooling_spot_name=spot.name,
                total_measurements=len(measurements),
                avg_temperature=round(avg_temp, 1),
                avg_cooling_effect=round(avg_effect, 2),
                max_cooling_effect=round(max_effect, 2),
                trend="improving"
            )

        # Mock 데이터
        return EffectSummary(
            cooling_spot_id=cooling_spot_id,
            cooling_spot_name=f"쿨링스팟 #{cooling_spot_id}",
            total_measurements=random.randint(50, 200),
            avg_temperature=round(28 + random.uniform(-2, 2), 1),
            avg_cooling_effect=round(random.uniform(0.5, 2.0), 2),
            max_cooling_effect=round(random.uniform(2.0, 3.5), 2),
            trend=random.choice(["improving", "stable", "improving"])
        )

    def get_overall_stats(self) -> OverallStats:
        """전체 통계 조회"""
        if self.db:
            total_spots = self.db.query(CoolingSpot).count()
            total_missions = self.db.query(Mission).filter(
                Mission.status == MissionStatus.COMPLETED
            ).count()
            total_measurements = self.db.query(EffectMeasurement).count()

            # 평균 냉각 효과
            avg_effect_result = self.db.query(
                func.avg(EffectMeasurement.cooling_effect)
            ).scalar()
            avg_effect = float(avg_effect_result) if avg_effect_result else 0.0

            # 미션별 예상 냉각 효과 합계
            total_cooling = self.db.query(
                func.sum(Mission.estimated_cooling_effect)
            ).filter(Mission.status == MissionStatus.COMPLETED).scalar()

            return OverallStats(
                total_cooling_spots=total_spots,
                total_missions_completed=total_missions,
                total_measurements=total_measurements,
                avg_cooling_effect=round(avg_effect, 2),
                total_estimated_cooling=round(float(total_cooling or 0), 2),
                total_trees_planted=total_missions * 5,  # 추정
                total_green_area_m2=total_spots * 500,  # 추정
                co2_reduction_kg=total_spots * 120  # 추정
            )

        # Mock 데이터
        return OverallStats(
            total_cooling_spots=24,
            total_missions_completed=156,
            total_measurements=4680,
            avg_cooling_effect=1.45,
            total_estimated_cooling=52.3,
            total_trees_planted=780,
            total_green_area_m2=12000,
            co2_reduction_kg=2880
        )

    def get_time_series(
        self,
        cooling_spot_id: Optional[int] = None,
        days: int = 30
    ) -> list[TimeSeriesData]:
        """시계열 데이터 조회"""
        if self.db and cooling_spot_id:
            start_date = datetime.now() - timedelta(days=days)
            measurements = self.db.query(EffectMeasurement).filter(
                EffectMeasurement.cooling_spot_id == cooling_spot_id,
                EffectMeasurement.measured_at >= start_date
            ).order_by(EffectMeasurement.measured_at).all()

            return [
                TimeSeriesData(
                    timestamp=m.measured_at,
                    temperature=m.temperature,
                    cooling_effect=m.cooling_effect or 0,
                    humidity=m.humidity
                )
                for m in measurements
            ]

        # Mock 데이터
        mock_data = generate_mock_measurements(
            cooling_spot_id or 1,
            days=days
        )
        return [
            TimeSeriesData(
                timestamp=m["measured_at"],
                temperature=m["temperature"],
                cooling_effect=m["cooling_effect"],
                humidity=m["humidity"]
            )
            for m in mock_data
        ]

    def get_before_after_comparison(
        self,
        cooling_spot_id: int,
        installation_date: Optional[datetime] = None
    ) -> list[ComparisonData]:
        """설치 전후 비교 데이터"""
        # Mock 비교 데이터 (주별)
        comparisons = []
        weeks = ["1주차", "2주차", "3주차", "4주차"]

        base_before = 32.5
        improvement_rate = 0.15  # 주당 15% 개선

        for i, week in enumerate(weeks):
            before_temp = base_before + random.uniform(-0.5, 0.5)
            cooling = 0.8 + (i * 0.3) + random.uniform(-0.1, 0.1)
            after_temp = before_temp - cooling
            improvement = (cooling / before_temp) * 100

            comparisons.append(ComparisonData(
                period=week,
                before_avg_temp=round(before_temp, 1),
                after_avg_temp=round(after_temp, 1),
                cooling_effect=round(cooling, 2),
                improvement_percent=round(improvement, 1)
            ))

        return comparisons

    def get_regional_stats(self) -> list[RegionalStats]:
        """지역별 통계"""
        # Mock 지역별 데이터
        regions = [
            ("수원시", 5, 28, 1.8, 2.1),
            ("성남시", 4, 22, 1.5, 1.7),
            ("부천시", 3, 18, 1.6, 1.9),
            ("고양시", 3, 15, 1.3, 1.5),
            ("용인시", 2, 12, 1.2, 1.4),
            ("안양시", 2, 14, 1.4, 1.6),
            ("시흥시", 2, 16, 1.7, 2.0),
            ("화성시", 2, 10, 1.1, 1.3),
            ("평택시", 1, 8, 1.0, 1.2),
            ("안산시", 1, 13, 1.5, 1.8),
        ]

        return [
            RegionalStats(
                district=r[0],
                cooling_spots_count=r[1],
                missions_completed=r[2],
                avg_cooling_effect=r[3],
                heat_island_reduction=r[4]
            )
            for r in regions
        ]

    def get_mission_type_effectiveness(self) -> dict:
        """미션 타입별 효과 분석"""
        return {
            "tree_planting": {
                "name": "나무 심기",
                "avg_cooling_effect": 0.65,
                "missions_completed": 45,
                "total_trees": 225,
                "co2_absorbed_kg": 540,
                "effectiveness_score": 85
            },
            "green_roof": {
                "name": "옥상 녹화",
                "avg_cooling_effect": 1.2,
                "missions_completed": 28,
                "area_m2": 5600,
                "energy_saved_kwh": 8400,
                "effectiveness_score": 92
            },
            "cool_pavement": {
                "name": "쿨페이브먼트",
                "avg_cooling_effect": 0.35,
                "missions_completed": 32,
                "area_m2": 12800,
                "surface_temp_reduction": 8.5,
                "effectiveness_score": 78
            },
            "water_feature": {
                "name": "수경시설",
                "avg_cooling_effect": 0.28,
                "missions_completed": 21,
                "water_usage_l": 15000,
                "humidity_increase": 12,
                "effectiveness_score": 72
            },
            "shade_structure": {
                "name": "그늘막 설치",
                "avg_cooling_effect": 0.15,
                "missions_completed": 30,
                "shaded_area_m2": 3000,
                "uv_reduction_percent": 85,
                "effectiveness_score": 68
            }
        }

    def calculate_environmental_impact(self) -> dict:
        """환경 영향 계산"""
        stats = self.get_overall_stats()

        return {
            "co2_reduction": {
                "value": stats.co2_reduction_kg,
                "unit": "kg",
                "equivalent": f"승용차 {int(stats.co2_reduction_kg / 2.3)}km 주행량"
            },
            "energy_saving": {
                "value": stats.total_cooling_spots * 150,
                "unit": "kWh/년",
                "equivalent": f"가정 {int(stats.total_cooling_spots * 150 / 300)}가구 월 전기 사용량"
            },
            "water_retention": {
                "value": stats.total_green_area_m2 * 0.5,
                "unit": "톤/년",
                "equivalent": "우수 저류 효과"
            },
            "air_quality": {
                "pm25_reduction": stats.total_trees_planted * 0.02,
                "unit": "kg/년",
                "description": "미세먼지 저감"
            },
            "biodiversity": {
                "habitat_area": stats.total_green_area_m2,
                "species_supported": int(stats.total_green_area_m2 / 100),
                "description": "생태 서식지 제공"
            }
        }
