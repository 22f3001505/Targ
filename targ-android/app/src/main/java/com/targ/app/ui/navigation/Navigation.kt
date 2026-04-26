package com.targ.app.ui.navigation

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.*
import androidx.compose.material.icons.automirrored.outlined.*
import androidx.compose.material.icons.filled.*
import androidx.compose.material.icons.outlined.*
import androidx.compose.ui.graphics.vector.ImageVector

sealed class Screen(
    val route: String,
    val title: String,
    val icon: ImageVector,
    val selectedIcon: ImageVector
) {
    data object Home : Screen("home", "Home", Icons.Outlined.Home, Icons.Filled.Home)
    data object Diet : Screen("diet", "Diet", Icons.Outlined.Restaurant, Icons.Filled.Restaurant)
    data object Workout : Screen("workout", "Workout", Icons.Outlined.FitnessCenter, Icons.Filled.FitnessCenter)
    data object Macro : Screen("macro", "Macros", Icons.Outlined.PieChart, Icons.Filled.PieChart)
    data object Account : Screen("account", "Account", Icons.Outlined.Person, Icons.Filled.Person)

    // Sub-screens (not in bottom nav)
    data object Recipes : Screen("recipes", "Recipes", Icons.AutoMirrored.Outlined.MenuBook, Icons.AutoMirrored.Filled.MenuBook)
    data object Planner : Screen("planner", "Planner", Icons.Outlined.CalendarMonth, Icons.Filled.CalendarMonth)
}

val bottomNavScreens = listOf(
    Screen.Home,
    Screen.Diet,
    Screen.Workout,
    Screen.Macro,
    Screen.Account
)
