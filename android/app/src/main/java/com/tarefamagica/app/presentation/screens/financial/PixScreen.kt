package com.tarefamagica.app.presentation.screens.financial

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PixScreen(
    onNavigateBack: () -> Unit,
    viewModel: PixViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    
    Column(
        modifier = Modifier.fillMaxSize()
    ) {
        // Header
        PixHeader(
            balance = uiState.balance,
            onNavigateBack = onNavigateBack
        )
        
        // Tabs
        PixTabs(
            selectedTab = uiState.selectedTab,
            onTabChange = { viewModel.updateSelectedTab(it) }
        )
        
        // Conteúdo baseado na tab selecionada
        when (uiState.selectedTab) {
            PixTab.CONFIGURATION -> {
                PixConfigurationContent(
                    uiState = uiState,
                    onPixKeyChange = { viewModel.updatePixKey(it) },
                    onPixKeyTypeChange = { viewModel.updatePixKeyType(it) },
                    onSaveConfiguration = { viewModel.savePixConfiguration() }
                )
            }
            PixTab.HISTORY -> {
                PixHistoryContent(
                    transactions = uiState.transactions,
                    onTransactionClick = { viewModel.selectTransaction(it) }
                )
            }
            PixTab.WITHDRAW -> {
                PixWithdrawContent(
                    uiState = uiState,
                    onAmountChange = { viewModel.updateWithdrawAmount(it) },
                    onWithdraw = { viewModel.requestWithdraw() }
                )
            }
        }
    }
    
    // Loading overlay
    if (uiState.isLoading) {
        LoadingOverlay()
    }
    
    // Dialog de detalhes da transação
    uiState.selectedTransaction?.let { transaction ->
        TransactionDetailDialog(
            transaction = transaction,
            onDismiss = { viewModel.clearSelectedTransaction() }
        )
    }
}

@Composable
private fun PixHeader(
    balance: Double,
    onNavigateBack: () -> Unit
) {
    Surface(
        modifier = Modifier.fillMaxWidth(),
        color = MaterialTheme.colorScheme.primary,
        shadowElevation = 4.dp
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                IconButton(onClick = onNavigateBack) {
                    Icon(
                        imageVector = Icons.Default.ArrowBack,
                        contentDescription = "Voltar",
                        tint = MaterialTheme.colorScheme.onPrimary
                    )
                }
                
                Text(
                    text = "PIX",
                    style = MaterialTheme.typography.headlineSmall,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.onPrimary
                )
                
                Spacer(modifier = Modifier.width(48.dp))
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Saldo
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.surface.copy(alpha = 0.9f)
                )
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text(
                        text = "Saldo Disponível",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)
                    )
                    
                    Text(
                        text = "R$ %.2f".format(balance),
                        style = MaterialTheme.typography.headlineMedium,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.onSurface
                    )
                    
                    Text(
                        text = "Convertido de ${(balance * 100).toInt()} pontos",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                    )
                }
            }
        }
    }
}

@Composable
private fun PixTabs(
    selectedTab: PixTab,
    onTabChange: (PixTab) -> Unit
) {
    Surface(
        modifier = Modifier.fillMaxWidth(),
        color = MaterialTheme.colorScheme.surface,
        shadowElevation = 2.dp
    ) {
        Row(
            modifier = Modifier.padding(16.dp),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            PixTab.values().forEach { tab ->
                FilterChip(
                    selected = selectedTab == tab,
                    onClick = { onTabChange(tab) },
                    label = {
                        Text(
                            text = tab.displayName,
                            style = MaterialTheme.typography.labelMedium
                        )
                    },
                    colors = FilterChipDefaults.filterChipColors(
                        selectedContainerColor = MaterialTheme.colorScheme.primary,
                        selectedLabelColor = MaterialTheme.colorScheme.onPrimary
                    )
                )
            }
        }
    }
}

