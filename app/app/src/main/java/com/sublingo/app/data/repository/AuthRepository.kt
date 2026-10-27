package com.sublingo.app.data.repository

import com.sublingo.app.data.local.TokenStore
import com.sublingo.app.data.remote.ApiResult
import com.sublingo.app.data.remote.ApiService
import com.sublingo.app.data.remote.RegisterRequest
import com.sublingo.app.data.remote.UserDto
import com.sublingo.app.data.remote.safeApiCall
import kotlinx.coroutines.flow.Flow

class AuthRepository(
    private val api: ApiService,
    private val tokenStore: TokenStore,
) {
    val tokenFlow: Flow<String?> = tokenStore.token

    suspend fun login(email: String, password: String): ApiResult<Unit> =
        safeApiCall(unauthorizedMessage = "Неверный email или пароль") {
            val token = api.login(email, password)
            tokenStore.save(token.accessToken)
        }

    suspend fun register(email: String, password: String): ApiResult<Unit> {
        val created = safeApiCall { api.register(RegisterRequest(email, password)) }
        return when (created) {
            is ApiResult.Success -> login(email, password)
            is ApiResult.Error -> created
        }
    }

    suspend fun currentUser(): ApiResult<UserDto> {
        val result = safeApiCall { api.me() }
        if (result is ApiResult.Error && result.code == 401) {
            tokenStore.clear()
        }
        return result
    }

    suspend fun logout() {
        tokenStore.clear()
    }
}