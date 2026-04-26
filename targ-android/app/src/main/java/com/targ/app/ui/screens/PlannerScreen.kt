package com.targ.app.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.targ.app.ui.components.*
import com.targ.app.ui.theme.*
import com.targ.app.viewmodel.HealthViewModel

// ─── Meal data ───
private data class Meal(val name: String, val calories: Int, val protein: Int, val carbs: Int, val fat: Int)

private val breakfastOptions = listOf(
    Meal("Greek Yogurt Parfait", 350, 20, 45, 10),
    Meal("Avocado Toast + Eggs", 420, 22, 30, 25),
    Meal("Oatmeal Bowl", 380, 14, 58, 8),
    Meal("Smoothie Bowl", 340, 15, 50, 6),
    Meal("Egg White Omelette", 280, 30, 8, 14),
    Meal("Protein Pancakes", 390, 28, 42, 12),
)
private val lunchOptions = listOf(
    Meal("Grilled Chicken Salad", 480, 42, 18, 26),
    Meal("Quinoa Buddha Bowl", 520, 22, 65, 18),
    Meal("Turkey Wrap", 450, 35, 38, 16),
    Meal("Mediterranean Plate", 510, 25, 48, 24),
    Meal("Salmon Poke Bowl", 540, 38, 50, 20),
    Meal("Paneer Tikka Wrap", 490, 28, 40, 22),
)
private val dinnerOptions = listOf(
    Meal("Baked Salmon & Veggies", 550, 45, 20, 30),
    Meal("Chicken Stir Fry", 480, 38, 35, 20),
    Meal("Lean Beef Tacos", 520, 35, 40, 24),
    Meal("Vegetable Curry + Rice", 460, 14, 65, 16),
    Meal("Grilled Tofu Bowl", 420, 24, 45, 18),
    Meal("Dal + Roti + Salad", 440, 20, 55, 14),
)
private val snackOptions = listOf(
    Meal("🍌 Banana + Almonds", 180, 5, 25, 8),
    Meal("🥜 Protein Bar", 220, 20, 22, 8),
    Meal("🍎 Apple + PB", 250, 7, 30, 14),
    Meal("🥛 Greek Yogurt", 150, 15, 12, 5),
    Meal("None", 0, 0, 0, 0),
)

