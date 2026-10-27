package com.sublingo.app.data.remote

import java.io.IOException
import kotlinx.serialization.SerializationException
import retrofit2.HttpException

sealed interface ApiResult<out T> {
    data class Success<T>(val value: T) : ApiResult<T>
    data class Error(val message: String, val code: Int? = null) : ApiResult<Nothing>
}

suspend fun <T> safeApiCall(
    unauthorizedMessage: String = "Сессия истекла, войдите снова",
    block: suspend () -> T,
): ApiResult<T> = try {
    ApiResult.Success(block())
} catch (e: HttpException) {
    val message = when (e.code()) {
        401 -> unauthorizedMessage
        409 -> "Этот email уже зарегистрирован"
        422 -> "Проверьте данные: пароль должен содержать минимум 8 символов"
        else -> "Ошибка сервера (${e.code()})"
    }
    ApiResult.Error(message, e.code())
} catch (e: IOException) {
    ApiResult.Error("Нет связи с сервером. Проверьте, что бэкенд запущен")
} catch (e: SerializationException) {
    ApiResult.Error("Неожиданный ответ сервера")
}