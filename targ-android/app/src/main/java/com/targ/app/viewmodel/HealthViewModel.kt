package com.targ.app.viewmodel

import android.app.Application
import android.content.Context
import android.util.Log
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.intPreferencesKey
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import com.targ.app.data.model.*
import com.targ.app.data.repository.HealthRepository

private val Context.authDataStore by preferencesDataStore(name = "targ_session")

class HealthViewModel(application: Application) : AndroidViewModel(application) {

    private val repository = HealthRepository()
    private val dataStore = application.authDataStore

    // ═══════════════════════════════════════════
    // API STATUS
    // ═══════════════════════════════════════════
    private val _apiStatus = MutableStateFlow<HealthCheckResponse?>(null)
    val apiStatus: StateFlow<HealthCheckResponse?> = _apiStatus

    private val _sessionReady = MutableStateFlow(false)
    val sessionReady: StateFlow<Boolean> = _sessionReady

    init {
        checkApiStatus()
        restoreSession()
    }

    fun checkApiStatus() {
        viewModelScope.launch {
            try {
                val result = repository.healthCheck()
                result.onSuccess { _apiStatus.value = it }
                result.onFailure { _apiStatus.value = null }
            } catch (e: Exception) {
                Log.e("TARG", "Health check failed", e)
                _apiStatus.value = null
            }
        }
    }

    // ═══════════════════════════════════════════
    // AUTH STATE
    // ═══════════════════════════════════════════
    private val _authToken = MutableStateFlow<String?>(null)
    val authToken: StateFlow<String?> = _authToken

    private val _userData = MutableStateFlow<UserData?>(null)
    val userData: StateFlow<UserData?> = _userData

    private val _userStats = MutableStateFlow<UserStatsResponse?>(null)
    val userStats: StateFlow<UserStatsResponse?> = _userStats

    val isLoggedIn: Boolean get() = _authToken.value != null

    private val _savedMeals = MutableStateFlow<List<SavedMealResponse>>(emptyList())
    val savedMeals: StateFlow<List<SavedMealResponse>> = _savedMeals

    // ═══════════════════════════════════════════
    // HEALTH STATE
    // ═══════════════════════════════════════════
    private val _healthData = MutableStateFlow<HealthResponse?>(null)
    val healthData: StateFlow<HealthResponse?> = _healthData

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading

    private val _errorMessage = MutableStateFlow<String?>(null)
    val errorMessage: StateFlow<String?> = _errorMessage

    // ═══════════════════════════════════════════
    // DIET STATE
    // ═══════════════════════════════════════════
    private val _dietData = MutableStateFlow<List<Recipe>>(emptyList())
    val dietData: StateFlow<List<Recipe>> = _dietData

    private val _isDietLoading = MutableStateFlow(false)
    val isDietLoading: StateFlow<Boolean> = _isDietLoading

    // ═══════════════════════════════════════════
    // EXERCISE STATE
    // ═══════════════════════════════════════════
    private val _exercises = MutableStateFlow<List<ExerciseItem>>(emptyList())
    val exercises: StateFlow<List<ExerciseItem>> = _exercises

    private val _exerciseCategories = MutableStateFlow<List<String>>(emptyList())
    val exerciseCategories: StateFlow<List<String>> = _exerciseCategories

    private val _calorieEstimate = MutableStateFlow<CalorieEstimateResponse?>(null)
    val calorieEstimate: StateFlow<CalorieEstimateResponse?> = _calorieEstimate

    private val _isExerciseLoading = MutableStateFlow(false)
    val isExerciseLoading: StateFlow<Boolean> = _isExerciseLoading

    // ═══════════════════════════════════════════
    // MACRO / FOOD / WATER STATE
    // ═══════════════════════════════════════════
    private val _foodResults = MutableStateFlow<List<FoodItem>>(emptyList())
    val foodResults: StateFlow<List<FoodItem>> = _foodResults

    private val _popularFoods = MutableStateFlow<List<FoodItem>>(emptyList())
    val popularFoods: StateFlow<List<FoodItem>> = _popularFoods

    private val _isFoodLoading = MutableStateFlow(false)
    val isFoodLoading: StateFlow<Boolean> = _isFoodLoading

    private val _waterData = MutableStateFlow<WaterIntakeResponse?>(null)
    val waterData: StateFlow<WaterIntakeResponse?> = _waterData

    // ═══════════════════════════════════════════
    // MEAL PLANNER STATE
    // ═══════════════════════════════════════════
    private val _mealPlan = MutableStateFlow<MealPlanResponse?>(null)
    val mealPlan: StateFlow<MealPlanResponse?> = _mealPlan

    private val _actionMessage = MutableStateFlow<String?>(null)
    val actionMessage: StateFlow<String?> = _actionMessage

