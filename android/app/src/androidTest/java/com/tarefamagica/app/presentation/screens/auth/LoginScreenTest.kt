package com.tarefamagica.app.presentation.screens.auth

import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.test.ext.junit.runners.AndroidJUnit4
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class LoginScreenTest {

    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun loginScreen_shouldDisplayAllElements() {
        // Given
        var onNavigateToRegisterCalled = false
        var onNavigateToDashboardCalled = false
        var onNavigateToTwoFactorCalled = false

        // When
        composeTestRule.setContent {
            LoginScreen(
                onNavigateToRegister = { onNavigateToRegisterCalled = true },
                onNavigateToDashboard = { onNavigateToDashboardCalled = true },
                onNavigateToTwoFactor = { onNavigateToTwoFactorCalled = true }
            )
        }

        // Then
        composeTestRule.onNodeWithText("TarefaMágica").assertExists()
        composeTestRule.onNodeWithText("Login").assertExists()
        composeTestRule.onNodeWithText("E-mail").assertExists()
        composeTestRule.onNodeWithText("Senha").assertExists()
        composeTestRule.onNodeWithText("Entrar").assertExists()
        composeTestRule.onNodeWithText("Criar conta").assertExists()
    }

    @Test
    fun whenEmailIsEmpty_loginButtonShouldBeDisabled() {
        // Given
        composeTestRule.setContent {
            LoginScreen(
                onNavigateToRegister = {},
                onNavigateToDashboard = {},
                onNavigateToTwoFactor = {}
            )
        }

        // When
        composeTestRule.onNodeWithText("Senha").performTextInput("password123")

        // Then
        composeTestRule.onNodeWithText("Entrar").assertIsNotEnabled()
    }

    @Test
    fun whenPasswordIsEmpty_loginButtonShouldBeDisabled() {
        // Given
        composeTestRule.setContent {
            LoginScreen(
                onNavigateToRegister = {},
                onNavigateToDashboard = {},
                onNavigateToTwoFactor = {}
            )
        }

        // When
        composeTestRule.onNodeWithText("E-mail").performTextInput("test@example.com")

        // Then
        composeTestRule.onNodeWithText("Entrar").assertIsNotEnabled()
    }

    @Test
    fun whenBothFieldsAreFilled_loginButtonShouldBeEnabled() {
        // Given
        composeTestRule.setContent {
            LoginScreen(
                onNavigateToRegister = {},
                onNavigateToDashboard = {},
                onNavigateToTwoFactor = {}
            )
        }

        // When
        composeTestRule.onNodeWithText("E-mail").performTextInput("test@example.com")
        composeTestRule.onNodeWithText("Senha").performTextInput("password123")

        // Then
        composeTestRule.onNodeWithText("Entrar").assertIsEnabled()
    }

    @Test
    fun whenRegisterButtonIsClicked_shouldNavigateToRegister() {
        // Given
        var onNavigateToRegisterCalled = false
        composeTestRule.setContent {
            LoginScreen(
                onNavigateToRegister = { onNavigateToRegisterCalled = true },
                onNavigateToDashboard = {},
                onNavigateToTwoFactor = {}
            )
        }

        // When
        composeTestRule.onNodeWithText("Criar conta").performClick()

        // Then
        assert(onNavigateToRegisterCalled)
    }

    @Test
    fun whenInvalidEmailIsEntered_shouldShowError() {
        // Given
        composeTestRule.setContent {
            LoginScreen(
                onNavigateToRegister = {},
                onNavigateToDashboard = {},
                onNavigateToTwoFactor = {}
            )
        }

        // When
        composeTestRule.onNodeWithText("E-mail").performTextInput("invalid-email")

        // Then
        composeTestRule.onNodeWithText("E-mail inválido").assertExists()
    }

    @Test
    fun whenPasswordIsTooShort_shouldShowError() {
        // Given
        composeTestRule.setContent {
            LoginScreen(
                onNavigateToRegister = {},
                onNavigateToDashboard = {},
                onNavigateToTwoFactor = {}
            )
        }

        // When
        composeTestRule.onNodeWithText("Senha").performTextInput("123")

        // Then
        composeTestRule.onNodeWithText("Senha deve ter pelo menos 6 caracteres").assertExists()
    }

    @Test
    fun whenLoginButtonIsClicked_shouldShowLoading() {
        // Given
        composeTestRule.setContent {
            LoginScreen(
                onNavigateToRegister = {},
                onNavigateToDashboard = {},
                onNavigateToTwoFactor = {}
            )
        }

        // When
        composeTestRule.onNodeWithText("E-mail").performTextInput("test@example.com")
        composeTestRule.onNodeWithText("Senha").performTextInput("password123")
        composeTestRule.onNodeWithText("Entrar").performClick()

        // Then
        composeTestRule.onNodeWithText("Entrando...").assertExists()
    }

    @Test
    fun whenForgotPasswordIsClicked_shouldShowDialog() {
        // Given
        composeTestRule.setContent {
            LoginScreen(
                onNavigateToRegister = {},
                onNavigateToDashboard = {},
                onNavigateToTwoFactor = {}
            )
        }

        // When
        composeTestRule.onNodeWithText("Esqueceu a senha?").performClick()

        // Then
        composeTestRule.onNodeWithText("Recuperar Senha").assertExists()
    }
} 