package com.tarefamagica.app.presentation.screens.achievements

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
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.tarefamagica.app.presentation.components.AnimatedIcon
import com.tarefamagica.app.presentation.components.SpinningStar

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AchievementsScreen(
    onNavigateBack: () -> Unit,
    viewModel: AchievementsViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    
    Column(
        modifier = Modifier.fillMaxSize()
    ) {
        // Header
        AchievementsHeader(
            totalAchievements = uiState.achievements.size,
            unlockedAchievements = uiState.achievements.count { it.isUnlocked },
            onNavigateBack = onNavigateBack
        )
        
        // Filtros
        AchievementsFilters(
            selectedFilter = uiState.selectedFilter,
            onFilterChange = { viewModel.updateFilter(it) }
        )
        
        // Lista de conquistas
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(horizontal = 16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
            contentPadding = PaddingValues(vertical = 16.dp)
        ) {
            items(
                items = uiState.filteredAchievements,
                key = { it.id }
            ) { achievement ->
                AchievementCard(
                    achievement = achievement,
                    onAchievementClick = { viewModel.selectAchievement(it) }
                )
            }
        }
    }
    
    // Loading overlay
    if (uiState.isLoading) {
        LoadingOverlay()
    }
    
    // Dialog de detalhes da conquista
    uiState.selectedAchievement?.let { achievement ->
        AchievementDetailDialog(
            achievement = achievement,
            onDismiss = { viewModel.clearSelectedAchievement() }
        )
    }
}

@Composable
private fun AchievementsHeader(
    totalAchievements: Int,
    unlockedAchievements: Int,
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
                    text = "Conquistas",
                    style = MaterialTheme.typography.headlineSmall,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.onPrimary
                )
                
                Spacer(modifier = Modifier.width(48.dp))
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Estatísticas
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                AchievementStat(
                    icon = Icons.Default.EmojiEvents,
                    value = unlockedAchievements.toString(),
                    label = "Desbloqueadas",
                    color = Color(0xFFFFD700)
                )
                
                AchievementStat(
                    icon = Icons.Default.Star,
                    value = totalAchievements.toString(),
                    label = "Total",
                    color = MaterialTheme.colorScheme.onPrimary
                )
                
                AchievementStat(
                    icon = Icons.Default.TrendingUp,
                    value = "${((unlockedAchievements.toFloat() / totalAchievements) * 100).toInt()}%",
                    label = "Progresso",
                    color = Color(0xFF4CAF50)
                )
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Barra de progresso
            LinearProgressIndicator(
                progress = if (totalAchievements > 0) unlockedAchievements.toFloat() / totalAchievements else 0f,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(8.dp)
                    .clip(RoundedCornerShape(4.dp)),
                color = Color(0xFFFFD700),
                trackColor = MaterialTheme.colorScheme.onPrimary.copy(alpha = 0.3f)
            )
        }
    }
}

@Composable
private fun AchievementStat(
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    value: String,
    label: String,
    color: Color
) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Icon(
            imageVector = icon,
            contentDescription = null,
            modifier = Modifier.size(24.dp),
            tint = color
        )
        
        Spacer(modifier = Modifier.height(4.dp))
        
        Text(
            text = value,
            style = MaterialTheme.typography.titleLarge,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.onPrimary
        )
        
        Text(
            text = label,
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onPrimary.copy(alpha = 0.8f)
        )
    }
}

@Composable
private fun AchievementsFilters(
    selectedFilter: AchievementFilter,
    onFilterChange: (AchievementFilter) -> Unit
) {
    Surface(
        modifier = Modifier.fillMaxWidth(),
        color = MaterialTheme.colorScheme.surface,
        shadowElevation = 2.dp
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            AchievementFilter.values().forEach { filter ->
                FilterChip(
                    selected = selectedFilter == filter,
                    onClick = { onFilterChange(filter) },
                    label = {
                        Text(
                            text = filter.displayName,
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
private fun AchievementCard(
    achievement: Achievement,
    onAchievementClick: (Achievement) -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = if (achievement.isUnlocked) 
                MaterialTheme.colorScheme.surface 
            else 
                MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f)
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Ícone da conquista
            Surface(
                modifier = Modifier.size(56.dp),
                shape = CircleShape,
                color = if (achievement.isUnlocked) 
                    Color(0xFFFFD700).copy(alpha = 0.2f)
                else 
                    MaterialTheme.colorScheme.outline.copy(alpha = 0.2f)
            ) {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    if (achievement.isUnlocked) {
                        SpinningStar(
                            modifier = Modifier.size(32.dp),
                            tint = Color(0xFFFFD700)
                        )
                    } else {
                        Icon(
                            imageVector = Icons.Default.Lock,
                            contentDescription = null,
                            modifier = Modifier.size(24.dp),
                            tint = MaterialTheme.colorScheme.outline
                        )
                    }
                }
            }
            
            Spacer(modifier = Modifier.width(16.dp))
            
            // Informações da conquista
            Column(
                modifier = Modifier.weight(1f)
            ) {
                Text(
                    text = achievement.title,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = if (achievement.isUnlocked) 
                        MaterialTheme.colorScheme.onSurface
                    else 
                        MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                )
                
                Text(
                    text = achievement.description,
                    style = MaterialTheme.typography.bodyMedium,
                    color = if (achievement.isUnlocked) 
                        MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)
                    else 
                        MaterialTheme.colorScheme.onSurface.copy(alpha = 0.5f)
                )
                
                Spacer(modifier = Modifier.height(8.dp))
                
                Row(
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    // Categoria
                    Surface(
                        color = getCategoryColor(achievement.category).copy(alpha = 0.2f),
                        shape = RoundedCornerShape(12.dp)
                    ) {
                        Text(
                            text = achievement.category.displayName,
                            style = MaterialTheme.typography.labelSmall,
                            color = getCategoryColor(achievement.category),
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                        )
                    }
                    
                    Spacer(modifier = Modifier.width(12.dp))
                    
                    // Pontos
                    Row(
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(
                            imageVector = Icons.Default.Star,
                            contentDescription = null,
                            modifier = Modifier.size(16.dp),
                            tint = Color(0xFFFFD700)
                        )
                        Spacer(modifier = Modifier.width(4.dp))
                        Text(
                            text = "${achievement.points} pts",
                            style = MaterialTheme.typography.labelMedium,
                            color = Color(0xFFFFD700)
                        )
                    }
                }
                
                // Data de desbloqueio
                if (achievement.isUnlocked && achievement.unlockedAt != null) {
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = "Desbloqueada em ${achievement.unlockedAt.format(java.time.format.DateTimeFormatter.ofPattern("dd/MM/yyyy"))}",
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.primary
                    )
                }
            }
            
            // Botão de detalhes
            IconButton(
                onClick = { onAchievementClick(achievement) }
            ) {
                Icon(
                    imageVector = Icons.Default.Info,
                    contentDescription = "Ver detalhes",
                    tint = MaterialTheme.colorScheme.primary
                )
            }
        }
    }
}

