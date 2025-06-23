package com.tarefamagica.security

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.OkHttpClient
import okhttp3.RequestBody
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.Request
import org.json.JSONObject
import java.io.ByteArrayOutputStream
import java.io.InputStream

/**
 * Gerenciador de Autenticação 2FA para Android
 * Implementa a integração com o sistema 2FA
 */
class TwoFactorManager(private val context: Context) {
    
    private val apiService: TarefaMagicaApi
    private val securePrefs: EncryptedSharedPreferences
    private val client = OkHttpClient()
    
    init {
        // Configurar cliente HTTP seguro
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
            "2fa_prefs",
            masterKey,
            EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
            EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
        ) as EncryptedSharedPreferences
    }
    
    /**
     * Habilita 2FA para um responsável
     */
    suspend fun enable2FA(
        parentId: String,
        email: String
    ): Result<TwoFactorSetup> = withContext(Dispatchers.IO) {
        try {
            val requestBody = JSONObject().apply {
                put("parent_id", parentId)
                put("email", email)
            }.toString()
            
            val request = Request.Builder()
                .url("${BuildConfig.API_BASE_URL}/2fa/enable")
                .addHeader("X-API-Key", BuildConfig.API_KEY)
                .addHeader("Content-Type", "application/json")
                .post(requestBody.toRequestBody("application/json".toMediaType()))
                .build()
                
            val response = client.newCall(request).execute()
            
            if (response.isSuccessful) {
                val jsonResponse = JSONObject(response.body?.string() ?: "")
                val backupCodes = jsonResponse.getJSONArray("backup_codes")
                    .let { codes ->
                        List(codes.length()) { codes.getString(it) }
                    }
                    
                // Salva backup codes de forma segura
                securePrefs.edit()
                    .putString("backup_codes_$parentId", backupCodes.joinToString(","))
                    .apply()
                    
                Result.success(TwoFactorSetup(
                    qrCodePath = jsonResponse.getString("qr_code_path"),
                    backupCodes = backupCodes
                ))
            } else {
                Result.failure(Exception("Erro: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Obtém QR code para configuração
     */
    suspend fun getQRCode(parentId: String): Result<Bitmap> = withContext(Dispatchers.IO) {
        try {
            val request = Request.Builder()
                .url("${BuildConfig.API_BASE_URL}/2fa/qr/$parentId")
                .addHeader("X-API-Key", BuildConfig.API_KEY)
                .get()
                .build()
                
            val response = client.newCall(request).execute()
            
            if (response.isSuccessful) {
                val inputStream: InputStream = response.body?.byteStream() ?: throw Exception("Stream vazio")
                val bitmap = BitmapFactory.decodeStream(inputStream)
                
                if (bitmap != null) {
                    Result.success(bitmap)
                } else {
                    Result.failure(Exception("Erro ao decodificar QR code"))
                }
            } else {
                Result.failure(Exception("Erro: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Verifica token 2FA
     */
    suspend fun verifyToken(
        parentId: String,
        token: String
    ): Result<Boolean> = withContext(Dispatchers.IO) {
        try {
            val requestBody = JSONObject().apply {
                put("parent_id", parentId)
                put("token", token)
            }.toString()
            
            val request = Request.Builder()
                .url("${BuildConfig.API_BASE_URL}/2fa/verify")
                .addHeader("X-API-Key", BuildConfig.API_KEY)
                .addHeader("Content-Type", "application/json")
                .post(requestBody.toRequestBody("application/json".toMediaType()))
                .build()
                
            val response = client.newCall(request).execute()
            
            if (response.isSuccessful) {
                Result.success(true)
            } else {
                Result.failure(Exception("Token inválido"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Verifica código de backup
     */
    suspend fun verifyBackupCode(
        parentId: String,
        code: String
    ): Result<Boolean> = withContext(Dispatchers.IO) {
        try {
            val requestBody = JSONObject().apply {
                put("parent_id", parentId)
                put("code", code)
            }.toString()
            
            val request = Request.Builder()
                .url("${BuildConfig.API_BASE_URL}/2fa/backup/verify")
                .addHeader("X-API-Key", BuildConfig.API_KEY)
                .addHeader("Content-Type", "application/json")
                .post(requestBody.toRequestBody("application/json".toMediaType()))
                .build()
                
            val response = client.newCall(request).execute()
            
            if (response.isSuccessful) {
                // Remove código usado
                removeBackupCode(parentId, code)
                Result.success(true)
            } else {
                Result.failure(Exception("Código de backup inválido"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Verifica status do 2FA
     */
    suspend fun get2FAStatus(parentId: String): Result<Boolean> = withContext(Dispatchers.IO) {
        try {
            val request = Request.Builder()
                .url("${BuildConfig.API_BASE_URL}/2fa/status/$parentId")
                .addHeader("X-API-Key", BuildConfig.API_KEY)
                .get()
                .build()
                
            val response = client.newCall(request).execute()
            
            if (response.isSuccessful) {
                val jsonResponse = JSONObject(response.body?.string() ?: "")
                val isEnabled = jsonResponse.getBoolean("2fa_enabled")
                Result.success(isEnabled)
            } else {
                Result.failure(Exception("Erro: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Desabilita 2FA
     */
    suspend fun disable2FA(parentId: String): Result<Boolean> = withContext(Dispatchers.IO) {
        try {
            val request = Request.Builder()
                .url("${BuildConfig.API_BASE_URL}/2fa/disable/$parentId")
                .addHeader("X-API-Key", BuildConfig.API_KEY)
                .delete()
                .build()
                
            val response = client.newCall(request).execute()
            
            if (response.isSuccessful) {
                // Limpa dados locais
                clearLocal2FAData(parentId)
                Result.success(true)
            } else {
                Result.failure(Exception("Erro: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Obtém códigos de backup salvos
     */
    fun getBackupCodes(parentId: String): List<String> {
        val codesString = securePrefs.getString("backup_codes_$parentId", "")
        return if (codesString.isNullOrEmpty()) {
            emptyList()
        } else {
            codesString.split(",")
        }
    }
    
    /**
     * Remove código de backup usado
     */
    private fun removeBackupCode(parentId: String, usedCode: String) {
        val currentCodes = getBackupCodes(parentId).toMutableList()
        currentCodes.remove(usedCode)
        
        securePrefs.edit()
            .putString("backup_codes_$parentId", currentCodes.joinToString(","))
            .apply()
    }
    
    /**
     * Limpa dados locais do 2FA
     */
    private fun clearLocal2FAData(parentId: String) {
        securePrefs.edit()
            .remove("backup_codes_$parentId")
            .apply()
    }
}

// Modelos de dados
data class TwoFactorSetup(
    val qrCodePath: String,
    val backupCodes: List<String>
)

// Interface da API
interface TarefaMagicaApi {
    @POST("2fa/enable")
    suspend fun enable2FA(@Body request: Enable2FARequest): Response<TwoFactorSetup>
    
    @GET("2fa/status/{parentId}")
    suspend fun get2FAStatus(@Path("parentId") parentId: String): Response<Boolean>
    
    @DELETE("2fa/disable/{parentId}")
    suspend fun disable2FA(@Path("parentId") parentId: String): Response<Unit>
}

data class Enable2FARequest(
    val parent_id: String,
    val email: String
) 