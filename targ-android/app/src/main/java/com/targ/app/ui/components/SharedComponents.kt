package com.targ.app.ui.components

import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.targ.app.ui.theme.*

// ═══════════════════════════════════════════════════
// PAGE HEADER — Gradient banner at the top of each screen
// ═══════════════════════════════════════════════════

@Composable
fun PageHeader(title: String, subtitle: String) {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .shadow(16.dp, RoundedCornerShape(24.dp))
            .clip(RoundedCornerShape(24.dp))
            .background(Brush.linearGradient(listOf(PrimaryGreen, DarkGreen)))
            .padding(horizontal = 28.dp, vertical = 36.dp),
        contentAlignment = Alignment.Center
    ) {
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            Text(title, fontSize = 28.sp, fontWeight = FontWeight.Bold, color = White)
            Spacer(Modifier.height(6.dp))
            Text(subtitle, fontSize = 14.sp, color = White.copy(alpha = 0.85f),
                textAlign = TextAlign.Center)
        }
    }
}

// ═══════════════════════════════════════════════════
// TARG CARD — White card with subtle shadow
// ═══════════════════════════════════════════════════

@Composable
fun TargCard(
    modifier: Modifier = Modifier,
    content: @Composable ColumnScope.() -> Unit
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        shape = RoundedCornerShape(CardRadius),
        colors = CardDefaults.cardColors(containerColor = White),
        elevation = CardDefaults.cardElevation(defaultElevation = CardElevation)
    ) {
        Column(modifier = Modifier.padding(20.dp), content = content)
    }
}

// ═══════════════════════════════════════════════════
// CARD TITLE — Section header inside cards
// ═══════════════════════════════════════════════════

@Composable
fun CardTitle(text: String, icon: String = "") {
    Row(verticalAlignment = Alignment.CenterVertically) {
        if (icon.isNotEmpty()) {
            Text(icon, fontSize = 20.sp)
            Spacer(Modifier.width(8.dp))
        }
        Text(text, fontSize = 18.sp, fontWeight = FontWeight.SemiBold, color = DarkGreen)
    }
    Spacer(Modifier.height(14.dp))
}

// ═══════════════════════════════════════════════════
// STAT CARD — Metric display with gradient
// ═══════════════════════════════════════════════════

@Composable
fun StatCard(
    icon: String,
    value: String,
    label: String,
    isPrimary: Boolean = false,
    modifier: Modifier = Modifier
) {
    val bg = if (isPrimary)
        Brush.linearGradient(listOf(PrimaryGreen, DarkGreen))
    else
        Brush.linearGradient(listOf(SoftMint, LightMint))
    val textColor = if (isPrimary) White else DarkGreen

    Box(
        modifier = modifier
            .clip(RoundedCornerShape(14.dp))
            .background(bg)
            .padding(18.dp),
        contentAlignment = Alignment.Center
    ) {
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            Text(icon, fontSize = 22.sp)
            Spacer(Modifier.height(8.dp))
            Text(value, fontSize = 24.sp, fontWeight = FontWeight.Bold, color = textColor)
            Spacer(Modifier.height(2.dp))
            Text(label, fontSize = 12.sp, color = textColor.copy(alpha = 0.8f))
        }
    }
}

// ═══════════════════════════════════════════════════
// BMI CATEGORY BADGE
// ═══════════════════════════════════════════════════

@Composable
fun BmiCategoryBadge(category: String) {
    val color = when (category) {
        "Normal" -> BmiNormal
        "Underweight" -> BmiUnderweight
        "Overweight" -> BmiOverweight
        "Obese" -> BmiObese
        else -> DarkText
    }
    Surface(
        shape = RoundedCornerShape(50.dp),
        color = color
    ) {
        Text(
            text = category,
            modifier = Modifier.padding(horizontal = 22.dp, vertical = 8.dp),
            color = White,
            fontWeight = FontWeight.SemiBold,
            fontSize = 14.sp
        )
    }
}

// ═══════════════════════════════════════════════════
// EXPLANATION BOX — ML explainability
// ═══════════════════════════════════════════════════

@Composable
fun ExplanationBox(text: String) {
    Surface(
        shape = RoundedCornerShape(12.dp),
        color = PaleGreen,
        modifier = Modifier.fillMaxWidth()
    ) {
        Row(modifier = Modifier.padding(16.dp), verticalAlignment = Alignment.Top) {
            Text("💡 ", fontSize = 16.sp)
            Text(text, fontSize = 13.sp, color = DarkText, lineHeight = 20.sp)
        }
    }
}

// ═══════════════════════════════════════════════════
// PRIMARY BUTTON — Green gradient with loading
// ═══════════════════════════════════════════════════

