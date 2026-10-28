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
    validationMessage: String = "Проверьте введённые данные",
    conflictMessage: String = "Конфликт данных",
    block: suspend () -> T,
): ApiResult<T> = try {
    ApiResult.Success(block())
} catch (e: HttpException) {
    val message = when (e.code()) {
        401 -> unauthorizedMessage
        404 -> "Не найдено"
        409 -> conflictMessage
        413 -> "Файл слишком большой (максимум 2 МБ)"
        422 -> validationMessage
        else -> "Ошибка сервера (${e.code()})"
    }
    ApiResult.Error(message, e.code())
} catch (e: IOException) {
    ApiResult.Error("Нет связи с сервером. Проверьте, что бэкенд запущен")
} catch (e: SerializationException) {
    ApiResult.Error("Неожиданный ответ сервера")
}