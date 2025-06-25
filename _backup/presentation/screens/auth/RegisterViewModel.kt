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
class RegisterViewModel @Inject constructor() : ViewModel() {
    
    private val _uiState = MutableStateFlow(RegisterUiState())
    val uiState: StateFlow<RegisterUiState> = _uiState.asStateFlow()
    
    fun updateName(name: String) {
        _uiState.update { it.copy(name = name) }
        validateForm()
    }
    
    fun updateEmail(email: String) {
        _uiState.update { it.copy(email = email) }
        validateForm()
    }
    
    fun updatePassword(password: String) {
        _uiState.update { it.copy(password = password) }
        validateForm()
    }
    
    fun updateConfirmPassword(confirmPassword: String) {
        _uiState.update { it.copy(confirmPassword = confirmPassword) }
        validateForm()
    }
    
    fun updateAge(age: String) {
        _uiState.update { it.copy(age = age) }
        validateForm()
    }
    
    fun togglePasswordVisibility() {
        _uiState.update { it.copy(showPassword = !it.showPassword) }
    }
    
    fun toggleConfirmPasswordVisibility() {
        _uiState.update { it.copy(showConfirmPassword = !it.showConfirmPassword) }
    }
    
    fun updateParentalConsent(consent: Boolean) {
        _uiState.update { it.copy(parentalConsent = consent) }
        validateForm()
    }
    
    fun updateTermsAcceptance(accepted: Boolean) {
        _uiState.update { it.copy(termsAccepted = accepted) }
        validateForm()
    }
    
    fun register(
        onSuccess: (String) -> Unit,
        onError: (String) -> Unit
    ) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, errorMessage = null) }
            
            try {
                // Validações
                val validationResult = validateAll()
                if (!validationResult.isValid) {
                    _uiState.update { 
                        it.copy(
                            isLoading = false,
                            errorMessage = validationResult.errorMessage
                        )
                    }
                    onError(validationResult.errorMessage)
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
                        errorMessage = "Erro ao criar conta: ${e.message}"
                    )
                }
                onError("Erro ao criar conta: ${e.message}")
            }
        }
    }
    
    private fun validateForm() {
        val currentState = _uiState.value
        val isValid = validateAll().isValid
        _uiState.update { it.copy(isFormValid = isValid) }
    }
    
    private fun validateAll(): ValidationResult {
        val currentState = _uiState.value
        
        // Nome
        if (currentState.name.length < 3) {
            return ValidationResult(false, "Nome deve ter pelo menos 3 caracteres")
        }
        
        // Email
        if (!isValidEmail(currentState.email)) {
            return ValidationResult(false, "E-mail inválido")
        }
        
        // Idade
        val age = currentState.age.toIntOrNull()
        if (age == null || age < 5 || age > 18) {
            return ValidationResult(false, "Idade deve estar entre 5 e 18 anos")
        }
        
        // Senha
        if (currentState.password.length < 8) {
            return ValidationResult(false, "Senha deve ter pelo menos 8 caracteres")
        }
        
        // Confirmar senha
        if (currentState.password != currentState.confirmPassword) {
            return ValidationResult(false, "Senhas não coincidem")
        }
        
        // Consentimento parental
        if (!currentState.parentalConsent) {
            return ValidationResult(false, "É necessário o consentimento parental")
        }
        
        // Termos
        if (!currentState.termsAccepted) {
            return ValidationResult(false, "É necessário aceitar os termos de uso")
        }
        
        return ValidationResult(true, "")
    }
    
    private fun isValidEmail(email: String): Boolean {
        return android.util.Patterns.EMAIL_ADDRESS.matcher(email).matches()
    }
}

data class RegisterUiState(
    val name: String = "",
    val email: String = "",
    val password: String = "",
    val confirmPassword: String = "",
    val age: String = "",
    val showPassword: Boolean = false,
    val showConfirmPassword: Boolean = false,
    val parentalConsent: Boolean = false,
    val termsAccepted: Boolean = false,
    val isLoading: Boolean = false,
    val isFormValid: Boolean = false,
    val errorMessage: String? = null
)

data class ValidationResult(
    val isValid: Boolean,
    val errorMessage: String
) 