@Composable
private fun PixConfigurationContent(
    uiState: PixUiState,
    onPixKeyChange: (String) -> Unit,
    onPixKeyTypeChange: (PixKeyType) -> Unit,
    onSaveConfiguration: () -> Unit
) {
    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.surface
                ),
                elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
            ) {
                Column(
                    modifier = Modifier.padding(16.dp)
                ) {
                    Text(
                        text = "Configuração PIX",
                        style = MaterialTheme.typography.titleLarge,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.onSurface
                    )
                    
                    Spacer(modifier = Modifier.height(16.dp))
                    
                    Text(
                        text = "Configure sua chave PIX para receber pagamentos",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)
                    )
                    
                    Spacer(modifier = Modifier.height(16.dp))
                    
                    // Tipo de chave PIX
                    Text(
                        text = "Tipo de Chave PIX",
                        style = MaterialTheme.typography.titleSmall,
                        fontWeight = FontWeight.Medium,
                        color = MaterialTheme.colorScheme.onSurface
                    )
                    
                    Spacer(modifier = Modifier.height(8.dp))
                    
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        PixKeyType.values().forEach { keyType ->
                            FilterChip(
                                selected = uiState.pixKeyType == keyType,
                                onClick = { onPixKeyTypeChange(keyType) },
                                label = {
                                    Text(
                                        text = keyType.displayName,
                                        style = MaterialTheme.typography.labelSmall
                                    )
                                },
                                colors = FilterChipDefaults.filterChipColors(
                                    selectedContainerColor = MaterialTheme.colorScheme.primary,
                                    selectedLabelColor = MaterialTheme.colorScheme.onPrimary
                                )
                            )
                        }
                    }
                    
                    Spacer(modifier = Modifier.height(16.dp))
                    
                    // Chave PIX
                    OutlinedTextField(
                        value = uiState.pixKey,
                        onValueChange = onPixKeyChange,
                        label = { Text("Chave PIX") },
                        placeholder = { Text(getPixKeyPlaceholder(uiState.pixKeyType)) },
                        leadingIcon = {
                            Icon(
                                imageVector = Icons.Default.Key,
                                contentDescription = null,
                                tint = MaterialTheme.colorScheme.primary
                            )
                        },
                        modifier = Modifier.fillMaxWidth(),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = MaterialTheme.colorScheme.primary,
                            unfocusedBorderColor = MaterialTheme.colorScheme.outline
                        )
                    )
                    
                    Spacer(modifier = Modifier.height(16.dp))
                    
                    // Botão salvar
                    Button(
                        onClick = onSaveConfiguration,
                        enabled = uiState.pixKey.isNotEmpty() && !uiState.isLoading,
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(56.dp),
                        shape = RoundedCornerShape(16.dp),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = MaterialTheme.colorScheme.primary
                        )
                    ) {
                        if (uiState.isLoading) {
                            CircularProgressIndicator(
                                modifier = Modifier.size(24.dp),
                                color = MaterialTheme.colorScheme.onPrimary,
                                strokeWidth = 2.dp
                            )
                        } else {
                            Icon(
                                imageVector = Icons.Default.Save,
                                contentDescription = null,
                                modifier = Modifier.size(20.dp)
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                            Text(
                                text = "Salvar Configuração",
                                style = MaterialTheme.typography.labelLarge
                            )
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun PixHistoryContent(
    transactions: List<Transaction>,
    onTransactionClick: (Transaction) -> Unit
) {
    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        items(
            items = transactions,
            key = { it.id }
        ) { transaction ->
            TransactionCard(
                transaction = transaction,
                onTransactionClick = onTransactionClick
            )
        }
    }
}

@Composable
private fun TransactionCard(
    transaction: Transaction,
    onTransactionClick: (Transaction) -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surface
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Ícone da transação
            Surface(
                modifier = Modifier.size(48.dp),
                shape = CircleShape,
                color = getTransactionColor(transaction.type).copy(alpha = 0.2f)
            ) {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        imageVector = getTransactionIcon(transaction.type),
                        contentDescription = null,
                        modifier = Modifier.size(24.dp),
                        tint = getTransactionColor(transaction.type)
                    )
                }
            }
            
            Spacer(modifier = Modifier.width(16.dp))
            
            // Informações da transação
            Column(
                modifier = Modifier.weight(1f)
            ) {
                Text(
                    text = transaction.description,
                    style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.Medium,
                    color = MaterialTheme.colorScheme.onSurface
                )
                
                Text(
                    text = transaction.createdAt.format(DateTimeFormatter.ofPattern("dd/MM/yyyy HH:mm")),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)
                )
                
                Text(
                    text = transaction.status.displayName,
                    style = MaterialTheme.typography.labelSmall,
                    color = getStatusColor(transaction.status)
                )
            }
            
            // Valor
            Column(
                horizontalAlignment = Alignment.End
            ) {
                Text(
                    text = "R$ %.2f".format(transaction.amount),
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = getTransactionColor(transaction.type)
                )
                
                Text(
                    text = transaction.type.displayName,
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                )
            }
        }
    }
}

