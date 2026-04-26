package com.targ.app.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.targ.app.ui.components.*
import com.targ.app.ui.theme.*
import com.targ.app.viewmodel.HealthViewModel

@Composable
fun WorkoutScreen(viewModel: HealthViewModel) {

    val healthData by viewModel.healthData.collectAsState()
    val exercises by viewModel.exercises.collectAsState()
    val categories by viewModel.exerciseCategories.collectAsState()
    val calorieEstimate by viewModel.calorieEstimate.collectAsState()
    val isExerciseLoading by viewModel.isExerciseLoading.collectAsState()
    val actionMessage by viewModel.actionMessage.collectAsState()
    val errorMessage by viewModel.errorMessage.collectAsState()

    // Load exercises on first render
    LaunchedEffect(Unit) {
        if (exercises.isEmpty()) viewModel.fetchExercises()
    }

    var selectedCategory by remember { mutableStateOf<String?>(null) }
    var selectedExercise by remember { mutableStateOf("") }
    var weightInput by remember { mutableStateOf("70") }
    var durationInput by remember { mutableStateOf("30") }

    // Workout log state
    val workoutLog = remember { mutableStateListOf<Map<String, String>>() }
    var totalCalBurned by remember { mutableIntStateOf(0) }
    var totalDuration by remember { mutableIntStateOf(0) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(OffWhite)
            .verticalScroll(rememberScrollState())
            .padding(PagePadding),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        PageHeader(title = "🏋️ Workout Plans", subtitle = "Personalized exercise routines & calorie calculator")

        actionMessage?.let {
            MessageBanner(it, onDismiss = { viewModel.clearActionMessage() })
        }
        errorMessage?.let {
            MessageBanner(it, isError = true, onDismiss = { viewModel.clearError() })
        }

        // ─── FLOW LOCK ───
        if (!viewModel.isHealthAnalyzed) {
            FlowLockCard("Complete your Health Analysis on the Diet tab first to unlock personalized workout recommendations.")

            // Still show the exercise calculator even without health analysis
            ExerciseCalculatorSection(
                exercises, categories, selectedCategory, selectedExercise,
                weightInput, durationInput, calorieEstimate, isExerciseLoading,
                onCategoryChange = { selectedCategory = it; viewModel.fetchExercises(it) },
                onExerciseChange = { selectedExercise = it },
                onWeightChange = { weightInput = it },
                onDurationChange = { durationInput = it },
                onCalculate = {
                    if (selectedExercise.isNotBlank()) {
                        viewModel.estimateCalories(
                            selectedExercise,
                            weightInput.toDoubleOrNull() ?: 70.0,
                            durationInput.toIntOrNull() ?: 30
                        )
                    }
                },
                onLogExercise = { name, cal, dur ->
                    workoutLog.add(mapOf("name" to name, "cal" to "$cal", "dur" to "$dur"))
                    totalCalBurned += cal
                    totalDuration += dur
                    viewModel.logWorkout(name, listOf(name), dur, cal)
                }
            )

            // Show workout log even without health analysis
            if (workoutLog.isNotEmpty()) {
                WorkoutLogSection(workoutLog, totalCalBurned, totalDuration)
            }

            Spacer(Modifier.height(24.dp))
            return
        }

        healthData?.let { data ->

            // BMI Status Card
            TargCard {
                CardTitle("📊 Your Profile", "")
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text("BMI: ${data.bmi}", fontSize = 20.sp, fontWeight = FontWeight.Bold, color = DarkGreen)
                        Text(data.bmiCategory.status, fontSize = 13.sp, color = MediumText)
                    }
                    BmiCategoryBadge(data.bmiCategory.category)
                }
            }

            // Workout Focus Card
            Surface(
                shape = RoundedCornerShape(20.dp),
                color = PrimaryGreen,
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(24.dp)) {
                    Text("🎯 ${data.workoutPlan.focus}", fontSize = 22.sp,
                        fontWeight = FontWeight.Bold, color = White)
                    Spacer(Modifier.height(20.dp))

                    data.workoutPlan.exercises.forEachIndexed { i, exercise ->
                        Surface(
                            shape = RoundedCornerShape(12.dp),
                            color = White.copy(alpha = 0.15f),
                            modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp)
                        ) {
                            Row(
                                modifier = Modifier.padding(14.dp),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Surface(shape = RoundedCornerShape(50), color = White.copy(alpha = 0.25f)) {
                                    Text("${i + 1}", modifier = Modifier.padding(horizontal = 11.dp, vertical = 5.dp),
                                        fontWeight = FontWeight.Bold, color = White, fontSize = 14.sp)
                                }
                                Spacer(Modifier.width(14.dp))
                                Text(exercise, color = White, fontSize = 15.sp)
                            }
                        }
                    }
                }
            }

            // Tips
            TargCard {
                CardTitle("💡 Pro Tips", "")
                Text(data.workoutPlan.tips, fontSize = 14.sp, color = MediumText, lineHeight = 22.sp)
            }

            // Weekly Schedule
            TargCard {
                CardTitle("📅 Sample Weekly Schedule", "")

                val schedule = listOf(
                    "Mon" to "Strength", "Tue" to "Cardio", "Wed" to "Rest",
                    "Thu" to "HIIT", "Fri" to "Strength", "Sat" to "Cardio", "Sun" to "Rest"
                )

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(6.dp)
                ) {
                    schedule.forEach { (day, activity) ->
                        val isRest = activity == "Rest"
                        Surface(
                            shape = RoundedCornerShape(10.dp),
                            color = if (isRest) LightGray else PrimaryGreen,
                            modifier = Modifier.weight(1f)
                        ) {
                            Column(
                                horizontalAlignment = Alignment.CenterHorizontally,
                                modifier = Modifier.padding(vertical = 12.dp, horizontal = 4.dp)
                            ) {
                                Text(day, fontSize = 11.sp, fontWeight = FontWeight.Bold,
                                    color = if (isRest) MediumText else White)
                                Spacer(Modifier.height(4.dp))
                                Text(
                                    if (isRest) "😴" else "💪",
                                    fontSize = 14.sp
                                )
                                Spacer(Modifier.height(2.dp))
                                Text(activity, fontSize = 9.sp,
                                    color = if (isRest) LightText else White.copy(alpha = 0.85f))
                            }
                        }
                    }
                }
            }

            // Calorie targets
            TargCard {
                CardTitle("🔥 Daily Calorie Targets", "")
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                    StatCard("🔥", "${data.dailyCalories.maintenance}", "Maintain", isPrimary = true, modifier = Modifier.weight(1f))
                    StatCard("📉", "${data.dailyCalories.weightLoss}", "Lose", modifier = Modifier.weight(1f))
                    StatCard("📈", "${data.dailyCalories.mildGain}", "Gain", modifier = Modifier.weight(1f))
                }
            }
        }

        // ─── EXERCISE CALORIE CALCULATOR ───
        ExerciseCalculatorSection(
            exercises, categories, selectedCategory, selectedExercise,
            weightInput, durationInput, calorieEstimate, isExerciseLoading,
            onCategoryChange = { selectedCategory = it; viewModel.fetchExercises(it) },
            onExerciseChange = { selectedExercise = it },
            onWeightChange = { weightInput = it },
            onDurationChange = { durationInput = it },
            onCalculate = {
                if (selectedExercise.isNotBlank()) {
                    viewModel.estimateCalories(
                        selectedExercise,
                        weightInput.toDoubleOrNull() ?: 70.0,
                        durationInput.toIntOrNull() ?: 30
                    )
                }
            },
            onLogExercise = { name, cal, dur ->
                workoutLog.add(mapOf("name" to name, "cal" to "$cal", "dur" to "$dur"))
                totalCalBurned += cal
                totalDuration += dur
                viewModel.logWorkout(name, listOf(name), dur, cal)
            }
        )

        // ─── WORKOUT LOG ───
        if (workoutLog.isNotEmpty()) {
            WorkoutLogSection(workoutLog, totalCalBurned, totalDuration)
        }

        ExplanationBox(
            "Exercise calorie estimates use MET values from the Compendium of Physical Activities. " +
            "Formula: MET × weight(kg) × duration(hrs). Always warm up before exercise."
        )

        Spacer(Modifier.height(24.dp))
    }
}

