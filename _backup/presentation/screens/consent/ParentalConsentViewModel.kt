package com.tarefamagica.app.presentation.screens.consent

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.tarefamagica.app.data.repository.AuthRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import java.time.LocalDate
import javax.inject.Inject

@HiltViewModel
class ParentalConsentViewModel @Inject constructor(
    private val authRepository: AuthRepository
) : ViewModel() {
    
    private val _uiState = MutableStateFlow(ParentalConsentUiState())
    val uiState: StateFlow<ParentalConsentUiState> = _uiState.asStateFlow()
    
    fun setUserId(userId: String) {
        _uiState.update { it.copy(userId = userId) }
    }
    
    fun updateParentName(name: String) {
        _uiState.update { it.copy(parentName = name) }
        validateForm()
    }
    
    fun updateParentEmail(email: String) {
        _uiState.update { it.copy(parentEmail = email) }
        validateForm()
    }
    
    fun updateParentPhone(phone: String) {
        _uiState.update { it.copy(parentPhone = phone) }
        validateForm()
    }
    
    fun updateRelationship(relationship: String) {
        _uiState.update { it.copy(relationship = relationship) }
        validateForm()
    }
    
    fun updateConsentDate(date: LocalDate) {
        _uiState.update { it.copy(consentDate = date) }
        validateForm()
    }
    
    fun updateTermsAccepted(accepted: Boolean) {
        _uiState.update { it.copy(termsAccepted = accepted) }
        validateForm()
    }
    
    fun updatePrivacyAccepted(accepted: Boolean) {
        _uiState.update { it.copy(privacyAccepted = accepted) }
        validateForm()
    }
    
    fun loadConsentStatus() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, errorMessage = null) }
            
            try {
                // Simular chamada de API para verificar status
                kotlinx.coroutines.delay(1000)
                
                val mockStatus = createMockConsentStatus()
                _uiState.update { 
                    it.copy(
                        isConsented = mockStatus.isConsented,
                        parentName = mockStatus.parentName,
                        parentEmail = mockStatus.parentEmail,
                        parentPhone = mockStatus.parentPhone,
                        relationship = mockStatus.relationship,
                        consentDate = mockStatus.consentDate,
                        isLoading = false
                    )
                }
                
            } catch (e: Exception) {
                _uiState.update { 
                    it.copy(
                        isLoading = false,
                        errorMessage = "Erro ao carregar status: ${e.message}"
                    )
                }
            }
        }
    }
    
    fun submitConsent() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, errorMessage = null) }
            
            try {
                // Validação final
                val validationResult = validateAll()
                if (!validationResult.isValid) {
                    _uiState.update { 
                        it.copy(
                            isLoading = false,
                            errorMessage = validationResult.errorMessage
                        )
                    }
                    return@launch
                }
                
                // Simular envio do consentimento
                kotlinx.coroutines.delay(2000)
                
                // Mock de sucesso
                _uiState.update { 
                    it.copy(
                        isLoading = false,
                        isSuccess = true,
                        isConsented = true,
                        consentDate = LocalDate.now()
                    )
                }
                
            } catch (e: Exception) {
                _uiState.update { 
                    it.copy(
                        isLoading = false,
                        errorMessage = "Erro ao enviar consentimento: ${e.message}"
                    )
                }
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
        
        // Nome do responsável
        if (currentState.parentName.length < 3) {
            return ValidationResult(false, "Nome do responsável deve ter pelo menos 3 caracteres")
        }
        
        // E-mail do responsável
        if (!isValidEmail(currentState.parentEmail)) {
            return ValidationResult(false, "E-mail do responsável inválido")
        }
        
        // Telefone do responsável
        if (currentState.parentPhone.length < 10) {
            return ValidationResult(false, "Telefone do responsável inválido")
        }
        
        // Relacionamento
        if (currentState.relationship.isEmpty()) {
            return ValidationResult(false, "Relacionamento é obrigatório")
        }
        
        // Aceitação dos termos
        if (!currentState.termsAccepted) {
            return ValidationResult(false, "É necessário aceitar os termos de uso")
        }
        
        // Aceitação da privacidade
        if (!currentState.privacyAccepted) {
            return ValidationResult(false, "É necessário aceitar a política de privacidade")
        }
        
        return ValidationResult(true, "")
    }
    
    private fun isValidEmail(email: String): Boolean {
        return android.util.Patterns.EMAIL_ADDRESS.matcher(email).matches()
    }
    
    private fun createMockConsentStatus(): ConsentStatusData {
        return ConsentStatusData(
            isConsented = false, // Mock: não tem consentimento ainda
            parentName = "",
            parentEmail = "",
            parentPhone = "",
            relationship = "",
            consentDate = null
        )
    }
}

data class ValidationResult(
    val isValid: Boolean,
    val errorMessage: String
)

data class ConsentStatusData(
    val isConsented: Boolean,
    val parentName: String?,
    val parentEmail: String?,
    val parentPhone: String?,
    val relationship: String?,
    val consentDate: LocalDate?
) 