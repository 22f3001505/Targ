package com.targ.app.data.repository

import com.targ.app.data.api.ApiClient
import com.targ.app.data.model.*

class HealthRepository {

    private val api = ApiClient.apiService
    companion object {
        const val SESSION_EXPIRED_MESSAGE = "Session expired. Please log in again."
    }

    private fun apiError(defaultMessage: String, errorBody: String?): String {
        if (errorBody.isNullOrBlank()) return defaultMessage
        val detail = Regex("\"detail\"\\s*:\\s*\"([^\"]+)\"").find(errorBody)
        if (detail != null) return detail.groupValues.getOrNull(1) ?: defaultMessage
        val validationMessage = Regex("\"msg\"\\s*:\\s*\"([^\"]+)\"").find(errorBody)
        return validationMessage?.groupValues?.getOrNull(1) ?: defaultMessage
    }

    private fun protectedError(statusCode: Int, defaultMessage: String, errorBody: String?): Exception {
        val message = if (statusCode == 401 || statusCode == 403) {
            SESSION_EXPIRED_MESSAGE
        } else {
            apiError(defaultMessage, errorBody)
        }
        return Exception(message)
    }

    // ═══════════════════════════════════════════
    // HEALTH CHECK (v6.0)
    // ═══════════════════════════════════════════
    suspend fun healthCheck(): Result<HealthCheckResponse> {
        return try {
            val response = api.healthCheck()
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("API unavailable"))
            }
        } catch (e: Exception) {
            Result.failure(Exception("Cannot connect to server: ${e.message}"))
        }
    }

    // ═══════════════════════════════════════════
    // HEALTH ANALYSIS (with local fallback + optional auth)
    // ═══════════════════════════════════════════
    suspend fun getHealthAnalysis(request: HealthRequest, authToken: String? = null): Result<HealthResponse> {
        return try {
            val bearerToken = authToken?.let { "Bearer $it" }
            val response = api.getHealthAnalysis(request, bearerToken)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else if (authToken != null && (response.code() == 401 || response.code() == 403)) {
                Result.failure(protectedError(response.code(), "Analysis sync failed", response.errorBody()?.string()))
            } else {
                // Fallback to local
                Result.success(localHealthCalc(request))
            }
        } catch (e: Exception) {
            // Fallback to local calculation
            try {
                Result.success(localHealthCalc(request))
            } catch (inner: Exception) {
                Result.failure(Exception("Health analysis failed: ${inner.message}"))
            }
        }
    }

    // ═══════════════════════════════════════════
    // DIET RECOMMENDATIONS (ML API)
    // ═══════════════════════════════════════════
    suspend fun getDietRecommendation(request: DietRequest): Result<DietResponse> {
        return try {
            val response = api.getDietRecommendation(request)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("No results from API (${response.code()})"))
            }
        } catch (e: Exception) {
            Result.failure(Exception("Cannot connect to recipe API: ${e.message}"))
        }
    }

    // ═══════════════════════════════════════════
    // EXERCISE DATABASE (v6.0)
    // ═══════════════════════════════════════════
    suspend fun getExercises(category: String? = null, difficulty: String? = null): Result<ExercisesResponse> {
        return try {
            val response = api.getExercises(category, difficulty)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Failed to fetch exercises"))
            }
        } catch (e: Exception) {
            Result.failure(Exception("Cannot connect: ${e.message}"))
        }
    }

    suspend fun estimateCalories(exerciseName: String, weightKg: Double, durationMin: Int): Result<CalorieEstimateResponse> {
        return try {
            val request = CalorieEstimateRequest(exerciseName, weightKg, durationMin)
            val response = api.estimateExerciseCalories(request)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Calorie estimation failed"))
            }
        } catch (e: Exception) {
            Result.failure(Exception("Cannot connect: ${e.message}"))
        }
    }

    // ═══════════════════════════════════════════
    // AUTH
    // ═══════════════════════════════════════════
    suspend fun login(username: String, password: String): Result<AuthResponse> {
        return try {
            val response = api.login(LoginRequest(username, password))
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                val msg = if (response.code() == 401) "Invalid username/email or password" else apiError("Login failed", response.errorBody()?.string())
                Result.failure(Exception(msg))
            }
        } catch (e: Exception) {
            Result.failure(Exception("Cannot connect to server: ${e.message}"))
        }
    }

    suspend fun signup(email: String, username: String, password: String, fullName: String): Result<AuthResponse> {
        return try {
            val response = api.signup(SignupRequest(email, username, password, fullName))
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                val msg = when (response.code()) {
                    400, 422 -> apiError("Check your email, username, and password", response.errorBody()?.string())
                    else -> apiError("Signup failed", response.errorBody()?.string())
                }
                Result.failure(Exception(msg))
            }
        } catch (e: Exception) {
            Result.failure(Exception("Cannot connect to server: ${e.message}"))
        }
    }

    suspend fun getUserStats(token: String): Result<UserStatsResponse> {
        return try {
            val response = api.getUserStats("Bearer $token")
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(protectedError(response.code(), "Failed to fetch stats", response.errorBody()?.string()))
            }
        } catch (e: Exception) {
            Result.failure(Exception("Cannot connect: ${e.message}"))
        }
    }

    suspend fun getProfile(token: String): Result<UserData> {
        return try {
            val response = api.getProfile("Bearer $token")
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(protectedError(response.code(), "Session expired", response.errorBody()?.string()))
            }
        } catch (e: Exception) {
            Result.failure(Exception("Cannot connect: ${e.message}"))
        }
    }

    suspend fun getSavedMeals(token: String, limit: Int = 20): Result<List<SavedMealResponse>> {
        return try {
            val response = api.getSavedMeals("Bearer $token", limit)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(protectedError(response.code(), "Failed to fetch meals", response.errorBody()?.string()))
            }
        } catch (e: Exception) {
            Result.failure(Exception("Cannot connect: ${e.message}"))
        }
    }

    suspend fun saveMeal(token: String, request: SaveMealRequest): Result<Unit> {
        return try {
            val response = api.saveMeal("Bearer $token", request)
            if (response.isSuccessful) Result.success(Unit) else Result.failure(protectedError(response.code(), "Save failed", response.errorBody()?.string()))
        } catch (e: Exception) {
            Result.failure(Exception("Cannot connect: ${e.message}"))
        }
    }

    suspend fun deleteMeal(token: String, mealId: Int): Result<Unit> {
        return try {
            val response = api.deleteMeal("Bearer $token", mealId)
            if (response.isSuccessful) Result.success(Unit) else Result.failure(protectedError(response.code(), "Delete failed", response.errorBody()?.string()))
        } catch (e: Exception) {
            Result.failure(Exception("Cannot connect: ${e.message}"))
        }
    }

    suspend fun clearTrackedMeals(token: String): Result<Unit> {
        return try {
            val response = api.clearTrackedMeals("Bearer $token")
            if (response.isSuccessful) Result.success(Unit) else Result.failure(protectedError(response.code(), "Clear failed", response.errorBody()?.string()))
        } catch (e: Exception) {
            Result.failure(Exception("Cannot connect: ${e.message}"))
        }
    }

    suspend fun logWorkout(token: String, request: LogWorkoutRequest): Result<Unit> {
        return try {
            val response = api.logWorkout("Bearer $token", request)
            if (response.isSuccessful) Result.success(Unit) else Result.failure(protectedError(response.code(), "Log failed", response.errorBody()?.string()))
        } catch (e: Exception) {
            Result.failure(Exception("Cannot connect: ${e.message}"))
        }
    }

    suspend fun saveMealPlan(token: String, request: SaveMealPlanRequest): Result<Unit> {
        return try {
            val response = api.saveMealPlan("Bearer $token", request)
            if (response.isSuccessful) Result.success(Unit) else Result.failure(protectedError(response.code(), "Meal plan save failed", response.errorBody()?.string()))
        } catch (e: Exception) {
            Result.failure(Exception("Cannot connect: ${e.message}"))
        }
    }

    suspend fun getMealPlan(token: String): Result<MealPlanResponse> {
        return try {
            val response = api.getMealPlan("Bearer $token")
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(protectedError(response.code(), "No meal plan found", response.errorBody()?.string()))
            }
        } catch (e: Exception) {
            Result.failure(Exception("Cannot connect: ${e.message}"))
        }
    }

    suspend fun searchFoods(query: String, limit: Int = 20): Result<List<FoodItem>> {
        return try {
            val response = api.searchFoods(query, limit)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!.foods)
            } else {
                Result.failure(Exception("Food search failed"))
            }
        } catch (e: Exception) {
            Result.failure(Exception("Cannot connect: ${e.message}"))
        }
    }

    suspend fun getPopularFoods(limit: Int = 30): Result<List<FoodItem>> {
        return try {
            val response = api.getPopularFoods(limit)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!.foods)
            } else {
                Result.failure(Exception("Popular foods unavailable"))
            }
        } catch (e: Exception) {
            Result.failure(Exception("Cannot connect: ${e.message}"))
        }
    }

    suspend fun logWater(token: String, glasses: Int = 0, ml: Int = 0): Result<WaterIntakeResponse> {
        return try {
            val response = api.logWater("Bearer $token", WaterIntakeRequest(glasses, ml))
            if (response.isSuccessful) {
                getWater(token)
            } else {
                Result.failure(protectedError(response.code(), "Water log failed", response.errorBody()?.string()))
            }
        } catch (e: Exception) {
            Result.failure(Exception("Cannot connect: ${e.message}"))
        }
    }

    suspend fun setWater(token: String, glasses: Int = 0, ml: Int = 0): Result<WaterIntakeResponse> {
        return try {
            val response = api.setWater("Bearer $token", WaterIntakeRequest(glasses, ml))
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(protectedError(response.code(), "Water update failed", response.errorBody()?.string()))
            }
        } catch (e: Exception) {
            Result.failure(Exception("Cannot connect: ${e.message}"))
        }
    }

    suspend fun getWater(token: String): Result<WaterIntakeResponse> {
        return try {
            val response = api.getWater("Bearer $token")
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(protectedError(response.code(), "Water data unavailable", response.errorBody()?.string()))
            }
        } catch (e: Exception) {
            Result.failure(Exception("Cannot connect: ${e.message}"))
        }
    }

    // ═══════════════════════════════════════════
    // LOCAL FALLBACK (offline health calc)
    // ═══════════════════════════════════════════
    private fun localHealthCalc(request: HealthRequest): HealthResponse {
        val heightM = request.height / 100f
        val bmi = (request.weight / (heightM * heightM)).let { Math.round(it * 100f) / 100f }

        val (cat, status, color) = when {
            bmi < 18.5f -> Triple("Underweight", "Below healthy range", "#FFA726")
            bmi < 25f -> Triple("Normal", "Healthy weight", "#4CAF50")
            bmi < 30f -> Triple("Overweight", "Above healthy range", "#FF7043")
            else -> Triple("Obese", "High health risk", "#EF5350")
        }

        val bmr = if (request.gender.lowercase() == "male")
            10 * request.weight + 6.25f * request.height - 5 * request.age + 5
        else
            10 * request.weight + 6.25f * request.height - 5 * request.age - 161

        val multiplier = when (request.activityLevel.lowercase()) {
            "sedentary" -> 1.2f; "light" -> 1.375f; "moderate" -> 1.55f
            "active" -> 1.725f; "extra_active" -> 1.9f; else -> 1.55f
        }
        val maintenance = (bmr * multiplier).toInt()

        val workoutPlans = mapOf(
            "Underweight" to WorkoutPlan("Strength & Muscle Building",
                listOf("Weight training (3-4 days/week)", "Resistance exercises", "Compound movements", "Progressive overload"),
                "Focus on caloric surplus with protein-rich diet."),
            "Normal" to WorkoutPlan("Balanced Fitness",
                listOf("Cardio + Strength mix", "HIIT (2x/week)", "Yoga/mobility", "Core work"),
                "Maintain balanced nutrition."),
            "Overweight" to WorkoutPlan("Cardio & Fat Burning",
                listOf("Brisk walking (30-45 min)", "Swimming/cycling", "Light weights", "Interval training"),
                "Create moderate caloric deficit."),
            "Obese" to WorkoutPlan("Low-Impact Movement",
                listOf("Walking (15-20 min)", "Water aerobics", "Stationary cycling", "Gentle stretching"),
                "Consult healthcare provider.")
        )

        return HealthResponse(
            bmi = bmi,
            bmiCategory = BmiCategory(cat, status, color),
            bmr = Math.round(bmr * 100f) / 100f,
            dailyCalories = DailyCalories(
                maintenance = maintenance,
                mildLoss = (maintenance * 0.9).toInt(),
                weightLoss = (maintenance * 0.8).toInt(),
                extremeLoss = (maintenance * 0.6).toInt(),
                mildGain = (maintenance * 1.1).toInt(),
                weightGain = (maintenance * 1.2).toInt()
            ),
            workoutPlan = workoutPlans[cat] ?: workoutPlans["Normal"]!!
        )
    }
}
