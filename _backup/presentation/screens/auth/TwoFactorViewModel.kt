package com.tarefamagica.app.presentation.screens.auth

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.tarefamagica.app.data.repository.AuthRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class TwoFactorViewModel @Inject constructor(
    private val authRepository: AuthRepository
) : ViewModel() {
    
    private val _uiState = MutableStateFlow(TwoFactorUiState())
    val uiState: StateFlow<TwoFactorUiState> = _uiState.asStateFlow()
    
    fun setUserId(userId: String) {
        _uiState.update { it.copy(userId = userId) }
    }
    
    fun updateVerificationCode(code: String) {
        _uiState.update { it.copy(verificationCode = code) }
    }
    
    fun updateBackupCode(code: String) {
        _uiState.update { it.copy(backupCode = code) }
    }
    
    fun loadTwoFactorSetup() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, errorMessage = null) }
            
            try {
                // Simular chamada de API para setup 2FA
                kotlinx.coroutines.delay(1000)
                
                val mockSetup = createMockTwoFactorSetup()
                _uiState.update { 
                    it.copy(
                        qrCodeUrl = mockSetup.qrCodeUrl,
                        secretKey = mockSetup.secretKey,
                        backupCodes = mockSetup.backupCodes,
                        mode = TwoFactorMode.SETUP,
                        isLoading = false
                    )
                }
                
            } catch (e: Exception) {
                _uiState.update { 
                    it.copy(
                        isLoading = false,
                        errorMessage = "Erro ao carregar configuração 2FA: ${e.message}"
                    )
                }
            }
        }
    }
    
    fun completeSetup() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, errorMessage = null) }
            
            try {
                val code = _uiState.value.verificationCode
                
                // Validação básica
                if (code.length != 6 || !code.all { it.isDigit() }) {
                    _uiState.update { 
                        it.copy(
                            isLoading = false,
                            errorMessage = "Código inválido. Digite 6 dígitos."
                        )
                    }
                    return@launch
                }
                
                // Simular verificação
                kotlinx.coroutines.delay(1500)
                
                // Mock de sucesso
                _uiState.update { 
                    it.copy(
                        isLoading = false,
                        isSuccess = true
                    )
                }
                
            } catch (e: Exception) {
                _uiState.update { 
                    it.copy(
                        isLoading = false,
                        errorMessage = "Erro ao verificar código: ${e.message}"
                    )
                }
            }
        }
    }
    
    fun verifyCode(code: String) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, errorMessage = null) }
            
            try {
                // Validação básica
                if (code.length != 6 || !code.all { it.isDigit() }) {
                    _uiState.update { 
                        it.copy(
                            isLoading = false,
                            errorMessage = "Código inválido. Digite 6 dígitos."
                        )
                    }
                    return@launch
                }
                
                // Simular verificação
                kotlinx.coroutines.delay(1500)
                
                // Mock de sucesso
                _uiState.update { 
                    it.copy(
                        isLoading = false,
                        isSuccess = true
                    )
                }
                
            } catch (e: Exception) {
                _uiState.update { 
                    it.copy(
                        isLoading = false,
                        errorMessage = "Erro ao verificar código: ${e.message}"
                    )
                }
            }
        }
    }
    
    fun verifyBackupCode(code: String) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, errorMessage = null) }
            
            try {
                // Validação básica
                if (code.length != 8 || !code.all { it.isDigit() }) {
                    _uiState.update { 
                        it.copy(
                            isLoading = false,
                            errorMessage = "Código de backup inválido. Digite 8 dígitos."
                        )
                    }
                    return@launch
                }
                
                // Verificar se o código está na lista de backup codes
                val backupCodes = _uiState.value.backupCodes
                if (!backupCodes.contains(code)) {
                    _uiState.update { 
                        it.copy(
                            isLoading = false,
                            errorMessage = "Código de backup inválido ou já usado."
                        )
                    }
                    return@launch
                }
                
                // Simular verificação
                kotlinx.coroutines.delay(1500)
                
                // Mock de sucesso
                _uiState.update { 
                    it.copy(
                        isLoading = false,
                        isSuccess = true
                    )
                }
                
            } catch (e: Exception) {
                _uiState.update { 
                    it.copy(
                        isLoading = false,
                        errorMessage = "Erro ao verificar código de backup: ${e.message}"
                    )
                }
            }
        }
    }
    
    fun switchToBackupMode() {
        _uiState.update { 
            it.copy(
                mode = TwoFactorMode.BACKUP,
                backupCode = "",
                errorMessage = null
            )
        }
    }
    
    fun switchToVerifyMode() {
        _uiState.update { 
            it.copy(
                mode = TwoFactorMode.VERIFY,
                verificationCode = "",
                errorMessage = null
            )
        }
    }
    
    private fun createMockTwoFactorSetup(): TwoFactorSetupData {
        return TwoFactorSetupData(
            qrCodeUrl = "https://api.tarefamagica.com/qr/2fa/user_123",
            secretKey = "JBSWY3DPEHPK3PXP",
            backupCodes = listOf(
                "12345678",
                "87654321",
                "11111111",
                "22222222",
                "33333333",
                "44444444",
                "55555555",
                "66666666",
                "77777777",
                "88888888"
            )
        )
    }
}

data class TwoFactorSetupData(
    val qrCodeUrl: String,
    val secretKey: String,
    val backupCodes: List<String>
) 