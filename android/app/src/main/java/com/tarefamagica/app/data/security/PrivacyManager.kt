package com.tarefamagica.app.data.security

import android.content.Context
import android.content.SharedPreferences
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class PrivacyManager @Inject constructor(
    private val context: Context,
    private val dataProtection: DataProtection
) {
    
    private val prefs: SharedPreferences = context.getSharedPreferences(
        "privacy_prefs",
        Context.MODE_PRIVATE
    )
    
    private val gson = Gson()
    
    fun setPrivacySettings(settings: PrivacySettings) {
        val encryptedSettings = dataProtection.encryptData(gson.toJson(settings))
        prefs.edit()
            .putString("privacy_settings", gson.toJson(encryptedSettings))
            .apply()
    }
    
    fun getPrivacySettings(): PrivacySettings {
        val encryptedJson = prefs.getString("privacy_settings", null)
        return if (encryptedJson != null) {
            val encryptedSettings = gson.fromJson(encryptedJson, EncryptedData::class.java)
            val decryptedJson = dataProtection.decryptData(encryptedSettings)
            gson.fromJson(decryptedJson, PrivacySettings::class.java)
        } else {
            PrivacySettings() // Default settings
        }
    }
    
    fun logDataAccess(access: DataAccessLog) {
        val logs = getDataAccessLogs().toMutableList()
        logs.add(access)
        
        // Manter apenas os últimos 100 logs
        if (logs.size > 100) {
            logs.removeAt(0)
        }
        
        val encryptedLogs = dataProtection.encryptData(gson.toJson(logs))
        prefs.edit()
            .putString("data_access_logs", gson.toJson(encryptedLogs))
            .apply()
    }
    
    fun getDataAccessLogs(): List<DataAccessLog> {
        val encryptedJson = prefs.getString("data_access_logs", null)
        return if (encryptedJson != null) {
            val encryptedLogs = gson.fromJson(encryptedJson, EncryptedData::class.java)
            val decryptedJson = dataProtection.decryptData(encryptedLogs)
            val type = object : TypeToken<List<DataAccessLog>>() {}.type
            gson.fromJson(decryptedJson, type)
        } else {
            emptyList()
        }
    }
    
    fun exportUserData(userId: String): UserDataExport {
        val export = UserDataExport(
            userId = userId,
            exportDate = LocalDateTime.now(),
            privacySettings = getPrivacySettings(),
            dataAccessLogs = getDataAccessLogs(),
            dataRetentionPolicy = getDataRetentionPolicy()
        )
        
        val encryptedExport = dataProtection.encryptData(gson.toJson(export))
        val backupFile = dataProtection.createSecureBackup(
            gson.toJson(encryptedExport),
            "user_data_export_${userId}_${System.currentTimeMillis()}"
        )
        
        return export.copy(backupFile = backupFile)
    }
    
    fun deleteUserData(userId: String) {
        // Log da exclusão
        logDataAccess(
            DataAccessLog(
                timestamp = LocalDateTime.now(),
                action = "DATA_DELETION",
                userId = userId,
                dataType = "ALL_USER_DATA",
                details = "User requested complete data deletion"
            )
        )
        
        // Deletar dados do usuário
        val userFiles = context.filesDir.listFiles()?.filter { 
            it.name.contains(userId) 
        } ?: emptyList()
        
        userFiles.forEach { file ->
            dataProtection.secureDelete(file)
        }
        
        // Limpar logs relacionados ao usuário
        val logs = getDataAccessLogs().filter { it.userId != userId }
        val encryptedLogs = dataProtection.encryptData(gson.toJson(logs))
        prefs.edit()
            .putString("data_access_logs", gson.toJson(encryptedLogs))
            .apply()
    }
    
    fun getDataRetentionPolicy(): DataRetentionPolicy {
        val encryptedJson = prefs.getString("retention_policy", null)
        return if (encryptedJson != null) {
            val encryptedPolicy = gson.fromJson(encryptedJson, EncryptedData::class.java)
            val decryptedJson = dataProtection.decryptData(encryptedPolicy)
            gson.fromJson(decryptedJson, DataRetentionPolicy::class.java)
        } else {
            DataRetentionPolicy() // Default policy
        }
    }
    
    fun setDataRetentionPolicy(policy: DataRetentionPolicy) {
        val encryptedPolicy = dataProtection.encryptData(gson.toJson(policy))
        prefs.edit()
            .putString("retention_policy", gson.toJson(encryptedPolicy))
            .apply()
    }
    
    fun cleanupExpiredData() {
        val policy = getDataRetentionPolicy()
        val logs = getDataAccessLogs().toMutableList()
        val now = LocalDateTime.now()
        
        // Remover logs expirados
        logs.removeAll { log ->
            when (log.dataType) {
                "LOGIN" -> log.timestamp.plusDays(policy.loginLogsRetentionDays.toLong()).isBefore(now)
                "TASK" -> log.timestamp.plusDays(policy.taskLogsRetentionDays.toLong()).isBefore(now)
                "ACHIEVEMENT" -> log.timestamp.plusDays(policy.achievementLogsRetentionDays.toLong()).isBefore(now)
                "FINANCIAL" -> log.timestamp.plusDays(policy.financialLogsRetentionDays.toLong()).isBefore(now)
                else -> log.timestamp.plusDays(policy.generalLogsRetentionDays.toLong()).isBefore(now)
            }
        }
        
        val encryptedLogs = dataProtection.encryptData(gson.toJson(logs))
        prefs.edit()
            .putString("data_access_logs", gson.toJson(encryptedLogs))
            .apply()
    }
    
    fun getPrivacyReport(): PrivacyReport {
        val settings = getPrivacySettings()
        val logs = getDataAccessLogs()
        val policy = getDataRetentionPolicy()
        
        return PrivacyReport(
            reportDate = LocalDateTime.now(),
            privacySettings = settings,
            totalDataAccessLogs = logs.size,
            recentDataAccessLogs = logs.filter { 
                it.timestamp.isAfter(LocalDateTime.now().minusDays(7)) 
            },
            dataRetentionPolicy = policy,
            dataExportAvailable = true,
            lastDataCleanup = getLastDataCleanup()
        )
    }
    
    private fun getLastDataCleanup(): LocalDateTime? {
        val timestamp = prefs.getLong("last_data_cleanup", 0)
        return if (timestamp > 0) {
            LocalDateTime.ofEpochSecond(timestamp, 0, java.time.ZoneOffset.UTC)
        } else {
            null
        }
    }
    
    fun setLastDataCleanup() {
        prefs.edit()
            .putLong("last_data_cleanup", LocalDateTime.now().toEpochSecond(java.time.ZoneOffset.UTC))
            .apply()
    }
}

