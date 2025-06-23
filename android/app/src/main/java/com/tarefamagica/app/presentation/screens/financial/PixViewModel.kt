package com.tarefamagica.app.presentation.screens.financial

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import java.time.LocalDateTime
import java.util.UUID
import javax.inject.Inject

@HiltViewModel
class PixViewModel @Inject constructor() : ViewModel() {
    
    private val _uiState = MutableStateFlow(PixUiState())
    val uiState: StateFlow<PixUiState> = _uiState.asStateFlow()
    
    init {
        loadPixData()
    }
    
    fun updateSelectedTab(tab: PixTab) {
        _uiState.update { it.copy(selectedTab = tab) }
    }
    
    fun updatePixKey(key: String) {
        _uiState.update { it.copy(pixKey = key) }
    }
    
    fun updatePixKeyType(keyType: PixKeyType) {
        _uiState.update { it.copy(pixKeyType = keyType) }
    }
    
    fun updateWithdrawAmount(amount: String) {
        _uiState.update { it.copy(withdrawAmount = amount) }
    }
    
    fun savePixConfiguration() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, errorMessage = null) }
            
            try {
                // Simular salvamento da configuração
                kotlinx.coroutines.delay(1500)
                
                // Mock de sucesso
                _uiState.update { 
                    it.copy(
                        isLoading = false,
                        selectedTab = PixTab.HISTORY
                    )
                }
                
                // Recarregar dados
                loadPixData()
                
            } catch (e: Exception) {
                _uiState.update { 
                    it.copy(
                        isLoading = false,
                        errorMessage = "Erro ao salvar configuração: ${e.message}"
                    )
                }
            }
        }
    }
    
    fun requestWithdraw() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, errorMessage = null) }
            
            try {
                val amount = _uiState.value.withdrawAmount.toDoubleOrNull()
                if (amount == null || amount <= 0) {
                    _uiState.update { 
                        it.copy(
                            isLoading = false,
                            errorMessage = "Valor inválido para saque"
                        )
                    }
                    return@launch
                }
                
                if (amount > _uiState.value.balance) {
                    _uiState.update { 
                        it.copy(
                            isLoading = false,
                            errorMessage = "Saldo insuficiente para o saque"
                        )
                    }
                    return@launch
                }
                
                // Simular processamento do saque
                kotlinx.coroutines.delay(2000)
                
                // Criar nova transação
                val newTransaction = Transaction(
                    id = UUID.randomUUID().toString(),
                    type = TransactionType.WITHDRAWAL,
                    amount = amount,
                    status = TransactionStatus.PROCESSING,
                    description = "Saque via PIX",
                    createdAt = LocalDateTime.now(),
                    processedAt = null
                )
                
                val updatedTransactions = _uiState.value.transactions.toMutableList()
                updatedTransactions.add(0, newTransaction)
                
                _uiState.update { 
                    it.copy(
                        isLoading = false,
                        balance = it.balance - amount,
                        withdrawAmount = "",
                        transactions = updatedTransactions,
                        selectedTab = PixTab.HISTORY
                    )
                }
                
            } catch (e: Exception) {
                _uiState.update { 
                    it.copy(
                        isLoading = false,
                        errorMessage = "Erro ao processar saque: ${e.message}"
                    )
                }
            }
        }
    }
    
    fun selectTransaction(transaction: Transaction) {
        _uiState.update { it.copy(selectedTransaction = transaction) }
    }
    
    fun clearSelectedTransaction() {
        _uiState.update { it.copy(selectedTransaction = null) }
    }
    
    private fun loadPixData() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, errorMessage = null) }
            
            try {
                // Simular carregamento de dados
                kotlinx.coroutines.delay(1000)
                
                // Mock de dados
                val mockBalance = 125.50
                val mockTransactions = createMockTransactions()
                val mockPixKey = "usuario@email.com"
                val mockPixKeyType = PixKeyType.EMAIL
                
                _uiState.update { 
                    it.copy(
                        balance = mockBalance,
                        transactions = mockTransactions,
                        pixKey = mockPixKey,
                        pixKeyType = mockPixKeyType,
                        isLoading = false
                    )
                }
                
            } catch (e: Exception) {
                _uiState.update { 
                    it.copy(
                        isLoading = false,
                        errorMessage = "Erro ao carregar dados: ${e.message}"
                    )
                }
            }
        }
    }
    
    private fun createMockTransactions(): List<Transaction> {
        return listOf(
            Transaction(
                id = "1",
                type = TransactionType.WITHDRAWAL,
                amount = 50.00,
                status = TransactionStatus.COMPLETED,
                description = "Saque via PIX",
                createdAt = LocalDateTime.now().minusDays(2),
                processedAt = LocalDateTime.now().minusDays(2).plusMinutes(5)
            ),
            Transaction(
                id = "2",
                type = TransactionType.DEPOSIT,
                amount = 25.00,
                status = TransactionStatus.COMPLETED,
                description = "Depósito por tarefas completas",
                createdAt = LocalDateTime.now().minusDays(5),
                processedAt = LocalDateTime.now().minusDays(5).plusMinutes(2)
            ),
            Transaction(
                id = "3",
                type = TransactionType.WITHDRAWAL,
                amount = 30.00,
                status = TransactionStatus.PROCESSING,
                description = "Saque via PIX",
                createdAt = LocalDateTime.now().minusHours(2),
                processedAt = null
            ),
            Transaction(
                id = "4",
                type = TransactionType.REFUND,
                amount = 15.00,
                status = TransactionStatus.COMPLETED,
                description = "Reembolso - tarefa cancelada",
                createdAt = LocalDateTime.now().minusDays(7),
                processedAt = LocalDateTime.now().minusDays(7).plusMinutes(10)
            )
        )
    }
} 