package com.tarefamagica.app.presentation.screens.levels

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
class LevelsViewModel @Inject constructor(
    private val gamificationRepository: GamificationRepository
) : ViewModel() {
    
    private val _uiState = MutableStateFlow(LevelsUiState())
    val uiState: StateFlow<LevelsUiState> = _uiState.asStateFlow()
    
    init {
        loadLevels()
    }
    
    fun selectLevel(level: LevelData) {
        _uiState.update { it.copy(selectedLevel = level) }
    }
    
    fun clearSelectedLevel() {
        _uiState.update { it.copy(selectedLevel = null) }
    }
    
    private fun loadLevels() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            
            try {
                val currentLevel = 5 // Mock do nível atual
                val currentExperience = 1250 // Mock da experiência atual
                val experienceToNextLevel = 2000 // Mock da experiência para o próximo nível
                val experienceProgress = 0.625f // Mock do progresso
                
                val levels = createMockLevels(currentLevel)
                
                _uiState.update { 
                    it.copy(
                        currentLevel = currentLevel,
                        currentExperience = currentExperience,
                        experienceToNextLevel = experienceToNextLevel,
                        experienceProgress = experienceProgress,
                        levels = levels,
                        isLoading = false
                    )
                }
                
            } catch (e: Exception) {
                _uiState.update { 
                    it.copy(
                        isLoading = false,
                        errorMessage = "Erro ao carregar níveis: ${e.message}"
                    )
                }
            }
        }
    }
    
    private fun createMockLevels(currentLevel: Int): List<LevelData> {
        return (1..50).map { level ->
            val experienceRequired = calculateLevelThreshold(level)
            val rewards = generateLevelRewards(level)
            val isUnlocked = level <= currentLevel
            
            LevelData(
                level = level,
                experienceRequired = experienceRequired,
                rewards = rewards,
                isUnlocked = isUnlocked
            )
        }
    }
    
    private fun calculateLevelThreshold(level: Int): Int {
        return when {
            level <= 5 -> level * 100
            level <= 10 -> 500 + (level - 5) * 150
            level <= 15 -> 1250 + (level - 10) * 200
            level <= 20 -> 2250 + (level - 15) * 250
            level <= 25 -> 3500 + (level - 20) * 300
            level <= 30 -> 5000 + (level - 25) * 400
            level <= 40 -> 7000 + (level - 30) * 500
            else -> 12000 + (level - 40) * 600
        }
    }
    
    private fun generateLevelRewards(level: Int): List<String> {
        val rewards = mutableListOf<String>()
        
        // Recompensas baseadas no nível
        when {
            level == 1 -> {
                rewards.add("Desbloqueia sistema de pontos")
                rewards.add("+50 pontos bônus")
            }
            level == 5 -> {
                rewards.add("Desbloqueia sistema de conquistas")
                rewards.add("+100 pontos bônus")
                rewards.add("Badge 'Iniciante'")
            }
            level == 10 -> {
                rewards.add("Desbloqueia leaderboard")
                rewards.add("+200 pontos bônus")
                rewards.add("Badge 'Aprendiz'")
                rewards.add("Tema personalizado")
            }
            level == 15 -> {
                rewards.add("Desbloqueia relatórios avançados")
                rewards.add("+300 pontos bônus")
                rewards.add("Badge 'Intermediário'")
                rewards.add("Sons personalizados")
            }
            level == 20 -> {
                rewards.add("Desbloqueia sistema financeiro")
                rewards.add("+500 pontos bônus")
                rewards.add("Badge 'Avançado'")
                rewards.add("Avatar exclusivo")
            }
            level == 25 -> {
                rewards.add("Desbloqueia configurações avançadas")
                rewards.add("+750 pontos bônus")
                rewards.add("Badge 'Expert'")
                rewards.add("Tema premium")
            }
            level == 30 -> {
                rewards.add("Desbloqueia modo offline")
                rewards.add("+1000 pontos bônus")
                rewards.add("Badge 'Mestre'")
                rewards.add("Animações especiais")
            }
            level == 40 -> {
                rewards.add("Desbloqueia modo beta")
                rewards.add("+1500 pontos bônus")
                rewards.add("Badge 'Lenda'")
                rewards.add("Acesso antecipado a features")
            }
            level == 50 -> {
                rewards.add("Desbloqueia modo deus")
                rewards.add("+2000 pontos bônus")
                rewards.add("Badge 'Deus'")
                rewards.add("Todas as features desbloqueadas")
            }
            else -> {
                // Recompensas padrão para outros níveis
                val basePoints = level * 10
                rewards.add("+$basePoints pontos bônus")
                
                // Recompensas especiais a cada 5 níveis
                if (level % 5 == 0) {
                    rewards.add("Multiplicador de pontos x1.1")
                }
                
                // Recompensas especiais a cada 10 níveis
                if (level % 10 == 0) {
                    rewards.add("Slot extra de tarefas")
                }
                
                // Recompensas especiais a cada 25 níveis
                if (level % 25 == 0) {
                    rewards.add("Reset de sequência protegido")
                }
            }
        }
        
        return rewards
    }
}

data class LevelsUiState(
    val currentLevel: Int = 1,
    val currentExperience: Int = 0,
    val experienceToNextLevel: Int = 100,
    val experienceProgress: Float = 0f,
    val levels: List<LevelData> = emptyList(),
    val selectedLevel: LevelData? = null,
    val isLoading: Boolean = false,
    val errorMessage: String? = null
) 