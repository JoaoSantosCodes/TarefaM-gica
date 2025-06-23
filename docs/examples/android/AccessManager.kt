package com.tarefamagica.security

import android.content.Context
import android.content.SharedPreferences
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import android.util.Log
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.security.KeyStore
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey
import javax.crypto.spec.GCMParameterSpec
import java.util.*

/**
 * Gerenciador de Controle de Acesso - TarefaMágica
 * Gerencia permissões e roles de usuários
 */
class AccessManager(private val context: Context) {
    
    companion object {
        private const val TAG = "AccessManager"
        private const val PREFS_NAME = "access_prefs"
        private const val KEY_USER_ID = "user_id"
        private const val KEY_USER_ROLE = "user_role"
        private const val KEY_PERMISSIONS = "permissions"
        private const val KEY_LAST_LOGIN = "last_login"
        private const val KEYSTORE_PROVIDER = "AndroidKeyStore"
        private const val KEY_ALIAS = "access_manager_key"
    }
    
    private val prefs: SharedPreferences = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
    private val apiClient = ApiClient()
    
    /**
     * Roles de usuário disponíveis
     */
    enum class UserRole(val value: String) {
        CHILD("child"),
        PARENT("parent"),
        ADMIN("admin"),
        MODERATOR("moderator")
    }
    
    /**
     * Permissões disponíveis
     */
    enum class Permission(val value: String) {
        READ_OWN_DATA("read_own_data"),
        WRITE_OWN_DATA("write_own_data"),
        READ_CHILD_DATA("read_child_data"),
        WRITE_CHILD_DATA("write_child_data"),
        CREATE_TRANSACTION("create_transaction"),
        APPROVE_TRANSACTION("approve_transaction"),
        VIEW_TRANSACTION_HISTORY("view_transaction_history"),
        MANAGE_CONSENT("manage_consent"),
        VIEW_CONSENT_HISTORY("view_consent_history"),
        MANAGE_USERS("manage_users"),
        VIEW_LOGS("view_logs"),
        MANAGE_SYSTEM("manage_system")
    }
    
    /**
     * Dados do usuário atual
     */
    data class User(
        val userId: String,
        val role: UserRole,
        val parentId: String? = null,
        val childId: String? = null,
        val permissions: Set<Permission> = emptySet(),
        val isActive: Boolean = true,
        val createdAt: String? = null,
        val lastLogin: String? = null
    )
    
    /**
     * Log de acesso
     */
    data class AccessLog(
        val logId: String,
        val userId: String,
        val action: String,
        val resource: String,
        val timestamp: String,
        val ipAddress: String? = null,
        val userAgent: String? = null,
        val success: Boolean = true,
        val details: String? = null
    )
    
    /**
     * Inicializa o gerenciador de acesso
     */
    suspend fun initialize(): Boolean = withContext(Dispatchers.IO) {
        try {
            // Verifica se usuário está logado
            val userId = getCurrentUserId()
            if (userId != null) {
                // Atualiza dados do usuário
                refreshUserData(userId)
                return@withContext true
            }
            return@withContext false
        } catch (e: Exception) {
            Log.e(TAG, "Erro ao inicializar AccessManager", e)
            return@withContext false
        }
    }
    
    /**
     * Cria um novo usuário
     */
    suspend fun createUser(
        userId: String,
        role: UserRole,
        parentId: String? = null,
        childId: String? = null
    ): Result<User> = withContext(Dispatchers.IO) {
        try {
            val requestBody = JSONObject().apply {
                put("user_id", userId)
                put("role", role.value)
                if (parentId != null) put("parent_id", parentId)
                if (childId != null) put("child_id", childId)
            }
            
            val response = apiClient.post("/api/access/users", requestBody.toString())
            
            if (response.isSuccessful) {
                val jsonResponse = JSONObject(response.body?.string() ?: "{}")
                if (jsonResponse.optBoolean("success")) {
                    val userJson = jsonResponse.getJSONObject("user")
                    val user = parseUserFromJson(userJson)
                    
                    // Salva dados localmente
                    saveUserLocally(user)
                    
                    Log.i(TAG, "Usuário criado com sucesso: $userId")
                    return@withContext Result.success(user)
                } else {
                    val error = jsonResponse.optString("error", "Erro desconhecido")
                    return@withContext Result.failure(Exception(error))
                }
            } else {
                return@withContext Result.failure(Exception("Erro na requisição: ${response.code}"))
            }
        } catch (e: Exception) {
            Log.e(TAG, "Erro ao criar usuário", e)
            return@withContext Result.failure(e)
        }
    }
    
    /**
     * Obtém dados do usuário atual
     */
    fun getCurrentUser(): User? {
        val userId = getCurrentUserId() ?: return null
        val roleStr = prefs.getString(KEY_USER_ROLE, null) ?: return null
        
        return try {
            val role = UserRole.valueOf(roleStr.uppercase())
            val permissionsStr = prefs.getStringSet(KEY_PERMISSIONS, emptySet()) ?: emptySet()
            val permissions = permissionsStr.map { Permission.valueOf(it.uppercase()) }.toSet()
            
            User(
                userId = userId,
                role = role,
                permissions = permissions
            )
        } catch (e: Exception) {
            Log.e(TAG, "Erro ao obter usuário atual", e)
            null
        }
    }
    
