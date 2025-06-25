package com.tarefamagica.app.presentation.screens.auth

import com.tarefamagica.app.data.repository.AuthRepository
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.*
import org.junit.After
import org.junit.Before
import org.junit.Test
import org.mockito.Mock
import org.mockito.MockitoAnnotations
import org.mockito.kotlin.whenever

@OptIn(ExperimentalCoroutinesApi::class)
class LoginViewModelTest {

    @Mock
    private lateinit var authRepository: AuthRepository

    private lateinit var viewModel: LoginViewModel
    private val testDispatcher = StandardTestDispatcher()

    @Before
    fun setup() {
        MockitoAnnotations.openMocks(this)
        Dispatchers.setMain(testDispatcher)
        viewModel = LoginViewModel(authRepository)
    }

    @After
    fun tearDown() {
        Dispatchers.resetMain()
    }

    @Test
    fun `when valid credentials are provided, login should succeed`() = runTest {
        // Given
        val email = "test@example.com"
        val password = "password123"
        whenever(authRepository.login(email, password)).thenReturn(Result.success("user123"))

        // When
        viewModel.updateEmail(email)
        viewModel.updatePassword(password)
        viewModel.login()

        // Then
        testDispatcher.scheduler.advanceUntilIdle()
        assert(viewModel.uiState.value.isSuccess)
        assert(viewModel.uiState.value.userId == "user123")
    }

    @Test
    fun `when invalid credentials are provided, login should fail`() = runTest {
        // Given
        val email = "invalid@example.com"
        val password = "wrongpassword"
        whenever(authRepository.login(email, password)).thenReturn(Result.failure(Exception("Invalid credentials")))

        // When
        viewModel.updateEmail(email)
        viewModel.updatePassword(password)
        viewModel.login()

        // Then
        testDispatcher.scheduler.advanceUntilIdle()
        assert(!viewModel.uiState.value.isSuccess)
        assert(viewModel.uiState.value.errorMessage != null)
    }

    @Test
    fun `when email is empty, form should be invalid`() {
        // Given
        viewModel.updateEmail("")
        viewModel.updatePassword("password123")

        // Then
        assert(!viewModel.uiState.value.isFormValid)
    }

    @Test
    fun `when password is empty, form should be invalid`() {
        // Given
        viewModel.updateEmail("test@example.com")
        viewModel.updatePassword("")

        // Then
        assert(!viewModel.uiState.value.isFormValid)
    }

    @Test
    fun `when both email and password are valid, form should be valid`() {
        // Given
        viewModel.updateEmail("test@example.com")
        viewModel.updatePassword("password123")

        // Then
        assert(viewModel.uiState.value.isFormValid)
    }

    @Test
    fun `when login is in progress, loading should be true`() = runTest {
        // Given
        val email = "test@example.com"
        val password = "password123"
        whenever(authRepository.login(email, password)).thenAnswer {
            delay(1000) // Simulate network delay
            Result.success("user123")
        }

        // When
        viewModel.updateEmail(email)
        viewModel.updatePassword(password)
        viewModel.login()

        // Then
        assert(viewModel.uiState.value.isLoading)
    }
} 