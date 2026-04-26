# 🥗 TARG — AI-Powered Health & Nutrition Intelligence Platform

<div align="center">

**Targeted AI-based Recipe Generator**

[![Version](https://img.shields.io/badge/version-7.2.6-green)]()
[![Python](https://img.shields.io/badge/Python-3.10+-blue)]()
[![Kotlin](https://img.shields.io/badge/Kotlin-2.1.10-purple)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-teal)]()
[![Compose](https://img.shields.io/badge/Jetpack_Compose-Material3-green)]()

*A full-stack health intelligence system with ML-powered recipe recommendations, BMI/BMR analysis, MET-based exercise calorie estimation, macro tracking, food nutrition search, water intake monitoring, and meal planning — available on Web and Android.*

</div>

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Tech Stack & Tool Usage](#-complete-tech-stack--tool-usage)
- [Architecture](#-system-architecture)
- [Project Structure](#-project-structure)
- [Features](#-key-features)
- [API Reference](#-api-reference-24-endpoints)
- [ML Pipeline](#-ml-pipeline)
- [Database Schema](#-database-schema)
- [Security](#-security-architecture)
- [Installation & Setup](#-installation--setup)
- [Docker Deployment](#-docker-deployment)

---

## 🎯 Overview

TARG is a **production-grade health intelligence system** — 3 platforms, 9,108+ lines of code, 25 API endpoints, with a 375K+ recipe source dataset and a Render-friendly lite runtime index.

| Metric | Value |
|--------|-------|
| **Total Source Files** | 35 |
| **Total Lines of Code** | 9,108 |
| **Backend** | 6 Python files · 1,536 LOC |
| **Web Frontend** | 12 Python files · 4,516 LOC |
| **Android App** | 16 Kotlin files · 3,056 LOC |
| **API Endpoints** | 25 RESTful |
| **Recipe Dataset** | 375,703 source recipes · 50K lite runtime sample |
| **Exercise Database** | 198 exercises with MET values |
| **Database Tables** | 5 |

---

## 🛠 Complete Tech Stack & Tool Usage

### Backend — Python + FastAPI

| Technology | Version | What It Is | How TARG Uses It |
|------------|---------|-----------|------------------|
| **Python** | 3.10+ | Programming language | Runtime for entire backend |
| **FastAPI** | ≥0.115 | Async web framework | 25 REST API endpoints with auto OpenAPI docs, request validation, dependency injection |
| **Uvicorn** | ≥0.30 | ASGI server | Runs FastAPI on port 8080, handles HTTP with async I/O |
| **Pydantic** | ≥2.10 | Data validation | Validates ALL request bodies — nutrition arrays, health inputs, auth forms |
| **Scikit-learn** | ≥1.5 | Machine Learning | KNN with cosine similarity for recipe matching, StandardScaler for normalization |
| **Pandas** | ≥2.2 | Data analysis | Loads 375K recipe CSV, DataFrame operations for filtering/extraction |
| **NumPy** | ≥2.0 | Numerical computing | Array operations for ML input vectors |
| **SQLAlchemy** | ≥2.0 | ORM | Maps Python classes to SQLite tables, session management, CRUD ops |
| **python-jose** | ≥3.3 | JWT library | Creates/validates JSON Web Tokens for authentication (7-day expiry) |
| **Passlib+Bcrypt** | ≥1.7 | Password hashing | Salted Bcrypt hashing — original password never stored |
| **python-multipart** | ≥0.0.9 | Form parser | Handles multipart form data for auth requests |

### Web Frontend — Streamlit

| Technology | Version | What It Is | How TARG Uses It |
|------------|---------|-----------|------------------|
| **Streamlit** | ≥1.28 | Web app framework | 7 interactive pages with forms, sliders, charts, session state, custom CSS |
| **Plotly** | ≥5.18 | Interactive charts | BMI gauges, macro donut charts, meal bar charts, health trend lines |
| **Altair** | ≥4.0 | Declarative viz | Nutrition distribution and workout analytics charts |
| **Streamlit-ECharts** | 0.4 | Apache ECharts | Animated gauges, radar nutrient profiles, heatmaps |
| **Requests** | 2.28 | HTTP client | ALL API calls from frontend to backend, centralized in `APIClient` class |
| **BeautifulSoup** | 4.11 | HTML parser | Parses recipe image search results for food image display |

### Android App — Kotlin + Jetpack Compose

| Technology | Version | What It Is | How TARG Uses It |
|------------|---------|-----------|------------------|
| **Kotlin** | 2.1.10 | Language | Entire Android app — type-safe, concise, coroutine support |
| **Jetpack Compose** | BOM 2024.12.01 | Declarative UI | ALL screens via `@Composable` functions — cards, forms, lists, animations |
| **Material3** | Latest | Design system | `Card`, `TextField`, `Button`, `NavigationBar`, color schemes, typography |
| **Retrofit** | 2.11 | HTTP client | Type-safe API client with `@GET`/`@POST` annotations for 16 endpoints |
| **OkHttp** | 4.12 | HTTP engine | Connection pooling, timeouts, request/response logging |
| **Gson** | 2.11 | JSON serializer | Converts API JSON ↔ Kotlin data classes via `@SerializedName` |
| **Navigation Compose** | 2.8.5 | Screen routing | `NavHost` + `NavController` with 5-tab bottom navigation |
| **ViewModel** | 2.8.7 | State management | `HealthViewModel` holds ALL app state as `StateFlow` |
| **DataStore** | 1.1.2 | Local storage | Persists JWT auth token across app restarts |
| **Coroutines** | Built-in | Async | `viewModelScope.launch {}` for non-blocking API calls |
| **Gradle** | 9.4.1 | Build system | Compiles Kotlin, resolves dependencies, generates APK |
| **AGP** | 8.9.1 | Android build plugin | Resource processing, manifest merging, APK packaging |

### Database

| Technology | What It Is | How TARG Uses It |
|------------|-----------|------------------|
| **SQLite 3** | Embedded relational DB | File-based `targ.db` — zero configuration, perfect for local deployment |
| **SQLAlchemy 2.0** | Python ORM | 5 model classes → 5 tables. Connection pooling, session lifecycle, query building |

### DevOps

| Technology | What It Is | How TARG Uses It |
|------------|-----------|------------------|
| **Docker Compose** | Container orchestration | 2 services (backend + frontend) on isolated network |
| **Git** | Version control | Source code management |

---

## 🏗 System Architecture

```
┌───────────────────────────────────────────────────────────┐
│                     CLIENT LAYER                          │
│                                                           │
│   ┌───────────────────┐     ┌───────────────────────┐    │
│   │  Streamlit Web     │     │  Android App          │    │
│   │  (Port 8501)       │     │  Kotlin + Compose     │    │
│   │  4,516 LOC         │     │  3,056 LOC            │    │
│   │                    │     │                       │    │
│   │  7 Pages:          │     │  7 Screens:           │    │
│   │  • Landing         │     │  • Home Dashboard     │    │
│   │  • Account/Auth    │     │  • Health Analysis    │    │
│   │  • Diet Analysis   │     │  • WorkoutCalc        │    │
│   │  • Custom Food     │     │  • Macro Tracker      │    │
│   │  • Workout         │     │  • Recipe Search      │    │
│   │  • Macro Tracker   │     │  • Meal Planner       │    │
│   │  • Meal Planner    │     │  • Account (Auth)     │    │
│   └─────────┬─────────┘     └──────────┬────────────┘    │
│             │ requests lib              │ Retrofit        │
│             └──────────┬────────────────┘                 │
│                        │ HTTP/REST + JSON                 │
└────────────────────────┼──────────────────────────────────┘
                         │
┌────────────────────────┼──────────────────────────────────┐
│             API LAYER — FastAPI (Port 8080)                │
│                        │                                  │
│   ┌────────────────────▼────────────────────────────┐     │
│   │           FastAPI v7.2.6  (1,536+ LOC)          │     │
│   │           25 REST Endpoints + CORS              │     │
│   │                                                 │     │
│   │  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │     │
│   │  │  Auth    │  │  Health  │  │  ML Engine   │  │     │
│   │  │  JWT +   │  │  BMI/BMR │  │  KNN+Cosine  │  │     │
│   │  │  Bcrypt  │  │  /TDEE   │  │  375K recipe  │  │     │
│   │  └─────┬────┘  └────┬─────┘  └───────┬──────┘  │     │
│   │        │             │                │         │     │
│   │  ┌─────▼────┐  ┌────▼─────┐  ┌───────▼──────┐  │     │
│   │  │Exercise  │  │  Food    │  │   Water      │  │     │
│   │  │DB (198   │  │  Search  │  │   Tracker    │  │     │
│   │  │MET-based)│  │  (v7.0)  │  │   (v7.0)     │  │     │
│   │  └──────────┘  └──────────┘  └──────────────┘  │     │
│   └─────────────────────────────────────────────────┘     │
│                        │                                  │
│   ┌────────────────────▼────────────────────────────┐     │
│   │              SQLite Database                    │     │
│   │  5 Tables: users, health_records, saved_meals,  │     │
│   │            workout_logs, meal_plans              │     │
│   └─────────────────────────────────────────────────┘     │
└───────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
Targ/
├── 📄 README.md                           # This file
├── 📄 docker-compose.yml                  # Docker multi-service config
├── 🖼️ logo.png                            # Project logo
├── 📓 targ-recommendation-system.ipynb    # ML research notebook
│
├── 📂 Data/
│   ├── 📄 dataset.csv                     # 375K+ source recipe dataset (gzip)
│   └── 📄 dataset_lite.csv                # 50K runtime sample for memory-limited deploys
│
├── 📂 FastAPI_Backend/               [1,536 LOC | 6 files]
│   ├── 📄 main.py                (730L)  # 24 API endpoints + schemas
│   ├── 📄 model.py               (184L)  # ML pipeline + BMI/BMR/TDEE
│   ├── 📄 auth.py                (185L)  # JWT + Bcrypt auth
│   ├── 📄 exercises_db.py        (287L)  # 198 MET exercises
│   ├── 📄 models_db.py           (116L)  # SQLAlchemy ORM (5 tables)
│   ├── 📄 database.py            (34L)   # DB engine + session
│   └── 📄 requirements.txt               # Python dependencies
│
├── 📂 Streamlit_Frontend/            [4,516 LOC | 12 files]
│   ├── 📄 Hello.py               (600L)  # Landing page + API status
│   ├── 📄 api.py                 (417L)  # Centralized API client
│   ├── 📄 ui/components.py       (232L)  # Shared UI components
│   ├── 📂 pages/
│   │   ├── 📄 0_🔐_Account.py    (386L)  # Auth + profile + stats
│   │   ├── 📄 1_💪_Diet.py       (555L)  # Health analysis + recipes
│   │   ├── 📄 2_🔍_Custom.py     (473L)  # Ingredient search
│   │   ├── 📄 3_🏋️_Workout.py    (601L)  # Workouts + calorie calc
│   │   ├── 📄 4_📊_Macro.py      (656L)  # Macros + food search + water
│   │   └── 📄 5_📅_Planner.py    (573L)  # Weekly meal planner
│   └── 📄 requirements.txt
│
└── 📂 targ-android/                  [3,056 LOC | 16 files]
    ├── 📄 build.gradle.kts                # AGP 8.9.1, Kotlin 2.1.10
    └── 📂 app/src/main/java/com/targ/app/
        ├── 📄 MainActivity.kt     (109L)  # Entry + NavHost
        ├── 📂 data/api/                   # Retrofit client (119L)
        ├── 📂 data/model/                 # 20+ data classes (276L)
        ├── 📂 data/repository/            # API + fallback (215L)
        ├── 📂 viewmodel/                  # StateFlow state (222L)
        └── 📂 ui/screens/                 # 7 Compose screens (2,115L)
```

---

## ✨ Key Features

| Feature | Technologies Used | Description |
|---------|------------------|-------------|
| 🤖 **ML Recipe Recommendations** | Scikit-learn KNN, Cosine Similarity, Pandas | 9-dimension nutritional matching against 375K recipes |
| 💪 **Health Analysis** | Mifflin-St Jeor, Harris-Benedict | BMI, BMR, TDEE, calorie targets for 6 goals |
| 🏋️ **Exercise Calorie Calculator** | MET Compendium, 198 exercises | `calories = MET × weight × duration` |
| 📊 **Macro Tracker** | Plotly charts, Backend sync | Daily goals, meal logging, progress visualization |
| 🔍 **Food Nutrition Search** (v7) | Recipe dataset index | Search 375K+ foods with real nutrition data |
| 💧 **Water Intake Tracker** (v7) | Backend persistence | Glass counting, daily progress toward 2.5L goal |
| 📅 **Meal Planner** | JSON storage | 7-day planner with per-day calorie totals |
| 🔐 **Authentication** | JWT + Bcrypt, SQLite | Signup/login, profile, data persistence |

---

## 🔌 API Reference (24 Endpoints)

### Public (7 endpoints)
```
GET  /                      Health check + version + stats
POST /predict/              ML recipe recommendation (KNN)
POST /health/               BMI, BMR, calorie analysis
GET  /exercises             List 198 exercises (filter: category, difficulty)
POST /exercises/calories    MET-based calorie estimation
GET  /foods/search          Food nutrition search (?q=chicken)
GET  /foods/popular         Popular food items for quick lookup
```

### Auth (4 endpoints)
```
POST /auth/signup           Create account → JWT token
POST /auth/login            Login → JWT token
GET  /auth/me               Get current user profile (🔒)
POST /auth/refresh          Refresh current JWT token (🔒)
```

### Protected (13 endpoints, require Bearer token)
```
GET  /user/health-records        Health analysis history
GET  /user/health-records/trend  BMI/weight trends for charts
GET  /user/stats                 Aggregated user statistics
POST /user/meals                 Save a meal
GET  /user/meals                 Get saved meals
DEL  /user/meals/{id}            Delete specific meal
DEL  /user/meals/clear           Clear today's tracked meals
POST /user/workouts              Log a workout session
GET  /user/workouts              Get workout history
POST /user/meal-plan             Save weekly meal plan
GET  /user/meal-plan             Get current meal plan
POST /user/water                 Log water intake (v7)
GET  /user/water                 Get today's water (v7)
```

---

## 🤖 ML Pipeline

```
Input: [Calories, Fat, SatFat, Cholesterol, Sodium, Carbs, Fiber, Sugar, Protein]
                                    │
                                    ▼
                        ┌───────────────────┐
                        │  StandardScaler   │  ← z-score normalization
                        └─────────┬─────────┘
                                  │
                                  ▼
                   ┌──────────────────────────┐
                   │   NearestNeighbors        │  ← metric='cosine'
                   │   algorithm='brute'       │     algorithm='brute'
                   │   n_neighbors=5           │
                   └──────────────┬────────────┘
                                  │
                                  ▼
                   Match against 375,703 recipes
                                  │
                                  ▼
            Top-K recipes with full nutrition + ingredients
```

---

## 💾 Database Schema

```
users                 health_records          saved_meals
├── id (PK)           ├── id (PK)             ├── id (PK)
├── email (UK)        ├── user_id (FK)        ├── user_id (FK)
├── username (UK)     ├── bmi                 ├── meal_name
├── hashed_password   ├── bmr                 ├── meal_type
├── full_name         ├── weight/height       ├── calories/protein
└── created_at        ├── age/gender          ├── carbs/fat
                      └── recorded_at         └── saved_at

workout_logs          meal_plans
├── id (PK)           ├── id (PK)
├── user_id (FK)      ├── user_id (FK)
├── workout_focus      ├── week_start
├── exercises          ├── plan_data (JSON)
├── duration/calories  └── created_at
└── logged_at
```

---

## 🔒 Security Architecture

| Layer | Technology | Implementation |
|-------|-----------|----------------|
| **Passwords** | Bcrypt (12 rounds) | Unique salt per password, hash-only storage |
| **Auth Tokens** | JWT (HS256) | 7-day expiry, signed with SECRET_KEY |
| **CORS** | FastAPI Middleware | Configurable allowed origins |
| **Input Safety** | Pydantic v2 | Type + range validation on all inputs |
| **SQL Safety** | SQLAlchemy ORM | Parameterized queries, no raw SQL |

---

## 🚀 Installation & Setup

```bash
# Clone
git clone https://github.com/yourusername/targ.git && cd targ

# Backend (Port 8080)
cd FastAPI_Backend
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8080

# Frontend (Port 8501)
cd Streamlit_Frontend
pip install -r requirements.txt
python -m streamlit run Hello.py --server.port 8501

# Android APK
cd targ-android
./gradlew assembleDebug
# → app/build/outputs/apk/debug/app-debug.apk
```

## 🐳 Docker Deployment

```bash
docker-compose up --build
# Backend → http://localhost:8080
# Frontend → http://localhost:8501
```

## ☁️ Render Deployment

This repo includes [render.yaml](/Users/jayaramreddy/Desktop/Targ/Targ/render.yaml:1) for a Render Blueprint with:

- `targ-api`: FastAPI backend
- `targ-web`: Streamlit frontend
- `targ-postgres`: persistent PostgreSQL database

See [RENDER_DEPLOYMENT.md](/Users/jayaramreddy/Desktop/Targ/Targ/RENDER_DEPLOYMENT.md:1) for the exact deployment steps and Android APK backend URL configuration.

Useful environment variables:

```bash
TARG_API_URL=http://localhost:8080              # Streamlit backend URL
CORS_ORIGINS=http://localhost:8501             # Backend allowed origins
CORS_ALLOW_CREDENTIALS=true                    # Enable credentialed CORS for explicit origins
DATABASE_URL=sqlite:///./targ.db               # Backend database
SECRET_KEY=change-this-in-production           # JWT signing key
```

## ✅ Verification

```bash
python3 scripts/verify_project.py
cd targ-android && ./gradlew assembleDebug
```

---

**v7.2.6** | 35+ files | 9,108+ LOC | 25 endpoints | 375K source recipes | 198 exercises | April 2026