@Composable
private fun PixWithdrawContent(
    uiState: PixUiState,
    onAmountChange: (String) -> Unit,
    onWithdraw: () -> Unit
) {
    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.surface
                ),
                elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
            ) {
                Column(
                    modifier = Modifier.padding(16.dp)
                ) {
                    Text(
                        text = "Solicitar Saque",
                        style = MaterialTheme.typography.titleLarge,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.onSurface
                    )
                    
                    Spacer(modifier = Modifier.height(16.dp))
                    
                    Text(
                        text = "Converta seus pontos em dinheiro e receba via PIX",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)
                    )
                    
                    Spacer(modifier = Modifier.height(16.dp))
                    
                    // Valor do saque
                    OutlinedTextField(
                        value = uiState.withdrawAmount,
                        onValueChange = onAmountChange,
                        label = { Text("Valor do saque (R$)") },
                        placeholder = { Text("0,00") },
                        leadingIcon = {
                            Icon(
                                imageVector = Icons.Default.AttachMoney,
                                contentDescription = null,
                                tint = MaterialTheme.colorScheme.primary
                            )
                        },
                        keyboardOptions = KeyboardOptions(
                            keyboardType = KeyboardType.Decimal,
                            imeAction = ImeAction.Done
                        ),
                        modifier = Modifier.fillMaxWidth(),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = MaterialTheme.colorScheme.primary,
                            unfocusedBorderColor = MaterialTheme.colorScheme.outline
                        )
                    )
                    
                    Spacer(modifier = Modifier.height(8.dp))
                    
                    Text(
                        text = "Pontos necessários: ${(uiState.withdrawAmount.toDoubleOrNull() ?: 0.0) * 100}",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                    )
                    
                    Spacer(modifier = Modifier.height(16.dp))
                    
                    // Botão de saque
                    Button(
                        onClick = onWithdraw,
                        enabled = uiState.withdrawAmount.isNotEmpty() && 
                                 uiState.withdrawAmount.toDoubleOrNull() != null &&
                                 uiState.withdrawAmount.toDoubleOrNull()!! > 0 &&
                                 !uiState.isLoading,
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(56.dp),
                        shape = RoundedCornerShape(16.dp),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = MaterialTheme.colorScheme.primary
                        )
                    ) {
                        if (uiState.isLoading) {
                            CircularProgressIndicator(
                                modifier = Modifier.size(24.dp),
                                color = MaterialTheme.colorScheme.onPrimary,
                                strokeWidth = 2.dp
                            )
                        } else {
                            Icon(
                                imageVector = Icons.Default.AccountBalanceWallet,
                                contentDescription = null,
                                modifier = Modifier.size(20.dp)
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                            Text(
                                text = "Solicitar Saque",
                                style = MaterialTheme.typography.labelLarge
                            )
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun TransactionDetailDialog(
    transaction: Transaction,
    onDismiss: () -> Unit
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = {
            Text(
                text = "Detalhes da Transação",
                style = MaterialTheme.typography.headlineSmall,
                fontWeight = FontWeight.Bold
            )
        },
        text = {
            Column {
                DetailRow("ID", transaction.id)
                DetailRow("Descrição", transaction.description)
                DetailRow("Valor", "R$ %.2f".format(transaction.amount))
                DetailRow("Tipo", transaction.type.displayName)
                DetailRow("Status", transaction.status.displayName)
                DetailRow("Data", transaction.createdAt.format(DateTimeFormatter.ofPattern("dd/MM/yyyy HH:mm")))
                transaction.processedAt?.let { 
                    DetailRow("Processado em", it.format(DateTimeFormatter.ofPattern("dd/MM/yyyy HH:mm")))
                }
            }
        },
        confirmButton = {
            TextButton(onClick = onDismiss) {
                Text("Fechar")
            }
        }
    )
}

@Composable
private fun DetailRow(label: String, value: String) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(
            text = label,
            style = MaterialTheme.typography.bodyMedium,
            fontWeight = FontWeight.Medium
        )
        Text(
            text = value,
            style = MaterialTheme.typography.bodyMedium
        )
    }
}