    // ═══════════════════════════════════════════
    // FLOW UNLOCK
    // ═══════════════════════════════════════════
    val isHealthAnalyzed: Boolean get() = _healthData.value != null

    private object SessionKeys {
        val TOKEN = stringPreferencesKey("auth_token")
        val USER_ID = intPreferencesKey("user_id")
        val EMAIL = stringPreferencesKey("email")
        val USERNAME = stringPreferencesKey("username")
        val FULL_NAME = stringPreferencesKey("full_name")
    }

    // ═══════════════════════════════════════════
    // AUTH ACTIONS
    // ═══════════════════════════════════════════
    private fun restoreSession() {
        viewModelScope.launch {
            try {
                val prefs = dataStore.data.first()
                val token = prefs[SessionKeys.TOKEN] ?: run {
                    _sessionReady.value = true
                    return@launch
                }
                _authToken.value = token
                _userData.value = UserData(
                    id = prefs[SessionKeys.USER_ID] ?: 0,
                    email = prefs[SessionKeys.EMAIL] ?: "",
                    username = prefs[SessionKeys.USERNAME] ?: "",
                    fullName = prefs[SessionKeys.FULL_NAME] ?: ""
                )

                repository.getProfile(token)
                    .onSuccess {
                        _userData.value = it
                        persistSession(token, it)
                        fetchUserStats()
                        loadSavedMeals()
                        loadWater()
                        loadMealPlan()
                    }
                    .onFailure {
                        clearStoredSession()
                    }
            } catch (e: Exception) {
                Log.e("TARG", "Session restore failed", e)
            } finally {
                _sessionReady.value = true
            }
        }
    }

    private fun persistSession(token: String, user: UserData) {
        viewModelScope.launch {
            dataStore.edit { prefs ->
                prefs[SessionKeys.TOKEN] = token
                prefs[SessionKeys.USER_ID] = user.id
                prefs[SessionKeys.EMAIL] = user.email
                prefs[SessionKeys.USERNAME] = user.username
                prefs[SessionKeys.FULL_NAME] = user.fullName
            }
        }
    }

    private fun clearStoredSession() {
        viewModelScope.launch {
            dataStore.edit { it.clear() }
        }
        _authToken.value = null
        _userData.value = null
        _userStats.value = null
        _savedMeals.value = emptyList()
        _waterData.value = null
        _mealPlan.value = null
        _healthData.value = null
        _dietData.value = emptyList()
        _foodResults.value = emptyList()
        _calorieEstimate.value = null
        _errorMessage.value = null
        _actionMessage.value = null
    }

    private fun handleRepositoryFailure(error: Throwable, useActionMessage: Boolean = false) {
        val message = error.message ?: "Something went wrong"
        if (message == HealthRepository.SESSION_EXPIRED_MESSAGE) {
            clearStoredSession()
            _errorMessage.value = message
            return
        }

        if (useActionMessage) {
            _actionMessage.value = message
        } else {
            _errorMessage.value = message
        }
    }

    fun login(username: String, password: String) {
        viewModelScope.launch {
            try {
                _isLoading.value = true
                _errorMessage.value = null
                _actionMessage.value = null
                val result = repository.login(username, password)
                result.onSuccess {
                    _authToken.value = it.accessToken
                    _userData.value = it.user
                    persistSession(it.accessToken, it.user)
                    fetchUserStats()
                    loadSavedMeals()
                    loadWater()
                    loadMealPlan()
                }
                result.onFailure { _errorMessage.value = it.message }
            } catch (e: Exception) {
                _errorMessage.value = "Login error: ${e.message}"
            } finally {
                _isLoading.value = false
            }
        }
    }

    fun signup(email: String, username: String, password: String, fullName: String) {
        viewModelScope.launch {
            try {
                _isLoading.value = true
                _errorMessage.value = null
                _actionMessage.value = null
                val result = repository.signup(email, username, password, fullName)
                result.onSuccess {
                    _authToken.value = it.accessToken
                    _userData.value = it.user
                    persistSession(it.accessToken, it.user)
                    fetchUserStats()
                    loadSavedMeals()
                    loadWater()
                    loadMealPlan()
                }
                result.onFailure { _errorMessage.value = it.message }
            } catch (e: Exception) {
                _errorMessage.value = "Signup error: ${e.message}"
            } finally {
                _isLoading.value = false
            }
        }
    }

    fun logout() {
        clearStoredSession()
    }

    fun refreshAccountData() {
        fetchUserStats()
        loadSavedMeals()
        loadWater()
        loadMealPlan()
    }

