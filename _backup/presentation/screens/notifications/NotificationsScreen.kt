package com.tarefamagica.app.presentation.screens.notifications

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
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun NotificationsScreen(
    onNavigateBack: () -> Unit,
    viewModel: NotificationsViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    
    Column(
        modifier = Modifier.fillMaxSize()
    ) {
        // Header
        NotificationsHeader(
            unreadCount = uiState.unreadCount,
            onNavigateBack = onNavigateBack,
            onClearAll = { viewModel.clearAllNotifications() }
        )
        
        // Tabs
        NotificationsTabs(
            selectedTab = uiState.selectedTab,
            onTabChange = { viewModel.updateSelectedTab(it) }
        )
        
        // Conteúdo baseado na tab
        when (uiState.selectedTab) {
            NotificationsTab.ALL -> {
                NotificationsList(
                    notifications = uiState.notifications,
                    onNotificationClick = { viewModel.markAsRead(it) },
                    onNotificationDelete = { viewModel.deleteNotification(it) }
                )
            }
            NotificationsTab.UNREAD -> {
                NotificationsList(
                    notifications = uiState.unreadNotifications,
                    onNotificationClick = { viewModel.markAsRead(it) },
                    onNotificationDelete = { viewModel.deleteNotification(it) }
                )
            }
            NotificationsTab.SETTINGS -> {
                NotificationSettings(
                    preferences = uiState.preferences,
                    onPreferenceChange = { viewModel.updatePreference(it) },
                    onSavePreferences = { viewModel.savePreferences() }
                )
            }
        }
    }
    
    // Loading overlay
    if (uiState.isLoading) {
        LoadingOverlay()
    }
}

@Composable
private fun NotificationsHeader(
    unreadCount: Int,
    onNavigateBack: () -> Unit,
    onClearAll: () -> Unit
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
            
            Column(
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Text(
                    text = "Notificações",
                    style = MaterialTheme.typography.headlineSmall,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.onPrimary
                )
                
                if (unreadCount > 0) {
                    Text(
                        text = "$unreadCount não lidas",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onPrimary.copy(alpha = 0.8f)
                    )
                }
            }
            
            IconButton(onClick = onClearAll) {
                Icon(
                    imageVector = Icons.Default.ClearAll,
                    contentDescription = "Limpar todas",
                    tint = MaterialTheme.colorScheme.onPrimary
                )
            }
        }
    }
}

@Composable
private fun NotificationsTabs(
    selectedTab: NotificationsTab,
    onTabChange: (NotificationsTab) -> Unit
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
            NotificationsTab.values().forEach { tab ->
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
private fun NotificationsList(
    notifications: List<NotificationData>,
    onNotificationClick: (NotificationData) -> Unit,
    onNotificationDelete: (NotificationData) -> Unit
) {
    if (notifications.isEmpty()) {
        EmptyNotificationsState()
    } else {
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            items(
                items = notifications,
                key = { it.id }
            ) { notification ->
                NotificationCard(
                    notification = notification,
                    onNotificationClick = onNotificationClick,
                    onNotificationDelete = onNotificationDelete
                )
            }
        }
    }
}

@Composable
private fun NotificationCard(
    notification: NotificationData,
    onNotificationClick: (NotificationData) -> Unit,
    onNotificationDelete: (NotificationData) -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = if (notification.isRead) {
                MaterialTheme.colorScheme.surface
            } else {
                MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.1f)
            }
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.Top
        ) {
            // Ícone da notificação
            Surface(
                modifier = Modifier.size(40.dp),
                shape = CircleShape,
                color = getNotificationColor(notification.type).copy(alpha = 0.2f)
            ) {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        imageVector = getNotificationIcon(notification.type),
                        contentDescription = null,
                        modifier = Modifier.size(20.dp),
                        tint = getNotificationColor(notification.type)
                    )
                }
            }
            
            Spacer(modifier = Modifier.width(12.dp))
            
            // Conteúdo da notificação
            Column(
                modifier = Modifier.weight(1f)
            ) {
                Text(
                    text = notification.title,
                    style = MaterialTheme.typography.titleSmall,
                    fontWeight = if (notification.isRead) FontWeight.Normal else FontWeight.Bold,
                    color = MaterialTheme.colorScheme.onSurface
                )
                
                Spacer(modifier = Modifier.height(4.dp))
                
                Text(
                    text = notification.body,
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f),
                    maxLines = 2,
                    overflow = TextOverflow.Ellipsis
                )
                
                Spacer(modifier = Modifier.height(8.dp))
                
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = notification.createdAt.format(DateTimeFormatter.ofPattern("dd/MM HH:mm")),
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                    )
                    
                    Row {
                        if (!notification.isRead) {
                            Surface(
                                modifier = Modifier.size(8.dp),
                                shape = CircleShape,
                                color = MaterialTheme.colorScheme.primary
                            ) {}
                            Spacer(modifier = Modifier.width(8.dp))
                        }
                        
                        IconButton(
                            onClick = { onNotificationDelete(notification) },
                            modifier = Modifier.size(24.dp)
                        ) {
                            Icon(
                                imageVector = Icons.Default.Delete,
                                contentDescription = "Deletar",
                                modifier = Modifier.size(16.dp),
                                tint = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                            )
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun EmptyNotificationsState() {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .padding(32.dp),
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Icon(
                imageVector = Icons.Default.NotificationsNone,
                contentDescription = null,
                modifier = Modifier.size(64.dp),
                tint = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.4f)
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            Text(
                text = "Nenhuma notificação",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Medium,
                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
            )
            
            Text(
                text = "Você receberá notificações sobre suas tarefas e conquistas aqui",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.4f),
                textAlign = androidx.compose.ui.text.style.TextAlign.Center
            )
        }
    }
}