@Composable
private fun AchievementDetailDialog(
    achievement: Achievement,
    onDismiss: () -> Unit
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = {
            Text(
                text = achievement.title,
                style = MaterialTheme.typography.headlineSmall,
                fontWeight = FontWeight.Bold
            )
        },
        text = {
            Column {
                if (achievement.isUnlocked) {
                    SpinningStar(
                        modifier = Modifier
                            .size(48.dp)
                            .align(Alignment.CenterHorizontally),
                        tint = Color(0xFFFFD700)
                    )
                    Spacer(modifier = Modifier.height(16.dp))
                }
                
                Text(
                    text = achievement.description,
                    style = MaterialTheme.typography.bodyLarge
                )
                
                Spacer(modifier = Modifier.height(16.dp))
                
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text(
                        text = "Categoria:",
                        style = MaterialTheme.typography.bodyMedium,
                        fontWeight = FontWeight.Medium
                    )
                    Text(
                        text = achievement.category.displayName,
                        style = MaterialTheme.typography.bodyMedium,
                        color = getCategoryColor(achievement.category)
                    )
                }
                
                Spacer(modifier = Modifier.height(8.dp))
                
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text(
                        text = "Pontos:",
                        style = MaterialTheme.typography.bodyMedium,
                        fontWeight = FontWeight.Medium
                    )
                    Text(
                        text = "${achievement.points} pts",
                        style = MaterialTheme.typography.bodyMedium,
                        color = Color(0xFFFFD700),
                        fontWeight = FontWeight.Bold
                    )
                }
                
                if (achievement.isUnlocked && achievement.unlockedAt != null) {
                    Spacer(modifier = Modifier.height(8.dp))
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text(
                            text = "Desbloqueada:",
                            style = MaterialTheme.typography.bodyMedium,
                            fontWeight = FontWeight.Medium
                        )
                        Text(
                            text = achievement.unlockedAt.format(java.time.format.DateTimeFormatter.ofPattern("dd/MM/yyyy 'às' HH:mm")),
                            style = MaterialTheme.typography.bodyMedium
                        )
                    }
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
                    text = "Carregando conquistas...",
                    style = MaterialTheme.typography.bodyMedium
                )
            }
        }
    }
}

private fun getCategoryColor(category: AchievementCategory): Color {
    return when (category) {
        AchievementCategory.TASK_COMPLETION -> Color(0xFF2196F3)
        AchievementCategory.STREAK -> Color(0xFFFF5722)
        AchievementCategory.POINTS -> Color(0xFFFFD700)
        AchievementCategory.SPECIAL -> Color(0xFF9C27B0)
        AchievementCategory.MILESTONE -> Color(0xFF4CAF50)
    }
}

enum class AchievementFilter(val displayName: String) {
    ALL("Todas"),
    UNLOCKED("Desbloqueadas"),
    LOCKED("Bloqueadas"),
    RECENT("Recentes")
}

enum class AchievementCategory(val displayName: String) {
    TASK_COMPLETION("Conclusão de Tarefas"),
    STREAK("Sequência"),
    POINTS("Pontos"),
    SPECIAL("Especial"),
    MILESTONE("Marco")
}

data class Achievement(
    val id: String,
    val title: String,
    val description: String,
    val points: Int,
    val icon: String,
    val isUnlocked: Boolean,
    val unlockedAt: java.time.LocalDateTime?,
    val category: AchievementCategory
) 