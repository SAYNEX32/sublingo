package com.sublingo.app.ui

import androidx.compose.runtime.Composable
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import com.sublingo.app.ui.episodes.EpisodesScreen
import com.sublingo.app.ui.exercises.ExerciseScreen
import com.sublingo.app.ui.placement.PlacementScreen
import com.sublingo.app.ui.report.ReportScreen

@Composable
fun AppNavHost(onLogout: () -> Unit) {
    val navController = rememberNavController()
    val episodeArgument = listOf(navArgument("episodeId") { type = NavType.IntType })

    NavHost(navController = navController, startDestination = "episodes") {
        composable("episodes") {
            EpisodesScreen(
                onOpenReport = { id -> navController.navigate("report/$id") },
                onOpenPlacement = { navController.navigate("placement") },
                onLogout = onLogout,
            )
        }
        composable("report/{episodeId}", arguments = episodeArgument) {
            ReportScreen(
                onBack = { navController.popBackStack() },
                onStartExercises = { id -> navController.navigate("exercises/$id") },
            )
        }
        composable("exercises/{episodeId}", arguments = episodeArgument) {
            ExerciseScreen(onBack = { navController.popBackStack() })
        }
        composable("placement") {
            PlacementScreen(onDone = { navController.popBackStack() })
        }
    }
}