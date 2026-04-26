package com.targ.app.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.targ.app.ui.components.*
import com.targ.app.ui.theme.*
import com.targ.app.viewmodel.HealthViewModel

@Composable
fun AccountScreen(viewModel: HealthViewModel) {

    val authToken by viewModel.authToken.collectAsState()
    val userData by viewModel.userData.collectAsState()
    val userStats by viewModel.userStats.collectAsState()
    val savedMeals by viewModel.savedMeals.collectAsState()
    val isLoading by viewModel.isLoading.collectAsState()
    val error by viewModel.errorMessage.collectAsState()
    val apiStatus by viewModel.apiStatus.collectAsState()

    LaunchedEffect(authToken) {
        if (authToken != null) viewModel.refreshAccountData()
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(OffWhite)
            .verticalScroll(rememberScrollState())
            .padding(PagePadding),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        PageHeader(
            title = "🔐 Account",
            subtitle = if (viewModel.isLoggedIn) "Welcome back!" else "Login or create an account"
        )

        // ─── API Status ───
        apiStatus?.let { status ->
            Surface(
                shape = RoundedCornerShape(12.dp),
                color = PaleGreen,
                modifier = Modifier.fillMaxWidth()
            ) {
                Row(
                    modifier = Modifier.padding(14.dp),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Text("🟢", fontSize = 14.sp)
                    Text(
                        "API v${status.version} · ${formatCount(status.datasetSize)} recipes · ${status.exerciseCount} exercises",
                        fontSize = 13.sp, color = DarkGreen, fontWeight = FontWeight.Medium
                    )
                }
            }
        } ?: run {
            Surface(
                shape = RoundedCornerShape(12.dp),
                color = BmiObese.copy(alpha = 0.1f),
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("🔴 API Offline — some features unavailable",
                    modifier = Modifier.padding(14.dp), fontSize = 13.sp, color = BmiObese)
            }
        }

        // ─── Error display ───
        error?.let {
            Surface(shape = RoundedCornerShape(12.dp), color = BmiObese.copy(alpha = 0.1f),
                modifier = Modifier.fillMaxWidth()) {
                Text("⚠️ $it", modifier = Modifier.padding(16.dp), color = BmiObese, fontSize = 13.sp)
            }
        }

        if (viewModel.isLoggedIn) {
            // ═══════════════ LOGGED IN VIEW ═══════════════
            LoggedInView(viewModel, userData, userStats, savedMeals)
        } else {
            // ═══════════════ AUTH FORMS ═══════════════
            AuthForms(viewModel, isLoading)
        }

        Spacer(Modifier.height(24.dp))
    }
}

