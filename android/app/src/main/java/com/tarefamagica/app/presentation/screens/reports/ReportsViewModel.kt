package com.tarefamagica.app.presentation.screens.reports

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import java.time.LocalDate
import java.util.UUID
import javax.inject.Inject

@HiltViewModel
class ReportsViewModel @Inject constructor() : ViewModel() {
    
    private val _uiState = MutableStateFlow(ReportsUiState())
    val uiState: StateFlow<ReportsUiState> = _uiState.asStateFlow()
    
    init {
        loadReports()
    }
    
    fun updatePeriod(period: ReportPeriod) {
        _uiState.update { it.copy(selectedPeriod = period) }
        loadReports()
    }
    
    fun exportReport() {
        _uiState.update { it.copy(showExportDialog = true) }
    }
    
    fun hideExportDialog() {
        _uiState.update { it.copy(showExportDialog = false) }
    }
    
    fun confirmExport(format: String) {
        viewModelScope.launch {
            _uiState.update { 
                it.copy(
                    showExportDialog = false,
                    isLoading = true
                )
            }
            
            try {
                // Simular exportação
                kotlinx.coroutines.delay(2000)
                
                // Mock de sucesso
                _uiState.update { 
                    it.copy(
                        isLoading = false,
                        exportMessage = "Relatório exportado com sucesso em formato $format"
                    )
                }
                
            } catch (e: Exception) {
                _uiState.update { 
                    it.copy(
                        isLoading = false,
                        errorMessage = "Erro ao exportar relatório: ${e.message}"
                    )
                }
            }
        }
    }
    
    fun viewReportDetails(reportId: String) {
        // Implementar navegação para detalhes do relatório
        _uiState.update { 
            it.copy(
                selectedReportId = reportId
            )
        }
    }
    