@Composable
private fun WorkoutLogSection(
    log: List<Map<String, String>>,
    totalCal: Int,
    totalDur: Int
) {
    TargCard {
        CardTitle("📋 Today's Workout Log (${log.size})", "")

        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
            StatCard("🔥", "$totalCal", "Cal Burned", isPrimary = true, modifier = Modifier.weight(1f))
            StatCard("⏱", "$totalDur min", "Duration", modifier = Modifier.weight(1f))
            StatCard("🏋️", "${log.size}", "Exercises", modifier = Modifier.weight(1f))
        }

        Spacer(Modifier.height(12.dp))

        log.forEach { entry ->
            Surface(
                shape = RoundedCornerShape(10.dp),
                color = OffWhite,
                modifier = Modifier.fillMaxWidth().padding(vertical = 3.dp)
            ) {
                Row(
                    modifier = Modifier.padding(14.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(entry["name"] ?: "", fontWeight = FontWeight.Medium,
                        color = DarkText, fontSize = 13.sp, modifier = Modifier.weight(1f))
                    Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                        NutrientBadge("🔥${entry["cal"]}", true)
                        NutrientBadge("⏱${entry["dur"]}m")
                    }
                }
            }
        }
    }
}

@Composable
private fun ExerciseCalculatorSection(
    exercises: List<com.targ.app.data.model.ExerciseItem>,
    categories: List<String>,
    selectedCategory: String?,
    selectedExercise: String,
    weightInput: String,
    durationInput: String,
    calorieEstimate: com.targ.app.data.model.CalorieEstimateResponse?,
    isLoading: Boolean,
    onCategoryChange: (String?) -> Unit,
    onExerciseChange: (String) -> Unit,
    onWeightChange: (String) -> Unit,
    onDurationChange: (String) -> Unit,
    onCalculate: () -> Unit,
    onLogExercise: (String, Int, Int) -> Unit = { _, _, _ -> }
) {
    TargCard {
        CardTitle("🔥 Exercise Calorie Calculator", "")
        Text("Select an exercise to estimate calories burned using MET values.",
            fontSize = 13.sp, color = MediumText, lineHeight = 19.sp)
        Spacer(Modifier.height(12.dp))

        // Category filter chips
        if (categories.isNotEmpty()) {
            Text("Category", fontSize = 13.sp, fontWeight = FontWeight.Medium, color = DarkText)
            Spacer(Modifier.height(6.dp))
            FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                FilterChip(
                    selected = selectedCategory == null,
                    onClick = { onCategoryChange(null) },
                    label = { Text("All", fontSize = 12.sp) },
                    colors = FilterChipDefaults.filterChipColors(
                        selectedContainerColor = PrimaryGreen,
                        selectedLabelColor = White
                    )
                )
                categories.take(6).forEach { cat ->
                    FilterChip(
                        selected = selectedCategory == cat,
                        onClick = { onCategoryChange(cat) },
                        label = { Text(cat, fontSize = 12.sp) },
                        colors = FilterChipDefaults.filterChipColors(
                            selectedContainerColor = PrimaryGreen,
                            selectedLabelColor = White
                        )
                    )
                }
            }
            Spacer(Modifier.height(12.dp))
        }

        // Exercise picker
        if (exercises.isNotEmpty()) {
            Text("Exercise (${exercises.size} available)", fontSize = 13.sp,
                fontWeight = FontWeight.Medium, color = DarkText)
            Spacer(Modifier.height(6.dp))
            FlowRow(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                exercises.take(12).forEach { ex ->
                    FilterChip(
                        selected = selectedExercise == ex.name,
                        onClick = { onExerciseChange(ex.name) },
                        label = {
                            Text("${ex.name} (${ex.met})", fontSize = 11.sp,
                                maxLines = 1)
                        },
                        colors = FilterChipDefaults.filterChipColors(
                            selectedContainerColor = DarkGreen,
                            selectedLabelColor = White
                        )
                    )
                }
            }
            Spacer(Modifier.height(12.dp))
        }

        // Weight and Duration inputs
        Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
            OutlinedTextField(
                value = weightInput, onValueChange = onWeightChange,
                label = { Text("Weight (kg)") },
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                modifier = Modifier.weight(1f), singleLine = true,
                shape = RoundedCornerShape(12.dp)
            )
            OutlinedTextField(
                value = durationInput, onValueChange = onDurationChange,
                label = { Text("Duration (min)") },
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                modifier = Modifier.weight(1f), singleLine = true,
                shape = RoundedCornerShape(12.dp)
            )
        }
        Spacer(Modifier.height(16.dp))

        PrimaryButton(
            text = "🔥 Calculate Calories",
            onClick = onCalculate,
            isLoading = isLoading
        )

        // Result
        calorieEstimate?.let { result ->
            Spacer(Modifier.height(16.dp))
            Surface(
                shape = RoundedCornerShape(16.dp),
                color = PaleGreen,
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(
                    modifier = Modifier.padding(20.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text("🔥", fontSize = 32.sp)
                    Spacer(Modifier.height(8.dp))
                    Text("${result.caloriesBurned}", fontSize = 40.sp,
                        fontWeight = FontWeight.ExtraBold, color = DarkGreen)
                    Text("calories burned", fontSize = 14.sp, color = MediumText)
                    Spacer(Modifier.height(10.dp))
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        NutrientBadge("MET: ${result.met}", true)
                        NutrientBadge("${result.durationMinutes} min")
                        NutrientBadge("${result.weightKg} kg")
                    }
                    Spacer(Modifier.height(6.dp))
                    Text("Source: ${result.source}", fontSize = 11.sp, color = LightText)

                    // Log exercise button
                    Spacer(Modifier.height(12.dp))
                    OutlinedButton(
                        onClick = {
                            onLogExercise(result.exercise, result.caloriesBurned, result.durationMinutes)
                        },
                        shape = RoundedCornerShape(10.dp),
                        colors = ButtonDefaults.outlinedButtonColors(contentColor = PrimaryGreen)
                    ) {
                        Text("📋 Log This Exercise", fontWeight = FontWeight.SemiBold)
                    }
                }
            }
        }
    }
}
