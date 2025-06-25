package com.tarefamagica.app.presentation.components

import androidx.compose.animation.*
import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.rotate
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

// ===== COMPONENTES DE GAMIFICAÇÃO =====

@Composable
fun AnimatedProgressBar(
    progress: Float,
    modifier: Modifier = Modifier,
    color: Color = MaterialTheme.colorScheme.primary,
    backgroundColor: Color = MaterialTheme.colorScheme.surfaceVariant
) {
    var animatedProgress by remember { mutableStateOf(0f) }
    
    LaunchedEffect(progress) {
        animate(
            initialValue = animatedProgress,
            targetValue = progress,
            animationSpec = tween(1000, easing = EaseOutCubic)
        ) { value, _ ->
            animatedProgress = value
        }
    }
    
    Box(
        modifier = modifier
            .height(12.dp)
            .clip(RoundedCornerShape(6.dp))
            .background(backgroundColor)
    ) {
        Box(
            modifier = Modifier
                .fillMaxHeight()
                .fillMaxWidth(animatedProgress)
                .clip(RoundedCornerShape(6.dp))
                .background(
                    Brush.horizontalGradient(
                        colors = listOf(
                            color,
                            color.copy(alpha = 0.8f)
                        )
                    )
                )
        )
    }
}

@Composable
fun FloatingPoints(
    points: Int,
    onAnimationComplete: () -> Unit = {}
) {
    var isVisible by remember { mutableStateOf(true) }
    val scope = rememberCoroutineScope()
    
    LaunchedEffect(Unit) {
        delay(2000)
        isVisible = false
        delay(500)
        onAnimationComplete()
    }
    
    AnimatedVisibility(
        visible = isVisible,
        enter = slideInVertically(
            initialOffsetY = { 0 },
            animationSpec = tween(500)
        ) + fadeIn(animationSpec = tween(500)),
        exit = slideOutVertically(
            targetOffsetY = { -100 },
            animationSpec = tween(500)
        ) + fadeOut(animationSpec = tween(500))
    ) {
        Card(
            modifier = Modifier.padding(8.dp),
            colors = CardDefaults.cardColors(
                containerColor = Color(0xFFFFD700)
            ),
            elevation = CardDefaults.cardElevation(defaultElevation = 8.dp)
        ) {
            Row(
                modifier = Modifier.padding(12.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(
                    imageVector = Icons.Default.Star,
                    contentDescription = null,
                    tint = Color.White,
                    modifier = Modifier.size(20.dp)
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = "+$points",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = Color.White
                )
            }
        }
    }
}

@Composable
fun AnimatedLevelUp(
    newLevel: Int,
    onAnimationComplete: () -> Unit = {}
) {
    var isVisible by remember { mutableStateOf(true) }
    val scope = rememberCoroutineScope()
    
    LaunchedEffect(Unit) {
        delay(3000)
        isVisible = false
        delay(500)
        onAnimationComplete()
    }
    
    AnimatedVisibility(
        visible = isVisible,
        enter = scaleIn(
            initialScale = 0.5f,
            animationSpec = tween(500, easing = EaseOutBack)
        ) + fadeIn(animationSpec = tween(500)),
        exit = scaleOut(
            targetScale = 1.2f,
            animationSpec = tween(500)
        ) + fadeOut(animationSpec = tween(500))
    ) {
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            colors = CardDefaults.cardColors(
                containerColor = MaterialTheme.colorScheme.primary
            ),
            elevation = CardDefaults.cardElevation(defaultElevation = 12.dp)
        ) {
            Column(
                modifier = Modifier.padding(24.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                AnimatedIcon(
                    icon = Icons.Default.EmojiEvents,
                    modifier = Modifier.size(64.dp),
                    tint = MaterialTheme.colorScheme.onPrimary
                )
                
                Spacer(modifier = Modifier.height(16.dp))
                
                Text(
                    text = "PARABÉNS!",
                    style = MaterialTheme.typography.headlineSmall,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.onPrimary
                )
                
                Text(
                    text = "Você chegou ao nível $newLevel!",
                    style = MaterialTheme.typography.titleLarge,
                    color = MaterialTheme.colorScheme.onPrimary,
                    textAlign = TextAlign.Center
                )
                
                Spacer(modifier = Modifier.height(8.dp))
                
                Text(
                    text = "Continue assim!",
                    style = MaterialTheme.typography.bodyLarge,
                    color = MaterialTheme.colorScheme.onPrimary.copy(alpha = 0.8f)
                )
            }
        }
    }
}

@Composable
fun AnimatedIcon(
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    modifier: Modifier = Modifier,
    tint: Color = MaterialTheme.colorScheme.primary
) {
    val infiniteTransition = rememberInfiniteTransition()
    val scale by infiniteTransition.animateFloat(
        initialValue = 1f,
        targetValue = 1.1f,
        animationSpec = infiniteRepeatable(
            animation = tween(1000, easing = EaseInOutQuad),
            repeatMode = RepeatMode.Reverse
        )
    )
    
    Icon(
        imageVector = icon,
        contentDescription = null,
        modifier = modifier.scale(scale),
        tint = tint
    )
}

@Composable
fun SpinningStar(
    modifier: Modifier = Modifier,
    tint: Color = Color(0xFFFFD700)
) {
    val infiniteTransition = rememberInfiniteTransition()
    val rotation by infiniteTransition.animateFloat(
        initialValue = 0f,
        targetValue = 360f,
        animationSpec = infiniteRepeatable(
            animation = tween(3000, easing = LinearEasing)
        )
    )
    
    Icon(
        imageVector = Icons.Default.Star,
        contentDescription = null,
        modifier = modifier.rotate(rotation),
        tint = tint
    )
}

@Composable
fun AchievementUnlocked(
    achievement: Achievement,
    onAnimationComplete: () -> Unit = {}
) {
    var isVisible by remember { mutableStateOf(true) }
    
    LaunchedEffect(Unit) {
        delay(2500)
        isVisible = false
        delay(500)
        onAnimationComplete()
    }
    
    AnimatedVisibility(
        visible = isVisible,
        enter = slideInHorizontally(
            initialOffsetX = { 300 },
            animationSpec = tween(500, easing = EaseOutCubic)
        ) + fadeIn(animationSpec = tween(500)),
        exit = slideOutHorizontally(
            targetOffsetX = { 300 },
            animationSpec = tween(500, easing = EaseInCubic)
        ) + fadeOut(animationSpec = tween(500))
    ) {
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            colors = CardDefaults.cardColors(
                containerColor = Color(0xFFFFD700)
            ),
            elevation = CardDefaults.cardElevation(defaultElevation = 8.dp)
        ) {
            Row(
                modifier = Modifier.padding(16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                SpinningStar(
                    modifier = Modifier.size(32.dp),
                    tint = Color.White
                )
                
                Spacer(modifier = Modifier.width(12.dp))
                
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = "Conquista Desbloqueada!",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                        color = Color.White
                    )
                    
                    Text(
                        text = achievement.title,
                        style = MaterialTheme.typography.bodyMedium,
                        color = Color.White.copy(alpha = 0.9f)
                    )
                    
                    Text(
                        text = "+${achievement.points} pontos",
                        style = MaterialTheme.typography.labelMedium,
                        color = Color.White.copy(alpha = 0.8f)
                    )
                }
            }
        }
    }
}

