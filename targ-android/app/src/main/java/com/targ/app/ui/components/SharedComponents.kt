package com.targ.app.ui.components

import androidx.compose.animation.core.*
import androidx.compose.foundation.BorderStroke
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
import androidx.compose.ui.text.style.TextOverflow
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
            .shadow(6.dp, RoundedCornerShape(14.dp))
            .clip(RoundedCornerShape(14.dp))
            .background(Brush.linearGradient(listOf(AccentTeal, PrimaryGreen, DarkGreen)))
            .padding(horizontal = 22.dp, vertical = 24.dp),
        contentAlignment = Alignment.Center
    ) {
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            Text(
                title,
                fontSize = 25.sp,
                lineHeight = 30.sp,
                fontWeight = FontWeight.Bold,
                color = White,
                textAlign = TextAlign.Center
            )
            Spacer(Modifier.height(6.dp))
            Text(
                subtitle,
                fontSize = 13.sp,
                lineHeight = 19.sp,
                color = White.copy(alpha = 0.86f),
                textAlign = TextAlign.Center
            )
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
        border = BorderStroke(1.dp, BorderLight),
        elevation = CardDefaults.cardElevation(defaultElevation = CardElevation)
    ) {
        Column(modifier = Modifier.padding(18.dp), content = content)
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
        Text(
            text,
            fontSize = 17.sp,
            lineHeight = 22.sp,
            fontWeight = FontWeight.SemiBold,
            color = DarkGreen,
            maxLines = 2,
            overflow = TextOverflow.Ellipsis
        )
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
        Brush.linearGradient(listOf(AccentTeal, PrimaryGreen))
    else
        Brush.linearGradient(listOf(White, PaleGreen))
    val textColor = if (isPrimary) White else DarkGreen

    Box(
        modifier = modifier
            .heightIn(min = 92.dp)
            .clip(RoundedCornerShape(10.dp))
            .background(bg)
            .padding(horizontal = 12.dp, vertical = 14.dp),
        contentAlignment = Alignment.Center
    ) {
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            Text(icon, fontSize = 19.sp)
            Spacer(Modifier.height(6.dp))
            Text(
                value,
                fontSize = 21.sp,
                lineHeight = 24.sp,
                fontWeight = FontWeight.Bold,
                color = textColor,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis
            )
            Spacer(Modifier.height(2.dp))
            Text(
                label,
                fontSize = 11.sp,
                lineHeight = 14.sp,
                color = textColor.copy(alpha = 0.82f),
                textAlign = TextAlign.Center,
                maxLines = 2,
                overflow = TextOverflow.Ellipsis
            )
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
        shape = RoundedCornerShape(8.dp),
        color = color
    ) {
        Text(
            text = category,
            modifier = Modifier.padding(horizontal = 16.dp, vertical = 8.dp),
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
        shape = RoundedCornerShape(10.dp),
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
// MESSAGE BANNER — Compact success/error feedback
// ═══════════════════════════════════════════════════

@Composable
fun MessageBanner(
    message: String,
    isError: Boolean = false,
    onDismiss: (() -> Unit)? = null,
    modifier: Modifier = Modifier
) {
    Surface(
        shape = RoundedCornerShape(10.dp),
        color = if (isError) BmiObese.copy(alpha = 0.10f) else PaleGreen,
        border = BorderStroke(1.dp, if (isError) BmiObese.copy(alpha = 0.20f) else BorderLight),
        modifier = modifier.fillMaxWidth()
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 14.dp, vertical = 12.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                if (isError) "!" else "✓",
                fontSize = 15.sp,
                fontWeight = FontWeight.Bold,
                color = if (isError) BmiObese else DarkGreen
            )
            Spacer(Modifier.width(10.dp))
            Text(
                message,
                modifier = Modifier.weight(1f),
                fontSize = 13.sp,
                lineHeight = 18.sp,
                color = if (isError) BmiObese else DarkGreen,
                maxLines = 3,
                overflow = TextOverflow.Ellipsis
            )
            if (onDismiss != null) {
                Spacer(Modifier.width(10.dp))
                Text(
                    "Dismiss",
                    modifier = Modifier.clickable { onDismiss() },
                    fontSize = 12.sp,
                    fontWeight = FontWeight.SemiBold,
                    color = if (isError) BmiObese else PrimaryGreen
                )
            }
        }
    }
}

// ═══════════════════════════════════════════════════
// PRIMARY BUTTON — Branded action with loading
// ═══════════════════════════════════════════════════

@Composable
fun PrimaryButton(
    text: String,
    onClick: () -> Unit,
    isLoading: Boolean = false,
    loadingText: String = "Analyzing...",
    enabled: Boolean = true,
    modifier: Modifier = Modifier
) {
    val contentColor = if (enabled && !isLoading) White else DarkGreen

    Button(
        onClick = onClick,
        modifier = modifier.fillMaxWidth().heightIn(min = 50.dp),
        shape = RoundedCornerShape(ButtonRadius),
        colors = ButtonDefaults.buttonColors(
            containerColor = PrimaryGreen,
            disabledContainerColor = LightMint,
            disabledContentColor = DarkGreen
        ),
        enabled = enabled && !isLoading
    ) {
        if (isLoading) {
            CircularProgressIndicator(
                modifier = Modifier.size(22.dp),
                color = contentColor,
                strokeWidth = 2.dp
            )
            Spacer(Modifier.width(12.dp))
            Text(loadingText, color = contentColor, fontWeight = FontWeight.SemiBold)
        } else {
            Text(text, color = contentColor, fontWeight = FontWeight.SemiBold, fontSize = 16.sp)
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
            .heightIn(min = 84.dp)
            .clickable { onClick() },
        shape = RoundedCornerShape(CardRadius),
        colors = CardDefaults.cardColors(containerColor = White),
        border = BorderStroke(1.dp, BorderLight),
        elevation = CardDefaults.cardElevation(defaultElevation = CardElevation)
    ) {
        Row(
            modifier = Modifier.padding(20.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Surface(
                shape = RoundedCornerShape(10.dp),
                color = PaleGreen,
                modifier = Modifier.size(52.dp)
            ) {
                Box(contentAlignment = Alignment.Center) {
                    Text(icon, fontSize = 24.sp)
                }
            }
            Spacer(Modifier.width(16.dp))
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    title,
                    fontSize = 16.sp,
                    fontWeight = FontWeight.SemiBold,
                    color = DarkText,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis
                )
                Text(
                    subtitle,
                    fontSize = 13.sp,
                    lineHeight = 18.sp,
                    color = MediumText,
                    maxLines = 2,
                    overflow = TextOverflow.Ellipsis
                )
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
        shape = RoundedCornerShape(8.dp),
        color = if (isPrimary) PrimaryGreen else PaleGreen
    ) {
        Text(
            text,
            modifier = Modifier.padding(horizontal = 10.dp, vertical = 5.dp),
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
            trackColor = LightGray,
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
