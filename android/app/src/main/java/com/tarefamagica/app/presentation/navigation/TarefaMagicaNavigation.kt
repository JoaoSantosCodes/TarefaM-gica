package com.tarefamagica.app.presentation.navigation

import androidx.compose.runtime.Composable
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import com.tarefamagica.app.presentation.screens.auth.LoginScreen
import com.tarefamagica.app.presentation.screens.auth.RegisterScreen
import com.tarefamagica.app.presentation.screens.auth.TwoFactorScreen
import com.tarefamagica.app.presentation.screens.consent.ParentalConsentScreen
import com.tarefamagica.app.presentation.screens.dashboard.DashboardScreen
import com.tarefamagica.app.presentation.screens.financial.PixScreen
import com.tarefamagica.app.presentation.screens.gamification.AchievementsScreen
import com.tarefamagica.app.presentation.screens.gamification.LeaderboardScreen
import com.tarefamagica.app.presentation.screens.gamification.MissionsScreen
import com.tarefamagica.app.presentation.screens.levels.LevelsScreen
import com.tarefamagica.app.presentation.screens.profile.ProfileScreen
import com.tarefamagica.app.presentation.screens.tasks.TaskDetailScreen
import com.tarefamagica.app.presentation.screens.tasks.TaskListScreen
import com.tarefamagica.app.presentation.screens.tasks.TasksScreen
import com.tarefamagica.app.presentation.screens.wallet.WalletScreen

