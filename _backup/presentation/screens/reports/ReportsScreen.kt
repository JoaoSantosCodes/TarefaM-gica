package com.tarefamagica.app.presentation.screens.reports

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
import java.time.LocalDate
import java.time.format.DateTimeFormatter

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ReportsScreen(
    onNavigateBack: () -> Unit,
    viewModel: ReportsViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    
    Column(
        modifier = Modifier.fillMaxSize()
    ) {
        // Header
        ReportsHeader(
            onNavigateBack = onNavigateBack,
            onExportReport = { viewModel.exportReport() }
        )
        
        // Filtros de período
        PeriodFilters(
            selectedPeriod = uiState.selectedPeriod,
            onPeriodChange = { viewModel.updatePeriod(it) }
        )
        
        // Conteúdo dos relatórios
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Resumo geral
            item {
                GeneralSummaryCard(summary = uiState.generalSummary)
            }
            
            // Progresso de tarefas
            item {
                TasksProgressCard(progress = uiState.tasksProgress)
            }
            
            // Conquistas
            item {
                AchievementsCard(achievements = uiState.achievements)
            }
            
            // Atividade financeira
            item {
                FinancialActivityCard(activity = uiState.financialActivity)
            }
            
            // Gráficos de atividade
            item {
                ActivityChartsCard(charts = uiState.activityCharts)
            }
            
            // Relatórios detalhados
            items(uiState.detailedReports) { report ->
                DetailedReportCard(
                    report = report,
                    onViewDetails = { viewModel.viewReportDetails(report.id) }
                )
            }
        }
    }
    
    // Loading overlay
    if (uiState.isLoading) {
        LoadingOverlay()
    }
    
    // Dialog de exportação
    if (uiState.showExportDialog) {
        ExportReportDialog(
            onExport = { format -> 
                viewModel.confirmExport(format)
            },
            onDismiss = { viewModel.hideExportDialog() }
        )
    }
}

@Composable
private fun ReportsHeader(
    onNavigateBack: () -> Unit,
    onExportReport: () -> Unit
) {
    Surface(
        modifier = Modifier.fillMaxWidth(),
        color = MaterialTheme.colorScheme.primary,
        shadowElevation = 4.dp
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
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
                text = "Relatórios",
                style = MaterialTheme.typography.headlineSmall,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onPrimary
            )
            
            IconButton(onClick = onExportReport) {
                Icon(
                    imageVector = Icons.Default.Download,
                    contentDescription = "Exportar",
                    tint = MaterialTheme.colorScheme.onPrimary
                )
            }
        }
    }
}

@Composable
private fun PeriodFilters(
    selectedPeriod: ReportPeriod,
    onPeriodChange: (ReportPeriod) -> Unit
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
            ReportPeriod.values().forEach { period ->
                FilterChip(
                    selected = selectedPeriod == period,
                    onClick = { onPeriodChange(period) },
                    label = {
                        Text(
                            text = period.displayName,
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
private fun GeneralSummaryCard(summary: GeneralSummary) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surface
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
    ) {
        Column(
            modifier = Modifier.padding(20.dp)
        ) {
            Text(
                text = "Resumo Geral",
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onSurface
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                SummaryItem(
                    icon = Icons.Default.Task,
                    label = "Tarefas",
                    value = "${summary.totalTasks}",
                    color = Color(0xFF2196F3)
                )
                
                SummaryItem(
                    icon = Icons.Default.Star,
                    label = "Conquistas",
                    value = "${summary.totalAchievements}",
                    color = Color(0xFFFF9800)
                )
                
                SummaryItem(
                    icon = Icons.Default.AccountBalanceWallet,
                    label = "Pontos",
                    value = "${summary.totalPoints}",
                    color = Color(0xFF4CAF50)
                )
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                SummaryItem(
                    icon = Icons.Default.TrendingUp,
                    label = "Nível",
                    value = "${summary.currentLevel}",
                    color = Color(0xFF9C27B0)
                )
                
                SummaryItem(
                    icon = Icons.Default.Schedule,
                    label = "Tempo Ativo",
                    value = "${summary.activeTime}h",
                    color = Color(0xFF607D8B)
                )
                
                SummaryItem(
                    icon = Icons.Default.AttachMoney,
                    label = "Saldo",
                    value = "R$ ${summary.balance}",
                    color = Color(0xFF795548)
                )
            }
        }
    }
}

@Composable
private fun SummaryItem(
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    label: String,
    value: String,
    color: Color
) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Surface(
            modifier = Modifier.size(48.dp),
            shape = CircleShape,
            color = color.copy(alpha = 0.2f)
        ) {
            Box(
                modifier = Modifier.fillMaxSize(),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = icon,
                    contentDescription = null,
                    modifier = Modifier.size(24.dp),
                    tint = color
                )
            }
        }
        
        Spacer(modifier = Modifier.height(8.dp))
        
        Text(
            text = value,
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.onSurface
        )
        
        Text(
            text = label,
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)
        )
    }
}