    /**
     * Verifica se usuário tem permissão
     */
    suspend fun checkPermission(
        permission: Permission,
        resourceId: String? = null
    ): Boolean = withContext(Dispatchers.IO) {
        try {
            val userId = getCurrentUserId() ?: return@withContext false
            
            val requestBody = JSONObject().apply {
                put("user_id", userId)
                put("permission", permission.value)
                if (resourceId != null) put("resource_id", resourceId)
            }
            
            val response = apiClient.post("/api/access/check", requestBody.toString())
            
            if (response.isSuccessful) {
                val jsonResponse = JSONObject(response.body?.string() ?: "{}")
                if (jsonResponse.optBoolean("success")) {
                    return@withContext jsonResponse.optBoolean("has_permission")
                }
            }
            
            return@withContext false
        } catch (e: Exception) {
            Log.e(TAG, "Erro ao verificar permissão", e)
            return@withContext false
        }
    }
    
    /**
     * Obtém permissões do usuário atual
     */
    fun getCurrentPermissions(): Set<Permission> {
        val permissionsStr = prefs.getStringSet(KEY_PERMISSIONS, emptySet()) ?: emptySet()
        return permissionsStr.mapNotNull { 
            try {
                Permission.valueOf(it.uppercase())
            } catch (e: Exception) {
                null
            }
        }.toSet()
    }
    
    /**
     * Concede permissão ao usuário atual
     */
    suspend fun grantPermission(permission: Permission): Result<Boolean> = withContext(Dispatchers.IO) {
        try {
            val userId = getCurrentUserId() ?: return@withContext Result.failure(Exception("Usuário não logado"))
            
            val requestBody = JSONObject().apply {
                put("permission", permission.value)
            }
            
            val response = apiClient.post("/api/access/users/$userId/permissions", requestBody.toString())
            
            if (response.isSuccessful) {
                val jsonResponse = JSONObject(response.body?.string() ?: "{}")
                if (jsonResponse.optBoolean("success")) {
                    // Atualiza permissões localmente
                    val currentPermissions = getCurrentPermissions().toMutableSet()
                    currentPermissions.add(permission)
                    savePermissionsLocally(currentPermissions)
                    
                    Log.i(TAG, "Permissão concedida: ${permission.value}")
                    return@withContext Result.success(true)
                } else {
                    val error = jsonResponse.optString("error", "Erro desconhecido")
                    return@withContext Result.failure(Exception(error))
                }
            } else {
                return@withContext Result.failure(Exception("Erro na requisição: ${response.code}"))
            }
        } catch (e: Exception) {
            Log.e(TAG, "Erro ao conceder permissão", e)
            return@withContext Result.failure(e)
        }
    }
    
    /**
     * Revoga permissão do usuário atual
     */
    suspend fun revokePermission(permission: Permission): Result<Boolean> = withContext(Dispatchers.IO) {
        try {
            val userId = getCurrentUserId() ?: return@withContext Result.failure(Exception("Usuário não logado"))
            
            val requestBody = JSONObject().apply {
                put("permission", permission.value)
            }
            
            val response = apiClient.delete("/api/access/users/$userId/permissions", requestBody.toString())
            
            if (response.isSuccessful) {
                val jsonResponse = JSONObject(response.body?.string() ?: "{}")
                if (jsonResponse.optBoolean("success")) {
                    // Atualiza permissões localmente
                    val currentPermissions = getCurrentPermissions().toMutableSet()
                    currentPermissions.remove(permission)
                    savePermissionsLocally(currentPermissions)
                    
                    Log.i(TAG, "Permissão revogada: ${permission.value}")
                    return@withContext Result.success(true)
                } else {
                    val error = jsonResponse.optString("error", "Erro desconhecido")
                    return@withContext Result.failure(Exception(error))
                }
            } else {
                return@withContext Result.failure(Exception("Erro na requisição: ${response.code}"))
            }
        } catch (e: Exception) {
            Log.e(TAG, "Erro ao revogar permissão", e)
            return@withContext Result.failure(e)
        }
    }
    
