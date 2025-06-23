package com.tarefamagica.security

import android.content.Context
import android.content.SharedPreferences
import android.provider.Settings
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.OkHttpClient
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.*

/**
 * Gerenciador de Consentimento para Android
 * Implementa a integração com a API de consentimento
 */
class ConsentManager(private val context: Context) {
    
    private val apiService: TarefaMagicaApi
    private val securePrefs: SharedPreferences
    private val deviceId: String
    
    init {
        // Configurar cliente HTTP seguro
        val client = OkHttpClient.Builder()
            .addInterceptor { chain ->
                val request = chain.request().newBuilder()
                    .addHeader("X-API-Key", BuildConfig.API_KEY)
                    .build()
                chain.proceed(request)
            }
            .build()
            
        // Configurar Retrofit
        apiService = Retrofit.Builder()
            .baseUrl(BuildConfig.API_BASE_URL)
            .client(client)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(TarefaMagicaApi::class.java)
            
        // Configurar armazenamento seguro
        val masterKey = MasterKey.Builder(context)
            .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
            .build()
            
        securePrefs = EncryptedSharedPreferences.create(
            context,
            "consent_prefs",
            masterKey,
            EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
            EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
        )
        
        // Gerar/recuperar ID do dispositivo
        deviceId = Settings.Secure.getString(
            context.contentResolver,
            Settings.Secure.ANDROID_ID
        )
    }
    
    /**
     * Solicita consentimento parental
     */
    suspend fun requestConsent(
        userId: String,
        childId: String,
        parentName: String,
        childName: String
    ): Result<ConsentResponse> = withContext(Dispatchers.IO) {
        try {
            val request = ConsentRequest(
                deviceId = deviceId,
                userId = userId,
                childId = childId,
                parentName = parentName,
                childName = childName
            )
            
            val response = apiService.requestConsent(request)
            
            if (response.isSuccessful) {
                response.body()?.let { consent ->
                    // Salvar token e ID do consentimento
                    securePrefs.edit()
                        .putString("consent_id", consent.consentId)
                        .putString("auth_token", consent.token)
                        .apply()
                        
                    Result.success(consent)
                } ?: Result.failure(Exception("Resposta vazia"))
            } else {
                Result.failure(Exception("Erro: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Concede consentimento parental
     */
    suspend fun grantConsent(userId: String): Result<Boolean> = withContext(Dispatchers.IO) {
        try {
            val consentId = securePrefs.getString("consent_id", null)
                ?: return@withContext Result.failure(Exception("ID do consentimento não encontrado"))
                
            val response = apiService.grantConsent(consentId, userId)
            
            if (response.isSuccessful) {
                securePrefs.edit()
                    .putBoolean("consent_granted", true)
                    .apply()
                    
                Result.success(true)
            } else {
                Result.failure(Exception("Erro: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Revoga consentimento parental
     */
    suspend fun revokeConsent(userId: String): Result<Boolean> = withContext(Dispatchers.IO) {
        try {
            val consentId = securePrefs.getString("consent_id", null)
                ?: return@withContext Result.failure(Exception("ID do consentimento não encontrado"))
                
            val response = apiService.revokeConsent(consentId, userId)
            
            if (response.isSuccessful) {
                securePrefs.edit()
                    .putBoolean("consent_granted", false)
                    .apply()
                    
                Result.success(true)
            } else {
                Result.failure(Exception("Erro: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Verifica se há consentimento ativo
     */
    fun hasActiveConsent(): Boolean {
        return securePrefs.getBoolean("consent_granted", false)
    }
    
    /**
     * Limpa dados de consentimento
     */
    fun clearConsentData() {
        securePrefs.edit().clear().apply()
    }
}

// Modelos de dados
data class ConsentRequest(
    val deviceId: String,
    val userId: String,
    val childId: String,
    val parentName: String,
    val childName: String
)

data class ConsentResponse(
    val status: String,
    val consentId: String,
    val token: String
)

// Interface da API
interface TarefaMagicaApi {
    @POST("mobile/consent/request")
    suspend fun requestConsent(@Body request: ConsentRequest): Response<ConsentResponse>
    
    @POST("mobile/consent/grant/{consentId}")
    suspend fun grantConsent(
        @Path("consentId") consentId: String,
        @Query("user_id") userId: String
    ): Response<Unit>
    
    @POST("mobile/consent/revoke/{consentId}")
    suspend fun revokeConsent(
        @Path("consentId") consentId: String,
        @Query("user_id") userId: String
    ): Response<Unit>
} 