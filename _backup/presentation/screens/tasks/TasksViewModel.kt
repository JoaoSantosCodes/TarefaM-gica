package com.tarefamagica.app.presentation.screens.tasks

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import java.time.LocalDate
import javax.inject.Inject

@HiltViewModel
class TasksViewModel @Inject constructor() : ViewModel() {
    
    private val _uiState = MutableStateFlow(TasksUiState())
    val uiState: StateFlow<TasksUiState> = _uiState.asStateFlow()
    
    init {
        loadTasks()
    }
    
    fun updateFilter(filter: TaskFilter) {
        _uiState.update { it.copy(selectedFilter = filter) }
        applyFilters()
    }
    
    fun updateSearch(query: String) {
        _uiState.update { it.copy(searchQuery = query) }
        applyFilters()
    }
    
    fun completeTask(taskId: String) {
        viewModelScope.launch {
            _uiState.update { currentState ->
                val updatedTasks = currentState.tasks.map { task ->
                    if (task.id == taskId) {
                        task.copy(isCompleted = !task.isCompleted)
                    } else {
                        task
                    }
                }
                currentState.copy(tasks = updatedTasks)
            }
            applyFilters()
        }
    }
    
    fun deleteTask(taskId: String) {
        viewModelScope.launch {
            _uiState.update { currentState ->
                val updatedTasks = currentState.tasks.filter { it.id != taskId }
                currentState.copy(tasks = updatedTasks)
            }
            applyFilters()
        }
    }
    
    private fun loadTasks() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            
            try {
                // Simular carregamento de tarefas
                kotlinx.coroutines.delay(1000)
                
                val mockTasks = createMockTasks()
                _uiState.update { 
                    it.copy(
                        tasks = mockTasks,
                        isLoading = false
                    )
                }
                applyFilters()
                
            } catch (e: Exception) {
                _uiState.update { 
                    it.copy(
                        isLoading = false,
                        errorMessage = "Erro ao carregar tarefas: ${e.message}"
                    )
                }
            }
        }
    }
    
    private fun applyFilters() {
        val currentState = _uiState.value
        var filteredTasks = currentState.tasks
        
        // Aplicar filtro
        filteredTasks = when (currentState.selectedFilter) {
            TaskFilter.ALL -> filteredTasks
            TaskFilter.PENDING -> filteredTasks.filter { !it.isCompleted }
            TaskFilter.COMPLETED -> filteredTasks.filter { it.isCompleted }
            TaskFilter.TODAY -> filteredTasks.filter { 
                it.dueDate?.isEqual(LocalDate.now()) == true 
            }
            TaskFilter.OVERDUE -> filteredTasks.filter { 
                it.dueDate?.isBefore(LocalDate.now()) == true && !it.isCompleted 
            }
        }
        
        // Aplicar busca
        if (currentState.searchQuery.isNotEmpty()) {
            filteredTasks = filteredTasks.filter { task ->
                task.title.contains(currentState.searchQuery, ignoreCase = true) ||
                task.description.contains(currentState.searchQuery, ignoreCase = true) ||
                task.category.displayName.contains(currentState.searchQuery, ignoreCase = true)
            }
        }
        
        _uiState.update { it.copy(filteredTasks = filteredTasks) }
    }
    
    private fun createMockTasks(): List<Task> {
        return listOf(
            Task(
                id = "1",
                title = "Fazer lição de matemática",
                description = "Exercícios 1 a 10 da página 45",
                category = TaskCategory.SCHOOL,
                points = 50,
                dueDate = LocalDate.now(),
                isCompleted = false
            ),
            Task(
                id = "2",
                title = "Arrumar o quarto",
                description = "Organizar brinquedos e roupas",
                category = TaskCategory.HOME,
                points = 30,
                dueDate = LocalDate.now().plusDays(1),
                isCompleted = true
            ),
            Task(
                id = "3",
                title = "Ler 30 minutos",
                description = "Continuar o livro de aventuras",
                category = TaskCategory.PERSONAL,
                points = 40,
                dueDate = LocalDate.now().plusDays(2),
                isCompleted = false
            ),
            Task(
                id = "4",
                title = "Fazer exercícios",
                description = "30 minutos de atividade física",
                category = TaskCategory.HEALTH,
                points = 60,
                dueDate = LocalDate.now().minusDays(1),
                isCompleted = false
            ),
            Task(
                id = "5",
                title = "Jogar videogame",
                description = "1 hora de diversão",
                category = TaskCategory.FUN,
                points = 20,
                dueDate = LocalDate.now().plusDays(3),
                isCompleted = false
            )
        )
    }
}

data class TasksUiState(
    val tasks: List<Task> = emptyList(),
    val filteredTasks: List<Task> = emptyList(),
    val selectedFilter: TaskFilter = TaskFilter.ALL,
    val searchQuery: String = "",
    val isLoading: Boolean = false,
    val errorMessage: String? = null
)

data class Task(
    val id: String,
    val title: String,
    val description: String,
    val category: TaskCategory,
    val points: Int,
    val dueDate: LocalDate?,
    val isCompleted: Boolean
)

enum class TaskFilter(val displayName: String) {
    ALL("Todas"),
    PENDING("Pendentes"),
    COMPLETED("Concluídas"),
    TODAY("Hoje"),
    OVERDUE("Atrasadas")
}

enum class TaskCategory(val displayName: String) {
    SCHOOL("Escola"),
    HOME("Casa"),
    PERSONAL("Pessoal"),
    HEALTH("Saúde"),
    FUN("Diversão")
} 