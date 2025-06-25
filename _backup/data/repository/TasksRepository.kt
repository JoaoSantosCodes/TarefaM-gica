package com.tarefamagica.app.data.repository

import com.tarefamagica.app.data.api.ApiService
import com.tarefamagica.app.data.api.CreateTaskRequest
import com.tarefamagica.app.data.api.UpdateTaskRequest
import com.tarefamagica.app.data.model.Result
import com.tarefamagica.app.data.model.Task
import com.tarefamagica.app.data.model.TaskCategory
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import java.time.LocalDate
import java.time.format.DateTimeFormatter
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class TasksRepository @Inject constructor(
    private val apiService: ApiService
) {
    
    suspend fun getTasks(
        filter: String? = null,
        search: String? = null,
        page: Int = 1,
        limit: Int = 20
    ): Flow<Result<List<Task>>> = flow {
        emit(Result.Loading)
        
        try {
            val response = apiService.getTasks(
                filter = filter,
                search = search,
                page = page,
                limit = limit
            )
            
            if (response.success && response.data != null) {
                emit(Result.Success(response.data.tasks))
            } else {
                emit(Result.Error(ApiError("TASKS_ERROR", response.message, null)))
            }
        } catch (e: Exception) {
            emit(Result.Error(ApiError("NETWORK_ERROR", "Erro de conexão: ${e.message}", null)))
        }
    }
    
    suspend fun getTask(taskId: String): Flow<Result<Task>> = flow {
        emit(Result.Loading)
        
        try {
            val response = apiService.getTask(taskId)
            
            if (response.success && response.data != null) {
                emit(Result.Success(response.data))
            } else {
                emit(Result.Error(ApiError("TASK_ERROR", response.message, null)))
            }
        } catch (e: Exception) {
            emit(Result.Error(ApiError("NETWORK_ERROR", "Erro de conexão: ${e.message}", null)))
        }
    }
    
    suspend fun createTask(
        title: String,
        description: String,
        category: TaskCategory,
        points: Int,
        dueDate: LocalDate?
    ): Flow<Result<Task>> = flow {
        emit(Result.Loading)
        
        try {
            val request = CreateTaskRequest(
                title = title,
                description = description,
                category = category.name,
                points = points,
                dueDate = dueDate?.format(DateTimeFormatter.ISO_LOCAL_DATE)
            )
            
            val response = apiService.createTask(request)
            
            if (response.success && response.data != null) {
                emit(Result.Success(response.data))
            } else {
                emit(Result.Error(ApiError("CREATE_TASK_ERROR", response.message, null)))
            }
        } catch (e: Exception) {
            emit(Result.Error(ApiError("NETWORK_ERROR", "Erro de conexão: ${e.message}", null)))
        }
    }
    
    suspend fun updateTask(
        taskId: String,
        title: String? = null,
        description: String? = null,
        category: TaskCategory? = null,
        points: Int? = null,
        dueDate: LocalDate? = null
    ): Flow<Result<Task>> = flow {
        emit(Result.Loading)
        
        try {
            val request = UpdateTaskRequest(
                title = title,
                description = description,
                category = category?.name,
                points = points,
                dueDate = dueDate?.format(DateTimeFormatter.ISO_LOCAL_DATE)
            )
            
            val response = apiService.updateTask(taskId, request)
            
            if (response.success && response.data != null) {
                emit(Result.Success(response.data))
            } else {
                emit(Result.Error(ApiError("UPDATE_TASK_ERROR", response.message, null)))
            }
        } catch (e: Exception) {
            emit(Result.Error(ApiError("NETWORK_ERROR", "Erro de conexão: ${e.message}", null)))
        }
    }
    
    suspend fun deleteTask(taskId: String): Flow<Result<Boolean>> = flow {
        emit(Result.Loading)
        
        try {
            val response = apiService.deleteTask(taskId)
            
            if (response.success) {
                emit(Result.Success(true))
            } else {
                emit(Result.Error(ApiError("DELETE_TASK_ERROR", response.message, null)))
            }
        } catch (e: Exception) {
            emit(Result.Error(ApiError("NETWORK_ERROR", "Erro de conexão: ${e.message}", null)))
        }
    }
    
    suspend fun completeTask(taskId: String): Flow<Result<CompleteTaskResult>> = flow {
        emit(Result.Loading)
        
        try {
            val response = apiService.completeTask(taskId)
            
            if (response.success && response.data != null) {
                val result = CompleteTaskResult(
                    pointsEarned = response.data.pointsEarned,
                    levelUp = response.data.levelUp,
                    newLevel = response.data.newLevel,
                    achievements = response.data.achievements
                )
                emit(Result.Success(result))
            } else {
                emit(Result.Error(ApiError("COMPLETE_TASK_ERROR", response.message, null)))
            }
        } catch (e: Exception) {
            emit(Result.Error(ApiError("NETWORK_ERROR", "Erro de conexão: ${e.message}", null)))
        }
    }
    
    // ===== FILTROS LOCAIS =====
    
    fun filterTasks(
        tasks: List<Task>,
        filter: TaskFilter,
        search: String = ""
    ): List<Task> {
        var filteredTasks = tasks
        
        // Aplicar filtro
        filteredTasks = when (filter) {
            TaskFilter.ALL -> filteredTasks
            TaskFilter.PENDING -> filteredTasks.filter { !it.isCompleted }
            TaskFilter.COMPLETED -> filteredTasks.filter { it.isCompleted }
            TaskFilter.TODAY -> filteredTasks.filter { it.isDueToday() }
            TaskFilter.OVERDUE -> filteredTasks.filter { it.isOverdue() }
        }
        
        // Aplicar busca
        if (search.isNotEmpty()) {
            filteredTasks = filteredTasks.filter { task ->
                task.title.contains(search, ignoreCase = true) ||
                task.description.contains(search, ignoreCase = true) ||
                task.category.displayName.contains(search, ignoreCase = true)
            }
        }
        
        return filteredTasks
    }
    
    fun sortTasks(tasks: List<Task>, sortBy: TaskSortBy): List<Task> {
        return when (sortBy) {
            TaskSortBy.DUE_DATE -> tasks.sortedBy { it.dueDate }
            TaskSortBy.POINTS -> tasks.sortedByDescending { it.points }
            TaskSortBy.CREATED_AT -> tasks.sortedByDescending { it.createdAt }
            TaskSortBy.CATEGORY -> tasks.sortedBy { it.category.displayName }
            TaskSortBy.PRIORITY -> tasks.sortedWith { task1, task2 ->
                // Prioridade: atrasadas > hoje > pendentes > concluídas
                val priority1 = getTaskPriority(task1)
                val priority2 = getTaskPriority(task2)
                priority2.compareTo(priority1)
            }
        }
    }
    
    private fun getTaskPriority(task: Task): Int {
        return when {
            task.isOverdue() -> 4
            task.isDueToday() -> 3
            !task.isCompleted -> 2
            else -> 1
        }
    }
}

// ===== MODELOS DE SUPORTE =====

enum class TaskFilter(val displayName: String) {
    ALL("Todas"),
    PENDING("Pendentes"),
    COMPLETED("Concluídas"),
    TODAY("Hoje"),
    OVERDUE("Atrasadas")
}

enum class TaskSortBy(val displayName: String) {
    DUE_DATE("Data de Vencimento"),
    POINTS("Pontos"),
    CREATED_AT("Data de Criação"),
    CATEGORY("Categoria"),
    PRIORITY("Prioridade")
}

data class CompleteTaskResult(
    val pointsEarned: Int,
    val levelUp: Boolean,
    val newLevel: Int?,
    val achievements: List<Achievement>
)

// ===== EXTENSÕES =====

fun Task.isOverdue(): Boolean {
    return dueDate != null && dueDate.isBefore(LocalDate.now()) && !isCompleted
}

fun Task.isDueToday(): Boolean {
    return dueDate != null && dueDate.isEqual(LocalDate.now())
}

// ===== API ERROR =====

data class ApiError(
    val code: String,
    val message: String,
    val details: Map<String, Any>?
) 