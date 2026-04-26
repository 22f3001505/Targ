package com.targ.app.ui.screens

import androidx.compose.animation.animateContentSize
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.targ.app.ui.components.*
import com.targ.app.ui.theme.*
import com.targ.app.viewmodel.HealthViewModel

// ─── Quick-add presets ───
private data class QuickMeal(val name: String, val cal: Int, val pro: Int, val carbs: Int, val fat: Int)

private val quickMeals = listOf(
    QuickMeal("🥚 Boiled Eggs (2)", 140, 12, 1, 10),
    QuickMeal("🍌 Banana", 105, 1, 27, 0),
    QuickMeal("🥛 Protein Shake", 200, 30, 10, 5),
    QuickMeal("🍗 Chicken Breast (150g)", 250, 46, 0, 5),
    QuickMeal("🍚 Rice (1 cup)", 205, 4, 45, 0),
    QuickMeal("🥗 Mixed Salad", 150, 5, 12, 8),
    QuickMeal("🍞 PB Toast", 320, 12, 30, 18),
    QuickMeal("🥩 Paneer (100g)", 265, 18, 1, 20),
    QuickMeal("🍳 Omelette (3 eggs)", 280, 21, 2, 21),
    QuickMeal("🥣 Oats + Milk", 310, 13, 50, 7),
)

