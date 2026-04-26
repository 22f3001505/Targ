"""Smoke-test the TARG backend and project wiring.

Run from the repository root:
    python3 scripts/verify_project.py
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "FastAPI_Backend"


def assert_status(response, expected: int = 200) -> None:
    if response.status_code != expected:
        raise AssertionError(f"{response.request.method} {response.request.url} returned {response.status_code}: {response.text}")


def main() -> int:
    db_path = Path(tempfile.gettempdir()) / "targ_verify_project.db"
    db_path.unlink(missing_ok=True)

    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
    os.environ.setdefault("SECRET_KEY", "verify-project-secret")
    sys.path.insert(0, str(BACKEND))

    from fastapi.testclient import TestClient
    from main import app

    with TestClient(app) as client:
        response = client.get("/")
        assert_status(response)
        root = response.json()
        assert root["version"].startswith("7.")
        assert root["dataset_size"] > 0

        response = client.get("/ready")
        assert_status(response)
        assert response.json()["database"] == "ok"

        response = client.post(
            "/health/",
            json={"age": 25, "height": 175, "weight": 70, "gender": "male", "activity_level": "moderate"},
        )
        assert_status(response)
        assert response.json()["bmi"] > 0

        response = client.post(
            "/predict/",
            json={
                "nutrition_input": [400, 15, 5, 50, 500, 45, 5, 10, 25],
                "ingredients": [],
                "params": {"n_neighbors": 2, "return_distance": False},
            },
        )
        assert_status(response)
        assert len(response.json()["output"]) == 2

        response = client.get("/foods/search", params={"q": "chicken", "limit": 3})
        assert_status(response)
        assert response.json()["total"] <= 3

        response = client.post(
            "/auth/signup",
            json={"email": "verify@example.com", "username": "verify", "password": "secret123", "full_name": "Verify User"},
        )
        assert_status(response)
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.post("/auth/login", json={"username": "verify@example.com", "password": "secret123"})
        assert_status(response)

        response = client.post("/auth/refresh", headers=headers)
        assert_status(response)

        response = client.get("/auth/me", headers=headers)
        assert_status(response)
        assert response.json()["username"] == "verify"

        response = client.post(
            "/health/",
            headers=headers,
            json={"age": 31, "height": 172, "weight": 74, "gender": "male", "activity_level": "moderate"},
        )
        assert_status(response)

        response = client.get("/user/stats", headers=headers)
        assert_status(response)
        stats = response.json()
        assert stats["total_health_analyses"] == 1
        assert stats["latest_bmi"] is not None

        response = client.post(
            "/user/meals",
            headers=headers,
            json={"meal_name": "Verify Meal", "meal_type": "tracked", "calories": 100, "protein": 10, "carbs": 8, "fat": 4},
        )
        assert_status(response)

        response = client.get("/user/meals", headers=headers)
        assert_status(response)
        assert any(meal["meal_name"] == "Verify Meal" for meal in response.json())

        response = client.get("/user/stats", headers=headers)
        assert_status(response)
        assert response.json()["total_saved_meals"] == 1

        response = client.delete("/user/meals/clear", headers=headers)
        assert_status(response)
        assert "Cleared" in response.json()["message"]

        response = client.get("/user/meals", headers=headers)
        assert_status(response)
        assert response.json() == []

        response = client.post(
            "/user/workouts",
            headers=headers,
            json={
                "workout_focus": "Verification",
                "exercises_completed": ["Running"],
                "duration_minutes": 30,
                "calories_burned": 260,
            },
        )
        assert_status(response)

        response = client.get("/user/workouts", headers=headers)
        assert_status(response)
        assert response.json()[0]["workout_focus"] == "Verification"

        response = client.get("/user/stats", headers=headers)
        assert_status(response)
        assert response.json()["total_workouts"] == 1

        response = client.post("/user/water", headers=headers, json={"glasses": 2})
        assert_status(response)
        response = client.get("/user/water", headers=headers)
        assert_status(response)
        assert response.json()["glasses"] == 2

        response = client.post("/user/water", headers=headers, json={"glasses": 0, "ml": 0})
        assert_status(response, 422)

        response = client.post(
            "/exercises/calories",
            json={"exercise_name": "Running", "weight_kg": -1, "duration_minutes": 30},
        )
        assert_status(response, 422)

        plan = {"Monday": {"breakfast": "Oats", "lunch": "Rice", "snack": "Fruit", "dinner": "Dal"}}
        response = client.post("/user/meal-plan", headers=headers, json={"plan_data": plan})
        assert_status(response)
        response = client.get("/user/meal-plan", headers=headers)
        assert_status(response)
        assert response.json()["plan_data"] == plan

    print("TARG verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
