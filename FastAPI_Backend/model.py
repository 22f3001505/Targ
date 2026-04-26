import numpy as np
import re
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer

# The 9 nutritional feature columns used by the ML model
NUTRITION_COLS = [
    "Calories", "FatContent", "SaturatedFatContent",
    "CholesterolContent", "SodiumContent", "CarbohydrateContent",
    "FiberContent", "SugarContent", "ProteinContent"
]

def scaling(dataframe):
    scaler=StandardScaler()
    prep_data=scaler.fit_transform(dataframe[NUTRITION_COLS].to_numpy())
    return prep_data,scaler

def nn_predictor(prep_data):
    neigh = NearestNeighbors(metric='cosine',algorithm='brute')
    neigh.fit(prep_data)
    return neigh

def build_pipeline(neigh,scaler,params):
    transformer = FunctionTransformer(neigh.kneighbors,kw_args=params)
    pipeline=Pipeline([('std_scaler',scaler),('NN',transformer)])
    return pipeline

def extract_data(dataframe,ingredients):
    extracted_data=dataframe.copy()
    extracted_data=extract_ingredient_filtered_data(extracted_data,ingredients)
    return extracted_data
    
def extract_ingredient_filtered_data(dataframe,ingredients):
    extracted_data=dataframe.copy()
    regex_string=''.join(map(lambda x:f'(?=.*{re.escape(x)})',ingredients))
    extracted_data=extracted_data[extracted_data['RecipeIngredientParts'].str.contains(regex_string,regex=True,flags=re.IGNORECASE)]
    return extracted_data

def apply_pipeline(pipeline,_input,extracted_data):
    _input=np.array(_input).reshape(1,-1)
    return extracted_data.iloc[pipeline.transform(_input)[0]]

def recommend(dataframe,_input,ingredients=[],params={'n_neighbors':5,'return_distance':False}):
        extracted_data=extract_data(dataframe,ingredients)
        if extracted_data.shape[0]>=params['n_neighbors']:
            prep_data,scaler=scaling(extracted_data)
            neigh=nn_predictor(prep_data)
            pipeline=build_pipeline(neigh,scaler,params)
            return apply_pipeline(pipeline,_input,extracted_data)
        else:
            return None

def extract_quoted_strings(s):
    # Find all the strings inside double quotes
    strings = re.findall(r'"([^"]*)"', s)
    # Join the strings with 'and'
    return strings

def output_recommended_recipes(dataframe):
    if dataframe is not None:
        output=dataframe.copy()
        output=output.to_dict("records")
        for recipe in output:
            recipe['RecipeIngredientParts']=extract_quoted_strings(recipe['RecipeIngredientParts'])
            recipe['RecipeInstructions']=extract_quoted_strings(recipe['RecipeInstructions'])
    else:
        output=None
    return output


# ========================
# HEALTH ANALYSIS FUNCTIONS
# ========================

def calculate_bmi(weight: float, height_cm: float) -> float:
    """
    Calculate Body Mass Index (BMI)
    BMI = weight (kg) / (height (m))²
    """
    height_m = height_cm / 100
    return round(weight / (height_m ** 2), 2)


def bmi_category(bmi: float) -> dict:
    """
    Categorize BMI value and return category with brand-consistent color hex
    """
    if bmi < 18.5:
        return {"category": "Underweight", "color": "#FFA726", "status": "Below healthy range"}
    elif bmi < 25:
        return {"category": "Normal", "color": "#4CAF50", "status": "Healthy weight"}
    elif bmi < 30:
        return {"category": "Overweight", "color": "#FF7043", "status": "Above healthy range"}
    else:
        return {"category": "Obese", "color": "#EF5350", "status": "High health risk"}


def workout_plan(category: str) -> dict:
    """
    Generate workout recommendations based on BMI category
    Rule-based system for explainability and safety
    """
    plans = {
        "Underweight": {
            "focus": "Strength & Muscle Building",
            "exercises": [
                "Weight training (3-4 days/week)",
                "Resistance exercises",
                "Compound movements (squats, deadlifts)",
                "Progressive overload training",
                "Limited cardio (light walking)"
            ],
            "tips": "Focus on caloric surplus with protein-rich diet. Rest adequately between workouts."
        },
        "Normal": {
            "focus": "Balanced Fitness",
            "exercises": [
                "Mix of cardio and strength (4-5 days/week)",
                "HIIT training (2 days/week)",
                "Flexibility exercises (yoga, stretching)",
                "Sports activities",
                "Core strengthening"
            ],
            "tips": "Maintain current weight with balanced nutrition. Focus on overall fitness and endurance."
        },
        "Overweight": {
            "focus": "Cardio & Fat Burning",
            "exercises": [
                "Moderate cardio (4-5 days/week)",
                "Brisk walking (30-45 min)",
                "Swimming or cycling",
                "Light strength training",
                "Interval training"
            ],
            "tips": "Create caloric deficit through exercise and diet. Start slow and gradually increase intensity."
        },
        "Obese": {
            "focus": "Low-Impact Cardio",
            "exercises": [
                "Walking (start with 15-20 min)",
                "Water aerobics",
                "Stationary cycling",
                "Chair exercises",
                "Gentle stretching"
            ],
            "tips": "Consult a healthcare provider before starting. Focus on consistency over intensity. Prioritize joint-friendly exercises."
        }
    }
    return plans.get(category, plans["Normal"])


def calculate_bmr(weight: float, height_cm: float, age: int, gender: str) -> float:
    """
    Calculate Basal Metabolic Rate using Mifflin-St Jeor Equation
    Male: BMR = 10W + 6.25H − 5A + 5
    Female: BMR = 10W + 6.25H − 5A − 161
    """
    if gender.lower() == "male":
        bmr = 10 * weight + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height_cm - 5 * age - 161
    return round(bmr, 2)


def calculate_daily_calories(bmr: float, activity_level: str) -> dict:
    """
    Calculate daily calorie needs based on BMR and activity level
    Uses TDEE (Total Daily Energy Expenditure) formula
    """
    activity_multipliers = {
        "sedentary": 1.2,           # Little/no exercise
        "light": 1.375,             # Light exercise 1-3 days/week
        "moderate": 1.55,           # Moderate exercise 3-5 days/week
        "active": 1.725,            # Very active 6-7 days/week
        "extra_active": 1.9         # Extra active (physical job)
    }
    
    multiplier = activity_multipliers.get(activity_level.lower(), 1.55)
    maintenance_calories = round(bmr * multiplier)
    
    return {
        "maintenance": maintenance_calories,
        "mild_loss": round(maintenance_calories * 0.9),      # -0.25 kg/week
        "weight_loss": round(maintenance_calories * 0.8),    # -0.5 kg/week
        "extreme_loss": round(maintenance_calories * 0.6),   # -1 kg/week
        "mild_gain": round(maintenance_calories * 1.1),      # +0.25 kg/week
        "weight_gain": round(maintenance_calories * 1.2)     # +0.5 kg/week
    }
