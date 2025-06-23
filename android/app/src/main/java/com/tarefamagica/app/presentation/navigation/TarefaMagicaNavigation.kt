package com.tarefamagica.app.presentation.navigation

import androidx.compose.runtime.Composable
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import com.tarefamagica.app.presentation.screens.auth.LoginScreen
import com.tarefamagica.app.presentation.screens.auth.RegisterScreen
import com.tarefamagica.app.presentation.screens.auth.TwoFactorScreen
import com.tarefamagica.app.presentation.screens.dashboard.DashboardScreen
import com.tarefamagica.app.presentation.screens.gamification.AchievementsScreen
import com.tarefamagica.app.presentation.screens.gamification.LeaderboardScreen
import com.tarefamagica.app.presentation.screens.gamification.MissionsScreen
import com.tarefamagica.app.presentation.screens.profile.ProfileScreen
import com.tarefamagica.app.presentation.screens.tasks.TaskDetailScreen
import com.tarefamagica.app.presentation.screens.tasks.TaskListScreen
import com.tarefamagica.app.presentation.screens.wallet.WalletScreen

@Composable
fun TarefaMagicaNavigation(
    navController: NavHostController = androidx.navigation.compose.rememberNavController()
) {
    NavHost(
        navController = navController,
        startDestination = Screen.Login.route
    ) {
        // Telas de Autenticação
        composable(Screen.Login.route) {
            LoginScreen(
                onNavigateToRegister = {
                    navController.navigate(Screen.Register.route)
                },
                onNavigateToTwoFactor = { userId ->
                    navController.navigate(Screen.TwoFactor.createRoute(userId))
                },
                onNavigateToDashboard = {
                    navController.navigate(Screen.Dashboard.route) {
                        popUpTo(Screen.Login.route) { inclusive = true }
                    }
                }
            )
        }
        
        composable(Screen.Register.route) {
            RegisterScreen(
                onNavigateToLogin = {
                    navController.navigate(Screen.Login.route) {
                        popUpTo(Screen.Register.route) { inclusive = true }
                    }
                },
                onNavigateToDashboard = {
                    navController.navigate(Screen.Dashboard.route) {
                        popUpTo(Screen.Register.route) { inclusive = true }
                    }
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
                onNavigateToDashboard = {
                    navController.navigate(Screen.Dashboard.route) {
                        popUpTo(Screen.Login.route) { inclusive = true }
                    }
                }
            )
        }
        
        // Dashboard Principal
        composable(Screen.Dashboard.route) {
            DashboardScreen(
                onNavigateToTasks = {
                    navController.navigate(Screen.TaskList.route)
                },
                onNavigateToMissions = {
                    navController.navigate(Screen.Missions.route)
                },
                onNavigateToWallet = {
                    navController.navigate(Screen.Wallet.route)
                },
                onNavigateToProfile = {
                    navController.navigate(Screen.Profile.route)
                },
                onNavigateToAchievements = {
                    navController.navigate(Screen.Achievements.route)
                },
                onNavigateToLeaderboard = {
                    navController.navigate(Screen.Leaderboard.route)
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
        
        // Carteira e Finanças
        composable(Screen.Wallet.route) {
            WalletScreen(
                onNavigateBack = {
                    navController.popBackStack()
                }
            )
        }
        
        // Perfil do Usuário
        composable(Screen.Profile.route) {
            ProfileScreen(
                onNavigateBack = {
                    navController.popBackStack()
                },
                onLogout = {
                    navController.navigate(Screen.Login.route) {
                        popUpTo(0) { inclusive = true }
                    }
                }
            )
        }
    }
} 