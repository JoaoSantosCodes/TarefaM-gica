package com.tarefamagica.app.presentation.screens.levels

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
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
import com.tarefamagica.app.presentation.components.AnimatedProgressBar

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun LevelsScreen(
    onNavigateBack: () -> Unit,
    viewModel: LevelsViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    
    Column(
        modifier = Modifier.fillMaxSize()
    ) {
        // Header com nível atual
        LevelsHeader(
            currentLevel = uiState.currentLevel,
            currentExperience = uiState.currentExperience,
            experienceToNextLevel = uiState.experienceToNextLevel,
            experienceProgress = uiState.experienceProgress,
            onNavigateBack = onNavigateBack
        )
        
        // Lista de níveis
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(horizontal = 16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
            contentPadding = PaddingValues(vertical = 16.dp)
        ) {
            items(
                items = uiState.levels,
                key = { it.level }
            ) { levelData ->
                LevelCard(
                    levelData = levelData,
                    currentLevel = uiState.currentLevel,
                    onLevelClick = { viewModel.selectLevel(it) }
                )
            }
        }
    }
    
    // Loading overlay
    if (uiState.isLoading) {
        LoadingOverlay()
    }
    
    // Dialog de detalhes do nível
    uiState.selectedLevel?.let { level ->
        LevelDetailDialog(
            level = level,
            onDismiss = { viewModel.clearSelectedLevel() }
        )
    }
}

@Composable
private fun LevelsHeader(
    currentLevel: Int,
    currentExperience: Int,
    experienceToNextLevel: Int,
    experienceProgress: Float,
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
                    text = "Níveis",
                    style = MaterialTheme.typography.headlineSmall,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.onPrimary
                )
                
                Spacer(modifier = Modifier.width(48.dp))
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Nível atual
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.Center,
                verticalAlignment = Alignment.CenterVertically
            ) {
                // Badge do nível
                Surface(
                    modifier = Modifier.size(80.dp),
                    shape = CircleShape,
                    color = MaterialTheme.colorScheme.secondary
                ) {
                    Box(
                        modifier = Modifier.fillMaxSize(),
                        contentAlignment = Alignment.Center
                    ) {
                        Text(
                            text = currentLevel.toString(),
                            style = MaterialTheme.typography.headlineMedium,
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.onSecondary
                        )
                    }
                }
                
                Spacer(modifier = Modifier.width(16.dp))
                
                Column {
                    Text(
                        text = getLevelTitle(currentLevel),
                        style = MaterialTheme.typography.titleLarge,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.onPrimary
                    )
                    
                    Text(
                        text = "Nível $currentLevel",
                        style = MaterialTheme.typography.bodyLarge,
                        color = MaterialTheme.colorScheme.onPrimary.copy(alpha = 0.8f)
                    )
                }
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Progresso de experiência
            Column {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text(
                        text = "Experiência",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onPrimary
                    )
                    
                    Text(
                        text = "$currentExperience / $experienceToNextLevel XP",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onPrimary
                    )
                }
                
                Spacer(modifier = Modifier.height(8.dp))
                
                AnimatedProgressBar(
                    progress = experienceProgress,
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(12.dp),
                    color = MaterialTheme.colorScheme.secondary,
                    backgroundColor = MaterialTheme.colorScheme.onPrimary.copy(alpha = 0.3f)
                )
            }
        }
    }
}