@Composable
fun StreakCounter(
    streak: Int,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier,
        colors = CardDefaults.cardColors(
            containerColor = if (streak > 0) Color(0xFFFF5722) else MaterialTheme.colorScheme.surfaceVariant
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
    ) {
        Row(
            modifier = Modifier.padding(12.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            AnimatedIcon(
                icon = Icons.Default.LocalFireDepartment,
                modifier = Modifier.size(24.dp),
                tint = if (streak > 0) Color.White else MaterialTheme.colorScheme.onSurfaceVariant
            )
            
            Spacer(modifier = Modifier.width(8.dp))
            
            Text(
                text = "$streak dias",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                color = if (streak > 0) Color.White else MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

@Composable
fun CategoryBadge(
    category: TaskCategory,
    modifier: Modifier = Modifier
) {
    val categoryColor = when (category) {
        TaskCategory.SCHOOL -> Color(0xFF2196F3)
        TaskCategory.HOME -> Color(0xFF4CAF50)
        TaskCategory.PERSONAL -> Color(0xFF9C27B0)
        TaskCategory.HEALTH -> Color(0xFFFF5722)
        TaskCategory.FUN -> Color(0xFFFF9800)
    }
    
    Surface(
        modifier = modifier,
        color = categoryColor.copy(alpha = 0.2f),
        shape = RoundedCornerShape(12.dp)
    ) {
        Text(
            text = category.displayName,
            style = MaterialTheme.typography.labelSmall,
            color = categoryColor,
            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
        )
    }
}

@Composable
fun PointsDisplay(
    points: Int,
    modifier: Modifier = Modifier,
    showIcon: Boolean = true
) {
    Row(
        modifier = modifier,
        verticalAlignment = Alignment.CenterVertically
    ) {
        if (showIcon) {
            Icon(
                imageVector = Icons.Default.Star,
                contentDescription = null,
                modifier = Modifier.size(16.dp),
                tint = Color(0xFFFFD700)
            )
            Spacer(modifier = Modifier.width(4.dp))
        }
        
        Text(
            text = "$points pts",
            style = MaterialTheme.typography.labelMedium,
            fontWeight = FontWeight.Bold,
            color = Color(0xFFFFD700)
        )
    }
}

@Composable
fun LevelDisplay(
    level: Int,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier,
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.primary
        ),
        shape = CircleShape
    ) {
        Box(
            modifier = Modifier
                .size(40.dp),
            contentAlignment = Alignment.Center
        ) {
            Text(
                text = level.toString(),
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onPrimary
            )
        }
    }
}

// ===== MODELOS DE SUPORTE =====

data class Achievement(
    val id: String,
    val title: String,
    val description: String,
    val points: Int,
    val icon: String
)

enum class TaskCategory(val displayName: String) {
    SCHOOL("Escola"),
    HOME("Casa"),
    PERSONAL("Pessoal"),
    HEALTH("Saúde"),
    FUN("Diversão")
} 