@Composable
private fun LoggedInView(
    viewModel: HealthViewModel,
    userData: com.targ.app.data.model.UserData?,
    userStats: com.targ.app.data.model.UserStatsResponse?,
    savedMeals: List<com.targ.app.data.model.SavedMealResponse>
) {
    // Profile Card
    TargCard {
        Column(
            modifier = Modifier.fillMaxWidth(),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            // Avatar
            Box(
                modifier = Modifier
                    .size(80.dp)
                    .clip(CircleShape)
                    .background(Brush.linearGradient(listOf(PrimaryGreen, DarkGreen))),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = (userData?.username?.firstOrNull()?.uppercase() ?: "T"),
                    fontSize = 32.sp, fontWeight = FontWeight.Bold, color = White
                )
            }
            Spacer(Modifier.height(14.dp))
            Text(
                userData?.fullName?.ifBlank { userData.username } ?: "User",
                fontSize = 22.sp, fontWeight = FontWeight.Bold, color = DarkText
            )
            Text(
                userData?.email ?: "",
                fontSize = 14.sp, color = MediumText
            )
            Text(
                "@${userData?.username ?: ""}",
                fontSize = 13.sp, color = LightText
            )
        }
    }

    // Stats Cards
    userStats?.let { stats ->
        TargCard {
            CardTitle("📊 Your Activity", "")
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                StatCard("🔬", "${stats.totalHealthAnalyses}", "Analyses",
                    isPrimary = true, modifier = Modifier.weight(1f))
                StatCard("🍽️", "${stats.totalSavedMeals}", "Meals",
                    modifier = Modifier.weight(1f))
                StatCard("🏋️", "${stats.totalWorkouts}", "Workouts",
                    modifier = Modifier.weight(1f))
            }
            Spacer(Modifier.height(12.dp))

            stats.latestBmi?.let { bmi ->
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                    StatCard("📊", "%.1f".format(bmi), "Latest BMI",
                        modifier = Modifier.weight(1f))
                    StatCard("🔥", "${stats.latestCalories ?: 0}", "Calories",
                        modifier = Modifier.weight(1f))
                }
            }
        }
    }

    if (savedMeals.isNotEmpty()) {
        TargCard {
            CardTitle("🍽️ Recent Meals", "")
            savedMeals.take(5).forEach { meal ->
                Surface(
                    shape = RoundedCornerShape(10.dp),
                    color = OffWhite,
                    modifier = Modifier.fillMaxWidth().padding(vertical = 3.dp)
                ) {
                    Row(
                        modifier = Modifier.padding(12.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column(modifier = Modifier.weight(1f)) {
                            Text(meal.mealName, fontSize = 13.sp,
                                fontWeight = FontWeight.SemiBold, color = DarkText)
                            Text(meal.mealType, fontSize = 11.sp, color = LightText)
                        }
                        NutrientBadge("🔥${meal.calories.toInt()}", true)
                    }
                }
            }
        }
    }

    OutlinedButton(
        onClick = { viewModel.refreshAccountData() },
        modifier = Modifier.fillMaxWidth().height(48.dp),
        shape = RoundedCornerShape(ButtonRadius),
        colors = ButtonDefaults.outlinedButtonColors(contentColor = PrimaryGreen)
    ) {
        Text("↻ Refresh Account Data", fontWeight = FontWeight.SemiBold)
    }

    // Logout Button
    Spacer(Modifier.height(8.dp))
    OutlinedButton(
        onClick = { viewModel.logout() },
        modifier = Modifier.fillMaxWidth().height(50.dp),
        shape = RoundedCornerShape(ButtonRadius),
        colors = ButtonDefaults.outlinedButtonColors(contentColor = BmiObese)
    ) {
        Text("🚪 Logout", fontWeight = FontWeight.SemiBold, fontSize = 16.sp)
    }
}

@Composable
private fun AuthForms(viewModel: HealthViewModel, isLoading: Boolean) {
    var isLogin by remember { mutableStateOf(true) }

    // Tab selector
    Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
        Surface(
            shape = RoundedCornerShape(12.dp),
            color = if (isLogin) PrimaryGreen else White,
            shadowElevation = if (isLogin) 4.dp else 1.dp,
            onClick = { isLogin = true },
            modifier = Modifier.weight(1f)
        ) {
            Text("🔑 Login",
                modifier = Modifier.padding(16.dp),
                textAlign = TextAlign.Center,
                fontWeight = FontWeight.SemiBold,
                color = if (isLogin) White else MediumText
            )
        }
        Surface(
            shape = RoundedCornerShape(12.dp),
            color = if (!isLogin) PrimaryGreen else White,
            shadowElevation = if (!isLogin) 4.dp else 1.dp,
            onClick = { isLogin = false },
            modifier = Modifier.weight(1f)
        ) {
            Text("📝 Sign Up",
                modifier = Modifier.padding(16.dp),
                textAlign = TextAlign.Center,
                fontWeight = FontWeight.SemiBold,
                color = if (!isLogin) White else MediumText
            )
        }
    }

    if (isLogin) {
        LoginForm(viewModel, isLoading)
    } else {
        SignupForm(viewModel, isLoading)
    }

    // Benefits card
    TargCard {
        CardTitle("✨ Why create an account?", "")
        val benefits = listOf(
            "📊 Track your BMI & health progress over time",
            "🍽️ Save your favorite recipes",
            "🏋️ Log workouts & calories burned",
            "📈 View health trends with interactive charts"
        )
        benefits.forEach { benefit ->
            Surface(
                shape = RoundedCornerShape(10.dp),
                color = PaleGreen,
                modifier = Modifier.fillMaxWidth().padding(vertical = 3.dp)
            ) {
                Text(benefit, modifier = Modifier.padding(14.dp),
                    fontSize = 14.sp, color = DarkText, lineHeight = 20.sp)
            }
        }
    }
}