    private fun fetchUserStats() {
        val token = _authToken.value ?: return
        viewModelScope.launch {
            try {
                val result = repository.getUserStats(token)
                result.onSuccess { _userStats.value = it }
                result.onFailure { handleRepositoryFailure(it) }
            } catch (e: Exception) {
                Log.e("TARG", "Fetch stats failed", e)
            }
        }
    }

    fun loadSavedMeals(limit: Int = 50) {
        val token = _authToken.value ?: return
        viewModelScope.launch {
            try {
                repository.getSavedMeals(token, limit)
                    .onSuccess { _savedMeals.value = it }
                    .onFailure { handleRepositoryFailure(it) }
            } catch (e: Exception) {
                Log.e("TARG", "Load meals failed", e)
            }
        }
    }

    // ═══════════════════════════════════════════
    // HEALTH ACTIONS
    // ═══════════════════════════════════════════
    fun fetchHealthAnalysis(age: Int, height: Float, weight: Float,
                            gender: String, activityLevel: String) {
        viewModelScope.launch {
            try {
                _isLoading.value = true
                _errorMessage.value = null
                val request = HealthRequest(age, height, weight, gender, activityLevel)
                val result = repository.getHealthAnalysis(request, _authToken.value)
                result.onSuccess {
                    _healthData.value = it
                    if (_authToken.value != null) {
                        fetchUserStats()
                        _actionMessage.value = "Health analysis saved"
                    }
                }
                result.onFailure { handleRepositoryFailure(it) }
            } catch (e: Exception) {
                _errorMessage.value = "Analysis error: ${e.message}"
            } finally {
                _isLoading.value = false
            }
        }
    }

    fun fetchDietRecommendation(calories: Double, fat: Double, saturatedFat: Double,
                                 cholesterol: Double, sodium: Double, carbs: Double,
                                 fiber: Double, sugar: Double, protein: Double,
                                 count: Int = 5) {
        viewModelScope.launch {
            try {
                _isDietLoading.value = true
                val nutritionInput = listOf(calories, fat, saturatedFat, cholesterol,
                                             sodium, carbs, fiber, sugar, protein)
                val request = DietRequest(nutritionInput, params = DietParams(nNeighbors = count))
                val result = repository.getDietRecommendation(request)
                result.onSuccess { _dietData.value = it.output ?: emptyList() }
                result.onFailure { _errorMessage.value = it.message }
            } catch (e: Exception) {
                _errorMessage.value = "Recipe error: ${e.message}"
            } finally {
                _isDietLoading.value = false
            }
        }
    }

    // ═══════════════════════════════════════════
    // EXERCISE ACTIONS
    // ═══════════════════════════════════════════
    fun fetchExercises(category: String? = null) {
        viewModelScope.launch {
            try {
                _isExerciseLoading.value = true
                val result = repository.getExercises(category)
                result.onSuccess {
                    _exercises.value = it.exercises
                    _exerciseCategories.value = it.categories
                }
                result.onFailure { _errorMessage.value = it.message }
            } catch (e: Exception) {
                Log.e("TARG", "Fetch exercises failed", e)
            } finally {
                _isExerciseLoading.value = false
            }
        }
    }

    fun estimateCalories(exerciseName: String, weightKg: Double, durationMin: Int) {
        viewModelScope.launch {
            try {
                _isExerciseLoading.value = true
                val result = repository.estimateCalories(exerciseName, weightKg, durationMin)
                result.onSuccess { _calorieEstimate.value = it }
                result.onFailure { _errorMessage.value = it.message }
            } catch (e: Exception) {
                Log.e("TARG", "Calorie estimate failed", e)
            } finally {
                _isExerciseLoading.value = false
            }
        }
    }

    fun clearCalorieEstimate() { _calorieEstimate.value = null }

    // ═══════════════════════════════════════════
    // MEAL & WORKOUT LOGGING
    // ═══════════════════════════════════════════
    fun saveMeal(name: String, calories: Double, protein: Double, carbs: Double, fat: Double) {
        val token = _authToken.value ?: run {
            _actionMessage.value = "Login to sync meals"
            return
        }
        viewModelScope.launch {
            try {
                repository.saveMeal(token, SaveMealRequest(name, "tracked", calories, protein, carbs, fat))
                    .onSuccess {
                        _actionMessage.value = "Meal added to today"
                        loadSavedMeals()
                        fetchUserStats()
                    }
                    .onFailure { handleRepositoryFailure(it) }
            } catch (e: Exception) {
                Log.e("TARG", "Save meal failed", e)
                _errorMessage.value = "Meal sync failed: ${e.message}"
            }
        }
    }

