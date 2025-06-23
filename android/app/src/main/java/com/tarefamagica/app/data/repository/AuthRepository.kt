package com.tarefamagica.app.data.repository

import com.tarefamagica.app.data.api.ApiService
import com.tarefamagica.app.data.api.LoginRequest
import com.tarefamagica.app.data.api.RegisterRequest
import com.tarefamagica.app.data.model.Result
import com.tarefamagica.app.data.model.UserProfile
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class AuthRepository @Inject constructor(
    private val apiService: ApiService,
    private val tokenManager: TokenManager
) {
    
    suspend fun login(email: String, password: String): Flow<Result<UserProfile>> = flow {
        emit(Result.Loading)
        
        try {
            val request = LoginRequest(email, password)
            val response = apiService.login(request)
            
            if (response.success && response.data != null) {
                // Salvar tokens
                tokenManager.saveTokens(
                    accessToken = response.data.accessToken,
                    refreshToken = response.data.refreshToken
                )
                
                // Se não requer 2FA, buscar perfil do usuário
                if (!response.data.requiresTwoFactor) {
                    val profileResponse = apiService.getUserProfile()
                    if (profileResponse.success && profileResponse.data != null) {
                        emit(Result.Success(profileResponse.data))
                    } else {
                        emit(Result.Error(ApiError("PROFILE_ERROR", "Erro ao carregar perfil", null)))
                    }
                } else {
                    // Requer 2FA - retornar usuário temporário
                    val tempUser = UserProfile(
                        id = response.data.userId,
                        name = "",
                        email = email,
                        age = 0,
                        avatar = null,
                        level = 1,
                        experience = 0,
                        experienceToNextLevel = 100,
                        experienceProgress = 0f,
                        createdAt = null,
                        lastLoginAt = null
                    )
                    emit(Result.Success(tempUser))
                }
            } else {
                emit(Result.Error(ApiError("LOGIN_ERROR", response.message, null)))
            }
        } catch (e: Exception) {
            emit(Result.Error(ApiError("NETWORK_ERROR", "Erro de conexão: ${e.message}", null)))
        }
    }
    
    suspend fun register(
        name: String,
        email: String,
        password: String,
        age: Int,
        parentalConsent: Boolean,
        termsAccepted: Boolean
    ): Flow<Result<String>> = flow {
        emit(Result.Loading)
        
        try {
            val request = RegisterRequest(
                name = name,
                email = email,
                password = password,
                age = age,
                parentalConsent = parentalConsent,
                termsAccepted = termsAccepted
            )
            
            val response = apiService.register(request)
            
            if (response.success && response.data != null) {
                emit(Result.Success(response.data.userId))
            } else {
                emit(Result.Error(ApiError("REGISTER_ERROR", response.message, null)))
            }
        } catch (e: Exception) {
            emit(Result.Error(ApiError("NETWORK_ERROR", "Erro de conexão: ${e.message}", null)))
        }
    }
    
    suspend fun logout(): Flow<Result<Boolean>> = flow {
        emit(Result.Loading)
        
        try {
            val response = apiService.logout()
            
            // Limpar tokens locais
            tokenManager.clearTokens()
            
            if (response.success) {
                emit(Result.Success(true))
            } else {
                emit(Result.Error(ApiError("LOGOUT_ERROR", response.message, null)))
            }
        } catch (e: Exception) {
            // Mesmo com erro, limpar tokens locais
            tokenManager.clearTokens()
            emit(Result.Success(true))
        }
    }
    
    suspend fun refreshToken(): Flow<Result<Boolean>> = flow {
        emit(Result.Loading)
        
        try {
            val refreshToken = tokenManager.getRefreshToken()
            if (refreshToken == null) {
                emit(Result.Error(ApiError("TOKEN_ERROR", "Refresh token não encontrado", null)))
                return@flow
            }
            
            val request = RefreshTokenRequest(refreshToken)
            val response = apiService.refreshToken(request)
            
            if (response.success && response.data != null) {
                tokenManager.saveTokens(
                    accessToken = response.data.accessToken,
                    refreshToken = response.data.refreshToken
                )
                emit(Result.Success(true))
            } else {
                // Token inválido, fazer logout
                tokenManager.clearTokens()
                emit(Result.Error(ApiError("TOKEN_ERROR", "Token inválido", null)))
            }
        } catch (e: Exception) {
            emit(Result.Error(ApiError("NETWORK_ERROR", "Erro de conexão: ${e.message}", null)))
        }
    }
    
    suspend fun isLoggedIn(): Boolean {
        return tokenManager.getAccessToken() != null
    }
    
    suspend fun getCurrentUser(): Flow<Result<UserProfile>> = flow {
        emit(Result.Loading)
        
        try {
            val profileResponse = apiService.getUserProfile()
            if (profileResponse.success && profileResponse.data != null) {
                emit(Result.Success(profileResponse.data))
            } else {
                emit(Result.Error(ApiError("PROFILE_ERROR", "Erro ao carregar perfil", null)))
            }
        } catch (e: Exception) {
            emit(Result.Error(ApiError("NETWORK_ERROR", "Erro de conexão: ${e.message}", null)))
        }
    }
}

// ===== TOKEN MANAGER =====

interface TokenManager {
    suspend fun saveTokens(accessToken: String, refreshToken: String)
    suspend fun getAccessToken(): String?
    suspend fun getRefreshToken(): String?
    suspend fun clearTokens()
}

// ===== API ERROR =====

data class ApiError(
    val code: String,
    val message: String,
    val details: Map<String, Any>?
) 