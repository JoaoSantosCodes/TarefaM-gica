package com.tarefamagica.app.data.model

import java.time.LocalDate
import java.time.LocalDateTime

// ===== MODELOS PRINCIPAIS =====

data class Task(
    val id: String,
    val title: String,
    val description: String,
    val category: TaskCategory,
    val points: Int,
    val dueDate: LocalDate?,
    val isCompleted: Boolean,
    val createdAt: LocalDateTime,
    val updatedAt: LocalDateTime,
    val completedAt: LocalDateTime?
)

enum class TaskCategory(val displayName: String, val color: String) {
    SCHOOL("Escola", "#2196F3"),
    HOME("Casa", "#4CAF50"),
    PERSONAL("Pessoal", "#9C27B0"),
    HEALTH("Saúde", "#FF5722"),
    FUN("Diversão", "#FF9800")
}

data class UserProfile(
    val id: String,
    val name: String,
    val email: String,
    val age: Int,
    val avatar: String?,
    val level: Int,
    val experience: Int,
    val experienceToNextLevel: Int,
    val experienceProgress: Float,
    val createdAt: LocalDateTime,
    val lastLoginAt: LocalDateTime?
)

data class UserStatistics(
    val completedTasks: Int,
    val totalPoints: Int,
    val achievements: Int,
    val streak: Int,
    val totalTasks: Int,
    val averagePointsPerTask: Float,
    val favoriteCategory: TaskCategory?
)

data class Achievement(
    val id: String,
    val title: String,
    val description: String,
    val points: Int,
    val icon: String,
    val isUnlocked: Boolean,
    val unlockedAt: LocalDateTime?,
    val category: AchievementCategory
)

enum class AchievementCategory(val displayName: String) {
    TASK_COMPLETION("Conclusão de Tarefas"),
    STREAK("Sequência"),
    POINTS("Pontos"),
    SPECIAL("Especial"),
    MILESTONE("Marco")
}

data class PointsHistory(
    val id: String,
    val points: Int,
    val reason: String,
    val taskId: String?,
    val createdAt: LocalDateTime
)

data class LeaderboardEntry(
    val rank: Int,
    val userId: String,
    val userName: String,
    val points: Int,
    val level: Int,
    val avatar: String?
)

data class Transaction(
    val id: String,
    val type: TransactionType,
    val amount: Double,
    val status: TransactionStatus,
    val pixKey: String?,
    val description: String,
    val createdAt: LocalDateTime,
    val processedAt: LocalDateTime?
)

enum class TransactionType(val displayName: String) {
    WITHDRAWAL("Saque"),
    DEPOSIT("Depósito"),
    REFUND("Reembolso")
}

enum class TransactionStatus(val displayName: String) {
    PENDING("Pendente"),
    PROCESSING("Processando"),
    COMPLETED("Concluída"),
    FAILED("Falhou"),
    CANCELLED("Cancelada")
}

data class AccessLog(
    val id: String,
    val action: String,
    val ipAddress: String,
    val userAgent: String,
    val timestamp: LocalDateTime,
    val success: Boolean,
    val details: String?
)

data class Notification(
    val id: String,
    val title: String,
    val message: String,
    val type: NotificationType,
    val isRead: Boolean,
    val createdAt: LocalDateTime,
    val data: Map<String, Any>?
)

enum class NotificationType(val displayName: String) {
    TASK_COMPLETED("Tarefa Concluída"),
    ACHIEVEMENT_UNLOCKED("Conquista Desbloqueada"),
    LEVEL_UP("Subiu de Nível"),
    POINTS_EARNED("Pontos Ganhos"),
    SECURITY_ALERT("Alerta de Segurança"),
    SYSTEM("Sistema")
}

// ===== MODELOS DE CONFIGURAÇÃO =====

data class AppConfig(
    val apiBaseUrl: String,
    val appVersion: String,
    val buildNumber: Int,
    val features: Map<String, Boolean>
)

