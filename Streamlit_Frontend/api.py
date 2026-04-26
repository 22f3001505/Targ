"""
TARG API Client
Centralized API communication layer — ALL backend calls go through here.
"""
import os
import requests
from typing import Optional, Dict, Any, List

# Backend URL — use TARG_API_URL=http://backend:8080 inside Docker Compose.
BASE_URL = os.getenv("TARG_API_URL", "http://localhost:8080").rstrip("/")
REQUEST_TIMEOUT = 10


def _extract_error(response: requests.Response, default: str) -> str:
    try:
        detail = response.json().get("detail", default)
        if isinstance(detail, list) and detail:
            first = detail[0]
            if isinstance(first, dict):
                return first.get("msg", default)
        if isinstance(detail, str):
            return detail
    except ValueError:
        pass
    return default


def _auth_headers(auth_token: Optional[str] = None) -> Dict[str, str]:
    return {"Authorization": f"Bearer {auth_token}"} if auth_token else {}


def _protected_failure(response: requests.Response, default: str, fallback_data: Any = None) -> Dict[str, Any]:
    if response.status_code in (401, 403):
        return {
            "success": False,
            "error": "Your session expired. Please sign in again.",
            "auth_expired": True,
            "data": fallback_data,
        }
    return {"success": False, "error": _extract_error(response, default), "data": fallback_data}