@Composable
fun TarefaMagicaNavigation(
    navController: NavHostController,
    startDestination: String = Screen.Login.route
) {
    NavHost(
        navController = navController,
        startDestination = startDestination
    ) {
        // Auth Screens
        composable(Screen.Login.route) {
            LoginScreen(
                onNavigateToRegister = {
                    navController.navigate(Screen.Register.route)
                },
                onNavigateToDashboard = { userId ->
                    navController.navigate(Screen.Dashboard.createRoute(userId)) {
                        popUpTo(Screen.Login.route) { inclusive = true }
                    }
                },
                onNavigateToTwoFactor = { userId ->
                    navController.navigate(Screen.TwoFactor.createRoute(userId))
                }
            )
        }
        
        composable(Screen.Register.route) {
            RegisterScreen(
                onNavigateBack = {
                    navController.popBackStack()
                },
                onNavigateToLogin = {
                    navController.navigate(Screen.Login.route) {
                        popUpTo(Screen.Register.route) { inclusive = true }
                    }
                },
                onNavigateToParentalConsent = { userId ->
                    navController.navigate(Screen.ParentalConsent.createRoute(userId))
                }
            )
        }
        
        composable(
            route = Screen.TwoFactor.route,
            arguments = Screen.TwoFactor.arguments
        ) { backStackEntry ->
            val userId = backStackEntry.arguments?.getString("userId") ?: ""
            TwoFactorScreen(
                userId = userId,
                onNavigateToDashboard = { verifiedUserId ->
                    navController.navigate(Screen.Dashboard.createRoute(verifiedUserId)) {
                        popUpTo(Screen.Login.route) { inclusive = true }
                    }
                },
                onNavigateBack = {
                    navController.popBackStack()
                }
            )
        }
        
        // Consent Screen
        composable(
            route = Screen.ParentalConsent.route,
            arguments = Screen.ParentalConsent.arguments
        ) { backStackEntry ->
            val userId = backStackEntry.arguments?.getString("userId") ?: ""
            ParentalConsentScreen(
                userId = userId,
                onNavigateToDashboard = { consentedUserId ->
                    navController.navigate(Screen.Dashboard.createRoute(consentedUserId)) {
                        popUpTo(Screen.Register.route) { inclusive = true }
                    }
                },
                onNavigateBack = {
                    navController.popBackStack()
                }
            )
        }
        
        // Main App Screens
        composable(
            route = Screen.Dashboard.route,
            arguments = Screen.Dashboard.arguments
        ) { backStackEntry ->
            val userId = backStackEntry.arguments?.getString("userId") ?: ""
            DashboardScreen(
                userId = userId,
                onNavigateToTasks = { dashboardUserId ->
                    navController.navigate(Screen.Tasks.createRoute(dashboardUserId))
                },
                onNavigateToLevels = { dashboardUserId ->
                    navController.navigate(Screen.Levels.createRoute(dashboardUserId))
                },
                onNavigateToProfile = { dashboardUserId ->
                    navController.navigate(Screen.Profile.createRoute(dashboardUserId))
                },
                onNavigateToPix = { dashboardUserId ->
                    navController.navigate(Screen.Pix.createRoute(dashboardUserId))
                },
                onLogout = {
                    navController.navigate(Screen.Login.route) {
                        popUpTo(0) { inclusive = true }
                    }
                }
            )
        }
        
        composable(
            route = Screen.Tasks.route,
            arguments = Screen.Tasks.arguments
        ) { backStackEntry ->
            val userId = backStackEntry.arguments?.getString("userId") ?: ""
            TasksScreen(
                userId = userId,
                onNavigateBack = {
                    navController.popBackStack()
                },
                onNavigateToDashboard = { tasksUserId ->
                    navController.navigate(Screen.Dashboard.createRoute(tasksUserId)) {
                        popUpTo(Screen.Dashboard.route) { inclusive = true }
                    }
                }
            )
        }
        
        composable(
            route = Screen.Levels.route,
            arguments = Screen.Levels.arguments
        ) { backStackEntry ->
            val userId = backStackEntry.arguments?.getString("userId") ?: ""
            LevelsScreen(
                userId = userId,
                onNavigateBack = {
                    navController.popBackStack()
                },
                onNavigateToDashboard = { levelsUserId ->
                    navController.navigate(Screen.Dashboard.createRoute(levelsUserId)) {
                        popUpTo(Screen.Dashboard.route) { inclusive = true }
                    }
                }
            )
        }
        
        composable(
            route = Screen.Profile.route,
            arguments = Screen.Profile.arguments
        ) { backStackEntry ->
            val userId = backStackEntry.arguments?.getString("userId") ?: ""
            ProfileScreen(
                userId = userId,
                onNavigateBack = {
                    navController.popBackStack()
                },
                onNavigateToDashboard = { profileUserId ->
                    navController.navigate(Screen.Dashboard.createRoute(profileUserId)) {
                        popUpTo(Screen.Dashboard.route) { inclusive = true }
                    }
                },
                onLogout = {
                    navController.navigate(Screen.Login.route) {
                        popUpTo(0) { inclusive = true }
                    }
                }
            )
        }
        
        // Financial Screen
        composable(
            route = Screen.Pix.route,
            arguments = Screen.Pix.arguments
        ) { backStackEntry ->
            val userId = backStackEntry.arguments?.getString("userId") ?: ""
            PixScreen(
                onNavigateBack = {
                    navController.popBackStack()
                }
            )
        }
        
        // Gamificação
        composable(Screen.Missions.route) {
            MissionsScreen(
                onNavigateBack = {
                    navController.popBackStack()
                }
            )
        }
        
        composable(Screen.Achievements.route) {
            AchievementsScreen(
                onNavigateBack = {
                    navController.popBackStack()
                }
            )
        }
        
        composable(Screen.Leaderboard.route) {
            LeaderboardScreen(
                onNavigateBack = {
                    navController.popBackStack()
                }
            )
        }
        
        // Sistema de Tarefas
        composable(Screen.TaskList.route) {
            TaskListScreen(
                onNavigateToTaskDetail = { taskId ->
                    navController.navigate(Screen.TaskDetail.createRoute(taskId))
                },
                onNavigateBack = {
                    navController.popBackStack()
                }
            )
        }
        
        composable(
            route = Screen.TaskDetail.route,
            arguments = Screen.TaskDetail.arguments
        ) { backStackEntry ->
            val taskId = backStackEntry.arguments?.getString("taskId") ?: ""
            TaskDetailScreen(
                taskId = taskId,
                onNavigateBack = {
                    navController.popBackStack()
                },
                onTaskCompleted = {
                    navController.popBackStack()
                }
            )
        }
        
        // Carteira e Finanças
        composable(Screen.Wallet.route) {
            WalletScreen(
                onNavigateBack = {
                    navController.popBackStack()
                }
            )
        }
    }
} 