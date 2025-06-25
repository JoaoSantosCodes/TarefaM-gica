package com.tarefamagica.app.data.repository

import com.tarefamagica.app.data.api.ApiService
import com.tarefamagica.app.data.model.*
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class GamificationRepository @Inject constructor(
    private val apiService: ApiService
) {
    
    suspend fun getPoints(): Flow<Result<PointsData>> = flow {
        emit(Result.Loading)
        
        try {
            val response = apiService.getPoints()
            
            if (response.success && response.data != null) {
                emit(Result.Success(response.data))
            } else {
                emit(Result.Error(ApiError("POINTS_ERROR", response.message, null)))
            }
        } catch (e: Exception) {
            emit(Result.Error(ApiError("NETWORK_ERROR", "Erro de conexão: ${e.message}", null)))
        }
    }
    
    suspend fun getLevel(): Flow<Result<LevelData>> = flow {
        emit(Result.Loading)
        
        try {
            val response = apiService.getLevel()
            
            if (response.success && response.data != null) {
                emit(Result.Success(response.data))
            } else {
                emit(Result.Error(ApiError("LEVEL_ERROR", response.message, null)))
            }
        } catch (e: Exception) {
            emit(Result.Error(ApiError("NETWORK_ERROR", "Erro de conexão: ${e.message}", null)))
        }
    }
    
    suspend fun getLeaderboard(): Flow<Result<LeaderboardData>> = flow {
        emit(Result.Loading)
        
        try {
            val response = apiService.getLeaderboard()
            
            if (response.success && response.data != null) {
                emit(Result.Success(response.data))
            } else {
                emit(Result.Error(ApiError("LEADERBOARD_ERROR", response.message, null)))
            }
        } catch (e: Exception) {
            emit(Result.Error(ApiError("NETWORK_ERROR", "Erro de conexão: ${e.message}", null)))
        }
    }
    
    suspend fun getUserAchievements(): Flow<Result<List<Achievement>>> = flow {
        emit(Result.Loading)
        
        try {
            val response = apiService.getUserAchievements()
            
            if (response.success && response.data != null) {
                emit(Result.Success(response.data.achievements))
            } else {
                emit(Result.Error(ApiError("ACHIEVEMENTS_ERROR", response.message, null)))
            }
        } catch (e: Exception) {
            emit(Result.Error(ApiError("NETWORK_ERROR", "Erro de conexão: ${e.message}", null)))
        }
    }
    
    // ===== LÓGICA LOCAL DE PONTUAÇÃO =====
    
    fun calculateTaskPoints(
        basePoints: Int,
        category: TaskCategory,
        difficulty: TaskDifficulty,
        streak: Int,
        timeBonus: Boolean = false
    ): Int {
        var points = basePoints
        
        // Multiplicador por categoria
        val categoryMultiplier = when (category) {
            TaskCategory.SCHOOL -> 1.2f
            TaskCategory.HOME -> 1.0f
            TaskCategory.PERSONAL -> 1.1f
            TaskCategory.HEALTH -> 1.3f
            TaskCategory.FUN -> 0.8f
        }
        
        // Multiplicador por dificuldade
        val difficultyMultiplier = when (difficulty) {
            TaskDifficulty.EASY -> 0.8f
            TaskDifficulty.MEDIUM -> 1.0f
            TaskDifficulty.HARD -> 1.5f
            TaskDifficulty.EXPERT -> 2.0f
        }
        
        // Bônus por sequência
        val streakBonus = when {
            streak >= 7 -> 0.5f
            streak >= 3 -> 0.2f
            else -> 0f
        }
        
        // Bônus por tempo (conclusão antes do prazo)
        val timeBonusMultiplier = if (timeBonus) 0.2f else 0f
        
        // Calcular pontos finais
        points = (points * categoryMultiplier * difficultyMultiplier).toInt()
        points += (points * streakBonus).toInt()
        points += (points * timeBonusMultiplier).toInt()
        
        return points
    }
    
    fun calculateLevelThreshold(level: Int): Int {
        return when {
            level <= 5 -> level * 100
            level <= 10 -> 500 + (level - 5) * 150
            level <= 15 -> 1250 + (level - 10) * 200
            level <= 20 -> 2250 + (level - 15) * 250
            else -> 3500 + (level - 20) * 300
        }
    }
    
    fun getLevelTitle(level: Int): String {
        return when {
            level <= 5 -> "Iniciante"
            level <= 10 -> "Aprendiz"
            level <= 15 -> "Intermediário"
            level <= 20 -> "Avançado"
            level <= 25 -> "Expert"
            level <= 30 -> "Mestre"
            level <= 40 -> "Lenda"
            else -> "Deus"
        }
    }
    
    fun checkLevelUp(currentExperience: Int, currentLevel: Int): LevelUpResult {
        val nextLevelThreshold = calculateLevelThreshold(currentLevel + 1)
        
        return if (currentExperience >= nextLevelThreshold) {
            LevelUpResult(
                levelUp = true,
                newLevel = currentLevel + 1,
                experienceNeeded = 0,
                experienceProgress = 1.0f
            )
        } else {
            val previousThreshold = calculateLevelThreshold(currentLevel)
            val experienceInCurrentLevel = currentExperience - previousThreshold
            val experienceNeededForNextLevel = nextLevelThreshold - currentExperience
            val progress = experienceInCurrentLevel.toFloat() / (nextLevelThreshold - previousThreshold)
            
            LevelUpResult(
                levelUp = false,
                newLevel = currentLevel,
                experienceNeeded = experienceNeededForNextLevel,
                experienceProgress = progress
            )
        }
    }
    
    fun generateAchievements(): List<AchievementConfig> {
        return listOf(
            // Conquistas por número de tarefas
            AchievementConfig(
                id = "first_task",
                title = "Primeira Conquista",
                description = "Completou sua primeira tarefa",
                points = 100,
                requirements = AchievementRequirements(taskCount = 1),
                icon = "star",
                category = AchievementCategory.TASK_COMPLETION
            ),
            AchievementConfig(
                id = "task_master_10",
                title = "Mestre das Tarefas",
                description = "Completou 10 tarefas",
                points = 200,
                requirements = AchievementRequirements(taskCount = 10),
                icon = "check_circle",
                category = AchievementCategory.TASK_COMPLETION
            ),
            AchievementConfig(
                id = "task_master_50",
                title = "Veterano",
                description = "Completou 50 tarefas",
                points = 500,
                requirements = AchievementRequirements(taskCount = 50),
                icon = "military_tech",
                category = AchievementCategory.TASK_COMPLETION
            ),
            
            // Conquistas por sequência
            AchievementConfig(
                id = "streak_3",
                title = "Consistente",
                description = "Manteve uma sequência de 3 dias",
                points = 150,
                requirements = AchievementRequirements(streakDays = 3),
                icon = "local_fire_department",
                category = AchievementCategory.STREAK
            ),
            AchievementConfig(
                id = "streak_7",
                title = "Dedicado",
                description = "Manteve uma sequência de 7 dias",
                points = 300,
                requirements = AchievementRequirements(streakDays = 7),
                icon = "whatshot",
                category = AchievementCategory.STREAK
            ),
            AchievementConfig(
                id = "streak_30",
                title = "Inabalável",
                description = "Manteve uma sequência de 30 dias",
                points = 1000,
                requirements = AchievementRequirements(streakDays = 30),
                icon = "auto_awesome",
                category = AchievementCategory.STREAK
            ),
            
            // Conquistas por pontos
            AchievementConfig(
                id = "points_1000",
                title = "Mil Pontos",
                description = "Acumulou 1.000 pontos",
                points = 250,
                requirements = AchievementRequirements(pointsRequired = 1000),
                icon = "stars",
                category = AchievementCategory.POINTS
            ),
            AchievementConfig(
                id = "points_5000",
                title = "Mestre dos Pontos",
                description = "Acumulou 5.000 pontos",
                points = 500,
                requirements = AchievementRequirements(pointsRequired = 5000),
                icon = "workspace_premium",
                category = AchievementCategory.POINTS
            ),
            
            // Conquistas por categoria
            AchievementConfig(
                id = "school_master",
                title = "Estudante Exemplar",
                description = "Completou 20 tarefas de escola",
                points = 400,
                requirements = AchievementRequirements(
                    categoryTasks = mapOf(TaskCategory.SCHOOL to 20)
                ),
                icon = "school",
                category = AchievementCategory.SPECIAL
            ),
            AchievementConfig(
                id = "home_master",
                title = "Organizador",
                description = "Completou 15 tarefas de casa",
                points = 300,
                requirements = AchievementRequirements(
                    categoryTasks = mapOf(TaskCategory.HOME to 15)
                ),
                icon = "home",
                category = AchievementCategory.SPECIAL
            ),
            AchievementConfig(
                id = "health_master",
                title = "Saúde em Dia",
                description = "Completou 10 tarefas de saúde",
                points = 350,
                requirements = AchievementRequirements(
                    categoryTasks = mapOf(TaskCategory.HEALTH to 10)
                ),
                icon = "favorite",
                category = AchievementCategory.SPECIAL
            )
        )
    }
}

// ===== MODELOS DE SUPORTE =====

enum class TaskDifficulty(val displayName: String, val multiplier: Float) {
    EASY("Fácil", 0.8f),
    MEDIUM("Médio", 1.0f),
    HARD("Difícil", 1.5f),
    EXPERT("Expert", 2.0f)
}

data class LevelUpResult(
    val levelUp: Boolean,
    val newLevel: Int,
    val experienceNeeded: Int,
    val experienceProgress: Float
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

enum class AchievementCategory(val displayName: String) {
    TASK_COMPLETION("Conclusão de Tarefas"),
    STREAK("Sequência"),
    POINTS("Pontos"),
    SPECIAL("Especial"),
    MILESTONE("Marco")
}

// ===== API ERROR =====

data class ApiError(
    val code: String,
    val message: String,
    val details: Map<String, Any>?
) 