package com.targ.app.data.api

import com.targ.app.data.model.*
import retrofit2.Response
import retrofit2.http.*

interface ApiService {

    // ─── PUBLIC: Health Check (v6.0) ───
    @GET("/")
    suspend fun healthCheck(): Response<HealthCheckResponse>

    // ─── PUBLIC: Health Analysis (optional auth for auto-save) ───
    @POST("/health/")
    suspend fun getHealthAnalysis(
        @Body request: HealthRequest,
        @Header("Authorization") token: String? = null
    ): Response<HealthResponse>

    // ─── PUBLIC: Diet Recommendations (ML) ───
    @POST("/predict/")
    suspend fun getDietRecommendation(@Body request: DietRequest): Response<DietResponse>

    // ─── PUBLIC: Exercise Database (v6.0) ───
    @GET("/exercises")
    suspend fun getExercises(
        @Query("category") category: String? = null,
        @Query("difficulty") difficulty: String? = null
    ): Response<ExercisesResponse>

    // ─── PUBLIC: Exercise Calorie Calculator (v6.0) ───
    @POST("/exercises/calories")
    suspend fun estimateExerciseCalories(
        @Body request: CalorieEstimateRequest
    ): Response<CalorieEstimateResponse>

    // ─── AUTH: Signup ───
    @POST("/auth/signup")
    suspend fun signup(@Body request: SignupRequest): Response<AuthResponse>

    // ─── AUTH: Login ───
    @POST("/auth/login")
    suspend fun login(@Body request: LoginRequest): Response<AuthResponse>

    // ─── AUTH: Get Profile ───
    @GET("/auth/me")
    suspend fun getProfile(@Header("Authorization") token: String): Response<UserData>

    // ─── PROTECTED: User Stats ───
    @GET("/user/stats")
    suspend fun getUserStats(@Header("Authorization") token: String): Response<UserStatsResponse>

    // ─── PROTECTED: Saved Meals ───
    @GET("/user/meals")
    suspend fun getSavedMeals(
        @Header("Authorization") token: String,
        @Query("limit") limit: Int = 20
    ): Response<List<SavedMealResponse>>

    // ─── PROTECTED: Save Meal ───
    @POST("/user/meals")
    suspend fun saveMeal(
        @Header("Authorization") token: String,
        @Body request: SaveMealRequest
    ): Response<Map<String, Any>>

    @DELETE("/user/meals/{mealId}")
    suspend fun deleteMeal(
        @Header("Authorization") token: String,
        @Path("mealId") mealId: Int
    ): Response<Map<String, Any>>

    @DELETE("/user/meals/clear")
    suspend fun clearTrackedMeals(
        @Header("Authorization") token: String
    ): Response<Map<String, Any>>

    // ─── PROTECTED: Log Workout ───
    @POST("/user/workouts")
    suspend fun logWorkout(
        @Header("Authorization") token: String,
        @Body request: LogWorkoutRequest
    ): Response<Map<String, Any>>

    // ─── PROTECTED: Meal Planner ───
    @POST("/user/meal-plan")
    suspend fun saveMealPlan(
        @Header("Authorization") token: String,
        @Body request: SaveMealPlanRequest
    ): Response<Map<String, Any>>

    @GET("/user/meal-plan")
    suspend fun getMealPlan(
        @Header("Authorization") token: String
    ): Response<MealPlanResponse>

    // ─── PUBLIC: Food Nutrition Search (v7.0) ───
    @GET("/foods/search")
    suspend fun searchFoods(
        @Query("q") query: String,
        @Query("limit") limit: Int = 20
    ): Response<FoodSearchResponse>

    // ─── PUBLIC: Popular Foods (v7.0) ───
    @GET("/foods/popular")
    suspend fun getPopularFoods(
        @Query("limit") limit: Int = 30
    ): Response<FoodSearchResponse>

    // ─── PROTECTED: Water Intake (v7.0) ───
    @POST("/user/water")
    suspend fun logWater(
        @Header("Authorization") token: String,
        @Body request: WaterIntakeRequest
    ): Response<Map<String, Any>>

    @PUT("/user/water")
    suspend fun setWater(
        @Header("Authorization") token: String,
        @Body request: WaterIntakeRequest
    ): Response<WaterIntakeResponse>

    @GET("/user/water")
    suspend fun getWater(
        @Header("Authorization") token: String
    ): Response<WaterIntakeResponse>
}
