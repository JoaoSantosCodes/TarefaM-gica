package com.tarefamagica.app.data.notification

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.os.Build
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import com.google.firebase.messaging.FirebaseMessagingService
import com.google.firebase.messaging.RemoteMessage
import com.tarefamagica.app.MainActivity
import com.tarefamagica.app.R
import dagger.hilt.android.AndroidEntryPoint
import javax.inject.Inject

@AndroidEntryPoint
class NotificationService : FirebaseMessagingService() {
    
    @Inject
    lateinit var notificationRepository: NotificationRepository
    
    companion object {
        const val CHANNEL_ID_TASKS = "tasks_channel"
        const val CHANNEL_ID_ACHIEVEMENTS = "achievements_channel"
        const val CHANNEL_ID_REWARDS = "rewards_channel"
        const val CHANNEL_ID_SECURITY = "security_channel"
        const val CHANNEL_ID_GENERAL = "general_channel"
        
        const val NOTIFICATION_ID_TASKS = 1001
        const val NOTIFICATION_ID_ACHIEVEMENTS = 1002
        const val NOTIFICATION_ID_REWARDS = 1003
        const val NOTIFICATION_ID_SECURITY = 1004
        const val NOTIFICATION_ID_GENERAL = 1005
    }
    
    override fun onCreate() {
        super.onCreate()
        createNotificationChannels()
    }
    
    override fun onMessageReceived(remoteMessage: RemoteMessage) {
        super.onMessageReceived(remoteMessage)
        
        // Log da notificação recebida
        notificationRepository.logNotificationReceived(remoteMessage)
        
        // Processar dados da notificação
        val notificationType = remoteMessage.data["type"] ?: "general"
        val title = remoteMessage.notification?.title ?: remoteMessage.data["title"] ?: "TarefaMágica"
        val body = remoteMessage.notification?.body ?: remoteMessage.data["body"] ?: ""
        val userId = remoteMessage.data["userId"]
        val taskId = remoteMessage.data["taskId"]
        val achievementId = remoteMessage.data["achievementId"]
        
        // Criar e exibir notificação
        when (notificationType) {
            "task" -> showTaskNotification(title, body, userId, taskId)
            "achievement" -> showAchievementNotification(title, body, userId, achievementId)
            "reward" -> showRewardNotification(title, body, userId)
            "security" -> showSecurityNotification(title, body, userId)
            else -> showGeneralNotification(title, body, userId)
        }
    }
    
    override fun onNewToken(token: String) {
        super.onNewToken(token)
        
        // Enviar novo token para o servidor
        notificationRepository.updateFcmToken(token)
    }
    
    private fun createNotificationChannels() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channels = listOf(
                NotificationChannel(
                    CHANNEL_ID_TASKS,
                    "Tarefas",
                    NotificationManager.IMPORTANCE_HIGH
                ).apply {
                    description = "Notificações sobre tarefas e atividades"
                    enableVibration(true)
                    enableLights(true)
                },
                NotificationChannel(
                    CHANNEL_ID_ACHIEVEMENTS,
                    "Conquistas",
                    NotificationManager.IMPORTANCE_DEFAULT
                ).apply {
                    description = "Notificações sobre conquistas e progresso"
                    enableVibration(true)
                },
                NotificationChannel(
                    CHANNEL_ID_REWARDS,
                    "Recompensas",
                    NotificationManager.IMPORTANCE_HIGH
                ).apply {
                    description = "Notificações sobre recompensas e PIX"
                    enableVibration(true)
                    enableLights(true)
                },
                NotificationChannel(
                    CHANNEL_ID_SECURITY,
                    "Segurança",
                    NotificationManager.IMPORTANCE_HIGH
                ).apply {
                    description = "Notificações de segurança e 2FA"
                    enableVibration(true)
                    enableLights(true)
                },
                NotificationChannel(
                    CHANNEL_ID_GENERAL,
                    "Geral",
                    NotificationManager.IMPORTANCE_LOW
                ).apply {
                    description = "Notificações gerais do app"
                }
            )
            
