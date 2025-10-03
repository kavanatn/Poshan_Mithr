"""
Nutrition calculation utilities
"""

from datetime import datetime, date
from typing import Tuple, List
from app.models import Gender, VegPreference, NutritionStatus


def calculate_age(birth_date: datetime) -> Tuple[int, int]:
    today = date.today()
    birth = birth_date.date() if isinstance(birth_date, datetime) else birth_date
    years = today.year - birth.year
    months = today.month - birth.month
    if months < 0:
        years -= 1
        months += 12
    return years, months


def calculate_bmi(height_cm: float, weight_kg: float) -> float:
    height_m = height_cm / 100
    bmi = weight_kg / (height_m**2)
    return round(bmi, 2)


def classify_bmi_status(
    bmi: float, age_years: int, gender: Gender
) -> Tuple[NutritionStatus, float]:
    if age_years < 2:
        if bmi < 14:
            return NutritionStatus.UNDERWEIGHT, 10
        elif bmi < 18:
            return NutritionStatus.HEALTHY, 50
        elif bmi < 20:
            return NutritionStatus.OVERWEIGHT, 85
        else:
            return NutritionStatus.OBESE, 95
    elif age_years < 5:
        if bmi < 13:
            return NutritionStatus.UNDERWEIGHT, 5
        elif bmi < 17:
            return NutritionStatus.HEALTHY, 50
        elif bmi < 19:
            return NutritionStatus.OVERWEIGHT, 85
        else:
            return NutritionStatus.OBESE, 95
    elif age_years < 12:
        if bmi < 15:
            return NutritionStatus.UNDERWEIGHT, 5
        elif bmi < 20:
            return NutritionStatus.HEALTHY, 50
        elif bmi < 23:
            return NutritionStatus.OVERWEIGHT, 85
        else:
            return NutritionStatus.OBESE, 95
    else:
        if bmi < 16:
            return NutritionStatus.UNDERWEIGHT, 5
        elif bmi < 23:
            return NutritionStatus.HEALTHY, 50
        elif bmi < 27:
            return NutritionStatus.OVERWEIGHT, 85
        else:
            return NutritionStatus.OBESE, 95


def identify_deficiencies(bmi_status: NutritionStatus, age_years: int) -> List[str]:
    deficiencies = []
    if bmi_status == NutritionStatus.UNDERWEIGHT:
        deficiencies.extend(
            [
                "Protein deficiency",
                "Iron deficiency",
                "Vitamin D deficiency",
                "Calcium deficiency",
                "Caloric insufficiency",
            ]
        )
    elif bmi_status in [NutritionStatus.OVERWEIGHT, NutritionStatus.OBESE]:
        deficiencies.extend(
            ["Micronutrient deficiency", "Fiber deficiency", "Healthy fat deficiency"]
        )
    if age_years < 2:
        deficiencies.append("Iron deficiency (common in toddlers)")
    elif age_years < 5:
        deficiencies.append("Vitamin A deficiency risk")
    elif age_years >= 12:
        deficiencies.append("Zinc deficiency (growth spurts)")
    return deficiencies


def generate_diet_recommendation(
    bmi_status: NutritionStatus,
    age_years: int,
    gender: Gender,
    veg_preference: VegPreference,
    deficiencies: List[str],
) -> str:
    recommendations = []
    if veg_preference == VegPreference.VEG:
        recommendations.extend(
            [
                "BREAKFAST: Ragi porridge with ghee, Poha with vegetables",
                "LUNCH: Dal-chawal with ghee, Vegetable sabzi, Roti with paneer",
                "DINNER: Light dal with roti, Vegetable soup, Curd rice",
                "SNACKS: Seasonal fruits, Sprouted moong, Homemade mathri",
            ]
        )
    else:
        recommendations.extend(
            [
                "BREAKFAST: Egg paratha, Upma with vegetables",
                "LUNCH: Dal-chawal, Chicken/fish curry (2-3 times/week), Egg curry",
                "DINNER: Light dal, Fish/chicken soup, Curd rice",
                "SNACKS: Seasonal fruits, Boiled eggs, Homemade snacks",
            ]
        )
    if bmi_status == NutritionStatus.UNDERWEIGHT:
        recommendations.extend(
            [
                "SPECIAL: Increase ghee/oil intake, Add banana and dates",
                "FREQUENCY: 6-7 small meals per day",
                "ADDITIONS: Groundnut chikki, Sesame laddu",
            ]
        )
    elif bmi_status in [NutritionStatus.OVERWEIGHT, NutritionStatus.OBESE]:
        recommendations.extend(
            [
                "SPECIAL: Reduce oil intake, Increase vegetables",
                "AVOID: Fried foods and sweets",
                "FOCUS: More fiber-rich foods, Physical activity",
            ]
        )
    if "Iron deficiency" in str(deficiencies):
        recommendations.append(
            "IRON: Include jaggery, green leafy vegetables, sprouted legumes"
        )
    if "Calcium deficiency" in str(deficiencies):
        recommendations.append("CALCIUM: Ensure milk/curd intake, sesame seeds, ragi")
    return "\n".join(recommendations)
