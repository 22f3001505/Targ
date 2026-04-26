"""
TARG - Database Models
Persistent storage for Users, HealthRecords, SavedMeals, WorkoutHistory
"""
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


# ═══════════════════════════════════════════
# USER — Core identity
# ═══════════════════════════════════════════
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(200), default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    health_records = relationship("HealthRecord", back_populates="user", cascade="all, delete-orphan")
    saved_meals = relationship("SavedMeal", back_populates="user", cascade="all, delete-orphan")
    workout_history = relationship("WorkoutLog", back_populates="user", cascade="all, delete-orphan")
    meal_plans = relationship("MealPlan", back_populates="user", cascade="all, delete-orphan")


# ═══════════════════════════════════════════
# HEALTH RECORD — BMI, BMR, calorie analysis snapshots
# ═══════════════════════════════════════════
class HealthRecord(Base):
    __tablename__ = "health_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Input
    age = Column(Integer)
    height = Column(Float)
    weight = Column(Float)
    gender = Column(String(10))
    activity_level = Column(String(20))

    # Computed
    bmi = Column(Float)
    bmi_category = Column(String(20))
    bmr = Column(Float)
    maintenance_calories = Column(Integer)

    recorded_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="health_records")


# ═══════════════════════════════════════════
# SAVED MEAL — User bookmarked recipes
# ═══════════════════════════════════════════
class SavedMeal(Base):
    __tablename__ = "saved_meals"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    meal_name = Column(String(300), nullable=False)
    meal_type = Column(String(20), default="other")  # breakfast, lunch, dinner, snack
    calories = Column(Float, default=0)
    protein = Column(Float, default=0)
    carbs = Column(Float, default=0)
    fat = Column(Float, default=0)
    fiber = Column(Float, default=0)
    recipe_data = Column(JSON, nullable=True)  # Full recipe JSON from API

    saved_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="saved_meals")


# ═══════════════════════════════════════════
# WORKOUT LOG — Completed workouts
# ═══════════════════════════════════════════
class WorkoutLog(Base):
    __tablename__ = "workout_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    workout_focus = Column(String(100))
    exercises_completed = Column(JSON)  # List of exercises done
    duration_minutes = Column(Integer, default=0)
    calories_burned = Column(Integer, default=0)
    notes = Column(Text, default="")

    logged_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="workout_history")


# ═══════════════════════════════════════════
# MEAL PLAN — Weekly meal planning persistence
# ═══════════════════════════════════════════
class MealPlan(Base):
    __tablename__ = "meal_plans"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    plan_data = Column(JSON, nullable=False)  # Full weekly plan as JSON
    week_start = Column(String(20), nullable=True)  # ISO date of week start

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="meal_plans")
