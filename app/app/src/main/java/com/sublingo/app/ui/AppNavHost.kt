package com.sublingo.app.ui

import androidx.compose.runtime.Composable
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import com.sublingo.app.ui.episodes.EpisodesScreen
import com.sublingo.app.ui.report.ReportScreen

@Composable
fun AppNavHost(onLogout: () -> Unit) {
    val navController = rememberNavController()

    NavHost(navController = navController, startDestination = "episodes") {
        composable("episodes") {
            EpisodesScreen(
                onOpenReport = { id -> navController.navigate("report/$id") },
                onLogout = onLogout,
            )
        }
        composable(
            route = "report/{episodeId}",
            arguments = listOf(navArgument("episodeId") { type = NavType.IntType }),
        ) {
            ReportScreen(onBack = { navController.popBackStack() })
        }
    }
}