@Composable
fun PrimaryButton(
    text: String,
    onClick: () -> Unit,
    isLoading: Boolean = false,
    modifier: Modifier = Modifier
) {
    Button(
        onClick = onClick,
        modifier = modifier.fillMaxWidth().height(54.dp),
        shape = RoundedCornerShape(ButtonRadius),
        colors = ButtonDefaults.buttonColors(containerColor = PrimaryGreen),
        enabled = !isLoading
    ) {
        if (isLoading) {
            CircularProgressIndicator(
                modifier = Modifier.size(22.dp),
                color = White,
                strokeWidth = 2.dp
            )
            Spacer(Modifier.width(12.dp))
            Text("Analyzing...", color = White, fontWeight = FontWeight.SemiBold)
        } else {
            Text(text, color = White, fontWeight = FontWeight.SemiBold, fontSize = 16.sp)
        }
    }
}

// ═══════════════════════════════════════════════════
// DASHBOARD CARD — Clickable navigation card for HomeScreen
// ═══════════════════════════════════════════════════

@Composable
fun DashboardCard(
    icon: String,
    title: String,
    subtitle: String,
    onClick: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { onClick() },
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = White),
        elevation = CardDefaults.cardElevation(defaultElevation = 3.dp)
    ) {
        Row(
            modifier = Modifier.padding(20.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Surface(
                shape = RoundedCornerShape(14.dp),
                color = PaleGreen,
                modifier = Modifier.size(56.dp)
            ) {
                Box(contentAlignment = Alignment.Center) {
                    Text(icon, fontSize = 26.sp)
                }
            }
            Spacer(Modifier.width(16.dp))
            Column(modifier = Modifier.weight(1f)) {
                Text(title, fontSize = 16.sp, fontWeight = FontWeight.SemiBold, color = DarkText)
                Text(subtitle, fontSize = 13.sp, color = MediumText)
            }
            Text("→", fontSize = 20.sp, color = PrimaryGreen, fontWeight = FontWeight.Bold)
        }
    }
}

// ═══════════════════════════════════════════════════
// NUTRIENT BADGE — Small pill badge
// ═══════════════════════════════════════════════════

@Composable
fun NutrientBadge(text: String, isPrimary: Boolean = false) {
    Surface(
        shape = RoundedCornerShape(20.dp),
        color = if (isPrimary) PrimaryGreen else PaleGreen
    ) {
        Text(
            text,
            modifier = Modifier.padding(horizontal = 12.dp, vertical = 5.dp),
            fontSize = 12.sp,
            fontWeight = FontWeight.Medium,
            color = if (isPrimary) White else DarkGreen
        )
    }
}

// ═══════════════════════════════════════════════════
// PROGRESS BAR — Branded macro progress
// ═══════════════════════════════════════════════════

@Composable
fun MacroProgressBar(
    label: String,
    icon: String,
    current: Int,
    goal: Int,
    color: Color = PrimaryGreen
) {
    val pct = if (goal > 0) (current.toFloat() / goal).coerceIn(0f, 1f) else 0f

    Column(modifier = Modifier.fillMaxWidth()) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Text("$icon $label", fontSize = 14.sp, fontWeight = FontWeight.Medium, color = DarkText)
            Text("$current / $goal", fontSize = 14.sp, fontWeight = FontWeight.SemiBold, color = color)
        }
        Spacer(Modifier.height(6.dp))
        LinearProgressIndicator(
            progress = { pct },
            modifier = Modifier
                .fillMaxWidth()
                .height(10.dp)
                .clip(RoundedCornerShape(5.dp)),
            color = color,
            trackColor = PaleGreen,
        )
        Spacer(Modifier.height(14.dp))
    }
}

// ═══════════════════════════════════════════════════
// SECTION DIVIDER
// ═══════════════════════════════════════════════════

@Composable
fun SectionSpacer() {
    Spacer(Modifier.height(16.dp))
}

// ═══════════════════════════════════════════════════
// FLOW LOCK CARD — Shown when step is required first
// ═══════════════════════════════════════════════════

@Composable
fun FlowLockCard(message: String, stepRequired: String = "Health Analysis") {
    TargCard {
        Column(
            modifier = Modifier.fillMaxWidth().padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text("🔒", fontSize = 44.sp)
            Spacer(Modifier.height(14.dp))
            Text("Step Required", fontSize = 20.sp, fontWeight = FontWeight.Bold, color = DarkText)
            Spacer(Modifier.height(10.dp))
            Text(
                message, fontSize = 14.sp, color = MediumText,
                textAlign = TextAlign.Center, lineHeight = 22.sp
            )
        }
    }
}
