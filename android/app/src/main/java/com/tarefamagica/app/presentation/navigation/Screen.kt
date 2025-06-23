package com.tarefamagica.app.presentation.navigation

import androidx.navigation.NavType
import androidx.navigation.navArgument

sealed class Screen(val route: String) {
    // Autenticação
    object Login : Screen("login")
    object Register : Screen("register")
    object TwoFactor : Screen("two_factor") {
        val arguments = listOf(
            navArgument("userId") { type = NavType.StringType }
        )
        
        fun createRoute(userId: String) = "$route/$userId"
    }
    
    object ParentalConsent : Screen("parental_consent") {
        val arguments = listOf(
            navArgument("userId") { type = NavType.StringType }
        )
        
        fun createRoute(userId: String) = "$route/$userId"
    }
    
    // Dashboard
    object Dashboard : Screen("dashboard") {
        val arguments = listOf(
            navArgument("userId") { type = NavType.StringType }
        )
        
        fun createRoute(userId: String) = "$route/$userId"
    }
    
    // Tarefas
    object TaskList : Screen("tasks") {
        val arguments = listOf(
            navArgument("userId") { type = NavType.StringType }
        )
        
        fun createRoute(userId: String) = "$route/$userId"
    }
    
    object TaskDetail : Screen("task/{taskId}") {
        val arguments = listOf(
            navArgument("taskId") { type = NavType.StringType }
        )
        
        fun createRoute(taskId: String) = "task/$taskId"
    }
    
    // Gamificação
    object Missions : Screen("missions")
    object Achievements : Screen("achievements")
    object Leaderboard : Screen("leaderboard")
    
    // Carteira
    object Wallet : Screen("wallet")
    
    // Perfil
    object Profile : Screen("profile") {
        val arguments = listOf(
            navArgument("userId") { type = NavType.StringType }
        )
        
        fun createRoute(userId: String) = "$route/$userId"
    }
    
    object Pix : Screen("pix") {
        val arguments = listOf(
            navArgument("userId") { type = NavType.StringType }
        )
        
        fun createRoute(userId: String) = "$route/$userId"
    }
} 