package com.targ.app.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Shapes

// ═══════════════════════════════════════════
// TARG BRAND COLORS (matches web design system)
// ═══════════════════════════════════════════

val PrimaryGreen = Color(0xFF4CAF50)
val DarkGreen = Color(0xFF2E7D32)
val SoftMint = Color(0xFFA5D6A7)
val LightMint = Color(0xFFC8E6C9)
val PaleGreen = Color(0xFFE8F5E9)

val DarkText = Color(0xFF333333)
val MediumText = Color(0xFF666666)
val LightText = Color(0xFF999999)

val White = Color(0xFFFFFFFF)
val OffWhite = Color(0xFFF8FFF8)
val LightGray = Color(0xFFF5F5F5)

// BMI Category Colors
val BmiNormal = Color(0xFF4CAF50)
val BmiUnderweight = Color(0xFFFFA726)
val BmiOverweight = Color(0xFFFF7043)
val BmiObese = Color(0xFFEF5350)

// Design tokens
val CardRadius = 16.dp
val ButtonRadius = 12.dp
val PagePadding = 16.dp
val CardElevation = 4.dp

// ═══════════════════════════════════════════
// COLOR SCHEMES
// ═══════════════════════════════════════════

private val LightColorScheme = lightColorScheme(
    primary = PrimaryGreen,
    onPrimary = White,
    primaryContainer = LightMint,
    onPrimaryContainer = DarkGreen,
    secondary = DarkGreen,
    onSecondary = White,
    secondaryContainer = PaleGreen,
    background = OffWhite,
    onBackground = DarkText,
    surface = White,
    onSurface = DarkText,
    surfaceVariant = LightGray,
    onSurfaceVariant = MediumText,
    error = BmiObese,
    onError = White
)

private val DarkColorScheme = darkColorScheme(
    primary = SoftMint,
    onPrimary = Color(0xFF003300),
    primaryContainer = DarkGreen,
    onPrimaryContainer = LightMint,
    secondary = SoftMint,
    onSecondary = Color(0xFF003300),
    secondaryContainer = Color(0xFF1B5E20),
    background = Color(0xFF121212),
    onBackground = Color(0xFFE0E0E0),
    surface = Color(0xFF1E1E1E),
    onSurface = Color(0xFFE0E0E0),
    surfaceVariant = Color(0xFF2C2C2C),
    onSurfaceVariant = Color(0xFFBBBBBB),
    error = Color(0xFFEF9A9A),
    onError = Color(0xFF121212)
)

// ═══════════════════════════════════════════
// SHAPES
// ═══════════════════════════════════════════

val TargShapes = Shapes(
    small = RoundedCornerShape(8.dp),
    medium = RoundedCornerShape(CardRadius),
    large = RoundedCornerShape(20.dp)
)

// ═══════════════════════════════════════════
// TYPOGRAPHY
// ═══════════════════════════════════════════

val TargTypography = Typography(
    headlineLarge = TextStyle(
        fontWeight = FontWeight.Bold,
        fontSize = 28.sp,
        lineHeight = 34.sp
    ),
    headlineMedium = TextStyle(
        fontWeight = FontWeight.SemiBold,
        fontSize = 22.sp,
        lineHeight = 28.sp
    ),
    titleLarge = TextStyle(
        fontWeight = FontWeight.SemiBold,
        fontSize = 18.sp,
        lineHeight = 24.sp
    ),
    titleMedium = TextStyle(
        fontWeight = FontWeight.Medium,
        fontSize = 16.sp,
        lineHeight = 22.sp
    ),
    bodyLarge = TextStyle(
        fontWeight = FontWeight.Normal,
        fontSize = 16.sp,
        lineHeight = 24.sp
    ),
    bodyMedium = TextStyle(
        fontWeight = FontWeight.Normal,
        fontSize = 14.sp,
        lineHeight = 20.sp
    ),
    labelLarge = TextStyle(
        fontWeight = FontWeight.SemiBold,
        fontSize = 14.sp,
        lineHeight = 20.sp
    )
)

// ═══════════════════════════════════════════
// THEME COMPOSABLE
// ═══════════════════════════════════════════

@Composable
fun TargTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    val colorScheme = if (darkTheme) DarkColorScheme else LightColorScheme

    MaterialTheme(
        colorScheme = colorScheme,
        typography = TargTypography,
        shapes = TargShapes,
        content = content
    )
}