@Composable
private fun LoginForm(viewModel: HealthViewModel, isLoading: Boolean) {
    var username by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }

    TargCard {
        CardTitle("🔑 Login to TARG", "")
        OutlinedTextField(
            value = username, onValueChange = { username = it },
            label = { Text("Username or email") },
            modifier = Modifier.fillMaxWidth(), singleLine = true,
            shape = RoundedCornerShape(12.dp)
        )
        Spacer(Modifier.height(10.dp))
        OutlinedTextField(
            value = password, onValueChange = { password = it },
            label = { Text("Password") },
            modifier = Modifier.fillMaxWidth(), singleLine = true,
            shape = RoundedCornerShape(12.dp),
            visualTransformation = PasswordVisualTransformation()
        )
        Spacer(Modifier.height(16.dp))
        PrimaryButton(
            text = "🔑 Login",
            onClick = { if (username.isNotBlank() && password.isNotBlank()) viewModel.login(username, password) },
            isLoading = isLoading
        )
    }
}

@Composable
private fun SignupForm(viewModel: HealthViewModel, isLoading: Boolean) {
    var fullName by remember { mutableStateOf("") }
    var email by remember { mutableStateOf("") }
    var username by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }

    TargCard {
        CardTitle("📝 Create Account", "")
        OutlinedTextField(
            value = fullName, onValueChange = { fullName = it },
            label = { Text("Full Name") },
            modifier = Modifier.fillMaxWidth(), singleLine = true,
            shape = RoundedCornerShape(12.dp)
        )
        Spacer(Modifier.height(10.dp))
        OutlinedTextField(
            value = email, onValueChange = { email = it },
            label = { Text("Email") },
            modifier = Modifier.fillMaxWidth(), singleLine = true,
            shape = RoundedCornerShape(12.dp)
        )
        Spacer(Modifier.height(10.dp))
        OutlinedTextField(
            value = username, onValueChange = { username = it },
            label = { Text("Username") },
            supportingText = { Text("3-32 chars: letters, numbers, _, . or -") },
            modifier = Modifier.fillMaxWidth(), singleLine = true,
            shape = RoundedCornerShape(12.dp)
        )
        Spacer(Modifier.height(10.dp))
        OutlinedTextField(
            value = password, onValueChange = { password = it },
            label = { Text("Password") },
            supportingText = { Text("Minimum 8 characters with a letter and number") },
            modifier = Modifier.fillMaxWidth(), singleLine = true,
            shape = RoundedCornerShape(12.dp),
            visualTransformation = PasswordVisualTransformation()
        )
        Spacer(Modifier.height(16.dp))
        PrimaryButton(
            text = "📝 Create Account",
            onClick = {
                val hasLetter = password.any { it.isLetter() }
                val hasNumber = password.any { it.isDigit() }
                if (email.isNotBlank() && username.isNotBlank() && password.length >= 8 && hasLetter && hasNumber) {
                    viewModel.signup(email, username, password, fullName)
                }
            },
            isLoading = isLoading
        )
    }
}

private fun formatCount(count: Int): String {
    return if (count >= 1000) "${count / 1000}K+" else "$count"
}
