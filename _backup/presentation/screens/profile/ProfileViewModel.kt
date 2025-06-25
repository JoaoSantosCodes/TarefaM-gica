package com.tarefamagica.app.presentation.screens.profile

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class ProfileViewModel @Inject constructor() : ViewModel() {
    
    private val _uiState = MutableStateFlow(ProfileUiState())
    val uiState: StateFlow<ProfileUiState> = _uiState.asStateFlow()
    
    init {
        loadProfile()
    }
    
    fun editProfile() {
        viewModelScope.launch {
            // Implementar edição de perfil
            _uiState.update { 
                it.copy(errorMessage = "Funcionalidade em desenvolvimento")
            }
        }
    }
    
    private fun loadProfile() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            
            try {
                // Simular carregamento de dados
                kotlinx.coroutines.delay(1000)
                
                val mockUser = createMockUser()
                val mockStatistics = createMockStatistics()
                val mockAchievements = createMockAchievements()
                
                _uiState.update { 
                    it.copy(
                        user = mockUser,
                        statistics = mockStatistics,
                        recentAchievements = mockAchievements,
                        isLoading = false
                    )
                }
                
            } catch (e: Exception) {
                _uiState.update { 
                    it.copy(
                        isLoading = false,
                        errorMessage = "Erro ao carregar perfil: ${e.message}"
                    )
                }
            }
        }
    }
    
    private fun createMockUser(): User {
        return User(
            id = "user_123",
            name = "João Silva",
            age = 12,
            level = 5,
            experience = 1250,
            experienceToNextLevel = 2000,
            experienceProgress = 0.625f
        )
    }
    
    private fun createMockStatistics(): UserStatistics {
        return UserStatistics(
            completedTasks = 47,
            totalPoints = 2840,
            achievements = 8,
            streak = 12
        )
    }
    
    private fun createMockAchievements(): List<Achievement> {
        return listOf(
            Achievement(
                id = "1",
                title = "Primeira Conquista",
                description = "Completou sua primeira tarefa",
                points = 100,
                icon = "star"
            ),
            Achievement(
                id = "2",
                title = "Sequência de 7 Dias",
                description = "Manteve uma sequência de 7 dias",
                points = 200,
                icon = "fire"
            ),
            Achievement(
                id = "3",
                title = "Mestre da Organização",
                description = "Completou 10 tarefas de casa",
                points = 150,
                icon = "home"
            )
        )
    }
}

data class ProfileUiState(
    val user: User = User(),
    val statistics: UserStatistics = UserStatistics(),
    val recentAchievements: List<Achievement> = emptyList(),
    val isLoading: Boolean = false,
    val errorMessage: String? = null
)

data class User(
    val id: String = "",
    val name: String = "",
    val age: Int = 0,
    val level: Int = 1,
    val experience: Int = 0,
    val experienceToNextLevel: Int = 100,
    val experienceProgress: Float = 0f
)

data class UserStatistics(
    val completedTasks: Int = 0,
    val totalPoints: Int = 0,
    val achievements: Int = 0,
    val streak: Int = 0
)

data class Achievement(
    val id: String,
    val title: String,
    val description: String,
    val points: Int,
    val icon: String
) 