data class PrivacySettings(
    val dataCollectionEnabled: Boolean = true,
    val analyticsEnabled: Boolean = true,
    val personalizedAds: Boolean = false,
    val shareDataWithPartners: Boolean = false,
    val allowDataExport: Boolean = true,
    val allowDataDeletion: Boolean = true,
    val notificationPreferences: NotificationPreferences = NotificationPreferences(),
    val dataSharingPreferences: DataSharingPreferences = DataSharingPreferences()
)

data class NotificationPreferences(
    val pushNotifications: Boolean = true,
    val emailNotifications: Boolean = true,
    val smsNotifications: Boolean = false,
    val marketingNotifications: Boolean = false
)

data class DataSharingPreferences(
    val shareWithFamily: Boolean = true,
    val shareWithTeachers: Boolean = false,
    val shareForResearch: Boolean = false,
    val shareForAnalytics: Boolean = true
)

data class DataAccessLog(
    val timestamp: LocalDateTime,
    val action: String,
    val userId: String,
    val dataType: String,
    val details: String
)

data class DataRetentionPolicy(
    val loginLogsRetentionDays: Int = 90,
    val taskLogsRetentionDays: Int = 365,
    val achievementLogsRetentionDays: Int = 730,
    val financialLogsRetentionDays: Int = 1825,
    val generalLogsRetentionDays: Int = 365,
    val autoCleanupEnabled: Boolean = true,
    val cleanupFrequencyDays: Int = 30
)

data class UserDataExport(
    val userId: String,
    val exportDate: LocalDateTime,
    val privacySettings: PrivacySettings,
    val dataAccessLogs: List<DataAccessLog>,
    val dataRetentionPolicy: DataRetentionPolicy,
    val backupFile: File? = null
)

data class PrivacyReport(
    val reportDate: LocalDateTime,
    val privacySettings: PrivacySettings,
    val totalDataAccessLogs: Int,
    val recentDataAccessLogs: List<DataAccessLog>,
    val dataRetentionPolicy: DataRetentionPolicy,
    val dataExportAvailable: Boolean,
    val lastDataCleanup: LocalDateTime?
) 