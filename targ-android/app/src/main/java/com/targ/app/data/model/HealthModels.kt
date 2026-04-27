package com.targ.app.data.model

import com.google.gson.annotations.SerializedName

// ═══════════════════════════════════════════
// HEALTH ANALYSIS
// ═══════════════════════════════════════════

data class HealthRequest(
    val age: Int,
    val height: Float,
    val weight: Float,
    val gender: String,
    @SerializedName("activity_level")
    val activityLevel: String
)

data class HealthResponse(
    val bmi: Float,
    @SerializedName("bmi_category")
    val bmiCategory: BmiCategory,
    val bmr: Float,
    @SerializedName("daily_calories")
    val dailyCalories: DailyCalories,
    @SerializedName("workout_plan")
    val workoutPlan: WorkoutPlan
)

data class BmiCategory(
    val category: String,
    val status: String,
    val color: String
)

data class DailyCalories(
    val maintenance: Int,
    @SerializedName("mild_loss")
    val mildLoss: Int,
    @SerializedName("weight_loss")
    val weightLoss: Int,
    @SerializedName("extreme_loss")
    val extremeLoss: Int,
    @SerializedName("mild_gain")
    val mildGain: Int,
    @SerializedName("weight_gain")
    val weightGain: Int
)

data class WorkoutPlan(
    val focus: String,
    val exercises: List<String>,
    val tips: String
)

// ═══════════════════════════════════════════
// DIET RECOMMENDATIONS
// ═══════════════════════════════════════════

data class DietRequest(
    @SerializedName("nutrition_input")
    val nutritionInput: List<Double>,
    val ingredients: List<String> = emptyList(),
    val params: DietParams = DietParams()
)

data class DietParams(
    @SerializedName("n_neighbors")
    val nNeighbors: Int = 5,
    @SerializedName("return_distance")
    val returnDistance: Boolean = false
)

data class DietResponse(
    val output: List<Recipe>?
)

data class Recipe(
    @SerializedName("Name")
    val name: String = "",
    @SerializedName("Calories")
    val calories: Double = 0.0,
    @SerializedName("ProteinContent")
    val proteinContent: Double = 0.0,
    @SerializedName("FatContent")
    val fatContent: Double = 0.0,
    @SerializedName("CarbohydrateContent")
    val carbohydrateContent: Double = 0.0,
    @SerializedName("FiberContent")
    val fiberContent: Double = 0.0,
    @SerializedName("SugarContent")
    val sugarContent: Double = 0.0,
    @SerializedName("SodiumContent")
    val sodiumContent: Double = 0.0,
    @SerializedName("CholesterolContent")
    val cholesterolContent: Double = 0.0,
    @SerializedName("SaturatedFatContent")
    val saturatedFatContent: Double = 0.0,
    @SerializedName("CookTime")
    val cookTime: Any? = "",
    @SerializedName("PrepTime")
    val prepTime: Any? = "",
    @SerializedName("TotalTime")
    val totalTime: Any? = "",
    @SerializedName("RecipeIngredientParts")
    val ingredients: Any? = emptyList<String>(),
    @SerializedName("RecipeInstructions")
    val instructions: Any? = emptyList<String>()
) {
    /** Safe getter — converts time fields to display string */
    fun getCookTimeDisplay(): String = cookTime?.toString() ?: ""
    fun getPrepTimeDisplay(): String = prepTime?.toString() ?: ""
    fun getTotalTimeDisplay(): String = totalTime?.toString() ?: ""

    /** Safe getter — converts ingredients to list */
    @Suppress("UNCHECKED_CAST")
    fun getIngredientsList(): List<String> = try {
        when (ingredients) {
            is List<*> -> ingredients.filterIsInstance<String>()
            is String -> if (ingredients.isNotEmpty()) listOf(ingredients) else emptyList()
            else -> emptyList()
        }
    } catch (_: Exception) { emptyList() }

    /** Safe getter — converts instructions to list */
    @Suppress("UNCHECKED_CAST")
    fun getInstructionsList(): List<String> = try {
        when (instructions) {
            is List<*> -> instructions.filterIsInstance<String>()
            is String -> if (instructions.isNotEmpty()) listOf(instructions) else emptyList()
            else -> emptyList()
        }
    } catch (_: Exception) { emptyList() }
}

// ═══════════════════════════════════════════
// AUTHENTICATION
// ═══════════════════════════════════════════

data class LoginRequest(
    val username: String,
    val password: String
)

data class SignupRequest(
    val email: String,
    val username: String,
    val password: String,
    @SerializedName("full_name")
    val fullName: String = ""
)

data class AuthResponse(
    @SerializedName("access_token")
    val accessToken: String,
    @SerializedName("token_type")
    val tokenType: String = "bearer",
    @SerializedName("expires_in")
    val expiresIn: Int = 0,
    val user: UserData
)

