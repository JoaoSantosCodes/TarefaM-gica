package com.tarefamagica.app.presentation.screens.auth

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
class LoginViewModel @Inject constructor() : ViewModel() {
    
    private val _uiState = MutableStateFlow(LoginUiState())
    val uiState: StateFlow<LoginUiState> = _uiState.asStateFlow()
    
    fun updateEmail(email: String) {
        _uiState.update { it.copy(email = email) }
    }
    
    fun updatePassword(password: String) {
        _uiState.update { it.copy(password = password) }
    }
    
    fun togglePasswordVisibility() {
        _uiState.update { it.copy(showPassword = !it.showPassword) }
    }
    
    fun login(
        onSuccess: (String) -> Unit,
        onError: (String) -> Unit
    ) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, errorMessage = null) }
            
            try {
                // Validação básica
                if (!isValidEmail(_uiState.value.email)) {
                    _uiState.update { 
                        it.copy(
                            isLoading = false,
                            errorMessage = "E-mail inválido"
                        )
                    }
                    onError("E-mail inválido")
                    return@launch
                }
                
                if (_uiState.value.password.length < 6) {
                    _uiState.update { 
                        it.copy(
                            isLoading = false,
                            errorMessage = "Senha deve ter pelo menos 6 caracteres"
                        )
                    }
                    onError("Senha deve ter pelo menos 6 caracteres")
                    return@launch
                }
                
                // Simular chamada de API
                kotlinx.coroutines.delay(2000)
                
                // Mock de sucesso
                val userId = "user_${System.currentTimeMillis()}"
                _uiState.update { it.copy(isLoading = false) }
                onSuccess(userId)
                
            } catch (e: Exception) {
                _uiState.update { 
                    it.copy(
                        isLoading = false,
                        errorMessage = "Erro ao fazer login: ${e.message}"
                    )
                }
                onError("Erro ao fazer login: ${e.message}")
            }
        }
    }
    
    fun forgotPassword() {
        viewModelScope.launch {
            // Implementar recuperação de senha
            _uiState.update { 
                it.copy(errorMessage = "Funcionalidade em desenvolvimento")
            }
        }
    }
    
    private fun isValidEmail(email: String): Boolean {
        return android.util.Patterns.EMAIL_ADDRESS.matcher(email).matches()
    }
}

data class LoginUiState(
    val email: String = "",
    val password: String = "",
    val showPassword: Boolean = false,
    val isLoading: Boolean = false,
    val errorMessage: String? = null
) 