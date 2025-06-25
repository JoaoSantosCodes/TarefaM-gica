package com.tarefamagica.app.presentation.screens.tasks

import com.tarefamagica.app.data.model.Task
import com.tarefamagica.app.data.repository.TasksRepository
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.*
import org.junit.After
import org.junit.Before
import org.junit.Test
import org.mockito.Mock
import org.mockito.MockitoAnnotations
import org.mockito.kotlin.whenever
import java.time.LocalDateTime

@OptIn(ExperimentalCoroutinesApi::class)
class TasksViewModelTest {

    @Mock
    private lateinit var tasksRepository: TasksRepository

    private lateinit var viewModel: TasksViewModel
    private val testDispatcher = StandardTestDispatcher()

    @Before
    fun setup() {
        MockitoAnnotations.openMocks(this)
        Dispatchers.setMain(testDispatcher)
        viewModel = TasksViewModel(tasksRepository)
    }

    @After
    fun tearDown() {
        Dispatchers.resetMain()
    }

    @Test
    fun `when loadTasks is called, tasks should be loaded successfully`() = runTest {
        // Given
        val userId = "user123"
        val mockTasks = listOf(
            Task(
                id = "1",
                title = "Arrumar a cama",
                description = "Arrumar a cama pela manhã",
                points = 50,
                money = 2.0,
                isCompleted = false,
                createdAt = LocalDateTime.now()
            ),
            Task(
                id = "2",
                title = "Lavar louça",
                description = "Lavar a louça do almoço",
                points = 100,
                money = 5.0,
                isCompleted = true,
                createdAt = LocalDateTime.now()
            )
        )
        whenever(tasksRepository.getTasks(userId)).thenReturn(Result.success(mockTasks))

        // When
        viewModel.loadTasks(userId)

        // Then
        testDispatcher.scheduler.advanceUntilIdle()
        assert(viewModel.uiState.value.tasks.size == 2)
        assert(!viewModel.uiState.value.isLoading)
        assert(viewModel.uiState.value.errorMessage == null)
    }

    @Test
    fun `when completeTask is called, task should be marked as completed`() = runTest {
        // Given
        val taskId = "1"
        val userId = "user123"
        whenever(tasksRepository.completeTask(taskId, userId)).thenReturn(Result.success(Unit))

        // When
        viewModel.completeTask(taskId, userId)

        // Then
        testDispatcher.scheduler.advanceUntilIdle()
        assert(!viewModel.uiState.value.isLoading)
        assert(viewModel.uiState.value.errorMessage == null)
    }

    @Test
    fun `when loadTasks fails, error should be shown`() = runTest {
        // Given
        val userId = "user123"
        whenever(tasksRepository.getTasks(userId)).thenReturn(Result.failure(Exception("Network error")))

        // When
        viewModel.loadTasks(userId)

        // Then
        testDispatcher.scheduler.advanceUntilIdle()
        assert(viewModel.uiState.value.errorMessage != null)
        assert(!viewModel.uiState.value.isLoading)
    }

    @Test
    fun `when completeTask fails, error should be shown`() = runTest {
        // Given
        val taskId = "1"
        val userId = "user123"
        whenever(tasksRepository.completeTask(taskId, userId)).thenReturn(Result.failure(Exception("Task not found")))

        // When
        viewModel.completeTask(taskId, userId)

        // Then
        testDispatcher.scheduler.advanceUntilIdle()
        assert(viewModel.uiState.value.errorMessage != null)
        assert(!viewModel.uiState.value.isLoading)
    }

    @Test
    fun `when filter is changed, filtered tasks should be updated`() {
        // Given
        val tasks = listOf(
            Task(
                id = "1",
                title = "Arrumar a cama",
                description = "Arrumar a cama pela manhã",
                points = 50,
                money = 2.0,
                isCompleted = false,
                createdAt = LocalDateTime.now()
            ),
            Task(
                id = "2",
                title = "Lavar louça",
                description = "Lavar a louça do almoço",
                points = 100,
                money = 5.0,
                isCompleted = true,
                createdAt = LocalDateTime.now()
            )
        )
        viewModel.updateTasks(tasks)

        // When - Filter completed tasks
        viewModel.updateFilter(TaskFilter.COMPLETED)

        // Then
        assert(viewModel.uiState.value.filteredTasks.size == 1)
        assert(viewModel.uiState.value.filteredTasks[0].isCompleted)
    }

    @Test
    fun `when search query is updated, filtered tasks should be updated`() {
        // Given
        val tasks = listOf(
            Task(
                id = "1",
                title = "Arrumar a cama",
                description = "Arrumar a cama pela manhã",
                points = 50,
                money = 2.0,
                isCompleted = false,
                createdAt = LocalDateTime.now()
            ),
            Task(
                id = "2",
                title = "Lavar louça",
                description = "Lavar a louça do almoço",
                points = 100,
                money = 5.0,
                isCompleted = false,
                createdAt = LocalDateTime.now()
            )
        )
        viewModel.updateTasks(tasks)

        // When
        viewModel.updateSearchQuery("cama")

        // Then
        assert(viewModel.uiState.value.filteredTasks.size == 1)
        assert(viewModel.uiState.value.filteredTasks[0].title.contains("cama", ignoreCase = true))
    }

    @Test
    fun `when tasks are loaded, total points should be calculated correctly`() = runTest {
        // Given
        val userId = "user123"
        val mockTasks = listOf(
            Task(
                id = "1",
                title = "Arrumar a cama",
                description = "Arrumar a cama pela manhã",
                points = 50,
                money = 2.0,
                isCompleted = true,
                createdAt = LocalDateTime.now()
            ),
            Task(
                id = "2",
                title = "Lavar louça",
                description = "Lavar a louça do almoço",
                points = 100,
                money = 5.0,
                isCompleted = true,
                createdAt = LocalDateTime.now()
            )
        )
        whenever(tasksRepository.getTasks(userId)).thenReturn(Result.success(mockTasks))

        // When
        viewModel.loadTasks(userId)

        // Then
        testDispatcher.scheduler.advanceUntilIdle()
        assert(viewModel.uiState.value.totalPoints == 150)
    }
} 