private val days = listOf("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
private val fullDays = listOf("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PlannerScreen(viewModel: HealthViewModel? = null) {

    // State for each day's meal selections
    val selectedBreakfast = remember { mutableStateMapOf<String, Int>().apply { days.forEach { put(it, 0) } } }
    val selectedLunch = remember { mutableStateMapOf<String, Int>().apply { days.forEach { put(it, 0) } } }
    val selectedDinner = remember { mutableStateMapOf<String, Int>().apply { days.forEach { put(it, 0) } } }
    val selectedSnack = remember { mutableStateMapOf<String, Int>().apply { days.forEach { put(it, 4) } } }

    var selectedDayIndex by remember { mutableIntStateOf(0) }
    val mealPlanState = viewModel?.mealPlan?.collectAsState()
    val actionMessageState = viewModel?.actionMessage?.collectAsState()
    val mealPlan = mealPlanState?.value
    val actionMessage = actionMessageState?.value

    fun buildPlanData(): Map<String, Map<String, String>> {
        return days.mapIndexed { index, day ->
            fullDays[index] to mapOf(
                "breakfast" to breakfastOptions[selectedBreakfast[day] ?: 0].name,
                "lunch" to lunchOptions[selectedLunch[day] ?: 0].name,
                "snack" to snackOptions[selectedSnack[day] ?: 4].name,
                "dinner" to dinnerOptions[selectedDinner[day] ?: 0].name
            )
        }.toMap()
    }

    fun applyPlan(planData: Map<String, Map<String, String>>) {
        fullDays.forEachIndexed { index, fullDay ->
            val shortDay = days[index]
            val dayPlan = planData[fullDay] ?: return@forEachIndexed
            selectedBreakfast[shortDay] = breakfastOptions.indexOfFirst { it.name == dayPlan["breakfast"] }.takeIf { it >= 0 } ?: 0
            selectedLunch[shortDay] = lunchOptions.indexOfFirst { it.name == dayPlan["lunch"] }.takeIf { it >= 0 } ?: 0
            selectedSnack[shortDay] = snackOptions.indexOfFirst { it.name == dayPlan["snack"] }.takeIf { it >= 0 } ?: 4
            selectedDinner[shortDay] = dinnerOptions.indexOfFirst { it.name == dayPlan["dinner"] }.takeIf { it >= 0 } ?: 0
        }
    }

    LaunchedEffect(viewModel) {
        viewModel?.loadMealPlan()
    }

    LaunchedEffect(mealPlan?.createdAt) {
        mealPlan?.planData?.let { applyPlan(it) }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(OffWhite)
            .verticalScroll(rememberScrollState())
            .padding(PagePadding),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        PageHeader(title = "📅 Weekly Meal Planner", subtitle = "Plan balanced meals for the whole week")

        // ─── DAY SELECTOR ───
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(6.dp)
        ) {
            days.forEachIndexed { i, day ->
                val isSelected = selectedDayIndex == i
                Surface(
                    shape = RoundedCornerShape(12.dp),
                    color = if (isSelected) PrimaryGreen else White,
                    shadowElevation = if (isSelected) 6.dp else 2.dp,
                    onClick = { selectedDayIndex = i },
                    modifier = Modifier.weight(1f)
                ) {
                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally,
                        modifier = Modifier.padding(vertical = 14.dp)
                    ) {
                        Text(day, fontSize = 13.sp, fontWeight = FontWeight.Bold,
                            color = if (isSelected) White else DarkText)

                        val dayTotal = getDayCalories(day, selectedBreakfast, selectedLunch, selectedDinner, selectedSnack)
                        Spacer(Modifier.height(2.dp))
                        Text("$dayTotal", fontSize = 10.sp,
                            color = if (isSelected) White.copy(alpha = 0.8f) else LightText)
                    }
                }
            }
        }

        val currentDay = days[selectedDayIndex]

        // ─── MEAL SELECTION ───
        TargCard {
            // Day header
            Surface(
                shape = RoundedCornerShape(12.dp),
                color = PrimaryGreen,
                modifier = Modifier.fillMaxWidth()
            ) {
                Row(
                    modifier = Modifier.padding(16.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text("📆 ${fullDays[selectedDayIndex]}", fontSize = 18.sp,
                        fontWeight = FontWeight.Bold, color = White)

                    val dayTotalCal = getDayCalories(currentDay, selectedBreakfast, selectedLunch, selectedDinner, selectedSnack)
                    Surface(shape = RoundedCornerShape(20.dp), color = White.copy(alpha = 0.2f)) {
                        Text("🔥 $dayTotalCal kcal", modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp),
                            color = White, fontSize = 13.sp, fontWeight = FontWeight.Medium)
                    }
                }
            }

            Spacer(Modifier.height(16.dp))

            MealSelector("🌅 Breakfast", breakfastOptions, selectedBreakfast[currentDay] ?: 0) { selectedBreakfast[currentDay] = it }
            Spacer(Modifier.height(12.dp))
            MealSelector("☀️ Lunch", lunchOptions, selectedLunch[currentDay] ?: 0) { selectedLunch[currentDay] = it }
            Spacer(Modifier.height(12.dp))
            MealSelector("🍫 Snack", snackOptions, selectedSnack[currentDay] ?: 4) { selectedSnack[currentDay] = it }
            Spacer(Modifier.height(12.dp))
            MealSelector("🌙 Dinner", dinnerOptions, selectedDinner[currentDay] ?: 0) { selectedDinner[currentDay] = it }
        }

        // ─── DAY NUTRITION BREAKDOWN ───
        TargCard {
            CardTitle("📊 ${fullDays[selectedDayIndex]} Nutrition", "")

            val b = breakfastOptions[selectedBreakfast[currentDay] ?: 0]
            val l = lunchOptions[selectedLunch[currentDay] ?: 0]
            val d = dinnerOptions[selectedDinner[currentDay] ?: 0]
            val s = snackOptions[selectedSnack[currentDay] ?: 4]

            val totalPro = b.protein + l.protein + d.protein + s.protein
            val totalCarbs = b.carbs + l.carbs + d.carbs + s.carbs
            val totalFat = b.fat + l.fat + d.fat + s.fat
            val totalCal = b.calories + l.calories + d.calories + s.calories

            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                StatCard("🔥", "$totalCal", "Calories", isPrimary = true, modifier = Modifier.weight(1f))
                StatCard("💪", "${totalPro}g", "Protein", modifier = Modifier.weight(1f))
                StatCard("🌾", "${totalCarbs}g", "Carbs", modifier = Modifier.weight(1f))
                StatCard("🥑", "${totalFat}g", "Fat", modifier = Modifier.weight(1f))
            }

            // Per-meal breakdown
            Spacer(Modifier.height(12.dp))
            listOf("🌅 Breakfast" to b, "☀️ Lunch" to l, "🍫 Snack" to s, "🌙 Dinner" to d).forEach { (label, meal) ->
                if (meal.calories > 0) {
                    Row(
                        modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text("$label: ${meal.name}", fontSize = 12.sp, color = DarkText,
                            modifier = Modifier.weight(1f))
                        Text("${meal.calories} kcal", fontSize = 12.sp, fontWeight = FontWeight.SemiBold,
                            color = PrimaryGreen)
                    }
                }
            }
        }

        // ─── WEEKLY SUMMARY ───
        TargCard {
            CardTitle("📊 Weekly Summary", "")

            val weekTotal = days.sumOf { day -> getDayCalories(day, selectedBreakfast, selectedLunch, selectedDinner, selectedSnack) }
            val weekProtein = days.sumOf { day -> getDayProtein(day, selectedBreakfast, selectedLunch, selectedDinner, selectedSnack) }
            val dailyAvg = weekTotal / 7

            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                StatCard("📊", "$weekTotal", "Total kcal", isPrimary = true, modifier = Modifier.weight(1f))
                StatCard("📈", "$dailyAvg", "Daily Avg", modifier = Modifier.weight(1f))
                StatCard("💪", "${weekProtein}g", "Protein", modifier = Modifier.weight(1f))
                StatCard("🍽️", "${days.size * 4}", "Meals", modifier = Modifier.weight(1f))
            }
        }

        // ─── CLOUD SYNC ───
        TargCard {
            CardTitle("☁️ Cloud Sync", "")
            Text(
                "Save this weekly plan to your account and load it later on the web or Android app.",
                fontSize = 13.sp,
                color = MediumText,
                lineHeight = 19.sp
            )
            Spacer(Modifier.height(12.dp))

            PrimaryButton(
                text = "💾 Save Weekly Plan",
                onClick = { viewModel?.saveMealPlan(buildPlanData()) }
            )
            Spacer(Modifier.height(10.dp))
            OutlinedButton(
                onClick = { viewModel?.loadMealPlan() },
                modifier = Modifier.fillMaxWidth().height(48.dp),
                shape = RoundedCornerShape(12.dp),
                colors = ButtonDefaults.outlinedButtonColors(contentColor = PrimaryGreen)
            ) {
                Text("↻ Load Saved Plan", fontWeight = FontWeight.SemiBold)
            }

            actionMessage?.let {
                Spacer(Modifier.height(10.dp))
                Surface(
                    shape = RoundedCornerShape(10.dp),
                    color = PaleGreen,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text(it, modifier = Modifier.padding(12.dp), fontSize = 13.sp, color = DarkGreen)
                }
            }
        }

        ExplanationBox("Select meals for each day of the week. Aim for a consistent daily calorie intake aligned with your health goals. Snacks are optional but help maintain energy levels.")

        Spacer(Modifier.height(24.dp))
    }
}