data class UserPreferences(
    val notificationsEnabled: Boolean,
    val soundEnabled: Boolean,
    val vibrationEnabled: Boolean,
    val theme: AppTheme,
    val language: String,
    val accessibilitySettings: AccessibilitySettings
)

enum class AppTheme(val displayName: String) {
    LIGHT("Claro"),
    DARK("Escuro"),
    AUTO("Automático")
}

data class AccessibilitySettings(
    val highContrast: Boolean,
    val largeText: Boolean,
    val screenReader: Boolean,
    val reducedMotion: Boolean
)

// ===== MODELOS DE SEGURANÇA =====

data class SecuritySettings(
    val twoFactorEnabled: Boolean,
    val biometricEnabled: Boolean,
    val pinEnabled: Boolean,
    val lastPasswordChange: LocalDateTime?,
    val failedLoginAttempts: Int,
    val accountLocked: Boolean,
    val lockUntil: LocalDateTime?
)

data class ParentalConsent(
    val id: String,
    val parentName: String,
    val parentEmail: String,
    val parentPhone: String,
    val relationship: String,
    val consentDate: LocalDateTime,
    val isActive: Boolean,
    val expiresAt: LocalDateTime?
)

// ===== MODELOS DE GAMIFICAÇÃO =====

data class GamificationConfig(
    val pointsPerTask: Int,
    val bonusMultiplier: Float,
    val streakBonus: Int,
    val levelThresholds: List<Int>,
    val achievementConfigs: List<AchievementConfig>
)

data class AchievementConfig(
    val id: String,
    val title: String,
    val description: String,
    val points: Int,
    val requirements: AchievementRequirements,
    val icon: String,
    val category: AchievementCategory
)

data class AchievementRequirements(
    val taskCount: Int? = null,
    val pointsRequired: Int? = null,
    val streakDays: Int? = null,
    val categoryTasks: Map<TaskCategory, Int>? = null,
    val specialCondition: String? = null
)

// ===== MODELOS DE RELATÓRIOS =====

data class ProgressReport(
    val period: String,
    val tasksCompleted: Int,
    val pointsEarned: Int,
    val achievementsUnlocked: Int,
    val streakMaintained: Int,
    val levelProgress: Float,
    val categoryBreakdown: Map<TaskCategory, Int>,
    val recommendations: List<String>
)

data class WeeklyReport(
    val weekStart: LocalDate,
    val weekEnd: LocalDate,
    val dailyProgress: List<DailyProgress>,
    val weeklyStats: WeeklyStats,
    val goals: List<Goal>,
    val achievements: List<Achievement>
)

data class DailyProgress(
    val date: LocalDate,
    val tasksCompleted: Int,
    val pointsEarned: Int,
    val streakCount: Int
)

data class WeeklyStats(
    val totalTasks: Int,
    val totalPoints: Int,
    val averageTasksPerDay: Float,
    val bestDay: LocalDate,
    val improvement: Float
)

data class Goal(
    val id: String,
    val title: String,
    val description: String,
    val target: Int,
    val current: Int,
    val unit: String,
    val deadline: LocalDate?,
    val isCompleted: Boolean
)

// ===== MODELOS DE ERRO =====

data class ApiError(
    val code: String,
    val message: String,
    val details: Map<String, Any>?,
    val timestamp: LocalDateTime
)

sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val error: ApiError) : Result<Nothing>()
    object Loading : Result<Nothing>()
}

// ===== EXTENSÕES ÚTEIS =====

fun Task.isOverdue(): Boolean {
    return dueDate != null && dueDate.isBefore(LocalDate.now()) && !isCompleted
}

fun Task.isDueToday(): Boolean {
    return dueDate != null && dueDate.isEqual(LocalDate.now())
}

fun UserProfile.getDisplayName(): String {
    return name.ifEmpty { "Usuário" }
}

fun UserProfile.getLevelTitle(): String {
    return when {
        level <= 5 -> "Iniciante"
        level <= 10 -> "Aprendiz"
        level <= 15 -> "Intermediário"
        level <= 20 -> "Avançado"
        level <= 25 -> "Expert"
        else -> "Mestre"
    }
} 