            val notificationManager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            channels.forEach { channel ->
                notificationManager.createNotificationChannel(channel)
            }
        }
    }
    
    private fun showTaskNotification(title: String, body: String, userId: String?, taskId: String?) {
        val intent = Intent(this, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            putExtra("screen", "tasks")
            putExtra("taskId", taskId)
            putExtra("userId", userId)
        }
        
        val pendingIntent = PendingIntent.getActivity(
            this,
            0,
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        
        val notification = NotificationCompat.Builder(this, CHANNEL_ID_TASKS)
            .setSmallIcon(R.drawable.ic_task)
            .setContentTitle(title)
            .setContentText(body)
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setAutoCancel(true)
            .setContentIntent(pendingIntent)
            .addAction(
                R.drawable.ic_check,
                "Completar",
                createActionPendingIntent("complete_task", taskId, userId)
            )
            .addAction(
                R.drawable.ic_view,
                "Ver Detalhes",
                createActionPendingIntent("view_task", taskId, userId)
            )
            .build()
        
        NotificationManagerCompat.from(this).notify(NOTIFICATION_ID_TASKS, notification)
    }
    
    private fun showAchievementNotification(title: String, body: String, userId: String?, achievementId: String?) {
        val intent = Intent(this, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            putExtra("screen", "achievements")
            putExtra("achievementId", achievementId)
            putExtra("userId", userId)
        }
        
        val pendingIntent = PendingIntent.getActivity(
            this,
            0,
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        
        val notification = NotificationCompat.Builder(this, CHANNEL_ID_ACHIEVEMENTS)
            .setSmallIcon(R.drawable.ic_achievement)
            .setContentTitle(title)
            .setContentText(body)
            .setPriority(NotificationCompat.PRIORITY_DEFAULT)
            .setAutoCancel(true)
            .setContentIntent(pendingIntent)
            .addAction(
                R.drawable.ic_view,
                "Ver Conquista",
                createActionPendingIntent("view_achievement", achievementId, userId)
            )
            .build()
        
        NotificationManagerCompat.from(this).notify(NOTIFICATION_ID_ACHIEVEMENTS, notification)
    }
    
    private fun showRewardNotification(title: String, body: String, userId: String?) {
        val intent = Intent(this, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            putExtra("screen", "pix")
            putExtra("userId", userId)
        }
        
        val pendingIntent = PendingIntent.getActivity(
            this,
            0,
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        
        val notification = NotificationCompat.Builder(this, CHANNEL_ID_REWARDS)
            .setSmallIcon(R.drawable.ic_reward)
            .setContentTitle(title)
            .setContentText(body)
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setAutoCancel(true)
            .setContentIntent(pendingIntent)
            .addAction(
                R.drawable.ic_view,
                "Ver Recompensa",
                createActionPendingIntent("view_reward", null, userId)
            )
            .build()
        
        NotificationManagerCompat.from(this).notify(NOTIFICATION_ID_REWARDS, notification)
    }
    
    private fun showSecurityNotification(title: String, body: String, userId: String?) {
        val intent = Intent(this, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            putExtra("screen", "security")
            putExtra("userId", userId)
        }
        
        val pendingIntent = PendingIntent.getActivity(
            this,
            0,
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        
        val notification = NotificationCompat.Builder(this, CHANNEL_ID_SECURITY)
            .setSmallIcon(R.drawable.ic_security)
            .setContentTitle(title)
            .setContentText(body)
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setAutoCancel(true)
            .setContentIntent(pendingIntent)
            .addAction(
                R.drawable.ic_view,
                "Ver Detalhes",
                createActionPendingIntent("view_security", null, userId)
            )
            .build()
        
        NotificationManagerCompat.from(this).notify(NOTIFICATION_ID_SECURITY, notification)
    }
    
    private fun showGeneralNotification(title: String, body: String, userId: String?) {
        val intent = Intent(this, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            putExtra("userId", userId)
        }
        
        val pendingIntent = PendingIntent.getActivity(
            this,
            0,
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        
        val notification = NotificationCompat.Builder(this, CHANNEL_ID_GENERAL)
            .setSmallIcon(R.drawable.ic_notification)
            .setContentTitle(title)
            .setContentText(body)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .setAutoCancel(true)
            .setContentIntent(pendingIntent)
            .build()
        
        NotificationManagerCompat.from(this).notify(NOTIFICATION_ID_GENERAL, notification)
    }
    
    private fun createActionPendingIntent(action: String, itemId: String?, userId: String?): PendingIntent {
        val intent = Intent(this, NotificationActionReceiver::class.java).apply {
            this.action = action
            putExtra("itemId", itemId)
            putExtra("userId", userId)
        }
        
        return PendingIntent.getBroadcast(
            this,
            action.hashCode(),
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
    }
} 