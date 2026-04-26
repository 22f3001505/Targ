package com.targ.app

import android.os.Bundle
import android.util.Log
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavDestination.Companion.hierarchy
import androidx.navigation.NavGraph.Companion.findStartDestination
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import com.targ.app.ui.navigation.*
import com.targ.app.ui.screens.*
import com.targ.app.ui.theme.*
import com.targ.app.viewmodel.HealthViewModel

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Global crash handler — prevents app crash, logs error
        Thread.setDefaultUncaughtExceptionHandler { thread, throwable ->
            Log.e("TARG_CRASH", "Uncaught exception on ${thread.name}", throwable)
        }

        setContent {
            TargApp()
        }
    }
}

@Composable
fun TargApp() {
    // Wrap the entire app in error state tracking
    var appError by remember { mutableStateOf<String?>(null) }

    TargTheme {
        if (appError != null) {
            // Fallback error UI
            Surface(modifier = Modifier.fillMaxSize(), color = OffWhite) {
                Column(
                    modifier = Modifier.fillMaxSize().padding(32.dp),
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.Center
                ) {
                    Text("🥗", fontSize = 64.sp)
                    Spacer(Modifier.height(16.dp))
                    Text("TARG", fontSize = 28.sp, fontWeight = FontWeight.Bold, color = PrimaryGreen)
                    Spacer(Modifier.height(12.dp))
                    Text("Something went wrong", fontSize = 18.sp, color = DarkText)
                    Spacer(Modifier.height(8.dp))
                    Text(appError ?: "", fontSize = 13.sp, color = MediumText, textAlign = TextAlign.Center)
                    Spacer(Modifier.height(24.dp))
                    Button(
                        onClick = { appError = null },
                        colors = ButtonDefaults.buttonColors(containerColor = PrimaryGreen)
                    ) {
                        Text("Retry", color = White)
                    }
                }
            }
        } else {
            MainContent()
        }
    }
}

@Composable
private fun MainContent() {
    val navController = rememberNavController()
    val viewModel: HealthViewModel = viewModel()

    Scaffold(
        bottomBar = {
            NavigationBar(
                containerColor = White,
                tonalElevation = 0.dp
            ) {
                val navBackStackEntry by navController.currentBackStackEntryAsState()
                val currentDestination = navBackStackEntry?.destination

                bottomNavScreens.forEach { screen ->
                    val isSelected = currentDestination?.hierarchy?.any { it.route == screen.route } == true

                    NavigationBarItem(
                        icon = {
                            Icon(
                                imageVector = if (isSelected) screen.selectedIcon else screen.icon,
                                contentDescription = screen.title
                            )
                        },
                        label = {
                            Text(
                                screen.title,
                                fontSize = 11.sp,
                                fontWeight = if (isSelected) FontWeight.SemiBold else FontWeight.Normal
                            )
                        },
                        selected = isSelected,
                        onClick = {
                            navController.navigate(screen.route) {
                                popUpTo(navController.graph.findStartDestination().id) {
                                    saveState = true
                                }
                                launchSingleTop = true
                                restoreState = true
                            }
                        },
                        colors = NavigationBarItemDefaults.colors(
                            selectedIconColor = PrimaryGreen,
                            selectedTextColor = PrimaryGreen,
                            unselectedIconColor = MediumText,
                            unselectedTextColor = MediumText,
                            indicatorColor = PaleGreen
                        )
                    )
                }
            }
        }
    ) { innerPadding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .background(OffWhite)
        ) {
            NavHost(
                navController = navController,
                startDestination = Screen.Home.route
            ) {
                composable(Screen.Home.route) { HomeScreen(navController, viewModel) }
                composable(Screen.Diet.route) { HealthScreen(viewModel) }
                composable(Screen.Workout.route) { WorkoutScreen(viewModel) }
                composable(Screen.Macro.route) { MacroScreen(viewModel) }
                composable(Screen.Account.route) { AccountScreen(viewModel) }
                composable(Screen.Recipes.route) { DietScreen(viewModel) }
                composable(Screen.Planner.route) { PlannerScreen(viewModel) }
            }
        }
    }
}
