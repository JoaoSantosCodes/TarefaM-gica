package com.tarefamagica.app.presentation.screens.achievements

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.tarefamagica.app.data.repository.GamificationRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class AchievementsViewModel @Inject constructor(
    private val gamificationRepository: GamificationRepository
) : ViewModel() {
    
    private val _uiState = MutableStateFlow(AchievementsUiState())
    val uiState: StateFlow<AchievementsUiState> = _uiState.asStateFlow()
    
    init {
        loadAchievements()
    }
    
    fun updateFilter(filter: AchievementFilter) {
        _uiState.update { it.copy(selectedFilter = filter) }
        applyFilters()
    }
    
    fun selectAchievement(achievement: Achievement) {
        _uiState.update { it.copy(selectedAchievement = achievement) }
    }
    
    fun clearSelectedAchievement() {
        _uiState.update { it.copy(selectedAchievement = null) }
    }
    
    private fun loadAchievements() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            
            try {
                val achievements = createMockAchievements()
                _uiState.update { 
                    it.copy(
                        achievements = achievements,
                        isLoading = false
                    )
                }
                applyFilters()
                
            } catch (e: Exception) {
                _uiState.update { 
                    it.copy(
                        isLoading = false,
                        errorMessage = "Erro ao carregar conquistas: ${e.message}"
                    )
                }
            }
        }
    }
    
    private fun applyFilters() {
        val currentState = _uiState.value
        var filteredAchievements = currentState.achievements
        
        // Aplicar filtro
        filteredAchievements = when (currentState.selectedFilter) {
            AchievementFilter.ALL -> filteredAchievements
            AchievementFilter.UNLOCKED -> filteredAchievements.filter { it.isUnlocked }
            AchievementFilter.LOCKED -> filteredAchievements.filter { !it.isUnlocked }
            AchievementFilter.RECENT -> filteredAchievements
                .filter { it.isUnlocked }
                .sortedByDescending { it.unlockedAt }
                .take(5)
        }
        
        _uiState.update { it.copy(filteredAchievements = filteredAchievements) }
    }
    
    private fun createMockAchievements(): List<Achievement> {
        return listOf(
            Achievement(
                id = "first_task",
                title = "Primeira Conquista",
                description = "Completou sua primeira tarefa e deu o primeiro passo em sua jornada mágica!",
                points = 100,
                icon = "star",
                isUnlocked = true,
                unlockedAt = java.time.LocalDateTime.now().minusDays(5),
                category = AchievementCategory.TASK_COMPLETION
            ),
            Achievement(
                id = "task_master_10",
                title = "Mestre das Tarefas",
                description = "Completou 10 tarefas e está se tornando um verdadeiro organizador!",
                points = 200,
                icon = "check_circle",
                isUnlocked = true,
                unlockedAt = java.time.LocalDateTime.now().minusDays(3),
                category = AchievementCategory.TASK_COMPLETION
            ),
            Achievement(
                id = "task_master_50",
                title = "Veterano",
                description = "Completou 50 tarefas! Você é um verdadeiro veterano da organização!",
                points = 500,
                icon = "military_tech",
                isUnlocked = false,
                unlockedAt = null,
                category = AchievementCategory.TASK_COMPLETION
            ),
            Achievement(
                id = "streak_3",
                title = "Consistente",
                description = "Manteve uma sequência de 3 dias! A consistência é a chave do sucesso!",
                points = 150,
                icon = "local_fire_department",
                isUnlocked = true,
                unlockedAt = java.time.LocalDateTime.now().minusDays(2),
                category = AchievementCategory.STREAK
            ),
            Achievement(
                id = "streak_7",
                title = "Dedicado",
                description = "Manteve uma sequência de 7 dias! Você é realmente dedicado!",
                points = 300,
                icon = "whatshot",
                isUnlocked = false,
                unlockedAt = null,
                category = AchievementCategory.STREAK
            ),
            Achievement(
                id = "streak_30",
                title = "Inabalável",
                description = "Manteve uma sequência de 30 dias! Você é inabalável!",
                points = 1000,
                icon = "auto_awesome",
                isUnlocked = false,
                unlockedAt = null,
                category = AchievementCategory.STREAK
            ),
            Achievement(
                id = "points_1000",
                title = "Mil Pontos",
                description = "Acumulou 1.000 pontos! Você está construindo uma fortuna mágica!",
                points = 250,
                icon = "stars",
                isUnlocked = true,
                unlockedAt = java.time.LocalDateTime.now().minusDays(1),
                category = AchievementCategory.POINTS
            ),
            Achievement(
                id = "points_5000",
                title = "Mestre dos Pontos",
                description = "Acumulou 5.000 pontos! Você é um verdadeiro mestre dos pontos!",
                points = 500,
                icon = "workspace_premium",
                isUnlocked = false,
                unlockedAt = null,
                category = AchievementCategory.POINTS
            ),
            Achievement(
                id = "school_master",
                title = "Estudante Exemplar",
                description = "Completou 20 tarefas de escola! O conhecimento é poder!",
                points = 400,
                icon = "school",
                isUnlocked = true,
                unlockedAt = java.time.LocalDateTime.now().minusHours(12),
                category = AchievementCategory.SPECIAL
            ),
            Achievement(
                id = "home_master",
                title = "Organizador",
                description = "Completou 15 tarefas de casa! Sua casa está sempre organizada!",
                points = 300,
                icon = "home",
                isUnlocked = false,
                unlockedAt = null,
                category = AchievementCategory.SPECIAL
            ),
            Achievement(
                id = "health_master",
                title = "Saúde em Dia",
                description = "Completou 10 tarefas de saúde! Sua saúde é sua prioridade!",
                points = 350,
                icon = "favorite",
                isUnlocked = false,
                unlockedAt = null,
                category = AchievementCategory.SPECIAL
            ),
            Achievement(
                id = "fun_master",
                title = "Diversão Garantida",
                description = "Completou 10 tarefas de diversão! A diversão é essencial!",
                points = 200,
                icon = "celebration",
                isUnlocked = false,
                unlockedAt = null,
                category = AchievementCategory.SPECIAL
            )
        )
    }
}

data class AchievementsUiState(
    val achievements: List<Achievement> = emptyList(),
    val filteredAchievements: List<Achievement> = emptyList(),
    val selectedFilter: AchievementFilter = AchievementFilter.ALL,
    val selectedAchievement: Achievement? = null,
    val isLoading: Boolean = false,
    val errorMessage: String? = null
) 