    private fun loadReports() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, errorMessage = null) }
            
            try {
                // Simular carregamento de dados
                kotlinx.coroutines.delay(1500)
                
                // Mock de dados baseado no período selecionado
                val mockData = createMockReportsData(_uiState.value.selectedPeriod)
                
                _uiState.update { 
                    it.copy(
                        generalSummary = mockData.generalSummary,
                        tasksProgress = mockData.tasksProgress,
                        achievements = mockData.achievements,
                        financialActivity = mockData.financialActivity,
                        activityCharts = mockData.activityCharts,
                        detailedReports = mockData.detailedReports,
                        isLoading = false
                    )
                }
                
            } catch (e: Exception) {
                _uiState.update { 
                    it.copy(
                        isLoading = false,
                        errorMessage = "Erro ao carregar relatórios: ${e.message}"
                    )
                }
            }
        }
    }
    
    private fun createMockReportsData(period: ReportPeriod): MockReportsData {
        return when (period) {
            ReportPeriod.TODAY -> createTodayData()
            ReportPeriod.WEEK -> createWeekData()
            ReportPeriod.MONTH -> createMonthData()
            ReportPeriod.QUARTER -> createQuarterData()
            ReportPeriod.YEAR -> createYearData()
        }
    }
    
    private fun createTodayData(): MockReportsData {
        return MockReportsData(
            generalSummary = GeneralSummary(
                totalTasks = 5,
                totalAchievements = 2,
                totalPoints = 150,
                currentLevel = 8,
                activeTime = 3,
                balance = 25.50
            ),
            tasksProgress = TasksProgress(
                completedTasks = 3,
                pendingTasks = 2,
                overdueTasks = 0,
                completionRate = 0.6f
            ),
            achievements = listOf(
                AchievementReport(
                    id = "1",
                    name = "Primeira Tarefa",
                    description = "Completou sua primeira tarefa do dia",
                    points = 50,
                    earnedAt = LocalDate.now()
                ),
                AchievementReport(
                    id = "2",
                    name = "Consistência",
                    description = "Completou 3 tarefas em um dia",
                    points = 100,
                    earnedAt = LocalDate.now()
                )
            ),
            financialActivity = FinancialActivity(
                totalEarnings = 25.50,
                totalWithdrawals = 0.0,
                currentBalance = 25.50,
                totalTransactions = 1
            ),
            activityCharts = ActivityCharts(
                dailyActivity = listOf(2, 3, 1, 4, 2, 3, 5),
                weeklyProgress = listOf(0.6f, 0.8f, 0.4f, 0.9f, 0.7f, 0.5f, 0.6f),
                monthlyTrends = listOf(150.0, 200.0, 180.0, 250.0)
            ),
            detailedReports = listOf(
                DetailedReport(
                    id = "1",
                    title = "Relatório Diário",
                    description = "Resumo das atividades de hoje",
                    generatedAt = LocalDate.now(),
                    data = mapOf(
                        "tasks_completed" to 3,
                        "points_earned" to 150,
                        "time_spent" to 3
                    )
                )
            )
        )
    }
    
    private fun createWeekData(): MockReportsData {
        return MockReportsData(
            generalSummary = GeneralSummary(
                totalTasks = 25,
                totalAchievements = 8,
                totalPoints = 750,
                currentLevel = 8,
                activeTime = 18,
                balance = 75.00
            ),
            tasksProgress = TasksProgress(
                completedTasks = 20,
                pendingTasks = 5,
                overdueTasks = 2,
                completionRate = 0.8f
            ),
            achievements = listOf(
                AchievementReport(
                    id = "1",
                    name = "Semana Produtiva",
                    description = "Completou 20 tarefas em uma semana",
                    points = 200,
                    earnedAt = LocalDate.now().minusDays(2)
                ),
                AchievementReport(
                    id = "2",
                    name = "Consistência Semanal",
                    description = "Manteve atividade por 7 dias seguidos",
                    points = 150,
                    earnedAt = LocalDate.now().minusDays(5)
                )
            ),
            financialActivity = FinancialActivity(
                totalEarnings = 75.00,
                totalWithdrawals = 25.00,
                currentBalance = 50.00,
                totalTransactions = 3
            ),
            activityCharts = ActivityCharts(
                dailyActivity = listOf(5, 4, 6, 3, 7, 2, 4),
                weeklyProgress = listOf(0.8f, 0.9f, 0.7f, 0.8f, 0.9f, 0.6f, 0.8f),
                monthlyTrends = listOf(750.0, 800.0, 700.0, 900.0)
            ),
            detailedReports = listOf(
                DetailedReport(
                    id = "1",
                    title = "Relatório Semanal",
                    description = "Resumo das atividades da semana",
                    generatedAt = LocalDate.now(),
                    data = mapOf(
                        "tasks_completed" to 20,
                        "points_earned" to 750,
                        "time_spent" to 18
                    )
                )
            )
        )
    }
    
    private fun createMonthData(): MockReportsData {
        return MockReportsData(
            generalSummary = GeneralSummary(
                totalTasks = 120,
                totalAchievements = 35,
                totalPoints = 3500,
                currentLevel = 12,
                activeTime = 85,
                balance = 350.00
            ),
            tasksProgress = TasksProgress(
                completedTasks = 110,
                pendingTasks = 10,
                overdueTasks = 5,
                completionRate = 0.92f
            ),
            achievements = listOf(
                AchievementReport(
                    id = "1",
                    name = "Mestre das Tarefas",
                    description = "Completou 100 tarefas em um mês",
                    points = 500,
                    earnedAt = LocalDate.now().minusDays(15)
                ),
                AchievementReport(
                    id = "2",
                    name = "Nível Avançado",
                    description = "Atingiu o nível 10",
                    points = 300,
                    earnedAt = LocalDate.now().minusDays(20)
                )
            ),
            financialActivity = FinancialActivity(
                totalEarnings = 350.00,
                totalWithdrawals = 150.00,
                currentBalance = 200.00,
                totalTransactions = 12
            ),
            activityCharts = ActivityCharts(
                dailyActivity = listOf(4, 5, 3, 6, 4, 5, 4),
                weeklyProgress = listOf(0.9f, 0.95f, 0.88f, 0.92f),
                monthlyTrends = listOf(3500.0, 3800.0, 3200.0, 4000.0)
            ),
            detailedReports = listOf(
                DetailedReport(
                    id = "1",
                    title = "Relatório Mensal",
                    description = "Resumo das atividades do mês",
                    generatedAt = LocalDate.now(),
                    data = mapOf(
                        "tasks_completed" to 110,
                        "points_earned" to 3500,
                        "time_spent" to 85
                    )
                )
            )
        )
    }
    
    private fun createQuarterData(): MockReportsData {
        return MockReportsData(
            generalSummary = GeneralSummary(
                totalTasks = 350,
                totalAchievements = 95,
                totalPoints = 10500,
                currentLevel = 18,
                activeTime = 250,
                balance = 1050.00
            ),
            tasksProgress = TasksProgress(
                completedTasks = 330,
                pendingTasks = 20,
                overdueTasks = 15,
                completionRate = 0.94f
            ),
            achievements = listOf(
                AchievementReport(
                    id = "1",
                    name = "Veterano",
                    description = "Completou 300 tarefas em um trimestre",
                    points = 1000,
                    earnedAt = LocalDate.now().minusDays(45)
                ),
                AchievementReport(
                    id = "2",
                    name = "Especialista",
                    description = "Atingiu o nível 15",
                    points = 800,
                    earnedAt = LocalDate.now().minusDays(60)
                )
            ),
            financialActivity = FinancialActivity(
                totalEarnings = 1050.00,
                totalWithdrawals = 400.00,
                currentBalance = 650.00,
                totalTransactions = 35
            ),
            activityCharts = ActivityCharts(
                dailyActivity = listOf(4, 5, 4, 6, 5, 4, 5),
                weeklyProgress = listOf(0.94f, 0.96f, 0.92f, 0.95f),
                monthlyTrends = listOf(10500.0, 11000.0, 10000.0, 12000.0)
            ),
            detailedReports = listOf(
                DetailedReport(
                    id = "1",
                    title = "Relatório Trimestral",
                    description = "Resumo das atividades do trimestre",
                    generatedAt = LocalDate.now(),
                    data = mapOf(
                        "tasks_completed" to 330,
                        "points_earned" to 10500,
                        "time_spent" to 250
                    )
                )
            )
        )
    }
    
    private fun createYearData(): MockReportsData {
        return MockReportsData(
            generalSummary = GeneralSummary(
                totalTasks = 1400,
                totalAchievements = 380,
                totalPoints = 42000,
                currentLevel = 25,
                activeTime = 1000,
                balance = 4200.00
            ),
            tasksProgress = TasksProgress(
                completedTasks = 1350,
                pendingTasks = 50,
                overdueTasks = 60,
                completionRate = 0.96f
            ),
            achievements = listOf(
                AchievementReport(
                    id = "1",
                    name = "Lenda",
                    description = "Completou 1000 tarefas em um ano",
                    points = 5000,
                    earnedAt = LocalDate.now().minusDays(180)
                ),
                AchievementReport(
                    id = "2",
                    name = "Mestre Supremo",
                    description = "Atingiu o nível 20",
                    points = 3000,
                    earnedAt = LocalDate.now().minusDays(240)
                )
            ),
            financialActivity = FinancialActivity(
                totalEarnings = 4200.00,
                totalWithdrawals = 1500.00,
                currentBalance = 2700.00,
                totalTransactions = 140
            ),
            activityCharts = ActivityCharts(
                dailyActivity = listOf(4, 5, 4, 6, 5, 4, 5),
                weeklyProgress = listOf(0.96f, 0.98f, 0.94f, 0.97f),
                monthlyTrends = listOf(42000.0, 45000.0, 40000.0, 48000.0)
            ),
            detailedReports = listOf(
                DetailedReport(
                    id = "1",
                    title = "Relatório Anual",
                    description = "Resumo das atividades do ano",
                    generatedAt = LocalDate.now(),
                    data = mapOf(
                        "tasks_completed" to 1350,
                        "points_earned" to 42000,
                        "time_spent" to 1000
                    )
                )
            )
        )
    }
}

data class ReportsUiState(
    val selectedPeriod: ReportPeriod = ReportPeriod.WEEK,
    val generalSummary: GeneralSummary = GeneralSummary(0, 0, 0, 0, 0, 0.0),
    val tasksProgress: TasksProgress = TasksProgress(0, 0, 0, 0.0f),
    val achievements: List<AchievementReport> = emptyList(),
    val financialActivity: FinancialActivity = FinancialActivity(0.0, 0.0, 0.0, 0),
    val activityCharts: ActivityCharts = ActivityCharts(emptyList(), emptyList(), emptyList()),
    val detailedReports: List<DetailedReport> = emptyList(),
    val selectedReportId: String? = null,
    val showExportDialog: Boolean = false,
    val isLoading: Boolean = false,
    val errorMessage: String? = null,
    val exportMessage: String? = null
)

data class MockReportsData(
    val generalSummary: GeneralSummary,
    val tasksProgress: TasksProgress,
    val achievements: List<AchievementReport>,
    val financialActivity: FinancialActivity,
    val activityCharts: ActivityCharts,
    val detailedReports: List<DetailedReport>
) 