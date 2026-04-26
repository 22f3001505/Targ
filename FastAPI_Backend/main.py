"""
TARG - Production API
FastAPI Backend with Auth, Database, ML Recommendations, and Health Analysis
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Annotated, Any, List, Optional
from datetime import datetime
from pathlib import Path
import os
import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session

# Internal modules
from model import (
    recommend, output_recommended_recipes,
    calculate_bmi, bmi_category, workout_plan,
    calculate_bmr, calculate_daily_calories
)
from database import get_db, init_db
from models_db import User, HealthRecord, SavedMeal, WorkoutLog, MealPlan
from auth import (
    SignupRequest, LoginRequest, TokenResponse,
    signup_user, login_user, get_current_user, require_auth,
    create_access_token
)
from exercises_db import (
    EXERCISE_DATABASE, EXERCISE_CATEGORIES,
    calculate_calories_burned
)


# ═══════════════════════════════════════════════════
# DATASET (memory-optimized for Render free tier 512MB)
# ═══════════════════════════════════════════════════
APP_VERSION = "7.2.4"
DATASET_DIR = Path(__file__).resolve().parent.parent / "Data"
DATASET_LITE = DATASET_DIR / "dataset_lite.csv"
DATASET_FULL = DATASET_DIR / "dataset.csv"

def _load_dataset() -> pd.DataFrame:
    """
    Load dataset with memory optimization for 512MB environments.
    Priority: dataset_lite.csv (pre-sampled 50K) > dataset.csv (full 375K, sampled on load)
    """
    float_cols = ["Calories", "FatContent", "SaturatedFatContent",
                  "CholesterolContent", "SodiumContent", "CarbohydrateContent",
                  "FiberContent", "SugarContent", "ProteinContent"]

    if DATASET_LITE.exists():
        print("📊 Loading lite dataset (pre-sampled 50K)...")
        df = pd.read_csv(DATASET_LITE)
        for col in float_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype('float32')
        print(f"✅ Dataset ready: {len(df)} recipes ({df.memory_usage(deep=True).sum() / 1024 / 1024:.1f} MB)")
        return df

    # Fallback: load full dataset and sample
    print("📊 Loading full dataset (sampling 50K)...")
    full = pd.read_csv(DATASET_FULL, compression='gzip')
    sample_size = min(50_000, len(full))
    df = full.sample(n=sample_size, random_state=42).reset_index(drop=True)
    del full
    for col in float_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype('float32')
    print(f"✅ Dataset ready: {len(df)} recipes ({df.memory_usage(deep=True).sum() / 1024 / 1024:.1f} MB)")
    return df

dataset = _load_dataset()


# ═══════════════════════════════════════════════════
# APP LIFESPAN (replaces deprecated on_event)
# ═══════════════════════════════════════════════════
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    print("✅ Database initialized")
    print(f"✅ Dataset loaded: {len(dataset)} recipes")
    yield  # App runs here
    print("🛑 Shutting down TARG API")


# ═══════════════════════════════════════════════════
# APP INIT
# ═══════════════════════════════════════════════════
app = FastAPI(
    title="TARG - Health & Nutrition API",
    description="ML-powered diet and workout recommendations with auth and persistent data",
    version=APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

def _cors_origins() -> list[str]:
    raw = os.getenv("CORS_ORIGINS", "*")
    return [origin.strip() for origin in raw.split(",") if origin.strip()]

_allowed_origins = _cors_origins()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=(
        os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"
        and "*" not in _allowed_origins
    ),
    allow_methods=["*"],
    allow_headers=["*"],
)


# ═══════════════════════════════════════════════════
# SCHEMAS
# ═══════════════════════════════════════════════════

class PredictionParams(BaseModel):
    n_neighbors: int = Field(5, ge=1, le=25)
    return_distance: bool = False

class PredictionIn(BaseModel):
    nutrition_input: Annotated[List[float], Field(min_length=9, max_length=9)]
    ingredients: List[str] = []
    params: Optional[PredictionParams] = None

class Recipe(BaseModel):
    Name: str
    CookTime: Any = ""
    PrepTime: Any = ""
    TotalTime: Any = ""
    RecipeIngredientParts: Any = []
    Calories: float = 0
    FatContent: float = 0
    SaturatedFatContent: float = 0
    CholesterolContent: float = 0
    SodiumContent: float = 0
    CarbohydrateContent: float = 0
    FiberContent: float = 0
    SugarContent: float = 0
    ProteinContent: float = 0
    RecipeInstructions: Any = []

class PredictionOut(BaseModel):
    output: Optional[List[Recipe]] = None

class HealthInput(BaseModel):
    age: int
    height: float
    weight: float
    gender: str
    activity_level: str = "moderate"

    @field_validator("age")
    @classmethod
    def validate_age(cls, v):
        if not 1 <= v <= 120:
            raise ValueError("Age must be between 1 and 120")
        return v

    @field_validator("height")
    @classmethod
    def validate_height(cls, v):
        if not 50 <= v <= 300:
            raise ValueError("Height must be between 50 and 300 cm")
        return v

    @field_validator("weight")
    @classmethod
    def validate_weight(cls, v):
        if not 10 <= v <= 500:
            raise ValueError("Weight must be between 10 and 500 kg")
        return v

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v):
        if v.lower() not in ["male", "female"]:
            raise ValueError("Gender must be 'male' or 'female'")
        return v.lower()

    @field_validator("activity_level")
    @classmethod
    def validate_activity(cls, v):
        valid = ["sedentary", "light", "moderate", "active", "extra_active"]
        if v.lower() not in valid:
            raise ValueError(f"Activity must be one of: {valid}")
        return v.lower()

class HealthOutput(BaseModel):
    bmi: float
    bmi_category: dict
    bmr: float
    daily_calories: dict
    workout_plan: dict

class SaveMealRequest(BaseModel):
    meal_name: str = Field(..., min_length=1, max_length=300)
    meal_type: str = Field("other", max_length=20)
    calories: float = Field(0, ge=0, le=10000)
    protein: float = Field(0, ge=0, le=1000)
    carbs: float = Field(0, ge=0, le=1000)
    fat: float = Field(0, ge=0, le=1000)
    fiber: float = Field(0, ge=0, le=500)
    recipe_data: Optional[dict] = None

    @field_validator("meal_name")
    @classmethod
    def clean_meal_name(cls, value: str) -> str:
        value = " ".join(value.strip().split())
        if not value:
            raise ValueError("Meal name is required")
        return value

    @field_validator("meal_type")
    @classmethod
    def clean_meal_type(cls, value: str) -> str:
        value = value.strip().lower() or "other"
        allowed = {"breakfast", "lunch", "dinner", "snack", "saved", "tracked", "water", "other"}
        if value not in allowed:
            raise ValueError(f"Meal type must be one of: {sorted(allowed)}")
        return value

class LogWorkoutRequest(BaseModel):
    workout_focus: str = Field(..., min_length=1, max_length=100)
    exercises_completed: List[str] = Field(default_factory=list, max_length=50)
    duration_minutes: int = Field(0, ge=0, le=1440)
    calories_burned: int = Field(0, ge=0, le=5000)
    notes: str = Field("", max_length=2000)

    @field_validator("workout_focus")
    @classmethod
    def clean_workout_focus(cls, value: str) -> str:
        value = " ".join(value.strip().split())
        if not value:
            raise ValueError("Workout focus is required")
        return value

    @field_validator("notes")
    @classmethod
    def clean_notes(cls, value: str) -> str:
        return " ".join(value.strip().split())

class SaveMealPlanRequest(BaseModel):
    plan_data: dict = Field(..., min_length=1)  # {"Monday": {"breakfast": "...", "lunch": "...", "dinner": "..."}, ...}
    week_start: Optional[str] = Field(None, max_length=20)  # ISO date string

class WaterIntakeRequest(BaseModel):
    glasses: int = Field(0, ge=0, le=40)
    ml: int = Field(0, ge=0, le=10000)

    @model_validator(mode="after")
    def validate_some_water(self):
        if self.glasses == 0 and self.ml == 0:
            raise ValueError("Provide glasses or ml to log water")
        return self

class FoodSearchResult(BaseModel):
    name: str
    calories: float = 0
    protein: float = 0
    carbs: float = 0
    fat: float = 0
    fiber: float = 0
    serving: str = "100g"


# ═══════════════════════════════════════════════════
# PUBLIC ENDPOINTS
# ═══════════════════════════════════════════════════

@app.get("/")
def home():
    return {
        "health_check": "OK",
        "api_name": "TARG - Health & Nutrition API",
        "version": APP_VERSION,
        "dataset_size": len(dataset),
        "exercise_count": len(EXERCISE_DATABASE),
        "endpoints": {
            "public": ["/", "/health/", "/predict/", "/exercises", "/exercises/calories", "/foods/search"],
            "auth": ["/auth/signup", "/auth/login", "/auth/me", "/auth/refresh"],
            "protected": ["/user/health-records", "/user/health-records/trend", "/user/meals", "/user/workouts", "/user/meal-plan", "/user/stats"]
        }
    }


@app.get("/ready")
def readiness(db: Session = Depends(get_db)):
    """Readiness probe that verifies app, dataset, and database access."""
    db.execute(text("SELECT 1"))
    return {
        "status": "ready",
        "database": "ok",
        "dataset_size": len(dataset),
        "exercise_count": len(EXERCISE_DATABASE),
        "version": APP_VERSION,
    }


@app.post("/predict/", response_model=PredictionOut)
def predict(prediction_input: PredictionIn):
    """Get diet recommendations based on nutritional targets."""
    params = prediction_input.params.model_dump() if prediction_input.params else {"n_neighbors": 5, "return_distance": False}
    recommendation_dataframe = recommend(
        dataset,
        prediction_input.nutrition_input,
        prediction_input.ingredients,
        params
    )
    output = output_recommended_recipes(recommendation_dataframe)
    return {"output": output}


@app.post("/health/", response_model=HealthOutput)
def health_analysis(
    health_input: HealthInput,
    user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Comprehensive health analysis.
    If authenticated, automatically saves to user's health records.
    """
    bmi = calculate_bmi(health_input.weight, health_input.height)
    category = bmi_category(bmi)
    bmr = calculate_bmr(health_input.weight, health_input.height, health_input.age, health_input.gender)
    calories = calculate_daily_calories(bmr, health_input.activity_level)
    workout = workout_plan(category["category"])

    # Auto-save for authenticated users
    if user:
        record = HealthRecord(
            user_id=user.id,
            age=health_input.age,
            height=health_input.height,
            weight=health_input.weight,
            gender=health_input.gender,
            activity_level=health_input.activity_level,
            bmi=bmi,
            bmi_category=category["category"],
            bmr=bmr,
            maintenance_calories=calories["maintenance"]
        )
        db.add(record)
        db.commit()

    return {
        "bmi": bmi,
        "bmi_category": category,
        "bmr": bmr,
        "daily_calories": calories,
        "workout_plan": workout
    }


