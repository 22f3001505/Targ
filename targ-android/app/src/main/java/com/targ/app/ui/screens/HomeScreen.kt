package com.targ.app.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import com.targ.app.ui.components.*
import com.targ.app.ui.theme.*
import com.targ.app.viewmodel.HealthViewModel

// Daily health tips that rotate
private val healthTips = listOf(
    "💡 Drink a glass of water right after waking up to kickstart your metabolism.",
    "💡 Eating protein with every meal helps maintain muscle mass and keeps you full.",
    "💡 Aim for 7-9 hours of sleep — poor sleep increases cortisol and promotes fat storage.",
    "💡 Take a 10-minute walk after meals to lower blood sugar spikes by up to 30%.",
    "💡 Eating slowly helps you consume fewer calories — your brain takes 20 min to register fullness.",
    "💡 Replace sugary drinks with water or green tea to save 200-500 calories daily.",
    "💡 Fiber-rich foods (oats, beans, veggies) keep you full longer and aid digestion.",
    "💡 Strength training boosts your resting metabolic rate — burn more calories even at rest.",
    "💡 Stress can increase belly fat. Try 5 minutes of deep breathing or meditation daily.",
    "💡 Colorful plates = better nutrition. Aim for 3+ colors of vegetables per meal.",
)

@Composable
fun HomeScreen(navController: NavController, viewModel: HealthViewModel) {

    val healthData by viewModel.healthData.collectAsState()
    val apiStatus by viewModel.apiStatus.collectAsState()

    // Compute stats from API or use defaults
    val recipeCount = apiStatus?.let { formatLargeCount(it.datasetSize) } ?: "375K+"
    val exerciseCount = apiStatus?.exerciseCount?.toString() ?: "198"

    // Daily tip (changes based on day of year)
    val dayOfYear = (System.currentTimeMillis() / 86400000).toInt()
    val todayTip = healthTips[dayOfYear % healthTips.size]

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(OffWhite)
            .verticalScroll(rememberScrollState())
            .padding(PagePadding)
    ) {
        // ─── HERO BANNER ───
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(14.dp))
                .background(Brush.linearGradient(listOf(AccentTeal, PrimaryGreen, DarkGreen)))
                .padding(24.dp),
            contentAlignment = Alignment.Center
        ) {
            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Text("🥗", fontSize = 42.sp)
                Spacer(Modifier.height(8.dp))
                Text("TARG", fontSize = 32.sp, fontWeight = FontWeight.ExtraBold, color = White)
                Text("AI-Powered Health & Nutrition", fontSize = 14.sp,
                    color = White.copy(alpha = 0.85f))

                Spacer(Modifier.height(8.dp))

                // Version badge
                apiStatus?.let {
                    Surface(
                        shape = RoundedCornerShape(20.dp),
                        color = White.copy(alpha = 0.2f)
                    ) {
                        Text("v${it.version}",
                            modifier = Modifier.padding(horizontal = 14.dp, vertical = 4.dp),
                            fontSize = 12.sp, color = White, fontWeight = FontWeight.Medium)
                    }
                }

                Spacer(Modifier.height(20.dp))

                // Stats Row — Real data from API
                Row(
                    horizontalArrangement = Arrangement.spacedBy(10.dp),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    StatsChip(recipeCount, "Recipes", Modifier.weight(1f))
                    StatsChip("9", "Nutrients", Modifier.weight(1f))
                    StatsChip(exerciseCount, "Exercises", Modifier.weight(1f))
                }
            }
        }

        SectionSpacer()

        // ─── DAILY TIP ───
        Surface(
            shape = RoundedCornerShape(16.dp),
            color = PaleGreen,
            modifier = Modifier.fillMaxWidth()
        ) {
            Column(modifier = Modifier.padding(18.dp)) {
                Text("🌟 Daily Health Tip", fontSize = 14.sp,
                    fontWeight = FontWeight.SemiBold, color = DarkGreen)
                Spacer(Modifier.height(8.dp))
                Text(todayTip, fontSize = 14.sp, color = DarkText, lineHeight = 22.sp)
            }
        }

        SectionSpacer()

        // ─── HEALTH STATUS (if analyzed) ───
        healthData?.let { data ->
            TargCard {
                CardTitle("📊 Your Health Status", "")
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text("BMI", fontSize = 13.sp, color = MediumText)
                        Text("${data.bmi}", fontSize = 32.sp, fontWeight = FontWeight.Bold, color = DarkGreen)
                    }
                    BmiCategoryBadge(data.bmiCategory.category)
                }
                Spacer(Modifier.height(12.dp))
                Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                    StatCard("🔥", "${data.dailyCalories.maintenance}", "kcal/day",
                        isPrimary = true, modifier = Modifier.weight(1f))
                    StatCard("⚡", "${data.bmr.toInt()}", "BMR",
                        modifier = Modifier.weight(1f))
                }

                // Calorie breakdown
                Spacer(Modifier.height(12.dp))
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    StatCard("📉", "${data.dailyCalories.mildLoss}", "Lose",
                        modifier = Modifier.weight(1f))
                    StatCard("⚖️", "${data.dailyCalories.maintenance}", "Maintain",
                        modifier = Modifier.weight(1f))
                    StatCard("📈", "${data.dailyCalories.mildGain}", "Gain",
                        modifier = Modifier.weight(1f))
                }
            }
            SectionSpacer()
        }

        // ─── QUICK ACTIONS ───
        Text("🚀 Quick Actions", fontSize = 18.sp, fontWeight = FontWeight.SemiBold, color = DarkText)
        Spacer(Modifier.height(12.dp))

        DashboardCard(
            icon = "💪",
            title = "Health & Diet Analysis",
            subtitle = "BMI, calories, and personalized meals",
            onClick = { navController.navigate("diet") }
        )
        Spacer(Modifier.height(10.dp))

        DashboardCard(
            icon = "🏋️",
            title = "Workout Plans",
            subtitle = "Exercise routines & calorie calculator",
            onClick = { navController.navigate("workout") }
        )
        Spacer(Modifier.height(10.dp))

        DashboardCard(
            icon = "📊",
            title = "Macro Tracker",
            subtitle = "Track daily protein, carbs, fat & water",
            onClick = { navController.navigate("macro") }
        )
        Spacer(Modifier.height(10.dp))

        DashboardCard(
            icon = "🍽️",
            title = "Recipe Search",
            subtitle = "ML-powered recipe matching from ${recipeCount} options",
            onClick = { navController.navigate("recipes") }
        )
        Spacer(Modifier.height(10.dp))

        DashboardCard(
            icon = "📅",
            title = "Meal Planner",
            subtitle = "Plan your weekly meals with calorie tracking",
            onClick = { navController.navigate("planner") }
        )
        Spacer(Modifier.height(10.dp))

        DashboardCard(
            icon = "👤",
            title = "Account & Stats",
            subtitle = "Login, track progress, view your history",
            onClick = { navController.navigate("account") }
        )

        SectionSpacer()
        SectionSpacer()

        // ─── ML EXPLAINER ───
        ExplanationBox(
            "TARG uses K-Nearest Neighbors with Cosine Similarity to match " +
            "your nutritional profile against ${recipeCount} real recipes across 9 dimensions."
        )

        // ─── TECH STACK ───
        TargCard {
            CardTitle("🛠️ Tech Stack", "")
            val stack = listOf(
                "🤖 ML Engine" to "KNN + Cosine Similarity (Scikit-learn)",
                "🏋️ Exercise DB" to "$exerciseCount MET-based exercises",
                "📊 Health Calc" to "Mifflin-St Jeor equation",
                "🌐 Backend" to "FastAPI + SQLAlchemy",
                "📱 Mobile" to "Kotlin + Jetpack Compose",
            )
            stack.forEach { (title, desc) ->
                Row(modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp)) {
                    Text(title, fontSize = 13.sp, fontWeight = FontWeight.SemiBold,
                        color = DarkGreen, modifier = Modifier.width(110.dp))
                    Text(desc, fontSize = 13.sp, color = MediumText)
                }
            }
        }

        Spacer(Modifier.height(40.dp))
    }
}

@Composable
private fun StatsChip(value: String, label: String, modifier: Modifier = Modifier) {
    Surface(
        shape = RoundedCornerShape(10.dp),
        color = White.copy(alpha = 0.15f),
        modifier = modifier
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            modifier = Modifier.padding(vertical = 12.dp, horizontal = 6.dp)
        ) {
            Text(value, fontSize = 18.sp, fontWeight = FontWeight.Bold, color = White)
            Text(label, fontSize = 11.sp, color = White.copy(alpha = 0.8f))
        }
    }
}

private fun formatLargeCount(count: Int): String {
    return if (count >= 1000) "${count / 1000}K+" else "$count"
}