@Composable
fun MacroScreen(viewModel: HealthViewModel? = null) {

    // ─── Local state for goals and logged meals ───
    var calorieGoal by remember { mutableIntStateOf(2000) }
    var proteinGoal by remember { mutableIntStateOf(150) }
    var carbsGoal by remember { mutableIntStateOf(250) }
    var fatGoal by remember { mutableIntStateOf(65) }

    var caloriesCurrent by remember { mutableIntStateOf(0) }
    var proteinCurrent by remember { mutableIntStateOf(0) }
    var carbsCurrent by remember { mutableIntStateOf(0) }
    var fatCurrent by remember { mutableIntStateOf(0) }

    var mealName by remember { mutableStateOf("") }
    var mealCalories by remember { mutableStateOf("400") }
    var mealProtein by remember { mutableStateOf("30") }
    var mealCarbs by remember { mutableStateOf("40") }
    var mealFat by remember { mutableStateOf("15") }

    val meals = remember { mutableStateListOf<Map<String, String>>() }
    var loadedServerMeals by remember { mutableStateOf(false) }

    // ─── Water tracker ───
    var waterGlasses by remember { mutableIntStateOf(0) }
    val waterGoal = 8

    // ─── Backend-powered food search ───
    var foodQuery by remember { mutableStateOf("") }
    val savedMealsState = viewModel?.savedMeals?.collectAsState()
    val foodResultsState = viewModel?.foodResults?.collectAsState()
    val popularFoodsState = viewModel?.popularFoods?.collectAsState()
    val waterDataState = viewModel?.waterData?.collectAsState()
    val isFoodLoadingState = viewModel?.isFoodLoading?.collectAsState()
    val savedMeals = savedMealsState?.value ?: emptyList()
    val foodResults = foodResultsState?.value ?: emptyList()
    val popularFoods = popularFoodsState?.value ?: emptyList()
    val waterData = waterDataState?.value
    val isFoodLoading = isFoodLoadingState?.value ?: false

    fun addMeal(name: String, cal: Int, pro: Int, carbs: Int, fat: Int) {
        meals.add(mapOf(
            "name" to name, "cal" to "$cal",
            "pro" to "$pro", "carbs" to "$carbs", "fat" to "$fat"
        ))
        caloriesCurrent += cal
        proteinCurrent += pro
        carbsCurrent += carbs
        fatCurrent += fat
        viewModel?.saveMeal(name, cal.toDouble(), pro.toDouble(), carbs.toDouble(), fat.toDouble())
    }

    LaunchedEffect(viewModel) {
        viewModel?.loadSavedMeals()
        viewModel?.loadPopularFoods()
        viewModel?.loadWater()
    }

    LaunchedEffect(savedMeals) {
        if (!loadedServerMeals && meals.isEmpty()) {
            val trackedMeals = savedMeals.filter { it.mealType == "tracked" }
            trackedMeals.forEach {
                meals.add(mapOf(
                    "name" to it.mealName,
                    "cal" to it.calories.toInt().toString(),
                    "pro" to it.protein.toInt().toString(),
                    "carbs" to it.carbs.toInt().toString(),
                    "fat" to it.fat.toInt().toString()
                ))
            }
            caloriesCurrent = trackedMeals.sumOf { it.calories.toInt() }
            proteinCurrent = trackedMeals.sumOf { it.protein.toInt() }
            carbsCurrent = trackedMeals.sumOf { it.carbs.toInt() }
            fatCurrent = trackedMeals.sumOf { it.fat.toInt() }
            loadedServerMeals = true
        }
    }

    LaunchedEffect(waterData?.glasses) {
        waterData?.let { waterGlasses = it.glasses }
    }

    // ─── Custom goal editing ───
    var editingGoals by remember { mutableStateOf(false) }
    var goalCalInput by remember { mutableStateOf("2000") }
    var goalProInput by remember { mutableStateOf("150") }
    var goalCarbInput by remember { mutableStateOf("250") }
    var goalFatInput by remember { mutableStateOf("65") }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(OffWhite)
            .verticalScroll(rememberScrollState())
            .padding(PagePadding),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        PageHeader(title = "📊 Macro Tracker", subtitle = "Track nutrition, water & daily goals")

        // ─── GOALS (editable) ───
        TargCard {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                CardTitle("🎯 Daily Goals", "")
                Surface(
                    shape = RoundedCornerShape(8.dp),
                    color = if (editingGoals) PrimaryGreen else PaleGreen,
                    onClick = {
                        if (editingGoals) {
                            calorieGoal = goalCalInput.toIntOrNull() ?: 2000
                            proteinGoal = goalProInput.toIntOrNull() ?: 150
                            carbsGoal = goalCarbInput.toIntOrNull() ?: 250
                            fatGoal = goalFatInput.toIntOrNull() ?: 65
                        }
                        editingGoals = !editingGoals
                    }
                ) {
                    Text(
                        if (editingGoals) "✅ Save" else "✏️ Edit",
                        modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp),
                        fontSize = 12.sp, fontWeight = FontWeight.Medium,
                        color = if (editingGoals) White else DarkGreen
                    )
                }
            }

            if (editingGoals) {
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    OutlinedTextField(
                        value = goalCalInput, onValueChange = { goalCalInput = it },
                        label = { Text("Cal", fontSize = 11.sp) },
                        modifier = Modifier.weight(1f), singleLine = true,
                        shape = RoundedCornerShape(10.dp)
                    )
                    OutlinedTextField(
                        value = goalProInput, onValueChange = { goalProInput = it },
                        label = { Text("Pro", fontSize = 11.sp) },
                        modifier = Modifier.weight(1f), singleLine = true,
                        shape = RoundedCornerShape(10.dp)
                    )
                    OutlinedTextField(
                        value = goalCarbInput, onValueChange = { goalCarbInput = it },
                        label = { Text("Carb", fontSize = 11.sp) },
                        modifier = Modifier.weight(1f), singleLine = true,
                        shape = RoundedCornerShape(10.dp)
                    )
                    OutlinedTextField(
                        value = goalFatInput, onValueChange = { goalFatInput = it },
                        label = { Text("Fat", fontSize = 11.sp) },
                        modifier = Modifier.weight(1f), singleLine = true,
                        shape = RoundedCornerShape(10.dp)
                    )
                }
            } else {
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                    StatCard("🔥", "$calorieGoal", "kcal", isPrimary = true, modifier = Modifier.weight(1f))
                    StatCard("💪", "${proteinGoal}g", "Protein", modifier = Modifier.weight(1f))
                    StatCard("🌾", "${carbsGoal}g", "Carbs", modifier = Modifier.weight(1f))
                    StatCard("🥑", "${fatGoal}g", "Fat", modifier = Modifier.weight(1f))
                }
            }
        }

        // ─── PROGRESS BARS ───
        TargCard {
            CardTitle("📈 Progress", "")
            MacroProgressBar("Calories", "🔥", caloriesCurrent, calorieGoal, PrimaryGreen)
            MacroProgressBar("Protein", "💪", proteinCurrent, proteinGoal, DarkGreen)
            MacroProgressBar("Carbs", "🌾", carbsCurrent, carbsGoal, SoftMint)
            MacroProgressBar("Fat", "🥑", fatCurrent, fatGoal, BmiUnderweight)
        }

        // ─── 💧 WATER TRACKER ───
        TargCard {
            CardTitle("💧 Water Intake", "")
            Text("Goal: $waterGoal glasses (2L)", fontSize = 13.sp, color = MediumText)
            Spacer(Modifier.height(12.dp))

            // Water glass visualization
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(6.dp)
            ) {
                for (i in 1..waterGoal) {
                    val isFilled = i <= waterGlasses
                    Surface(
                        shape = RoundedCornerShape(10.dp),
                        color = if (isFilled) PrimaryGreen.copy(alpha = 0.8f) else PaleGreen,
                        onClick = {
                            val diff = i - waterGlasses
                            waterGlasses = i
                            if (diff > 0) viewModel?.logWater(glasses = diff)
                        },
                        modifier = Modifier.weight(1f).height(48.dp)
                    ) {
                        Box(contentAlignment = Alignment.Center) {
                            Text(
                                if (isFilled) "💧" else "○",
                                fontSize = if (isFilled) 18.sp else 14.sp,
                                color = if (isFilled) White else LightText
                            )
                        }
                    }
                }
            }
            Spacer(Modifier.height(10.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text("$waterGlasses / $waterGoal glasses", fontSize = 14.sp,
                    fontWeight = FontWeight.SemiBold, color = DarkGreen)

                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Surface(
                        shape = RoundedCornerShape(8.dp), color = PaleGreen,
                        onClick = { if (waterGlasses > 0) waterGlasses-- }
                    ) {
                        Text("➖", modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp))
                    }
                    Surface(
                        shape = RoundedCornerShape(8.dp), color = PrimaryGreen,
                        onClick = {
                            if (waterGlasses < 15) waterGlasses++
                            viewModel?.logWater(glasses = 1)
                        }
                    ) {
                        Text("➕", modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp))
                    }
                }
            }
            Spacer(Modifier.height(6.dp))
            LinearProgressIndicator(
                progress = { (waterGlasses.toFloat() / waterGoal).coerceIn(0f, 1f) },
                modifier = Modifier.fillMaxWidth().height(8.dp).clip(RoundedCornerShape(4.dp)),
                color = PrimaryGreen, trackColor = PaleGreen,
            )
        }

        // ─── ⚡ QUICK ADD ───
        TargCard {
            CardTitle("⚡ Quick Add", "")
            Text("Tap to instantly log common foods:", fontSize = 13.sp, color = MediumText)
            Spacer(Modifier.height(10.dp))

            FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)) {
                quickMeals.forEach { qm ->
                    Surface(
                        shape = RoundedCornerShape(12.dp),
                        color = PaleGreen,
                        onClick = {
                            meals.add(mapOf(
                                "name" to qm.name, "cal" to "${qm.cal}",
                                "pro" to "${qm.pro}", "carbs" to "${qm.carbs}", "fat" to "${qm.fat}"
                            ))
                            caloriesCurrent += qm.cal
                            proteinCurrent += qm.pro
                            carbsCurrent += qm.carbs
                            fatCurrent += qm.fat
                            viewModel?.saveMeal(qm.name, qm.cal.toDouble(), qm.pro.toDouble(),
                                qm.carbs.toDouble(), qm.fat.toDouble())
                        }
                    ) {
                        Column(modifier = Modifier.padding(10.dp)) {
                            Text(qm.name, fontSize = 12.sp, fontWeight = FontWeight.Medium, color = DarkText)
                            Text("${qm.cal} kcal · ${qm.pro}g pro", fontSize = 10.sp, color = MediumText)
                        }
                    }
                }
            }
        }

        // ─── BACKEND FOOD SEARCH ───
        TargCard {
            CardTitle("🔍 Food Search", "")
            Text("Search real recipe nutrition data from the backend dataset.",
                fontSize = 13.sp, color = MediumText)
            Spacer(Modifier.height(10.dp))

            OutlinedTextField(
                value = foodQuery,
                onValueChange = {
                    foodQuery = it
                    viewModel?.searchFoods(it)
                },
                label = { Text("Search food") },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true,
                shape = RoundedCornerShape(12.dp),
                placeholder = { Text("e.g., chicken, oats, paneer") }
            )

            if (isFoodLoading) {
                Spacer(Modifier.height(12.dp))
                LinearProgressIndicator(
                    modifier = Modifier.fillMaxWidth().height(6.dp).clip(RoundedCornerShape(3.dp)),
                    color = PrimaryGreen,
                    trackColor = PaleGreen
                )
            }

            val foodsToShow = if (foodQuery.length >= 2) foodResults else popularFoods
            if (foodsToShow.isNotEmpty()) {
                Spacer(Modifier.height(12.dp))
                Text(
                    if (foodQuery.length >= 2) "Results" else "Popular foods",
                    fontSize = 13.sp,
                    fontWeight = FontWeight.SemiBold,
                    color = DarkText
                )
                Spacer(Modifier.height(8.dp))
                foodsToShow.take(8).forEach { food ->
                    Surface(
                        shape = RoundedCornerShape(12.dp),
                        color = OffWhite,
                        onClick = {
                            addMeal(
                                food.name,
                                food.calories.toInt(),
                                food.protein.toInt(),
                                food.carbs.toInt(),
                                food.fat.toInt()
                            )
                        },
                        modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp)
                    ) {
                        Row(
                            modifier = Modifier.padding(12.dp),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Column(modifier = Modifier.weight(1f)) {
                                Text(food.name, fontSize = 13.sp,
                                    fontWeight = FontWeight.SemiBold, color = DarkText)
                                Text(food.serving, fontSize = 11.sp, color = LightText)
                            }
                            Row(horizontalArrangement = Arrangement.spacedBy(5.dp)) {
                                NutrientBadge("🔥${food.calories.toInt()}", true)
                                NutrientBadge("💪${food.protein.toInt()}g")
                            }
                        }
                    }
                }
            }
        }

        // ─── MANUAL LOG ───
        TargCard {
            CardTitle("🍽️ Log Custom Meal", "")

            OutlinedTextField(
                value = mealName, onValueChange = { mealName = it },
                label = { Text("Meal Name", color = DarkText) },
                modifier = Modifier.fillMaxWidth(), singleLine = true,
                shape = RoundedCornerShape(12.dp),
                placeholder = { Text("e.g., Chicken Salad") }
            )
            Spacer(Modifier.height(10.dp))

            Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                OutlinedTextField(
                    value = mealCalories, onValueChange = { mealCalories = it },
                    label = { Text("Cal", color = DarkText) },
                    modifier = Modifier.weight(1f), singleLine = true,
                    shape = RoundedCornerShape(12.dp)
                )
                OutlinedTextField(
                    value = mealProtein, onValueChange = { mealProtein = it },
                    label = { Text("Pro", color = DarkText) },
                    modifier = Modifier.weight(1f), singleLine = true,
                    shape = RoundedCornerShape(12.dp)
                )
            }
            Spacer(Modifier.height(8.dp))

            Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                OutlinedTextField(
                    value = mealCarbs, onValueChange = { mealCarbs = it },
                    label = { Text("Carbs", color = DarkText) },
                    modifier = Modifier.weight(1f), singleLine = true,
                    shape = RoundedCornerShape(12.dp)
                )
                OutlinedTextField(
                    value = mealFat, onValueChange = { mealFat = it },
                    label = { Text("Fat", color = DarkText) },
                    modifier = Modifier.weight(1f), singleLine = true,
                    shape = RoundedCornerShape(12.dp)
                )
            }
            Spacer(Modifier.height(16.dp))

            PrimaryButton(
                text = "➕ Add Meal",
                onClick = {
                    if (mealName.isNotBlank()) {
                        val cal = mealCalories.toIntOrNull() ?: 0
                        val pro = mealProtein.toIntOrNull() ?: 0
                        val carb = mealCarbs.toIntOrNull() ?: 0
                        val f = mealFat.toIntOrNull() ?: 0

                        addMeal(mealName, cal, pro, carb, f)
                        mealName = ""
                    }
                }
            )
        }

        // ─── TODAY'S MEALS (with delete) ───
        TargCard {
            CardTitle("📋 Today's Meals (${meals.size})", "")

            if (meals.isEmpty()) {
                Column(
                    modifier = Modifier.fillMaxWidth().padding(24.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text("🍽️", fontSize = 32.sp)
                    Spacer(Modifier.height(8.dp))
                    Text("No meals logged yet", fontSize = 14.sp, color = MediumText)
                    Text("Use Quick Add or log a custom meal", fontSize = 12.sp, color = LightText)
                }
            } else {
                meals.forEachIndexed { index, meal ->
                    Surface(
                        shape = RoundedCornerShape(12.dp),
                        color = OffWhite,
                        modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp)
                            .animateContentSize()
                    ) {
                        Row(
                            modifier = Modifier.padding(14.dp),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Column(modifier = Modifier.weight(1f)) {
                                Text(meal["name"] ?: "", fontWeight = FontWeight.SemiBold,
                                    color = DarkText, fontSize = 14.sp)
                                Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                                    NutrientBadge("🔥${meal["cal"]}", true)
                                    NutrientBadge("💪${meal["pro"]}")
                                    NutrientBadge("🌾${meal["carbs"]}")
                                }
                            }
                            // Delete button
                            Surface(
                                shape = RoundedCornerShape(8.dp),
                                color = BmiObese.copy(alpha = 0.1f),
                                onClick = {
                                    val removed = meals[index]
                                    caloriesCurrent -= (removed["cal"]?.toIntOrNull() ?: 0)
                                    proteinCurrent -= (removed["pro"]?.toIntOrNull() ?: 0)
                                    carbsCurrent -= (removed["carbs"]?.toIntOrNull() ?: 0)
                                    fatCurrent -= (removed["fat"]?.toIntOrNull() ?: 0)
                                    meals.removeAt(index)
                                }
                            ) {
                                Text("🗑", modifier = Modifier.padding(8.dp), fontSize = 16.sp)
                            }
                        }
                    }
                }

                // Clear all
                Spacer(Modifier.height(8.dp))
                OutlinedButton(
                    onClick = {
                        meals.clear()
                        caloriesCurrent = 0; proteinCurrent = 0
                        carbsCurrent = 0; fatCurrent = 0
                        loadedServerMeals = true
                        viewModel?.clearTrackedMeals()
                    },
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(10.dp),
                    colors = ButtonDefaults.outlinedButtonColors(contentColor = BmiObese)
                ) {
                    Text("🗑️ Clear All Meals", fontWeight = FontWeight.Medium)
                }
            }
        }

        // ─── SUMMARY ───
        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
            StatCard("🔥", "$caloriesCurrent", "Consumed", isPrimary = true, modifier = Modifier.weight(1f))
            StatCard("🎯", "${(calorieGoal - caloriesCurrent).coerceAtLeast(0)}", "Remaining", modifier = Modifier.weight(1f))
        }

        // Macro split
        if (caloriesCurrent > 0) {
            TargCard {
                CardTitle("🥧 Macro Split", "")
                val totalMacroCal = (proteinCurrent * 4) + (carbsCurrent * 4) + (fatCurrent * 9)
                if (totalMacroCal > 0) {
                    val proPct = (proteinCurrent * 4 * 100) / totalMacroCal
                    val carbPct = (carbsCurrent * 4 * 100) / totalMacroCal
                    val fatPct = (fatCurrent * 9 * 100) / totalMacroCal

                    Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                        StatCard("💪", "$proPct%", "Protein", modifier = Modifier.weight(1f))
                        StatCard("🌾", "$carbPct%", "Carbs", modifier = Modifier.weight(1f))
                        StatCard("🥑", "$fatPct%", "Fat", modifier = Modifier.weight(1f))
                    }
                }
            }
        }

        ExplanationBox("Track your macros daily to stay within your nutritional targets. " +
            "Consistent tracking leads to better outcomes. Aim for 8 glasses of water daily.")

        Spacer(Modifier.height(24.dp))
    }
}