    fun clearTrackedMeals() {
        val token = _authToken.value ?: run {
            _actionMessage.value = "Local meals cleared. Login to sync meal history."
            return
        }
        viewModelScope.launch {
            try {
                repository.clearTrackedMeals(token)
                    .onSuccess {
                        _actionMessage.value = "Today's meals cleared"
                        loadSavedMeals()
                        fetchUserStats()
                    }
                    .onFailure { handleRepositoryFailure(it) }
            } catch (e: Exception) {
                Log.e("TARG", "Clear meals failed", e)
                _errorMessage.value = "Meal clear failed: ${e.message}"
            }
        }
    }

    fun deleteMeal(mealId: Int) {
        val token = _authToken.value ?: run {
            _actionMessage.value = "Login to sync meal deletes"
            return
        }
        viewModelScope.launch {
            try {
                repository.deleteMeal(token, mealId)
                    .onSuccess {
                        _actionMessage.value = "Meal deleted"
                        loadSavedMeals()
                        fetchUserStats()
                    }
                    .onFailure { handleRepositoryFailure(it, useActionMessage = true) }
            } catch (e: Exception) {
                Log.e("TARG", "Delete meal failed", e)
                _errorMessage.value = "Meal delete failed: ${e.message}"
            }
        }
    }

    fun logWorkout(focus: String, exercises: List<String>, duration: Int, caloriesBurned: Int) {
        val token = _authToken.value ?: run {
            _actionMessage.value = "Login to sync workouts"
            return
        }
        viewModelScope.launch {
            try {
                repository.logWorkout(token, LogWorkoutRequest(focus, exercises, duration, caloriesBurned))
                    .onSuccess {
                        _actionMessage.value = "Workout logged"
                        fetchUserStats()
                    }
                    .onFailure { handleRepositoryFailure(it) }
            } catch (e: Exception) {
                Log.e("TARG", "Log workout failed", e)
                _errorMessage.value = "Workout log failed: ${e.message}"
            }
        }
    }

    fun searchFoods(query: String, limit: Int = 12) {
        if (query.length < 2) {
            _foodResults.value = emptyList()
            return
        }
        viewModelScope.launch {
            try {
                _isFoodLoading.value = true
                repository.searchFoods(query, limit)
                    .onSuccess { _foodResults.value = it }
                    .onFailure { handleRepositoryFailure(it) }
            } catch (e: Exception) {
                _errorMessage.value = "Food search error: ${e.message}"
            } finally {
                _isFoodLoading.value = false
            }
        }
    }

    fun loadPopularFoods(limit: Int = 12) {
        viewModelScope.launch {
            try {
                _isFoodLoading.value = true
                repository.getPopularFoods(limit)
                    .onSuccess { _popularFoods.value = it }
            } catch (e: Exception) {
                Log.e("TARG", "Popular foods failed", e)
            } finally {
                _isFoodLoading.value = false
            }
        }
    }

    fun logWater(glasses: Int = 0, ml: Int = 0) {
        val token = _authToken.value ?: run {
            _actionMessage.value = "Login to sync water"
            return
        }
        viewModelScope.launch {
            try {
                repository.logWater(token, glasses, ml)
                    .onSuccess {
                        _waterData.value = it
                        _actionMessage.value = "Water updated"
                    }
                    .onFailure { handleRepositoryFailure(it) }
            } catch (e: Exception) {
                Log.e("TARG", "Log water failed", e)
                _errorMessage.value = "Water sync failed: ${e.message}"
            }
        }
    }

    fun loadWater() {
        val token = _authToken.value ?: return
        viewModelScope.launch {
            try {
                repository.getWater(token)
                    .onSuccess { _waterData.value = it }
                    .onFailure { handleRepositoryFailure(it) }
            } catch (e: Exception) {
                Log.e("TARG", "Load water failed", e)
            }
        }
    }

    fun saveMealPlan(planData: Map<String, Map<String, String>>) {
        val token = _authToken.value ?: run {
            _actionMessage.value = "Login to sync your meal plan"
            return
        }
        viewModelScope.launch {
            try {
                repository.saveMealPlan(token, SaveMealPlanRequest(planData))
                    .onSuccess {
                        _actionMessage.value = "Meal plan saved"
                        loadMealPlan()
                    }
                    .onFailure { handleRepositoryFailure(it, useActionMessage = true) }
            } catch (e: Exception) {
                _actionMessage.value = "Meal plan error: ${e.message}"
            }
        }
    }

    fun loadMealPlan() {
        val token = _authToken.value ?: return
        viewModelScope.launch {
            try {
                repository.getMealPlan(token)
                    .onSuccess { _mealPlan.value = it }
                    .onFailure { handleRepositoryFailure(it) }
            } catch (e: Exception) {
                Log.e("TARG", "Load meal plan failed", e)
            }
        }
    }

    fun clearError() { _errorMessage.value = null }
    fun clearActionMessage() { _actionMessage.value = null }
}
