package com.tarefamagica.financial

import android.content.Context
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.OkHttpClient
import okhttp3.RequestBody
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.Request
import org.json.JSONObject
import java.util.*

/**
 * Gerenciador Financeiro para Android
 * Implementa a integração com o sistema financeiro
 */
class FinancialManager(private val context: Context) {
    
    private val client = OkHttpClient()
    private val securePrefs: EncryptedSharedPreferences
    
    init {
        // Configurar armazenamento seguro
        val masterKey = MasterKey.Builder(context)
            .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
            .build()
            
        securePrefs = EncryptedSharedPreferences.create(
            context,
            "financial_prefs",
            masterKey,
            EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
            EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
        ) as EncryptedSharedPreferences
    }
    
    /**
     * Cria uma nova transação PIX
     */
    suspend fun createTransaction(
        parentId: String,
        childId: String,
        amount: Double,
        pixKey: String,
        description: String
    ): Result<Transaction> = withContext(Dispatchers.IO) {
        try {
            val requestBody = JSONObject().apply {
                put("parent_id", parentId)
                put("child_id", childId)
                put("amount", amount)
                put("pix_key", pixKey)
                put("description", description)
            }.toString()
            
            val request = Request.Builder()
                .url("${BuildConfig.API_BASE_URL}/financial/transaction/create")
                .addHeader("X-API-Key", BuildConfig.API_KEY)
                .addHeader("Content-Type", "application/json")
                .post(requestBody.toRequestBody("application/json".toMediaType()))
                .build()
                
            val response = client.newCall(request).execute()
            
            if (response.isSuccessful) {
                val jsonResponse = JSONObject(response.body?.string() ?: "")
                val transactionData = jsonResponse.getJSONObject("transaction")
                
                val transaction = Transaction(
                    transactionId = transactionData.getString("transaction_id"),
                    parentId = parentId,
                    childId = childId,
                    amount = amount,
                    pixKey = pixKey,
                    description = description,
                    status = TransactionStatus.PENDING,
                    riskLevel = RiskLevel.valueOf(transactionData.getString("risk_level").uppercase()),
                    createdAt = Date()
                )
                
                Result.success(transaction)
            } else {
                val errorBody = response.body?.string() ?: "Erro desconhecido"
                Result.failure(Exception("Erro: ${response.code()} - $errorBody"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Aprova uma transação
     */
    suspend fun approveTransaction(
        transactionId: String,
        parentId: String
    ): Result<Boolean> = withContext(Dispatchers.IO) {
        try {
            val requestBody = JSONObject().apply {
                put("transaction_id", transactionId)
                put("parent_id", parentId)
            }.toString()
            
            val request = Request.Builder()
                .url("${BuildConfig.API_BASE_URL}/financial/transaction/approve")
                .addHeader("X-API-Key", BuildConfig.API_KEY)
                .addHeader("Content-Type", "application/json")
                .post(requestBody.toRequestBody("application/json".toMediaType()))
                .build()
                
            val response = client.newCall(request).execute()
            
            if (response.isSuccessful) {
                Result.success(true)
            } else {
                Result.failure(Exception("Erro: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Rejeita uma transação
     */
    suspend fun rejectTransaction(
        transactionId: String,
        parentId: String,
        reason: String
    ): Result<Boolean> = withContext(Dispatchers.IO) {
        try {
            val requestBody = JSONObject().apply {
                put("transaction_id", transactionId)
                put("parent_id", parentId)
                put("reason", reason)
            }.toString()
            
            val request = Request.Builder()
                .url("${BuildConfig.API_BASE_URL}/financial/transaction/reject")
                .addHeader("X-API-Key", BuildConfig.API_KEY)
                .addHeader("Content-Type", "application/json")
                .post(requestBody.toRequestBody("application/json".toMediaType()))
                .build()
                
            val response = client.newCall(request).execute()
            
            if (response.isSuccessful) {
                Result.success(true)
            } else {
                Result.failure(Exception("Erro: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Obtém detalhes de uma transação
     */
    suspend fun getTransaction(
        transactionId: String,
        parentId: String
    ): Result<Transaction> = withContext(Dispatchers.IO) {
        try {
            val request = Request.Builder()
                .url("${BuildConfig.API_BASE_URL}/financial/transaction/$transactionId?parent_id=$parentId")
                .addHeader("X-API-Key", BuildConfig.API_KEY)
                .get()
                .build()
                
            val response = client.newCall(request).execute()
            
            if (response.isSuccessful) {
                val jsonResponse = JSONObject(response.body?.string() ?: "")
                
                val transaction = Transaction(
                    transactionId = jsonResponse.getString("transaction_id"),
                    parentId = jsonResponse.getString("parent_id"),
                    childId = jsonResponse.getString("child_id"),
                    amount = jsonResponse.getDouble("amount"),
                    pixKey = jsonResponse.getString("pix_key"),
                    description = jsonResponse.getString("description"),
                    status = TransactionStatus.valueOf(jsonResponse.getString("status").uppercase()),
                    riskLevel = RiskLevel.valueOf(jsonResponse.getString("risk_level").uppercase()),
                    createdAt = Date(jsonResponse.getString("created_at"))
                )
                
                Result.success(transaction)
            } else {
                Result.failure(Exception("Erro: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Obtém histórico de transações
     */
    suspend fun getTransactionHistory(
        parentId: String,
        days: Int = 30
    ): Result<List<Transaction>> = withContext(Dispatchers.IO) {
        try {
            val request = Request.Builder()
                .url("${BuildConfig.API_BASE_URL}/financial/history/$parentId?days=$days")
                .addHeader("X-API-Key", BuildConfig.API_KEY)
                .get()
                .build()
                
            val response = client.newCall(request).execute()
            
            if (response.isSuccessful) {
                val jsonResponse = JSONObject(response.body?.string() ?: "")
                val transactionsArray = jsonResponse.getJSONArray("transactions")
                
                val transactions = mutableListOf<Transaction>()
                for (i in 0 until transactionsArray.length()) {
                    val transactionData = transactionsArray.getJSONObject(i)
                    
                    val transaction = Transaction(
                        transactionId = transactionData.getString("transaction_id"),
                        parentId = parentId,
                        childId = transactionData.getString("child_id"),
                        amount = transactionData.getDouble("amount"),
                        pixKey = transactionData.getString("pix_key"),
                        description = transactionData.getString("description"),
                        status = TransactionStatus.valueOf(transactionData.getString("status").uppercase()),
                        riskLevel = RiskLevel.valueOf(transactionData.getString("risk_level").uppercase()),
                        createdAt = Date(transactionData.getString("created_at"))
                    )
                    
                    transactions.add(transaction)
                }
                
                Result.success(transactions)
            } else {
                Result.failure(Exception("Erro: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Obtém limites financeiros
     */
    suspend fun getLimits(parentId: String): Result<FinancialLimits> = withContext(Dispatchers.IO) {
        try {
            val request = Request.Builder()
                .url("${BuildConfig.API_BASE_URL}/financial/limits/$parentId")
                .addHeader("X-API-Key", BuildConfig.API_KEY)
                .get()
                .build()
                
            val response = client.newCall(request).execute()
            
            if (response.isSuccessful) {
                val jsonResponse = JSONObject(response.body?.string() ?: "")
                val limitsData = jsonResponse.getJSONObject("limits")
                val usageData = jsonResponse.getJSONObject("current_usage")
                
                val limits = FinancialLimits(
                    maxDailyAmount = limitsData.getDouble("max_daily_amount"),
                    maxTransactionAmount = limitsData.getDouble("max_transaction_amount"),
                    maxMonthlyAmount = limitsData.getDouble("max_monthly_amount"),
                    dailyTotal = usageData.getDouble("daily_total"),
                    dailyRemaining = usageData.getDouble("daily_remaining"),
                    transactionsToday = usageData.getInt("transactions_today")
                )
                
                Result.success(limits)
            } else {
                Result.failure(Exception("Erro: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Salva chave PIX de forma segura
     */
    fun savePixKey(parentId: String, pixKey: String) {
        securePrefs.edit()
            .putString("pix_key_$parentId", pixKey)
            .apply()
    }
    
    /**
     * Obtém chave PIX salva
     */
    fun getPixKey(parentId: String): String? {
        return securePrefs.getString("pix_key_$parentId", null)
    }
}

// Modelos de dados
data class Transaction(
    val transactionId: String,
    val parentId: String,
    val childId: String,
    val amount: Double,
    val pixKey: String,
    val description: String,
    val status: TransactionStatus,
    val riskLevel: RiskLevel,
    val createdAt: Date
)

enum class TransactionStatus {
    PENDING, APPROVED, REJECTED, CANCELLED
}

enum class RiskLevel {
    LOW, MEDIUM, HIGH, CRITICAL
}

data class FinancialLimits(
    val maxDailyAmount: Double,
    val maxTransactionAmount: Double,
    val maxMonthlyAmount: Double,
    val dailyTotal: Double,
    val dailyRemaining: Double,
    val transactionsToday: Int
) 