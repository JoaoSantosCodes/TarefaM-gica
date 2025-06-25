package com.tarefamagica.app.data.notification

import com.tarefamagica.app.data.api.ApiService
import com.tarefamagica.app.data.model.NotificationData
import com.tarefamagica.app.data.model.NotificationPreferences
import com.google.firebase.messaging.RemoteMessage
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import java.time.LocalDateTime
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class NotificationRepository @Inject constructor(
    private val apiService: ApiService
) {
    
    private val _notifications = MutableStateFlow<List<NotificationData>>(emptyList())
    val notifications: Flow<List<NotificationData>> = _notifications.asStateFlow()
    
    private val _preferences = MutableStateFlow(NotificationPreferences())
    val preferences: Flow<NotificationPreferences> = _preferences.asStateFlow()
    
    suspend fun updateFcmToken(token: String) {
        try {
            // Enviar token para o servidor
            apiService.updateFcmToken(token)
        } catch (e: Exception) {
            // Log do erro
            logNotificationError("Erro ao atualizar FCM token", e)
        }
    }
    
    suspend fun getNotifications(userId: String): List<NotificationData> {
        return try {
            val notifications = apiService.getNotifications(userId)
            _notifications.value = notifications
            notifications
        } catch (e: Exception) {
            logNotificationError("Erro ao buscar notificações", e)
            emptyList()
        }
    }
    
    suspend fun markAsRead(notificationId: String) {
        try {
            apiService.markNotificationAsRead(notificationId)
            
            // Atualizar lista local
            val updatedNotifications = _notifications.value.map { notification ->
                if (notification.id == notificationId) {
                    notification.copy(isRead = true, readAt = LocalDateTime.now())
                } else {
                    notification
                }
            }
            _notifications.value = updatedNotifications
            
        } catch (e: Exception) {
            logNotificationError("Erro ao marcar notificação como lida", e)
        }
    }
    
    suspend fun deleteNotification(notificationId: String) {
        try {
            apiService.deleteNotification(notificationId)
            
            // Remover da lista local
            val updatedNotifications = _notifications.value.filter { 
                it.id != notificationId 
            }
            _notifications.value = updatedNotifications
            
        } catch (e: Exception) {
            logNotificationError("Erro ao deletar notificação", e)
        }
    }
    
    suspend fun getNotificationPreferences(userId: String): NotificationPreferences {
        return try {
            val preferences = apiService.getNotificationPreferences(userId)
            _preferences.value = preferences
            preferences
        } catch (e: Exception) {
            logNotificationError("Erro ao buscar preferências", e)
            NotificationPreferences()
        }
    }
    
    suspend fun updateNotificationPreferences(
        userId: String,
        preferences: NotificationPreferences
    ) {
        try {
            apiService.updateNotificationPreferences(userId, preferences)
            _preferences.value = preferences
        } catch (e: Exception) {
            logNotificationError("Erro ao atualizar preferências", e)
        }
    }
    
    suspend fun subscribeToTopic(topic: String) {
        try {
            apiService.subscribeToTopic(topic)
        } catch (e: Exception) {
            logNotificationError("Erro ao se inscrever no tópico", e)
        }
    }
    
    suspend fun unsubscribeFromTopic(topic: String) {
        try {
            apiService.unsubscribeFromTopic(topic)
        } catch (e: Exception) {
            logNotificationError("Erro ao se desinscrever do tópico", e)
        }
    }
    
    fun logNotificationReceived(remoteMessage: RemoteMessage) {
        // Log local da notificação recebida
        val notificationLog = NotificationLog(
            timestamp = LocalDateTime.now(),
            title = remoteMessage.notification?.title ?: remoteMessage.data["title"] ?: "",
            body = remoteMessage.notification?.body ?: remoteMessage.data["body"] ?: "",
            type = remoteMessage.data["type"] ?: "unknown",
            userId = remoteMessage.data["userId"],
            data = remoteMessage.data
        )
        
        // Salvar log localmente
        saveNotificationLog(notificationLog)
    }
    
    private fun saveNotificationLog(log: NotificationLog) {
        // Implementar salvamento local do log
        // Pode usar Room Database ou SharedPreferences
    }
    
    private fun logNotificationError(message: String, error: Exception) {
        // Log de erro para debugging
        println("NotificationRepository Error: $message - ${error.message}")
    }
    
    fun getUnreadCount(): Int {
        return _notifications.value.count { !it.isRead }
    }
    
    fun clearAllNotifications() {
        _notifications.value = emptyList()
    }
    
    suspend fun sendLocalNotification(
        title: String,
        body: String,
        type: String,
        userId: String?
    ) {
        val notification = NotificationData(
            id = generateNotificationId(),
            title = title,
            body = body,
            type = type,
            userId = userId,
            createdAt = LocalDateTime.now(),
            isRead = false,
            readAt = null
        )
        
        val updatedNotifications = _notifications.value.toMutableList()
        updatedNotifications.add(0, notification)
        _notifications.value = updatedNotifications
    }
    
    private fun generateNotificationId(): String {
        return "local_${System.currentTimeMillis()}"
    }
}

data class NotificationLog(
    val timestamp: LocalDateTime,
    val title: String,
    val body: String,
    val type: String,
    val userId: String?,
    val data: Map<String, String>
) 