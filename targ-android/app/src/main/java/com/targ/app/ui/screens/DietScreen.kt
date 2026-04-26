package com.targ.app.ui.screens

import androidx.compose.animation.animateContentSize
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

@Composable
fun DietScreen(viewModel: HealthViewModel) {

    val dietData by viewModel.dietData.collectAsState()
    val isDietLoading by viewModel.isDietLoading.collectAsState()
    val healthData by viewModel.healthData.collectAsState()
    val apiStatus by viewModel.apiStatus.collectAsState()
    val recipeCount = apiStatus?.let { if (it.datasetSize >= 1000) "${it.datasetSize / 1000}K+" else "${it.datasetSize}" } ?: "375K+"

    var calories by remember { mutableFloatStateOf(400f) }
    var protein by remember { mutableFloatStateOf(30f) }
    var carbs by remember { mutableFloatStateOf(50f) }
    var fat by remember { mutableFloatStateOf(15f) }
    var fiber by remember { mutableFloatStateOf(5f) }
    var sugar by remember { mutableFloatStateOf(10f) }
    var resultCount by remember { mutableIntStateOf(5) }
    var showAdvanced by remember { mutableStateOf(false) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(OffWhite)
            .verticalScroll(rememberScrollState())
            .padding(PagePadding),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        PageHeader(title = "🍽 Recipe Search", subtitle = "ML-powered recipes from $recipeCount options")

        // ─── FLOW LOCK ───
        if (!viewModel.isHealthAnalyzed) {
            FlowLockCard("Complete your Health Analysis on the Diet tab first to unlock recipe search.")
            return
        }

        // ─── NUTRITION SLIDERS ───
        TargCard {
            CardTitle("📊 Set Nutritional Targets", "")

            SliderRow("🔥 Calories", calories, 100f..1000f) { calories = it }
            SliderRow("💪 Protein (g)", protein, 0f..100f) { protein = it }
            SliderRow("🌾 Carbs (g)", carbs, 0f..150f) { carbs = it }
            SliderRow("🥑 Fat (g)", fat, 0f..50f) { fat = it }

            // Advanced toggle
            Surface(
                shape = RoundedCornerShape(8.dp),
                color = PaleGreen,
                onClick = { showAdvanced = !showAdvanced },
                modifier = Modifier.fillMaxWidth()
            ) {
                Text(
                    if (showAdvanced) "▼ Hide Advanced" else "▶ Show Advanced (Fiber, Sugar)",
                    modifier = Modifier.padding(12.dp),
                    fontSize = 13.sp, color = DarkGreen, fontWeight = FontWeight.Medium
                )
            }

            if (showAdvanced) {
                Spacer(Modifier.height(8.dp))
                SliderRow("🥦 Fiber (g)", fiber, 0f..30f) { fiber = it }
                SliderRow("🍬 Sugar (g)", sugar, 0f..50f) { sugar = it }
            }

            Spacer(Modifier.height(12.dp))

            // Result count
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text("Results: $resultCount", fontSize = 14.sp, color = DarkText, fontWeight = FontWeight.Medium)
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    listOf(3, 5, 10).forEach { n ->
                        FilterChip(
                            selected = resultCount == n,
                            onClick = { resultCount = n },
                            label = { Text("$n", fontSize = 12.sp) },
                            colors = FilterChipDefaults.filterChipColors(
                                selectedContainerColor = PrimaryGreen,
                                selectedLabelColor = White
                            )
                        )
                    }
                }
            }

            Spacer(Modifier.height(16.dp))

            PrimaryButton(
                text = "🔍 Find Matching Recipes",
                onClick = {
                    viewModel.fetchDietRecommendation(
                        calories = calories.toDouble(), fat = fat.toDouble(),
                        saturatedFat = 5.0, cholesterol = 50.0, sodium = 500.0,
                        carbs = carbs.toDouble(), fiber = fiber.toDouble(),
                        sugar = sugar.toDouble(), protein = protein.toDouble(),
                        count = resultCount
                    )
                },
                isLoading = isDietLoading
            )
        }

        ExplanationBox(
            "Recipes are matched using Cosine Similarity and K-Nearest Neighbors " +
            "across 9 nutritional dimensions from a dataset of $recipeCount real recipes."
        )

        // ─── RECIPE RESULTS ───
        if (dietData.isNotEmpty()) {
            TargCard {
                CardTitle("✅ ${dietData.size} Matching Recipes", "")

                dietData.forEachIndexed { idx, recipe ->
                    var expanded by remember { mutableStateOf(idx == 0) }

                    Surface(
                        shape = RoundedCornerShape(14.dp),
                        color = OffWhite,
                        modifier = Modifier.fillMaxWidth().padding(vertical = 5.dp)
                            .animateContentSize(),
                        onClick = { expanded = !expanded }
                    ) {
                        Column(modifier = Modifier.padding(16.dp)) {
                            // Header
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Text(
                                    recipe.name,
                                    fontSize = 16.sp,
                                    fontWeight = FontWeight.SemiBold,
                                    color = DarkText,
                                    modifier = Modifier.weight(1f)
                                )
                                Text(
                                    if (expanded) "▼" else "▶",
                                    fontSize = 14.sp, color = PrimaryGreen
                                )
                            }

                            Spacer(Modifier.height(8.dp))

                            // Nutrition badges
                            FlowRow(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                                NutrientBadge("🔥 ${recipe.calories.toInt()} kcal", true)
                                NutrientBadge("💪 ${recipe.proteinContent.toInt()}g")
                                NutrientBadge("🌾 ${recipe.carbohydrateContent.toInt()}g")
                                NutrientBadge("🥑 ${recipe.fatContent.toInt()}g")
                            }

                            // Time info
                            val timeDisplay = recipe.getCookTimeDisplay()
                            if (timeDisplay.isNotBlank() && timeDisplay != "null") {
                                Spacer(Modifier.height(6.dp))
                                Text("⏱ Cook: $timeDisplay", fontSize = 12.sp, color = MediumText)
                            }

                            // Expanded content: ingredients + instructions
                            if (expanded) {
                                Spacer(Modifier.height(12.dp))
                                HorizontalDivider(color = PaleGreen)
                                Spacer(Modifier.height(12.dp))

                                // Extra nutrition
                                FlowRow(
                                    horizontalArrangement = Arrangement.spacedBy(6.dp),
                                    verticalArrangement = Arrangement.spacedBy(4.dp)
                                ) {
                                    NutrientBadge("🥦 Fiber: ${recipe.fiberContent.toInt()}g")
                                    NutrientBadge("🍬 Sugar: ${recipe.sugarContent.toInt()}g")
                                    NutrientBadge("🧂 Sodium: ${recipe.sodiumContent.toInt()}mg")
                                    NutrientBadge("💊 Chol: ${recipe.cholesterolContent.toInt()}mg")
                                }

                                // Ingredients
                                val ingredients = recipe.getIngredientsList()
                                if (ingredients.isNotEmpty()) {
                                    Spacer(Modifier.height(12.dp))
                                    Text("🧾 Ingredients", fontSize = 14.sp,
                                        fontWeight = FontWeight.SemiBold, color = DarkGreen)
                                    Spacer(Modifier.height(6.dp))
                                    ingredients.take(15).forEach { ing ->
                                        Text("  • $ing", fontSize = 13.sp, color = DarkText,
                                            lineHeight = 20.sp)
                                    }
                                    if (ingredients.size > 15) {
                                        Text("  ... and ${ingredients.size - 15} more",
                                            fontSize = 12.sp, color = LightText)
                                    }
                                }

                                // Instructions
                                val instructions = recipe.getInstructionsList()
                                if (instructions.isNotEmpty()) {
                                    Spacer(Modifier.height(12.dp))
                                    Text("📝 Instructions", fontSize = 14.sp,
                                        fontWeight = FontWeight.SemiBold, color = DarkGreen)
                                    Spacer(Modifier.height(6.dp))
                                    instructions.take(10).forEachIndexed { i, step ->
                                        Text("  ${i + 1}. $step", fontSize = 13.sp,
                                            color = DarkText, lineHeight = 20.sp)
                                        Spacer(Modifier.height(4.dp))
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        Spacer(Modifier.height(24.dp))
    }
}

@Composable
private fun SliderRow(
    label: String,
    value: Float,
    range: ClosedFloatingPointRange<Float>,
    onValueChange: (Float) -> Unit
) {
    Column {
        Text("$label: ${value.toInt()}", color = DarkText, fontWeight = FontWeight.Medium, fontSize = 14.sp)
        Slider(
            value = value, onValueChange = onValueChange,
            valueRange = range,
            colors = SliderDefaults.colors(
                thumbColor = PrimaryGreen,
                activeTrackColor = PrimaryGreen,
                inactiveTrackColor = PaleGreen
            )
        )
    }
}
