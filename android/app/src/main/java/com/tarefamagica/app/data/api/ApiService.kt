package com.tarefamagica.app.data.api

import com.tarefamagica.app.data.model.*
import retrofit2.http.*

interface ApiService {
    
    // ===== AUTENTICAÇÃO =====
    @POST("auth/login")
    suspend fun login(@Body request: LoginRequest): LoginResponse
    
    @POST("auth/register")
    suspend fun register(@Body request: RegisterRequest): RegisterResponse
    
    @POST("auth/logout")
    suspend fun logout(): LogoutResponse
    
    @POST("auth/refresh")
    suspend fun refreshToken(@Body request: RefreshTokenRequest): RefreshTokenResponse
    
    // ===== 2FA =====
    @GET("two-factor/setup")
    suspend fun getTwoFactorSetup(): TwoFactorSetupResponse
    
    @POST("two-factor/verify")
    suspend fun verifyTwoFactor(@Body request: TwoFactorVerifyRequest): TwoFactorVerifyResponse
    
    @POST("two-factor/disable")
    suspend fun disableTwoFactor(@Body request: TwoFactorDisableRequest): TwoFactorDisableResponse
    
    // ===== CONSENTIMENTO PARENTAL =====
    @POST("consent/parental")
    suspend fun submitParentalConsent(@Body request: ParentalConsentRequest): ParentalConsentResponse
    
    @GET("consent/parental/status")
    suspend fun getParentalConsentStatus(): ParentalConsentStatusResponse
    
    // ===== TAREFAS =====
    @GET("tasks")
    suspend fun getTasks(
        @Query("filter") filter: String? = null,
        @Query("search") search: String? = null,
        @Query("page") page: Int = 1,
        @Query("limit") limit: Int = 20
    ): TasksResponse
    
    @GET("tasks/{taskId}")
    suspend fun getTask(@Path("taskId") taskId: String): TaskResponse
    
    @POST("tasks")
    suspend fun createTask(@Body request: CreateTaskRequest): TaskResponse
    
    @PUT("tasks/{taskId}")
    suspend fun updateTask(
        @Path("taskId") taskId: String,
        @Body request: UpdateTaskRequest
    ): TaskResponse
    
    @DELETE("tasks/{taskId}")
    suspend fun deleteTask(@Path("taskId") taskId: String): DeleteTaskResponse
    
    @POST("tasks/{taskId}/complete")
    suspend fun completeTask(@Path("taskId") taskId: String): CompleteTaskResponse
    
    // ===== USUÁRIO =====
    @GET("user/profile")
    suspend fun getUserProfile(): UserProfileResponse
    
    @PUT("user/profile")
    suspend fun updateUserProfile(@Body request: UpdateUserProfileRequest): UserProfileResponse
    
    @GET("user/statistics")
    suspend fun getUserStatistics(): UserStatisticsResponse
    
    @GET("user/achievements")
    suspend fun getUserAchievements(): AchievementsResponse
    
    // ===== GAMIFICAÇÃO =====
    @GET("gamification/points")
    suspend fun getPoints(): PointsResponse
    
    @GET("gamification/level")
    suspend fun getLevel(): LevelResponse
    
    @GET("gamification/leaderboard")
    suspend fun getLeaderboard(): LeaderboardResponse
    
    // ===== FINANCEIRO =====
    @GET("financial/balance")
    suspend fun getBalance(): BalanceResponse
    
    @GET("financial/transactions")
    suspend fun getTransactions(): TransactionsResponse
    
    @POST("financial/withdraw")
    suspend fun withdrawPoints(@Body request: WithdrawRequest): WithdrawResponse
    
    // ===== SEGURANÇA =====
    @GET("security/status")
    suspend fun getSecurityStatus(): SecurityStatusResponse
    
    @POST("security/change-password")
    suspend fun changePassword(@Body request: ChangePasswordRequest): ChangePasswordResponse
    
    @GET("security/access-logs")
    suspend fun getAccessLogs(): AccessLogsResponse
    
    // ===== NOTIFICAÇÕES =====
    @GET("notifications")
    suspend fun getNotifications(): NotificationsResponse
    
    @POST("notifications/{notificationId}/read")
    suspend fun markNotificationAsRead(@Path("notificationId") notificationId: String): MarkReadResponse
    
    @DELETE("notifications/{notificationId}")
    suspend fun deleteNotification(@Path("notificationId") notificationId: String): DeleteNotificationResponse
}

// ===== MODELOS DE REQUISIÇÃO =====

data class LoginRequest(
    val email: String,
    val password: String
)

data class RegisterRequest(
    val name: String,
    val email: String,
    val password: String,
    val age: Int,
    val parentalConsent: Boolean,
    val termsAccepted: Boolean
)

data class RefreshTokenRequest(
    val refreshToken: String
)

data class TwoFactorVerifyRequest(
    val code: String
)

data class TwoFactorDisableRequest(
    val password: String
)

data class ParentalConsentRequest(
    val parentName: String,
    val parentEmail: String,
    val parentPhone: String,
    val relationship: String,
    val consentDate: String
)

data class CreateTaskRequest(
    val title: String,
    val description: String,
    val category: String,
    val points: Int,
    val dueDate: String?
)

data class UpdateTaskRequest(
    val title: String? = null,
    val description: String? = null,
    val category: String? = null,
    val points: Int? = null,
    val dueDate: String? = null
)