private fun getDayCalories(
    day: String,
    breakfast: Map<String, Int>, lunch: Map<String, Int>,
    dinner: Map<String, Int>, snack: Map<String, Int>
): Int {
    return breakfastOptions[breakfast[day] ?: 0].calories +
            lunchOptions[lunch[day] ?: 0].calories +
            dinnerOptions[dinner[day] ?: 0].calories +
            snackOptions[snack[day] ?: 4].calories
}

private fun getDayProtein(
    day: String,
    breakfast: Map<String, Int>, lunch: Map<String, Int>,
    dinner: Map<String, Int>, snack: Map<String, Int>
): Int {
    return breakfastOptions[breakfast[day] ?: 0].protein +
            lunchOptions[lunch[day] ?: 0].protein +
            dinnerOptions[dinner[day] ?: 0].protein +
            snackOptions[snack[day] ?: 4].protein
}

@Composable
private fun MealSelector(
    label: String,
    options: List<Meal>,
    selectedIndex: Int,
    onSelect: (Int) -> Unit
) {
    Column {
        Text(label, fontSize = 14.sp, fontWeight = FontWeight.SemiBold, color = DarkGreen)
        Spacer(Modifier.height(6.dp))

        options.forEachIndexed { i, meal ->
            val isSelected = i == selectedIndex
            Surface(
                shape = RoundedCornerShape(10.dp),
                color = if (isSelected) PaleGreen else OffWhite,
                onClick = { onSelect(i) },
                modifier = Modifier.fillMaxWidth().padding(vertical = 3.dp)
            ) {
                Row(
                    modifier = Modifier.padding(12.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.weight(1f)) {
                        RadioButton(
                            selected = isSelected,
                            onClick = { onSelect(i) },
                            colors = RadioButtonDefaults.colors(selectedColor = PrimaryGreen)
                        )
                        Column {
                            Text(meal.name, fontSize = 14.sp, color = DarkText,
                                fontWeight = if (isSelected) FontWeight.SemiBold else FontWeight.Normal)
                            if (meal.calories > 0) {
                                Text("${meal.protein}g pro · ${meal.carbs}g carbs · ${meal.fat}g fat",
                                    fontSize = 11.sp, color = LightText)
                            }
                        }
                    }
                    if (meal.calories > 0) {
                        NutrientBadge("🔥 ${meal.calories}", isSelected)
                    }
                }
            }
        }
    }
}