# ═══════════════════════════════════════════════════
# AUTH ENDPOINTS
# ═══════════════════════════════════════════════════

@app.post("/auth/signup", response_model=TokenResponse)
def signup(req: SignupRequest, db: Session = Depends(get_db)):
    """Register a new user account."""
    return signup_user(req, db)


@app.post("/auth/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """Login and receive JWT token."""
    return login_user(req, db)


@app.get("/auth/me")
def get_profile(user: User = Depends(require_auth)):
    """Get current user profile (requires auth)."""
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "full_name": user.full_name,
        "created_at": str(user.created_at)
    }


@app.post("/auth/refresh", response_model=TokenResponse)
def refresh_token(user: User = Depends(require_auth)):
    """Issue a fresh JWT for the current authenticated user."""
    token = create_access_token({"user_id": user.id, "username": user.username})
    return TokenResponse(
        access_token=token,
        user={"id": user.id, "email": user.email, "username": user.username, "full_name": user.full_name}
    )


# ═══════════════════════════════════════════════════
# PROTECTED ENDPOINTS (Require Auth)
# ═══════════════════════════════════════════════════

# ─── Health Records ───
@app.get("/user/health-records")
def get_health_records(
    user: User = Depends(require_auth),
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=50)
):
    """Get user's health analysis history."""
    records = (
        db.query(HealthRecord)
        .filter(HealthRecord.user_id == user.id)
        .order_by(HealthRecord.recorded_at.desc())
        .limit(limit)
        .all()
    )
    return [{
        "id": r.id,
        "bmi": r.bmi,
        "bmi_category": r.bmi_category,
        "bmr": r.bmr,
        "maintenance_calories": r.maintenance_calories,
        "weight": r.weight,
        "height": r.height,
        "recorded_at": str(r.recorded_at)
    } for r in records]


# ─── Saved Meals ───
@app.post("/user/meals")
def save_meal(
    req: SaveMealRequest,
    user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Save a meal to user's collection."""
    meal = SavedMeal(
        user_id=user.id,
        meal_name=req.meal_name,
        meal_type=req.meal_type,
        calories=req.calories,
        protein=req.protein,
        carbs=req.carbs,
        fat=req.fat,
        fiber=req.fiber,
        recipe_data=req.recipe_data
    )
    db.add(meal)
    db.commit()
    return {"message": f"Saved: {req.meal_name}", "meal_id": meal.id}


@app.get("/user/meals")
def get_saved_meals(
    user: User = Depends(require_auth),
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
    include_water: bool = Query(False, description="Include internal water tracker rows")
):
    """Get user's saved meals."""
    query = (
        db.query(SavedMeal)
        .filter(SavedMeal.user_id == user.id)
    )
    if not include_water:
        query = query.filter(SavedMeal.meal_type != "water")

    meals = query.order_by(SavedMeal.saved_at.desc()).limit(limit).all()
    return [{
        "id": m.id,
        "meal_name": m.meal_name,
        "meal_type": m.meal_type,
        "calories": m.calories,
        "protein": m.protein,
        "carbs": m.carbs,
        "fat": m.fat,
        "fiber": m.fiber,
        "saved_at": str(m.saved_at),
        "created_at": str(m.saved_at)
    } for m in meals]


@app.delete("/user/meals/clear")
def clear_meals(
    user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Clear all tracked meals for the user (today's macro tracker reset)."""
    today_start = datetime.combine(datetime.utcnow().date(), datetime.min.time())
    deleted = (
        db.query(SavedMeal)
        .filter(
            SavedMeal.user_id == user.id,
            SavedMeal.meal_type == "tracked",
            SavedMeal.saved_at >= today_start
        )
        .delete()
    )
    db.commit()
    return {"message": f"Cleared {deleted} tracked meals"}


@app.delete("/user/meals/{meal_id}")
def delete_meal(
    meal_id: int,
    user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Delete a saved meal."""
    meal = db.query(SavedMeal).filter(
        SavedMeal.id == meal_id,
        SavedMeal.user_id == user.id
    ).first()
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")
    db.delete(meal)
    db.commit()
    return {"message": "Meal deleted"}


# ─── Workout Logs ───
@app.post("/user/workouts")
def log_workout(
    req: LogWorkoutRequest,
    user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Log a completed workout."""
    log = WorkoutLog(
        user_id=user.id,
        workout_focus=req.workout_focus,
        exercises_completed=req.exercises_completed,
        duration_minutes=req.duration_minutes,
        calories_burned=req.calories_burned,
        notes=req.notes
    )
    db.add(log)
    db.commit()
    return {"message": "Workout logged", "log_id": log.id}


@app.get("/user/workouts")
def get_workout_logs(
    user: User = Depends(require_auth),
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=50)
):
    """Get user's workout history."""
    logs = (
        db.query(WorkoutLog)
        .filter(WorkoutLog.user_id == user.id)
        .order_by(WorkoutLog.logged_at.desc())
        .limit(limit)
        .all()
    )
    return [{
        "id": l.id,
        "workout_focus": l.workout_focus,
        "exercises_completed": l.exercises_completed,
        "duration_minutes": l.duration_minutes,
        "calories_burned": l.calories_burned,
        "notes": l.notes,
        "logged_at": str(l.logged_at)
    } for l in logs]


# ─── User Stats ───
@app.get("/user/stats")
def get_user_stats(
    user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Get aggregated user statistics."""
    health_count = db.query(HealthRecord).filter(HealthRecord.user_id == user.id).count()
    meal_count = (
        db.query(SavedMeal)
        .filter(SavedMeal.user_id == user.id, SavedMeal.meal_type != "water")
        .count()
    )
    workout_count = db.query(WorkoutLog).filter(WorkoutLog.user_id == user.id).count()

    latest_health = (
        db.query(HealthRecord)
        .filter(HealthRecord.user_id == user.id)
        .order_by(HealthRecord.recorded_at.desc())
        .first()
    )

    return {
        "total_health_analyses": health_count,
        "total_saved_meals": meal_count,
        "total_workouts": workout_count,
        "latest_bmi": latest_health.bmi if latest_health else None,
        "latest_calories": latest_health.maintenance_calories if latest_health else None,
        "member_since": str(user.created_at)
    }


# ─── Meal Plans ───
@app.post("/user/meal-plan")
def save_meal_plan(
    req: SaveMealPlanRequest,
    user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Save or update a weekly meal plan."""
    # Upsert: delete old plan for this week, save new one
    existing = (
        db.query(MealPlan)
        .filter(MealPlan.user_id == user.id)
        .order_by(MealPlan.created_at.desc())
        .first()
    )
    if existing:
        existing.plan_data = req.plan_data
        existing.week_start = req.week_start
        existing.created_at = datetime.utcnow()
    else:
        plan = MealPlan(
            user_id=user.id,
            plan_data=req.plan_data,
            week_start=req.week_start
        )
        db.add(plan)
    db.commit()
    return {"message": "Meal plan saved"}


@app.get("/user/meal-plan")
def get_meal_plan(
    user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Get the user's latest meal plan."""
    plan = (
        db.query(MealPlan)
        .filter(MealPlan.user_id == user.id)
        .order_by(MealPlan.created_at.desc())
        .first()
    )
    if not plan:
        return {"plan_data": None}
    return {
        "plan_data": plan.plan_data,
        "week_start": plan.week_start,
        "created_at": str(plan.created_at)
    }


# ─── Exercise Database ───
@app.get("/exercises")
def list_exercises(
    category: Optional[str] = Query(None, description="Filter by category"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty")
):
    """Get exercise database with MET values. Optionally filter by category or difficulty."""
    results = EXERCISE_DATABASE
    if category:
        results = [e for e in results if e["category"].lower() == category.lower()]
    if difficulty:
        results = [e for e in results if e["difficulty"].lower() == difficulty.lower()]
    return {
        "total": len(results),
        "categories": EXERCISE_CATEGORIES,
        "exercises": results
    }


class CalorieEstimateRequest(BaseModel):
    exercise_name: str = Field(..., min_length=1, max_length=120)
    weight_kg: float = Field(..., ge=10, le=500)
    duration_minutes: int = Field(..., ge=1, le=1440)

    @field_validator("exercise_name")
    @classmethod
    def clean_exercise_name(cls, value: str) -> str:
        value = " ".join(value.strip().split())
        if not value:
            raise ValueError("Exercise name is required")
        return value


@app.post("/exercises/calories")
def estimate_calories(req: CalorieEstimateRequest):
    """Estimate calories burned for a specific exercise using MET formula."""
    match = next((e for e in EXERCISE_DATABASE if e["name"].lower() == req.exercise_name.lower()), None)
    met = match["met"] if match else 5.0
    calories = calculate_calories_burned(met, req.weight_kg, req.duration_minutes)
    return {
        "exercise": req.exercise_name,
        "met": met,
        "weight_kg": req.weight_kg,
        "duration_minutes": req.duration_minutes,
        "calories_burned": calories,
        "source": "Compendium of Physical Activities" if match else "Default estimate"
    }


# ─── Health Trend ───
@app.get("/user/health-records/trend")
def get_health_trend(
    user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Get user's health metrics over time for charting."""
    records = (
        db.query(HealthRecord)
        .filter(HealthRecord.user_id == user.id)
        .order_by(HealthRecord.recorded_at.asc())
        .limit(100)
        .all()
    )
    return {
        "total": len(records),
        "data": [{
            "date": str(r.recorded_at)[:10],
            "bmi": r.bmi,
            "weight": r.weight,
            "bmr": r.bmr,
            "calories": r.maintenance_calories,
            "category": r.bmi_category
        } for r in records]
    }


# ═══════════════════════════════════════════════════
# FOOD NUTRITION DATABASE (v7.1 — memory optimized)
# ═══════════════════════════════════════════════════

_food_nutrition_db = []

def _build_food_db():
    """Build food lookup from already-loaded dataset (no extra sampling needed)."""
    global _food_nutrition_db
    if _food_nutrition_db:
        return
    try:
        seen = set()
        for _, row in dataset.iterrows():
            name = str(row.get("Name", "")).strip()
            if name and name.lower() not in seen and len(name) < 80:
                seen.add(name.lower())
                _food_nutrition_db.append({
                    "name": name,
                    "calories": round(float(row.get("Calories", 0)), 1),
                    "protein": round(float(row.get("ProteinContent", 0)), 1),
                    "carbs": round(float(row.get("CarbohydrateContent", 0)), 1),
                    "fat": round(float(row.get("FatContent", 0)), 1),
                    "fiber": round(float(row.get("FiberContent", 0)), 1),
                    "serving": "1 serving"
                })
        print(f"✅ Food DB: {len(_food_nutrition_db)} unique items")
    except Exception as exc:
        print(f"⚠️ Food nutrition index unavailable: {exc}")

_build_food_db()


@app.get("/foods/search")
def search_foods(q: str = Query(..., min_length=2, description="Search query"), limit: int = Query(20, ge=1, le=50)):
    """Search food items for nutrition data. Uses the recipe dataset as a real food database."""
    query = q.strip().lower()
    results = [f for f in _food_nutrition_db if query in f["name"].lower()][:limit]
    return {
        "query": q,
        "total": len(results),
        "foods": results
    }


@app.get("/foods/popular")
def popular_foods(limit: int = Query(30, ge=1, le=50)):
    """Get popular food items for quick macro tracking."""
    # Return first N items as popular recommendations
    return {
        "total": min(limit, len(_food_nutrition_db)),
        "foods": _food_nutrition_db[:limit]
    }


# ═══════════════════════════════════════════════════
# WATER INTAKE (v7.0)
# ═══════════════════════════════════════════════════

@app.post("/user/water")
def log_water(
    req: WaterIntakeRequest,
    user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Log water intake for today."""
    # Store as a special meal type for simplicity
    today_start = datetime.combine(datetime.utcnow().date(), datetime.min.time())
    
    # Check if there's already a water entry today
    existing = (
        db.query(SavedMeal)
        .filter(
            SavedMeal.user_id == user.id,
            SavedMeal.meal_type == "water",
            SavedMeal.saved_at >= today_start
        )
        .first()
    )
    
    added_ml = req.ml + req.glasses * 250  # 250ml per glass
    
    if existing:
        new_total_ml = int(float(existing.calories)) + added_ml
        existing.calories = float(new_total_ml)
        existing.meal_name = f"{new_total_ml // 250} glasses"
    else:
        new_total_ml = added_ml
        water = SavedMeal(
            user_id=user.id,
            meal_name=f"{new_total_ml // 250} glasses",
            meal_type="water",
            calories=float(new_total_ml),
            protein=0, carbs=0, fat=0
        )
        db.add(water)

    db.commit()
    return {"message": "Water logged", "added_ml": added_ml, "total_ml": new_total_ml}


@app.get("/user/water")
def get_water(
    user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Get today's water intake."""
    today_start = datetime.combine(datetime.utcnow().date(), datetime.min.time())
    entry = (
        db.query(SavedMeal)
        .filter(
            SavedMeal.user_id == user.id,
            SavedMeal.meal_type == "water",
            SavedMeal.saved_at >= today_start
        )
        .first()
    )
    total_ml = int(float(entry.calories)) if entry else 0
    return {
        "total_ml": total_ml,
        "glasses": total_ml // 250,
        "goal_ml": 2500,
        "percent": min(100, round(total_ml / 2500 * 100))
    }