data class UpdateUserProfileRequest(
    val name: String? = null,
    val avatar: String? = null,
    val preferences: Map<String, Any>? = null
)

data class WithdrawRequest(
    val amount: Int,
    val pixKey: String
)

data class ChangePasswordRequest(
    val currentPassword: String,
    val newPassword: String
)

// ===== MODELOS DE RESPOSTA =====

data class LoginResponse(
    val success: Boolean,
    val message: String,
    val data: LoginData? = null
)

data class LoginData(
    val userId: String,
    val accessToken: String,
    val refreshToken: String,
    val requiresTwoFactor: Boolean
)

data class RegisterResponse(
    val success: Boolean,
    val message: String,
    val data: RegisterData? = null
)

data class RegisterData(
    val userId: String,
    val requiresParentalConsent: Boolean
)

data class LogoutResponse(
    val success: Boolean,
    val message: String
)

data class RefreshTokenResponse(
    val success: Boolean,
    val message: String,
    val data: RefreshTokenData? = null
)

data class RefreshTokenData(
    val accessToken: String,
    val refreshToken: String
)

data class TwoFactorSetupResponse(
    val success: Boolean,
    val message: String,
    val data: TwoFactorSetupData? = null
)

data class TwoFactorSetupData(
    val qrCodeUrl: String,
    val secretKey: String,
    val backupCodes: List<String>
)

data class TwoFactorVerifyResponse(
    val success: Boolean,
    val message: String,
    val data: TwoFactorVerifyData? = null
)

data class TwoFactorVerifyData(
    val accessToken: String,
    val refreshToken: String
)

data class TwoFactorDisableResponse(
    val success: Boolean,
    val message: String
)

data class ParentalConsentResponse(
    val success: Boolean,
    val message: String
)

data class ParentalConsentStatusResponse(
    val success: Boolean,
    val message: String,
    val data: ParentalConsentStatusData? = null
)

data class ParentalConsentStatusData(
    val isConsented: Boolean,
    val consentDate: String?,
    val parentName: String?
)

data class TasksResponse(
    val success: Boolean,
    val message: String,
    val data: TasksData? = null
)

data class TasksData(
    val tasks: List<Task>,
    val total: Int,
    val page: Int,
    val totalPages: Int
)

data class TaskResponse(
    val success: Boolean,
    val message: String,
    val data: Task? = null
)

data class DeleteTaskResponse(
    val success: Boolean,
    val message: String
)

data class CompleteTaskResponse(
    val success: Boolean,
    val message: String,
    val data: CompleteTaskData? = null
)

data class CompleteTaskData(
    val pointsEarned: Int,
    val levelUp: Boolean,
    val newLevel: Int?,
    val achievements: List<Achievement>
)

data class UserProfileResponse(
    val success: Boolean,
    val message: String,
    val data: UserProfile? = null
)

data class UserStatisticsResponse(
    val success: Boolean,
    val message: String,
    val data: UserStatistics? = null
)

data class AchievementsResponse(
    val success: Boolean,
    val message: String,
    val data: AchievementsData? = null
)

data class AchievementsData(
    val achievements: List<Achievement>,
    val total: Int
)

data class PointsResponse(
    val success: Boolean,
    val message: String,
    val data: PointsData? = null
)

data class PointsData(
    val currentPoints: Int,
    val totalPoints: Int,
    val pointsHistory: List<PointsHistory>
)

data class LevelResponse(
    val success: Boolean,
    val message: String,
    val data: LevelData? = null
)

data class LevelData(
    val currentLevel: Int,
    val currentExperience: Int,
    val experienceToNextLevel: Int,
    val progress: Float
)

data class LeaderboardResponse(
    val success: Boolean,
    val message: String,
    val data: LeaderboardData? = null
)

data class LeaderboardData(
    val leaderboard: List<LeaderboardEntry>,
    val userRank: Int
)

data class BalanceResponse(
    val success: Boolean,
    val message: String,
    val data: BalanceData? = null
)

data class BalanceData(
    val balance: Double,
    val pendingBalance: Double,
    val totalEarned: Double
)

data class TransactionsResponse(
    val success: Boolean,
    val message: String,
    val data: TransactionsData? = null
)

data class TransactionsData(
    val transactions: List<Transaction>,
    val total: Int
)

data class WithdrawResponse(
    val success: Boolean,
    val message: String,
    val data: WithdrawData? = null
)

data class WithdrawData(
    val transactionId: String,
    val amount: Double,
    val status: String
)

data class SecurityStatusResponse(
    val success: Boolean,
    val message: String,
    val data: SecurityStatusData? = null
)

data class SecurityStatusData(
    val twoFactorEnabled: Boolean,
    val lastLogin: String,
    val suspiciousActivity: Boolean
)

data class ChangePasswordResponse(
    val success: Boolean,
    val message: String
)

data class AccessLogsResponse(
    val success: Boolean,
    val message: String,
    val data: AccessLogsData? = null
)

data class AccessLogsData(
    val logs: List<AccessLog>,
    val total: Int
)

data class NotificationsResponse(
    val success: Boolean,
    val message: String,
    val data: NotificationsData? = null
)

data class NotificationsData(
    val notifications: List<Notification>,
    val total: Int,
    val unreadCount: Int
)

data class MarkReadResponse(
    val success: Boolean,
    val message: String
)

data class DeleteNotificationResponse(
    val success: Boolean,
    val message: String
) 