data class UserData(
    val id: Int,
    val email: String,
    val username: String,
    @SerializedName("full_name")
    val fullName: String = ""
)

// ═══════════════════════════════════════════
// USER DATA (Protected endpoints)
// ═══════════════════════════════════════════

data class UserStatsResponse(
    @SerializedName("total_health_analyses")
    val totalHealthAnalyses: Int = 0,
    @SerializedName("total_saved_meals")
    val totalSavedMeals: Int = 0,
    @SerializedName("total_workouts")
    val totalWorkouts: Int = 0,
    @SerializedName("latest_bmi")
    val latestBmi: Float? = null,
    @SerializedName("latest_calories")
    val latestCalories: Int? = null,
    @SerializedName("member_since")
    val memberSince: String = ""
)

data class SavedMealResponse(
    val id: Int = 0,
    @SerializedName("meal_name")
    val mealName: String = "",
    @SerializedName("meal_type")
    val mealType: String = "other",
    val calories: Double = 0.0,
    val protein: Double = 0.0,
    val carbs: Double = 0.0,
    val fat: Double = 0.0,
    @SerializedName("saved_at")
    val savedAt: String = ""
)

data class SaveMealRequest(
    @SerializedName("meal_name")
    val mealName: String,
    @SerializedName("meal_type")
    val mealType: String = "other",
    val calories: Double = 0.0,
    val protein: Double = 0.0,
    val carbs: Double = 0.0,
    val fat: Double = 0.0
)

data class LogWorkoutRequest(
    @SerializedName("workout_focus")
    val workoutFocus: String,
    @SerializedName("exercises_completed")
    val exercisesCompleted: List<String> = emptyList(),
    @SerializedName("duration_minutes")
    val durationMinutes: Int = 0,
    @SerializedName("calories_burned")
    val caloriesBurned: Int = 0,
    val notes: String = ""
)

data class SaveMealPlanRequest(
    @SerializedName("plan_data")
    val planData: Map<String, Map<String, String>>,
    @SerializedName("week_start")
    val weekStart: String? = null
)

data class MealPlanResponse(
    @SerializedName("plan_data")
    val planData: Map<String, Map<String, String>>? = null,
    @SerializedName("week_start")
    val weekStart: String? = null,
    @SerializedName("created_at")
    val createdAt: String? = null
)

// ═══════════════════════════════════════════
// EXERCISE DATABASE (v6.0)
// ═══════════════════════════════════════════

data class ExerciseItem(
    val name: String = "",
    val met: Double = 0.0,
    val category: String = "",
    val difficulty: String = "Moderate"
)

data class ExercisesResponse(
    val exercises: List<ExerciseItem> = emptyList(),
    val total: Int = 0,
    val categories: List<String> = emptyList()
)

data class CalorieEstimateRequest(
    @SerializedName("exercise_name")
    val exerciseName: String,
    @SerializedName("weight_kg")
    val weightKg: Double,
    @SerializedName("duration_minutes")
    val durationMinutes: Int
)

data class CalorieEstimateResponse(
    val exercise: String = "",
    val met: Double = 0.0,
    @SerializedName("weight_kg")
    val weightKg: Double = 0.0,
    @SerializedName("duration_minutes")
    val durationMinutes: Int = 0,
    @SerializedName("calories_burned")
    val caloriesBurned: Int = 0,
    val source: String = ""
)

// ═══════════════════════════════════════════
// HEALTH CHECK (v6.0)
// ═══════════════════════════════════════════

data class HealthCheckResponse(
    @SerializedName("health_check")
    val healthCheck: String = "",
    @SerializedName("api_name")
    val apiName: String = "",
    val version: String = "",
    @SerializedName("dataset_size")
    val datasetSize: Int = 0,
    @SerializedName("exercise_count")
    val exerciseCount: Int = 0
)

// ═══════════════════════════════════════════
// FOOD NUTRITION SEARCH (v7.0)
// ═══════════════════════════════════════════

data class FoodItem(
    val name: String = "",
    val calories: Double = 0.0,
    val protein: Double = 0.0,
    val carbs: Double = 0.0,
    val fat: Double = 0.0,
    val fiber: Double = 0.0,
    val serving: String = "1 serving"
)

data class FoodSearchResponse(
    val query: String = "",
    val total: Int = 0,
    val foods: List<FoodItem> = emptyList()
)

// ═══════════════════════════════════════════
// WATER INTAKE (v7.0)
// ═══════════════════════════════════════════

data class WaterIntakeRequest(
    val glasses: Int = 0,
    val ml: Int = 0
)

data class WaterIntakeResponse(
    @SerializedName("total_ml")
    val totalMl: Int = 0,
    val glasses: Int = 0,
    @SerializedName("goal_ml")
    val goalMl: Int = 2500,
    val percent: Int = 0
)
