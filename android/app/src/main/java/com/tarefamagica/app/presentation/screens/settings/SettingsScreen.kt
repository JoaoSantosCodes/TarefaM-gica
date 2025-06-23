package com.tarefamagica.app.presentation.screens.settings

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
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SettingsScreen(
    onNavigateBack: () -> Unit,
    viewModel: SettingsViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()

    Column(
        modifier = Modifier.fillMaxSize()
    ) {
        // Header
        SettingsHeader(onNavigateBack = onNavigateBack)

        // Preferências
        SettingsSection(title = "Preferências") {
            SettingsItem(
                icon = Icons.Default.Palette,
                label = "Tema Escuro",
                checked = uiState.darkTheme,
                onCheckedChange = { viewModel.toggleDarkTheme() }
            )
            SettingsItem(
                icon = Icons.Default.Language,
                label = "Idioma: ${uiState.language}",
                checked = false,
                onCheckedChange = null,
                onClick = { viewModel.showLanguageDialog() }
            )
        }

        // Segurança
        SettingsSection(title = "Segurança") {
            SettingsItem(
                icon = Icons.Default.Fingerprint,
                label = "Biometria",
                checked = uiState.biometricEnabled,
                onCheckedChange = { viewModel.toggleBiometric() }
            )
            SettingsItem(
                icon = Icons.Default.Security,
                label = "Autenticação em 2 Fatores",
                checked = uiState.twoFactorEnabled,
                onCheckedChange = { viewModel.toggleTwoFactor() }
            )
            SettingsItem(
                icon = Icons.Default.Notifications,
                label = "Notificações Push",
                checked = uiState.pushNotifications,
                onCheckedChange = { viewModel.togglePushNotifications() }
            )
        }

        // Conta
        SettingsSection(title = "Conta") {
            SettingsItem(
                icon = Icons.Default.Download,
                label = "Exportar Dados",
                checked = false,
                onCheckedChange = null,
                onClick = { viewModel.exportUserData() }
            )
            SettingsItem(
                icon = Icons.Default.Delete,
                label = "Excluir Conta",
                checked = false,
                onCheckedChange = null,
                onClick = { viewModel.showDeleteDialog() },
                color = Color.Red
            )
            SettingsItem(
                icon = Icons.Default.Logout,
                label = "Sair",
                checked = false,
                onCheckedChange = null,
                onClick = { viewModel.logout() }
            )
        }
    }

    // Dialogs
    if (uiState.showLanguageDialog) {
        LanguageDialog(
            selectedLanguage = uiState.language,
            onSelect = { viewModel.setLanguage(it) },
            onDismiss = { viewModel.hideLanguageDialog() }
        )
    }
    if (uiState.showDeleteDialog) {
        DeleteAccountDialog(
            onConfirm = { viewModel.confirmDeleteAccount() },
            onDismiss = { viewModel.hideDeleteDialog() }
        )
    }
    if (uiState.showExportDialog) {
        ExportDataDialog(
            onConfirm = { viewModel.confirmExportUserData() },
            onDismiss = { viewModel.hideExportDialog() }
        )
    }
}

@Composable
private fun SettingsHeader(onNavigateBack: () -> Unit) {
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
                text = "Configurações",
                style = MaterialTheme.typography.headlineSmall,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onPrimary
            )
            Spacer(modifier = Modifier.width(48.dp))
        }
    }
}

@Composable
private fun SettingsSection(title: String, content: @Composable ColumnScope.() -> Unit) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 12.dp, horizontal = 16.dp)
    ) {
        Text(
            text = title,
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.primary
        )
        Spacer(modifier = Modifier.height(8.dp))
        content()
    }
}

@Composable
private fun SettingsItem(
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    label: String,
    checked: Boolean,
    onCheckedChange: ((Boolean) -> Unit)? = null,
    onClick: (() -> Unit)? = null,
    color: Color = MaterialTheme.colorScheme.onSurface
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .background(MaterialTheme.colorScheme.surfaceVariant)
            .padding(12.dp)
            .let { if (onClick != null) it.clickable { onClick() } else it },
        verticalAlignment = Alignment.CenterVertically
    ) {
        Surface(
            modifier = Modifier.size(32.dp),
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
                    modifier = Modifier.size(18.dp),
                    tint = color
                )
            }
        }
        Spacer(modifier = Modifier.width(12.dp))
        Text(
            text = label,
            style = MaterialTheme.typography.bodyLarge,
            color = color,
            modifier = Modifier.weight(1f)
        )
        if (onCheckedChange != null) {
            Switch(
                checked = checked,
                onCheckedChange = onCheckedChange
            )
        }
    }
}

@Composable
private fun LanguageDialog(selectedLanguage: String, onSelect: (String) -> Unit, onDismiss: () -> Unit) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Escolher idioma") },
        text = {
            Column {
                listOf("Português", "English", "Español").forEach { lang ->
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(vertical = 8.dp)
                            .clip(RoundedCornerShape(8.dp))
                            .background(if (selectedLanguage == lang) MaterialTheme.colorScheme.primary.copy(alpha = 0.1f) else Color.Transparent)
                            .clickable { onSelect(lang) },
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        RadioButton(
                            selected = selectedLanguage == lang,
                            onClick = { onSelect(lang) }
                        )
                        Text(
                            text = lang,
                            style = MaterialTheme.typography.bodyLarge,
                            modifier = Modifier.padding(start = 8.dp)
                        )
                    }
                }
            }
        },
        confirmButton = {
            TextButton(onClick = onDismiss) { Text("Fechar") }
        }
    )
}

@Composable
private fun DeleteAccountDialog(onConfirm: () -> Unit, onDismiss: () -> Unit) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Excluir Conta") },
        text = { Text("Tem certeza que deseja excluir sua conta? Esta ação não pode ser desfeita.") },
        confirmButton = {
            TextButton(onClick = onConfirm) { Text("Excluir", color = Color.Red) }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) { Text("Cancelar") }
        }
    )
}

@Composable
private fun ExportDataDialog(onConfirm: () -> Unit, onDismiss: () -> Unit) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Exportar Dados") },
        text = { Text("Deseja exportar todos os seus dados em formato seguro?") },
        confirmButton = {
            TextButton(onClick = onConfirm) { Text("Exportar") }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) { Text("Cancelar") }
        }
    )
}

data class SettingsUiState(
    val darkTheme: Boolean = false,
    val language: String = "Português",
    val biometricEnabled: Boolean = false,
    val twoFactorEnabled: Boolean = false,
    val pushNotifications: Boolean = true,
    val showLanguageDialog: Boolean = false,
    val showDeleteDialog: Boolean = false,
    val showExportDialog: Boolean = false
) 