@Composable
private fun TasksProgressCard(progress: TasksProgress) {
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
                text = "Progresso de Tarefas",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onSurface
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Barra de progresso geral
            LinearProgressIndicator(
                progress = progress.completionRate,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(8.dp)
                    .clip(RoundedCornerShape(4.dp)),
                color = MaterialTheme.colorScheme.primary,
                trackColor = MaterialTheme.colorScheme.surfaceVariant
            )
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Text(
                text = "${(progress.completionRate * 100).toInt()}% concluído",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Estatísticas detalhadas
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                ProgressStat(
                    label = "Completadas",
                    value = "${progress.completedTasks}",
                    color = Color(0xFF4CAF50)
                )
                
                ProgressStat(
                    label = "Pendentes",
                    value = "${progress.pendingTasks}",
                    color = Color(0xFFFF9800)
                )
                
                ProgressStat(
                    label = "Atrasadas",
                    value = "${progress.overdueTasks}",
                    color = Color(0xFFFF5722)
                )
            }
        }
    }
}

@Composable
private fun ProgressStat(
    label: String,
    value: String,
    color: Color
) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = value,
            style = MaterialTheme.typography.titleLarge,
            fontWeight = FontWeight.Bold,
            color = color
        )
        
        Text(
            text = label,
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)
        )
    }
}

@Composable
private fun AchievementsCard(achievements: List<AchievementReport>) {
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
                text = "Conquistas Recentes",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onSurface
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            if (achievements.isEmpty()) {
                Text(
                    text = "Nenhuma conquista no período selecionado",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f),
                    textAlign = TextAlign.Center
                )
            } else {
                achievements.forEach { achievement ->
                    AchievementItem(achievement = achievement)
                    Spacer(modifier = Modifier.height(8.dp))
                }
            }
        }
    }
}

@Composable
private fun AchievementItem(achievement: AchievementReport) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Surface(
            modifier = Modifier.size(40.dp),
            shape = CircleShape,
            color = Color(0xFFFF9800).copy(alpha = 0.2f)
        ) {
            Box(
                modifier = Modifier.fillMaxSize(),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = Icons.Default.Star,
                    contentDescription = null,
                    modifier = Modifier.size(20.dp),
                    tint = Color(0xFFFF9800)
                )
            }
        }
        
        Spacer(modifier = Modifier.width(12.dp))
        
        Column(
            modifier = Modifier.weight(1f)
        ) {
            Text(
                text = achievement.name,
                style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.Medium,
                color = MaterialTheme.colorScheme.onSurface
            )
            
            Text(
                text = achievement.description,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)
            )
        }
        
        Text(
            text = "+${achievement.points} pts",
            style = MaterialTheme.typography.labelMedium,
            fontWeight = FontWeight.Bold,
            color = Color(0xFFFF9800)
        )
    }
}