class APIClient:
    """Centralized API client for all backend calls"""

    # ═══════════════════════════════════════════
    # AUTH
    # ═══════════════════════════════════════════
    @staticmethod
    def login(username: str, password: str) -> Dict[str, Any]:
        """Login with username/email and password."""
        try:
            response = requests.post(
                f"{BASE_URL}/auth/login",
                json={"username": username.strip(), "password": password},
                timeout=REQUEST_TIMEOUT
            )
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            message = "Invalid username/email or password" if response.status_code == 401 else _extract_error(response, "Login failed")
            return {"success": False, "error": message}
        except requests.exceptions.Timeout:
            return {"success": False, "error": "Login timed out. Please try again."}
        except requests.exceptions.ConnectionError:
            return {"success": False, "error": "Cannot connect to backend."}
        except requests.exceptions.RequestException as exc:
            return {"success": False, "error": str(exc)}

    @staticmethod
    def signup(email: str, username: str, password: str, full_name: str = "") -> Dict[str, Any]:
        """Create a new account."""
        try:
            response = requests.post(
                f"{BASE_URL}/auth/signup",
                json={
                    "email": email.strip(),
                    "username": username.strip(),
                    "password": password,
                    "full_name": full_name.strip()
                },
                timeout=REQUEST_TIMEOUT
            )
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            return {"success": False, "error": _extract_error(response, "Signup failed")}
        except requests.exceptions.Timeout:
            return {"success": False, "error": "Signup timed out. Please try again."}
        except requests.exceptions.ConnectionError:
            return {"success": False, "error": "Cannot connect to backend."}
        except requests.exceptions.RequestException as exc:
            return {"success": False, "error": str(exc)}
    
    # ═══════════════════════════════════════════
    # HEALTH ANALYSIS
    # ═══════════════════════════════════════════
    @staticmethod
    def health_analysis(age: int, height: float, weight: float, 
                       gender: str, activity_level: str, auth_token: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive health analysis (BMI, BMR, calories, workout plan)."""
        payload = {
            "age": age, "height": height, "weight": weight,
            "gender": gender, "activity_level": activity_level
        }
        headers = _auth_headers(auth_token)
        try:
            response = requests.post(f"{BASE_URL}/health/", json=payload, headers=headers, timeout=10)
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            return _protected_failure(response, f"API Error: {response.status_code}")
        except requests.exceptions.ConnectionError:
            return {"success": False, "error": "Backend not available", "use_fallback": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ═══════════════════════════════════════════
    # DIET / RECIPE RECOMMENDATIONS
    # ═══════════════════════════════════════════
    @staticmethod
    def diet_recommendation(nutrition_input: list, ingredients: list = None, k: int = 5) -> Dict[str, Any]:
        """Get ML-powered diet recommendations."""
        payload = {
            "nutrition_input": nutrition_input,
            "ingredients": ingredients or [],
            "params": {"n_neighbors": k, "return_distance": False}
        }
        try:
            response = requests.post(f"{BASE_URL}/predict/", json=payload, timeout=15)
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            return {"success": False, "error": f"API Error: {response.status_code}"}
        except requests.exceptions.ConnectionError:
            return {"success": False, "error": "Backend not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ═══════════════════════════════════════════
    # SAVED MEALS
    # ═══════════════════════════════════════════
    @staticmethod
    def save_meal(meal_name: str, calories: float, protein: float, carbs: float, fat: float,
                  meal_type: str = "saved", auth_token: str = None) -> Dict[str, Any]:
        """Save a meal/recipe to the user's collection."""
        if not auth_token:
            return {"success": False, "error": "Not authenticated"}
        try:
            response = requests.post(
                f"{BASE_URL}/user/meals",
                json={"meal_name": meal_name, "meal_type": meal_type,
                      "calories": calories, "protein": protein, "carbs": carbs, "fat": fat},
                headers={"Authorization": f"Bearer {auth_token}"},
                timeout=5
            )
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            return _protected_failure(response, "Could not save meal")
        except:
            return {"success": False, "error": "Connection failed"}
    
    @staticmethod
    def get_saved_meals(auth_token: str, meal_type: str = None, limit: int = 20) -> Dict[str, Any]:
        """Get user's saved meals."""
        if not auth_token:
            return {"success": False, "error": "Not authenticated", "data": []}
        try:
            response = requests.get(
                f"{BASE_URL}/user/meals",
                params={"limit": limit},
                headers={"Authorization": f"Bearer {auth_token}"},
                timeout=5
            )
            if response.status_code == 200:
                meals = response.json()
                if meal_type:
                    meals = [m for m in meals if m.get("meal_type") == meal_type]
                return {"success": True, "data": meals}
            return _protected_failure(response, "Could not load meals", [])
        except:
            return {"success": False, "data": []}
    
    @staticmethod
    def clear_tracked_meals(auth_token: str) -> Dict[str, Any]:
        """Clear today's tracked meals."""
        if not auth_token:
            return {"success": False, "error": "Not authenticated"}
        try:
            response = requests.delete(
                f"{BASE_URL}/user/meals/clear",
                headers={"Authorization": f"Bearer {auth_token}"},
                timeout=5
            )
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            return _protected_failure(response, "Could not clear meals")
        except requests.exceptions.Timeout:
            return {"success": False, "error": "Clear meals timed out. Please try again."}
        except requests.exceptions.ConnectionError:
            return {"success": False, "error": "Cannot connect to backend."}
        except requests.exceptions.RequestException as exc:
            return {"success": False, "error": str(exc)}
    
    # ═══════════════════════════════════════════
    # WORKOUT LOGS
    # ═══════════════════════════════════════════
    @staticmethod
    def log_workout(workout_focus: str, exercises: list, duration: int = 0,
                    calories_burned: int = 0, notes: str = "", auth_token: str = None) -> Dict[str, Any]:
        """Log a completed workout."""
        if not auth_token:
            return {"success": False, "error": "Not authenticated"}
        try:
            response = requests.post(
                f"{BASE_URL}/user/workouts",
                json={"workout_focus": workout_focus, "exercises_completed": exercises,
                      "duration_minutes": duration, "calories_burned": calories_burned, "notes": notes},
                headers={"Authorization": f"Bearer {auth_token}"},
                timeout=5
            )
            if response.status_code == 200:
                return {"success": True}
            return _protected_failure(response, "Could not log workout")
        except:
            return {"success": False, "error": "Connection failed"}
    
    @staticmethod
    def get_workout_history(auth_token: str, limit: int = 10) -> Dict[str, Any]:
        """Get user's workout history."""
        if not auth_token:
            return {"success": False, "error": "Not authenticated", "data": []}
        try:
            response = requests.get(
                f"{BASE_URL}/user/workouts",
                params={"limit": limit},
                headers={"Authorization": f"Bearer {auth_token}"},
                timeout=5
            )
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            return _protected_failure(response, "Could not load workouts", [])
        except:
            return {"success": False, "data": []}
    
    # ═══════════════════════════════════════════
    # MEAL PLANS
    # ═══════════════════════════════════════════
    @staticmethod
    def save_meal_plan(plan_data: dict, auth_token: str, week_start: str = None) -> Dict[str, Any]:
        """Save a weekly meal plan."""
        if not auth_token:
            return {"success": False, "error": "Not authenticated"}
        try:
            response = requests.post(
                f"{BASE_URL}/user/meal-plan",
                json={"plan_data": plan_data, "week_start": week_start},
                headers={"Authorization": f"Bearer {auth_token}"},
                timeout=5
            )
            if response.status_code == 200:
                return {"success": True}
            return _protected_failure(response, "Could not save meal plan")
        except:
            return {"success": False, "error": "Connection failed"}
    
    @staticmethod
    def get_meal_plan(auth_token: str) -> Dict[str, Any]:
        """Get the user's latest meal plan."""
        if not auth_token:
            return {"success": False, "error": "Not authenticated", "data": None}
        try:
            response = requests.get(
                f"{BASE_URL}/user/meal-plan",
                headers={"Authorization": f"Bearer {auth_token}"},
                timeout=5
            )
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            return _protected_failure(response, "Could not load meal plan", None)
        except:
            return {"success": False, "data": None}
    
    # ═══════════════════════════════════════════
    # EXERCISE DATABASE
    # ═══════════════════════════════════════════
    @staticmethod
    def get_exercises(category: str = None, difficulty: str = None) -> Dict[str, Any]:
        """Get exercises from the database, optionally filtered."""
        try:
            params = {}
            if category:
                params["category"] = category
            if difficulty:
                params["difficulty"] = difficulty
            response = requests.get(f"{BASE_URL}/exercises", params=params, timeout=5)
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            return {"success": False, "data": {"exercises": [], "categories": []}}
        except:
            return {"success": False, "data": {"exercises": [], "categories": []}}
    
    @staticmethod
    def estimate_exercise_calories(exercise_name: str, weight_kg: float, duration_minutes: int) -> Dict[str, Any]:
        """Estimate calories burned using MET formula via backend."""
        try:
            response = requests.post(
                f"{BASE_URL}/exercises/calories",
                json={"exercise_name": exercise_name, "weight_kg": weight_kg, "duration_minutes": duration_minutes},
                timeout=5
            )
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            return {"success": False, "data": None}
        except:
            return {"success": False, "data": None}
    
    # ═══════════════════════════════════════════
    # HEALTH TREND (Chart Data)
    # ═══════════════════════════════════════════
    @staticmethod
    def get_health_trend(auth_token: str) -> Dict[str, Any]:
        """Get health metrics over time for charting."""
        if not auth_token:
            return {"success": False, "error": "Not authenticated", "data": []}
        try:
            response = requests.get(
                f"{BASE_URL}/user/health-records/trend",
                headers={"Authorization": f"Bearer {auth_token}"},
                timeout=5
            )
            if response.status_code == 200:
                return {"success": True, "data": response.json().get("data", [])}
            return _protected_failure(response, "Could not load health trend", [])
        except:
            return {"success": False, "data": []}
    
    # ═══════════════════════════════════════════
    # USER STATS
    # ═══════════════════════════════════════════
    @staticmethod
    def get_user_stats(auth_token: str) -> Dict[str, Any]:
        """Get aggregated user statistics."""
        if not auth_token:
            return {"success": False, "error": "Not authenticated", "data": {}}
        try:
            response = requests.get(
                f"{BASE_URL}/user/stats",
                headers={"Authorization": f"Bearer {auth_token}"},
                timeout=5
            )
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            return _protected_failure(response, "Could not load stats", {})
        except:
            return {"success": False, "data": {}}
    
    # ═══════════════════════════════════════════
    # DELETE MEAL
    # ═══════════════════════════════════════════
    @staticmethod
    def delete_meal(meal_id: int, auth_token: str) -> Dict[str, Any]:
        """Delete a saved meal by ID."""
        if not auth_token:
            return {"success": False, "error": "Not authenticated"}
        try:
            response = requests.delete(
                f"{BASE_URL}/user/meals/{meal_id}",
                headers={"Authorization": f"Bearer {auth_token}"},
                timeout=5
            )
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            return _protected_failure(response, "Could not delete meal")
        except requests.exceptions.Timeout:
            return {"success": False, "error": "Delete meal timed out. Please try again."}
        except requests.exceptions.ConnectionError:
            return {"success": False, "error": "Cannot connect to backend."}
        except requests.exceptions.RequestException as exc:
            return {"success": False, "error": str(exc)}
    
    # ═══════════════════════════════════════════
    # FOOD NUTRITION SEARCH (v7.0)
    # ═══════════════════════════════════════════
    @staticmethod
    def search_foods(query: str, limit: int = 20) -> Dict[str, Any]:
        """Search food items for nutrition data."""
        try:
            response = requests.get(f"{BASE_URL}/foods/search", params={"q": query, "limit": limit}, timeout=5)
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            return {"success": False, "data": {"foods": []}}
        except:
            return {"success": False, "data": {"foods": []}}

    @staticmethod
    def get_popular_foods(limit: int = 30) -> Dict[str, Any]:
        """Get popular food items for quick macro tracking."""
        try:
            response = requests.get(f"{BASE_URL}/foods/popular", params={"limit": limit}, timeout=5)
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            return {"success": False, "data": {"foods": []}}
        except:
            return {"success": False, "data": {"foods": []}}

    # ═══════════════════════════════════════════
    # WATER INTAKE (v7.0)
    # ═══════════════════════════════════════════
    @staticmethod
    def log_water(glasses: int = 0, ml: int = 0, auth_token: str = None) -> Dict[str, Any]:
        """Log water intake."""
        if not auth_token:
            return {"success": False, "error": "Not authenticated"}
        try:
            response = requests.post(
                f"{BASE_URL}/user/water",
                json={"glasses": glasses, "ml": ml},
                headers={"Authorization": f"Bearer {auth_token}"},
                timeout=5
            )
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            return _protected_failure(response, "Could not log water")
        except:
            return {"success": False, "error": "Connection failed"}

    @staticmethod
    def set_water(glasses: int = 0, ml: int = 0, auth_token: str = None) -> Dict[str, Any]:
        """Set today's water intake exactly."""
        if not auth_token:
            return {"success": False, "error": "Not authenticated"}
        try:
            response = requests.put(
                f"{BASE_URL}/user/water",
                json={"glasses": glasses, "ml": ml},
                headers={"Authorization": f"Bearer {auth_token}"},
                timeout=5
            )
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            return _protected_failure(response, "Could not update water")
        except:
            return {"success": False, "error": "Connection failed"}

    @staticmethod
    def get_water(auth_token: str = None) -> Dict[str, Any]:
        """Get today's water intake."""
        if not auth_token:
            return {"success": False, "error": "Not authenticated", "data": {"total_ml": 0, "glasses": 0, "goal_ml": 2500, "percent": 0}}
        try:
            response = requests.get(
                f"{BASE_URL}/user/water",
                headers={"Authorization": f"Bearer {auth_token}"},
                timeout=5
            )
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            return _protected_failure(response, "Could not load water", {"total_ml": 0, "glasses": 0, "goal_ml": 2500, "percent": 0})
        except:
            return {"success": False, "data": {"total_ml": 0, "glasses": 0, "goal_ml": 2500, "percent": 0}}

    # ═══════════════════════════════════════════
    # HEALTH CHECK
    # ═══════════════════════════════════════════
    @staticmethod
    def check_health() -> Dict[str, Any]:
        """Check if backend is available and return status info."""
        try:
            response = requests.get(f"{BASE_URL}/", timeout=3)
            if response.status_code == 200:
                data = response.json()
                return {
                    "connected": True,
                    "version": data.get("version", "?"),
                    "dataset_size": data.get("dataset_size", 0),
                    "exercise_count": data.get("exercise_count", 0)
                }
            return {"connected": False}
        except:
            return {"connected": False}


# ═══════════════════════════════════════════════════
# Health calculation fallbacks (when backend unavailable)
# ═══════════════════════════════════════════════════
class HealthCalculator:
    """Local health calculations as fallback"""
    
    @staticmethod
    def calculate_bmi(weight: float, height: float) -> float:
        height_m = height / 100
        return round(weight / (height_m ** 2), 2)
    
    @staticmethod
    def get_bmi_category(bmi: float) -> Dict[str, str]:
        if bmi < 18.5:
            return {"category": "Underweight", "status": "Below healthy range", "color": "#FFA726"}
        elif bmi < 25:
            return {"category": "Normal", "status": "Healthy weight", "color": "#4CAF50"}
        elif bmi < 30:
            return {"category": "Overweight", "status": "Above healthy range", "color": "#FF7043"}
        else:
            return {"category": "Obese", "status": "High health risk", "color": "#EF5350"}
    
    @staticmethod
    def calculate_bmr(weight: float, height: float, age: int, gender: str) -> float:
        if gender.lower() == "male":
            return round(10 * weight + 6.25 * height - 5 * age + 5, 2)
        else:
            return round(10 * weight + 6.25 * height - 5 * age - 161, 2)
    
    @staticmethod
    def calculate_tdee(bmr: float, activity_level: str) -> Dict[str, int]:
        multipliers = {"sedentary": 1.2, "light": 1.375, "moderate": 1.55, "active": 1.725, "extra_active": 1.9}
        multiplier = multipliers.get(activity_level, 1.55)
        maintenance = round(bmr * multiplier)
        return {
            "maintenance": maintenance,
            "mild_loss": round(maintenance * 0.9),
            "weight_loss": round(maintenance * 0.8),
            "extreme_loss": round(maintenance * 0.6),
            "mild_gain": round(maintenance * 1.1),
            "weight_gain": round(maintenance * 1.2)
        }
    
    @staticmethod
    def get_workout_plan(category: str) -> Dict[str, Any]:
        plans = {
            "Underweight": {"focus": "Strength & Muscle Building", "exercises": ["Weight training (3-4 days/week)", "Compound movements (squats, deadlifts, bench press)", "Progressive overload training", "Resistance band exercises", "Limited cardio (15-20 min walking)"], "tips": "Focus on caloric surplus with protein-rich foods. Rest 48h between muscle groups."},
            "Normal": {"focus": "Balanced Fitness & Maintenance", "exercises": ["Mix of cardio and strength (4-5 days/week)", "HIIT training (2 sessions/week)", "Yoga or mobility work (2 days/week)", "Sports activities for fun", "Core strengthening exercises"], "tips": "Maintain balanced nutrition. Focus on endurance, strength, and flexibility."},
            "Overweight": {"focus": "Cardio & Fat Burning", "exercises": ["Brisk walking (30-45 min daily)", "Swimming or cycling (low impact)", "Light strength training", "Interval training", "Dance or aerobics classes"], "tips": "Create moderate caloric deficit. Start slow and increase intensity gradually."},
            "Obese": {"focus": "Low-Impact Movement", "exercises": ["Walking (start with 15-20 min)", "Water aerobics (joint-friendly)", "Stationary cycling", "Chair-based exercises", "Gentle stretching and mobility"], "tips": "Consult healthcare provider first. Focus on consistency over intensity."}
        }
        return plans.get(category, plans["Normal"])
