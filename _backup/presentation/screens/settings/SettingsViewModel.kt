package com.tarefamagica.app.presentation.screens.settings

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class SettingsViewModel @Inject constructor() : ViewModel() {
    private val _uiState = MutableStateFlow(SettingsUiState())
    val uiState: StateFlow<SettingsUiState> = _uiState.asStateFlow()

    fun toggleDarkTheme() {
        _uiState.update { it.copy(darkTheme = !it.darkTheme) }
    }

    fun showLanguageDialog() {
        _uiState.update { it.copy(showLanguageDialog = true) }
    }
    fun hideLanguageDialog() {
        _uiState.update { it.copy(showLanguageDialog = false) }
    }
    fun setLanguage(language: String) {
        _uiState.update { it.copy(language = language, showLanguageDialog = false) }
    }

    fun toggleBiometric() {
        _uiState.update { it.copy(biometricEnabled = !it.biometricEnabled) }
    }
    fun toggleTwoFactor() {
        _uiState.update { it.copy(twoFactorEnabled = !it.twoFactorEnabled) }
    }
    fun togglePushNotifications() {
        _uiState.update { it.copy(pushNotifications = !it.pushNotifications) }
    }

    fun showDeleteDialog() {
        _uiState.update { it.copy(showDeleteDialog = true) }
    }
    fun hideDeleteDialog() {
        _uiState.update { it.copy(showDeleteDialog = false) }
    }
    fun confirmDeleteAccount() {
        // Lógica de exclusão de conta
        _uiState.update { it.copy(showDeleteDialog = false) }
    }

    fun exportUserData() {
        _uiState.update { it.copy(showExportDialog = true) }
    }
    fun hideExportDialog() {
        _uiState.update { it.copy(showExportDialog = false) }
    }
    fun confirmExportUserData() {
        // Lógica de exportação de dados
        _uiState.update { it.copy(showExportDialog = false) }
    }

    fun logout() {
        // Lógica de logout
    }
} 