    /**
     * Obtém logs de acesso
     */
    suspend fun getAccessLogs(userId: String? = null, days: Int = 30): Result<List<AccessLog>> = withContext(Dispatchers.IO) {
        try {
            val url = buildString {
                append("/api/access/logs?days=$days")
                if (userId != null) append("&user_id=$userId")
            }
            
            val response = apiClient.get(url)
            
            if (response.isSuccessful) {
                val jsonResponse = JSONObject(response.body?.string() ?: "{}")
                if (jsonResponse.optBoolean("success")) {
                    val logsArray = jsonResponse.getJSONArray("logs")
                    val logs = mutableListOf<AccessLog>()
                    
                    for (i in 0 until logsArray.length()) {
                        val logJson = logsArray.getJSONObject(i)
                        val log = parseLogFromJson(logJson)
                        logs.add(log)
                    }
                    
                    return@withContext Result.success(logs)
                } else {
                    val error = jsonResponse.optString("error", "Erro desconhecido")
                    return@withContext Result.failure(Exception(error))
                }
            } else {
                return@withContext Result.failure(Exception("Erro na requisição: ${response.code}"))
            }
        } catch (e: Exception) {
            Log.e(TAG, "Erro ao obter logs de acesso", e)
            return@withContext Result.failure(e)
        }
    }
    
    /**
     * Desativa usuário atual
     */
    suspend fun deactivateCurrentUser(): Result<Boolean> = withContext(Dispatchers.IO) {
        try {
            val userId = getCurrentUserId() ?: return@withContext Result.failure(Exception("Usuário não logado"))
            
            val response = apiClient.post("/api/access/users/$userId/deactivate", "{}")
            
            if (response.isSuccessful) {
                val jsonResponse = JSONObject(response.body?.string() ?: "{}")
                if (jsonResponse.optBoolean("success")) {
                    // Limpa dados locais
                    clearLocalData()
                    
                    Log.i(TAG, "Usuário desativado: $userId")
                    return@withContext Result.success(true)
                } else {
                    val error = jsonResponse.optString("error", "Erro desconhecido")
                    return@withContext Result.failure(Exception(error))
                }
            } else {
                return@withContext Result.failure(Exception("Erro na requisição: ${response.code}"))
            }
        } catch (e: Exception) {
            Log.e(TAG, "Erro ao desativar usuário", e)
            return@withContext Result.failure(e)
        }
    }
    
    /**
     * Atualiza dados do usuário
     */
    private suspend fun refreshUserData(userId: String) {
        try {
            val response = apiClient.get("/api/access/users/$userId")
            
            if (response.isSuccessful) {
                val jsonResponse = JSONObject(response.body?.string() ?: "{}")
                if (jsonResponse.optBoolean("success")) {
                    val userJson = jsonResponse.getJSONObject("user")
                    val user = parseUserFromJson(userJson)
                    saveUserLocally(user)
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "Erro ao atualizar dados do usuário", e)
        }
    }
    
    /**
     * Salva usuário localmente
     */
    private fun saveUserLocally(user: User) {
        prefs.edit().apply {
            putString(KEY_USER_ID, user.userId)
            putString(KEY_USER_ROLE, user.role.name.lowercase())
            putStringSet(KEY_PERMISSIONS, user.permissions.map { it.name.lowercase() }.toSet())
            if (user.lastLogin != null) putString(KEY_LAST_LOGIN, user.lastLogin)
            apply()
        }
    }
    
    /**
     * Salva permissões localmente
     */
    private fun savePermissionsLocally(permissions: Set<Permission>) {
        prefs.edit().apply {
            putStringSet(KEY_PERMISSIONS, permissions.map { it.name.lowercase() }.toSet())
            apply()
        }
    }
    
    /**
     * Obtém ID do usuário atual
     */
    private fun getCurrentUserId(): String? {
        return prefs.getString(KEY_USER_ID, null)
    }
    
    /**
     * Limpa dados locais
     */
    private fun clearLocalData() {
        prefs.edit().clear().apply()
    }
    
    /**
     * Converte JSON para User
     */
    private fun parseUserFromJson(json: JSONObject): User {
        return User(
            userId = json.getString("user_id"),
            role = UserRole.valueOf(json.getString("role").uppercase()),
            parentId = json.optString("parent_id").takeIf { it.isNotEmpty() },
            childId = json.optString("child_id").takeIf { it.isNotEmpty() },
            permissions = json.optJSONArray("permissions")?.let { array ->
                (0 until array.length()).mapNotNull { i ->
                    try {
                        Permission.valueOf(array.getString(i).uppercase())
                    } catch (e: Exception) {
                        null
                    }
                }.toSet()
            } ?: emptySet(),
            isActive = json.optBoolean("is_active", true),
            createdAt = json.optString("created_at").takeIf { it.isNotEmpty() },
            lastLogin = json.optString("last_login").takeIf { it.isNotEmpty() }
        )
    }
    
    /**
     * Converte JSON para AccessLog
     */
    private fun parseLogFromJson(json: JSONObject): AccessLog {
        return AccessLog(
            logId = json.getString("log_id"),
            userId = json.getString("user_id"),
            action = json.getString("action"),
            resource = json.getString("resource"),
            timestamp = json.getString("timestamp"),
            ipAddress = json.optString("ip_address").takeIf { it.isNotEmpty() },
            userAgent = json.optString("user_agent").takeIf { it.isNotEmpty() },
            success = json.optBoolean("success", true),
            details = json.optString("details").takeIf { it.isNotEmpty() }
        )
    }
} 