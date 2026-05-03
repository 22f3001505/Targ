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
fun HealthScreen(viewModel: HealthViewModel) {

    val healthData by viewModel.healthData.collectAsState()
    val isLoading by viewModel.isLoading.collectAsState()
    val error by viewModel.errorMessage.collectAsState()
    val actionMessage by viewModel.actionMessage.collectAsState()
    val apiStatus by viewModel.apiStatus.collectAsState()
    val recipeCount = apiStatus?.let { if (it.datasetSize >= 1000) "${it.datasetSize / 1000}K+" else "${it.datasetSize}" } ?: "375K+"

    var age by remember { mutableStateOf("25") }
    var height by remember { mutableStateOf("170") }
    var weight by remember { mutableStateOf("70") }
    var selectedGender by remember { mutableStateOf("male") }
    var selectedActivity by remember { mutableStateOf("moderate") }

    val genderOptions = listOf("male", "female")
    val activityOptions = listOf("sedentary", "light", "moderate", "active", "extra_active")

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(OffWhite)
            .verticalScroll(rememberScrollState())
            .padding(PagePadding),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        PageHeader(
            title = "💪 Health & Diet Analysis",
            subtitle = "BMI, BMR, calories & personalized recommendations"
        )

        // ─── INPUT FORM ───
        TargCard {
            CardTitle("📋 Your Details", "")

            OutlinedTextField(
                value = age, onValueChange = { age = it },
                label = { Text("Age", color = DarkText) },
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                modifier = Modifier.fillMaxWidth(),
                singleLine = true,
                shape = RoundedCornerShape(12.dp)
            )
            Spacer(Modifier.height(10.dp))

            Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                OutlinedTextField(
                    value = height, onValueChange = { height = it },
                    label = { Text("Height (cm)", color = DarkText) },
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                    modifier = Modifier.weight(1f), singleLine = true,
                    shape = RoundedCornerShape(12.dp)
                )
                OutlinedTextField(
                    value = weight, onValueChange = { weight = it },
                    label = { Text("Weight (kg)", color = DarkText) },
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                    modifier = Modifier.weight(1f), singleLine = true,
                    shape = RoundedCornerShape(12.dp)
                )
            }
            Spacer(Modifier.height(12.dp))

            // Gender chips
            Text("Gender", fontSize = 14.sp, color = MediumText, fontWeight = FontWeight.Medium)
            Spacer(Modifier.height(6.dp))
            Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                genderOptions.forEach { g ->
                    FilterChip(
                        selected = selectedGender == g,
                        onClick = { selectedGender = g },
                        label = { Text(g.replaceFirstChar { it.uppercase() }) },
                        colors = FilterChipDefaults.filterChipColors(
                            labelColor = DarkText,
                            selectedContainerColor = LightMint,
                            selectedLabelColor = DarkText
                        )
                    )
                }
            }
            Spacer(Modifier.height(14.dp))

            // Activity level
            Text("Activity Level", fontSize = 14.sp, color = MediumText, fontWeight = FontWeight.Medium)
            Spacer(Modifier.height(6.dp))
            FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                activityOptions.forEach { level ->
                    FilterChip(
                        selected = selectedActivity == level,
                        onClick = { selectedActivity = level },
                        label = {
                            Text(level.replace("_", " ").replaceFirstChar { it.uppercase() },
                                fontSize = 12.sp)
                        },
                        colors = FilterChipDefaults.filterChipColors(
                            labelColor = DarkText,
                            selectedContainerColor = LightMint,
                            selectedLabelColor = DarkText
                        )
                    )
                }
            }
            Spacer(Modifier.height(18.dp))

            PrimaryButton(
                text = "🔍 Analyze Health",
                onClick = {
                    viewModel.fetchHealthAnalysis(
                        age.toIntOrNull() ?: 25,
                        height.toFloatOrNull() ?: 170f,
                        weight.toFloatOrNull() ?: 70f,
                        selectedGender, selectedActivity
                    )
                },
                isLoading = isLoading
            )
        }

        // ─── FEEDBACK ───
        actionMessage?.let {
            MessageBanner(it, onDismiss = { viewModel.clearActionMessage() })
        }
        error?.let {
            MessageBanner(it, isError = true, onDismiss = { viewModel.clearError() })
        }

        // ─── RESULTS ───
        healthData?.let { data ->

            // BMI Result
            TargCard {
                CardTitle("📊 BMI Result", "")
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text("${data.bmi}", fontSize = 44.sp, fontWeight = FontWeight.ExtraBold, color = DarkGreen)
                        Text(data.bmiCategory.status, fontSize = 13.sp, color = MediumText)
                    }
                    BmiCategoryBadge(data.bmiCategory.category)
                }
                Spacer(Modifier.height(14.dp))
                ExplanationBox("BMI = weight(kg) ÷ height(m)². A screening tool, not a diagnostic measure.")
            }

            // Calorie targets
            TargCard {
                CardTitle("🎯 Daily Calorie Targets", "")
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                    StatCard("🔥", "${data.dailyCalories.maintenance}", "Maintain", isPrimary = true, modifier = Modifier.weight(1f))
                    StatCard("📉", "${data.dailyCalories.mildLoss}", "Mild Loss", modifier = Modifier.weight(1f))
                }
                Spacer(Modifier.height(12.dp))
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                    StatCard("⬇️", "${data.dailyCalories.weightLoss}", "Weight Loss", modifier = Modifier.weight(1f))
                    StatCard("⚡", "${data.dailyCalories.extremeLoss}", "Extreme Loss", modifier = Modifier.weight(1f))
                }
                Spacer(Modifier.height(12.dp))
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                    StatCard("📈", "${data.dailyCalories.mildGain}", "Mild Gain", modifier = Modifier.weight(1f))
                    StatCard("💪", "${data.dailyCalories.weightGain}", "Weight Gain", modifier = Modifier.weight(1f))
                }
                Spacer(Modifier.height(14.dp))
                ExplanationBox("Calculated using Mifflin-St Jeor equation. BMR: ${data.bmr.toInt()} kcal × activity multiplier.")
            }

            // Diet Recommendations — trigger fetch
            TargCard {
                CardTitle("🥗 Get Diet Recommendations", "")
                Text("Find personalized recipes matching your nutritional needs from $recipeCount options.",
                    fontSize = 14.sp, color = MediumText, lineHeight = 20.sp)
                Spacer(Modifier.height(16.dp))
                PrimaryButton(
                    text = "🔍 Find Matching Recipes",
                    onClick = {
                        viewModel.fetchDietRecommendation(
                            calories = data.dailyCalories.maintenance / 3.0,
                            fat = 15.0, saturatedFat = 5.0, cholesterol = 50.0,
                            sodium = 500.0, carbs = 50.0, fiber = 5.0,
                            sugar = 10.0, protein = 30.0
                        )
                    }
                )
            }

            // Medical disclaimer
            Surface(
                shape = RoundedCornerShape(12.dp),
                color = BmiUnderweight.copy(alpha = 0.1f),
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("⚠️ Consult a healthcare professional before starting any diet or exercise program.",
                    modifier = Modifier.padding(16.dp), fontSize = 12.sp, color = MediumText)
            }
        }

        Spacer(Modifier.height(24.dp))
    }
}