@Composable
private fun LoadingOverlay() {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.surface.copy(alpha = 0.8f)),
        contentAlignment = Alignment.Center
    ) {
        Card(
            modifier = Modifier.padding(24.dp),
            colors = CardDefaults.cardColors(
                containerColor = MaterialTheme.colorScheme.surface
            )
        ) {
            Column(
                modifier = Modifier.padding(24.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                CircularProgressIndicator(
                    color = MaterialTheme.colorScheme.primary
                )
                Spacer(modifier = Modifier.height(16.dp))
                Text(
                    text = "Processando...",
                    style = MaterialTheme.typography.bodyMedium
                )
            }
        }
    }
}

private fun getPixKeyPlaceholder(keyType: PixKeyType): String {
    return when (keyType) {
        PixKeyType.CPF -> "000.000.000-00"
        PixKeyType.EMAIL -> "seu@email.com"
        PixKeyType.PHONE -> "(11) 99999-9999"
        PixKeyType.RANDOM -> "Chave aleatória"
    }
}

private fun getTransactionColor(type: TransactionType): Color {
    return when (type) {
        TransactionType.WITHDRAWAL -> Color(0xFFFF5722)
        TransactionType.DEPOSIT -> Color(0xFF4CAF50)
        TransactionType.REFUND -> Color(0xFFFF9800)
    }
}

private fun getTransactionIcon(type: TransactionType): androidx.compose.ui.graphics.vector.ImageVector {
    return when (type) {
        TransactionType.WITHDRAWAL -> Icons.Default.AccountBalanceWallet
        TransactionType.DEPOSIT -> Icons.Default.AccountBalance
        TransactionType.REFUND -> Icons.Default.Refresh
    }
}

private fun getStatusColor(status: TransactionStatus): Color {
    return when (status) {
        TransactionStatus.PENDING -> Color(0xFFFF9800)
        TransactionStatus.PROCESSING -> Color(0xFF2196F3)
        TransactionStatus.COMPLETED -> Color(0xFF4CAF50)
        TransactionStatus.FAILED -> Color(0xFFFF5722)
        TransactionStatus.CANCELLED -> Color(0xFF9E9E9E)
    }
}

enum class PixTab(val displayName: String) {
    CONFIGURATION("Configuração"),
    HISTORY("Histórico"),
    WITHDRAW("Saque")
}

enum class PixKeyType(val displayName: String) {
    CPF("CPF"),
    EMAIL("E-mail"),
    PHONE("Telefone"),
    RANDOM("Chave Aleatória")
}

enum class TransactionType(val displayName: String) {
    WITHDRAWAL("Saque"),
    DEPOSIT("Depósito"),
    REFUND("Reembolso")
}

enum class TransactionStatus(val displayName: String) {
    PENDING("Pendente"),
    PROCESSING("Processando"),
    COMPLETED("Concluída"),
    FAILED("Falhou"),
    CANCELLED("Cancelada")
}

data class Transaction(
    val id: String,
    val type: TransactionType,
    val amount: Double,
    val status: TransactionStatus,
    val description: String,
    val createdAt: LocalDateTime,
    val processedAt: LocalDateTime?
)

data class PixUiState(
    val balance: Double = 0.0,
    val selectedTab: PixTab = PixTab.CONFIGURATION,
    val pixKey: String = "",
    val pixKeyType: PixKeyType = PixKeyType.EMAIL,
    val withdrawAmount: String = "",
    val transactions: List<Transaction> = emptyList(),
    val selectedTransaction: Transaction? = null,
    val isLoading: Boolean = false,
    val errorMessage: String? = null
) 