@Composable
private fun LevelCard(
    levelData: LevelData,
    currentLevel: Int,
    onLevelClick: (LevelData) -> Unit
) {
    val isUnlocked = levelData.level <= currentLevel
    val isCurrentLevel = levelData.level == currentLevel
    
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = when {
                isCurrentLevel -> MaterialTheme.colorScheme.primary.copy(alpha = 0.1f)
                isUnlocked -> MaterialTheme.colorScheme.surface
                else -> MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f)
            }
        ),
        elevation = CardDefaults.cardElevation(
            defaultElevation = if (isCurrentLevel) 4.dp else 2.dp
        )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Badge do nível
            Surface(
                modifier = Modifier.size(56.dp),
                shape = CircleShape,
                color = when {
                    isCurrentLevel -> MaterialTheme.colorScheme.primary
                    isUnlocked -> MaterialTheme.colorScheme.secondary
                    else -> MaterialTheme.colorScheme.outline.copy(alpha = 0.3f)
                }
            ) {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    if (isUnlocked) {
                        Text(
                            text = levelData.level.toString(),
                            style = MaterialTheme.typography.titleLarge,
                            fontWeight = FontWeight.Bold,
                            color = if (isCurrentLevel) 
                                MaterialTheme.colorScheme.onPrimary 
                            else 
                                MaterialTheme.colorScheme.onSecondary
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
            
            // Informações do nível
            Column(
                modifier = Modifier.weight(1f)
            ) {
                Text(
                    text = getLevelTitle(levelData.level),
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = if (isUnlocked) 
                        MaterialTheme.colorScheme.onSurface
                    else 
                        MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                )
                
                Text(
                    text = "Nível ${levelData.level}",
                    style = MaterialTheme.typography.bodyMedium,
                    color = if (isUnlocked) 
                        MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)
                    else 
                        MaterialTheme.colorScheme.onSurface.copy(alpha = 0.5f)
                )
                
                Spacer(modifier = Modifier.height(8.dp))
                
                // Recompensas
                Row(
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        imageVector = Icons.Default.CardGiftcard,
                        contentDescription = null,
                        modifier = Modifier.size(16.dp),
                        tint = Color(0xFFFFD700)
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Text(
                        text = levelData.rewards.joinToString(", "),
                        style = MaterialTheme.typography.bodySmall,
                        color = Color(0xFFFFD700)
                    )
                }
                
                // Experiência necessária
                if (!isUnlocked) {
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = "${levelData.experienceRequired} XP necessários",
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.primary
                    )
                }
            }
            
            // Status do nível
            Column(
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                when {
                    isCurrentLevel -> {
                        Surface(
                            color = MaterialTheme.colorScheme.primary,
                            shape = RoundedCornerShape(12.dp)
                        ) {
                            Text(
                                text = "ATUAL",
                                style = MaterialTheme.typography.labelSmall,
                                color = MaterialTheme.colorScheme.onPrimary,
                                modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                            )
                        }
                    }
                    isUnlocked -> {
                        Icon(
                            imageVector = Icons.Default.CheckCircle,
                            contentDescription = null,
                            modifier = Modifier.size(24.dp),
                            tint = Color(0xFF4CAF50)
                        )
                    }
                    else -> {
                        Icon(
                            imageVector = Icons.Default.Lock,
                            contentDescription = null,
                            modifier = Modifier.size(24.dp),
                            tint = MaterialTheme.colorScheme.outline
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun LevelDetailDialog(
    level: LevelData,
    onDismiss: () -> Unit
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = {
            Text(
                text = "Nível ${level.level} - ${getLevelTitle(level.level)}",
                style = MaterialTheme.typography.headlineSmall,
                fontWeight = FontWeight.Bold
            )
        },
        text = {
            Column {
                // Badge do nível
                Surface(
                    modifier = Modifier
                        .size(64.dp)
                        .align(Alignment.CenterHorizontally),
                    shape = CircleShape,
                    color = MaterialTheme.colorScheme.primary
                ) {
                    Box(
                        modifier = Modifier.fillMaxSize(),
                        contentAlignment = Alignment.Center
                    ) {
                        Text(
                            text = level.level.toString(),
                            style = MaterialTheme.typography.headlineMedium,
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.onPrimary
                        )
                    }
                }
                
                Spacer(modifier = Modifier.height(16.dp))
                
                // Descrição
                Text(
                    text = getLevelDescription(level.level),
                    style = MaterialTheme.typography.bodyLarge,
                    textAlign = TextAlign.Center
                )
                
                Spacer(modifier = Modifier.height(16.dp))
                
                // Recompensas
                Text(
                    text = "Recompensas:",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
                
                Spacer(modifier = Modifier.height(8.dp))
                
                level.rewards.forEach { reward ->
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(
                            imageVector = Icons.Default.CardGiftcard,
                            contentDescription = null,
                            modifier = Modifier.size(20.dp),
                            tint = Color(0xFFFFD700)
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            text = reward,
                            style = MaterialTheme.typography.bodyMedium
                        )
                    }
                    Spacer(modifier = Modifier.height(4.dp))
                }
                
                Spacer(modifier = Modifier.height(16.dp))
                
                // Experiência necessária
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text(
                        text = "Experiência necessária:",
                        style = MaterialTheme.typography.bodyMedium,
                        fontWeight = FontWeight.Medium
                    )
                    Text(
                        text = "${level.experienceRequired} XP",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.primary,
                        fontWeight = FontWeight.Bold
                    )
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
                    text = "Carregando níveis...",
                    style = MaterialTheme.typography.bodyMedium
                )
            }
        }
    }
}

private fun getLevelTitle(level: Int): String {
    return when {
        level <= 5 -> "Iniciante"
        level <= 10 -> "Aprendiz"
        level <= 15 -> "Intermediário"
        level <= 20 -> "Avançado"
        level <= 25 -> "Expert"
        level <= 30 -> "Mestre"
        level <= 40 -> "Lenda"
        else -> "Deus"
    }
}

private fun getLevelDescription(level: Int): String {
    return when {
        level <= 5 -> "Você está começando sua jornada mágica. Cada tarefa te aproxima de grandes conquistas!"
        level <= 10 -> "Você já aprendeu o básico. Continue assim para se tornar um verdadeiro mestre!"
        level <= 15 -> "Você está no caminho certo! Sua dedicação está sendo recompensada."
        level <= 20 -> "Você é um organizador experiente! Suas habilidades são impressionantes."
        level <= 25 -> "Você é um expert! Poucos conseguem chegar tão longe."
        level <= 30 -> "Você é um mestre! Sua sabedoria é reconhecida por todos."
        level <= 40 -> "Você é uma lenda! Suas conquistas são históricas."
        else -> "Você é um deus da organização! Nada é impossível para você!"
    }
}

data class LevelData(
    val level: Int,
    val experienceRequired: Int,
    val rewards: List<String>,
    val isUnlocked: Boolean = false
) 