@Composable
private fun NotificationSettings(
    preferences: NotificationPreferences,
    onPreferenceChange: (NotificationPreferences) -> Unit,
    onSavePreferences: () -> Unit
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
                        text = "Preferências de Notificação",
                        style = MaterialTheme.typography.titleLarge,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.onSurface
                    )
                    
                    Spacer(modifier = Modifier.height(16.dp))
                    
                    // Push notifications
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(
                            imageVector = Icons.Default.Notifications,
                            contentDescription = null,
                            tint = MaterialTheme.colorScheme.primary
                        )
                        Spacer(modifier = Modifier.width(12.dp))
                        Text(
                            text = "Notificações Push",
                            style = MaterialTheme.typography.titleSmall,
                            modifier = Modifier.weight(1f)
                        )
                        Switch(
                            checked = preferences.pushNotifications,
                            onCheckedChange = { 
                                onPreferenceChange(preferences.copy(pushNotifications = it))
                            }
                        )
                    }
                    
                    Spacer(modifier = Modifier.height(12.dp))
                    
                    // Email notifications
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(
                            imageVector = Icons.Default.Email,
                            contentDescription = null,
                            tint = MaterialTheme.colorScheme.primary
                        )
                        Spacer(modifier = Modifier.width(12.dp))
                        Text(
                            text = "Notificações por E-mail",
                            style = MaterialTheme.typography.titleSmall,
                            modifier = Modifier.weight(1f)
                        )
                        Switch(
                            checked = preferences.emailNotifications,
                            onCheckedChange = { 
                                onPreferenceChange(preferences.copy(emailNotifications = it))
                            }
                        )
                    }
                    
                    Spacer(modifier = Modifier.height(12.dp))
                    
                    // Task notifications
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(
                            imageVector = Icons.Default.Task,
                            contentDescription = null,
                            tint = MaterialTheme.colorScheme.primary
                        )
                        Spacer(modifier = Modifier.width(12.dp))
                        Text(
                            text = "Notificações de Tarefas",
                            style = MaterialTheme.typography.titleSmall,
                            modifier = Modifier.weight(1f)
                        )
                        Switch(
                            checked = preferences.taskNotifications,
                            onCheckedChange = { 
                                onPreferenceChange(preferences.copy(taskNotifications = it))
                            }
                        )
                    }
                    
                    Spacer(modifier = Modifier.height(12.dp))
                    
                    // Achievement notifications
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(
                            imageVector = Icons.Default.Star,
                            contentDescription = null,
                            tint = MaterialTheme.colorScheme.primary
                        )
                        Spacer(modifier = Modifier.width(12.dp))
                        Text(
                            text = "Notificações de Conquistas",
                            style = MaterialTheme.typography.titleSmall,
                            modifier = Modifier.weight(1f)
                        )
                        Switch(
                            checked = preferences.achievementNotifications,
                            onCheckedChange = { 
                                onPreferenceChange(preferences.copy(achievementNotifications = it))
                            }
                        )
                    }
                    
                    Spacer(modifier = Modifier.height(12.dp))
                    
                    // Reward notifications
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(
                            imageVector = Icons.Default.AccountBalanceWallet,
                            contentDescription = null,
                            tint = MaterialTheme.colorScheme.primary
                        )
                        Spacer(modifier = Modifier.width(12.dp))
                        Text(
                            text = "Notificações de Recompensas",
                            style = MaterialTheme.typography.titleSmall,
                            modifier = Modifier.weight(1f)
                        )
                        Switch(
                            checked = preferences.rewardNotifications,
                            onCheckedChange = { 
                                onPreferenceChange(preferences.copy(rewardNotifications = it))
                            }
                        )
                    }
                    
                    Spacer(modifier = Modifier.height(24.dp))
                    
                    // Botão salvar
                    Button(
                        onClick = onSavePreferences,
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(56.dp),
                        shape = RoundedCornerShape(16.dp),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = MaterialTheme.colorScheme.primary
                        )
                    ) {
                        Icon(
                            imageVector = Icons.Default.Save,
                            contentDescription = null,
                            modifier = Modifier.size(20.dp)
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            text = "Salvar Preferências",
                            style = MaterialTheme.typography.labelLarge
                        )
                    }
                }
            }
        }
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
                    text = "Carregando...",
                    style = MaterialTheme.typography.bodyMedium
                )
            }
        }
    }
}

private fun getNotificationColor(type: String): Color {
    return when (type) {
        "task" -> Color(0xFF2196F3)
        "achievement" -> Color(0xFFFF9800)
        "reward" -> Color(0xFF4CAF50)
        "security" -> Color(0xFFFF5722)
        else -> Color(0xFF9E9E9E)
    }
}

private fun getNotificationIcon(type: String): androidx.compose.ui.graphics.vector.ImageVector {
    return when (type) {
        "task" -> Icons.Default.Task
        "achievement" -> Icons.Default.Star
        "reward" -> Icons.Default.AccountBalanceWallet
        "security" -> Icons.Default.Security
        else -> Icons.Default.Notifications
    }
}

enum class NotificationsTab(val displayName: String) {
    ALL("Todas"),
    UNREAD("Não lidas"),
    SETTINGS("Configurações")
}

data class NotificationData(
    val id: String,
    val title: String,
    val body: String,
    val type: String,
    val userId: String?,
    val createdAt: LocalDateTime,
    val isRead: Boolean,
    val readAt: LocalDateTime?
)

data class NotificationPreferences(
    val pushNotifications: Boolean = true,
    val emailNotifications: Boolean = true,
    val taskNotifications: Boolean = true,
    val achievementNotifications: Boolean = true,
    val rewardNotifications: Boolean = true
) 