@Composable
private fun FinancialActivityCard(activity: FinancialActivity) {
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
                text = "Atividade Financeira",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onSurface
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                FinancialStat(
                    label = "Ganhos",
                    value = "R$ ${activity.totalEarnings}",
                    color = Color(0xFF4CAF50)
                )
                
                FinancialStat(
                    label = "Saques",
                    value = "R$ ${activity.totalWithdrawals}",
                    color = Color(0xFFFF5722)
                )
                
                FinancialStat(
                    label = "Saldo",
                    value = "R$ ${activity.currentBalance}",
                    color = Color(0xFF2196F3)
                )
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            Text(
                text = "Transações: ${activity.totalTransactions}",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)
            )
        }
    }
}

@Composable
private fun FinancialStat(
    label: String,
    value: String,
    color: Color
) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = value,
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold,
            color = color
        )
        
        Text(
            text = label,
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)
        )
    }
}

@Composable
private fun ActivityChartsCard(charts: ActivityCharts) {
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
                text = "Gráficos de Atividade",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onSurface
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Placeholder para gráficos
            Surface(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(200.dp),
                shape = RoundedCornerShape(8.dp),
                color = MaterialTheme.colorScheme.surfaceVariant
            ) {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Icon(
                            imageVector = Icons.Default.BarChart,
                            contentDescription = null,
                            modifier = Modifier.size(48.dp),
                            tint = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.4f)
                        )
                        
                        Spacer(modifier = Modifier.height(8.dp))
                        
                        Text(
                            text = "Gráficos em desenvolvimento",
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun DetailedReportCard(
    report: DetailedReport,
    onViewDetails: () -> Unit
) {
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
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = report.title,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.onSurface
                )
                
                IconButton(onClick = onViewDetails) {
                    Icon(
                        imageVector = Icons.Default.Visibility,
                        contentDescription = "Ver detalhes",
                        tint = MaterialTheme.colorScheme.primary
                    )
                }
            }
            
            Text(
                text = report.description,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)
            )
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Text(
                text = "Gerado em: ${report.generatedAt.format(DateTimeFormatter.ofPattern("dd/MM/yyyy HH:mm"))}",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
            )
        }
    }
}

@Composable
private fun ExportReportDialog(
    onExport: (String) -> Unit,
    onDismiss: () -> Unit
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = {
            Text(
                text = "Exportar Relatório",
                style = MaterialTheme.typography.headlineSmall,
                fontWeight = FontWeight.Bold
            )
        },
        text = {
            Text(
                text = "Escolha o formato para exportar o relatório:",
                style = MaterialTheme.typography.bodyMedium
            )
        },
        confirmButton = {
            Column {
                TextButton(
                    onClick = { onExport("PDF") }
                ) {
                    Text("PDF")
                }
                TextButton(
                    onClick = { onExport("CSV") }
                ) {
                    Text("CSV")
                }
                TextButton(
                    onClick = { onExport("JSON") }
                ) {
                    Text("JSON")
                }
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text("Cancelar")
            }
        }
    )
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
                    text = "Gerando relatórios...",
                    style = MaterialTheme.typography.bodyMedium
                )
            }
        }
    }
}

enum class ReportPeriod(val displayName: String) {
    TODAY("Hoje"),
    WEEK("Esta Semana"),
    MONTH("Este Mês"),
    QUARTER("Este Trimestre"),
    YEAR("Este Ano")
}

data class GeneralSummary(
    val totalTasks: Int,
    val totalAchievements: Int,
    val totalPoints: Int,
    val currentLevel: Int,
    val activeTime: Int,
    val balance: Double
)

data class TasksProgress(
    val completedTasks: Int,
    val pendingTasks: Int,
    val overdueTasks: Int,
    val completionRate: Float
)

data class AchievementReport(
    val id: String,
    val name: String,
    val description: String,
    val points: Int,
    val earnedAt: LocalDate
)

data class FinancialActivity(
    val totalEarnings: Double,
    val totalWithdrawals: Double,
    val currentBalance: Double,
    val totalTransactions: Int
)

data class ActivityCharts(
    val dailyActivity: List<Int>,
    val weeklyProgress: List<Float>,
    val monthlyTrends: List<Double>
)

data class DetailedReport(
    val id: String,
    val title: String,
    val description: String,
    val generatedAt: LocalDate,
    val data: Map<String, Any>
) 