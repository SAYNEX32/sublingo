package com.sublingo.app.data.repository

import android.content.Context
import android.net.Uri
import android.provider.OpenableColumns
import com.sublingo.app.data.remote.ApiResult
import com.sublingo.app.data.remote.ApiService
import com.sublingo.app.data.remote.EpisodeDto
import com.sublingo.app.data.remote.ReportDto
import com.sublingo.app.data.remote.safeApiCall
import java.io.IOException
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.toRequestBody

class PickedFile(val name: String, val bytes: ByteArray)

class EpisodeRepository(
    private val api: ApiService,
    private val context: Context,
) {
    suspend fun list(): ApiResult<List<EpisodeDto>> = safeApiCall { api.episodes() }

    suspend fun report(episodeId: Int): ApiResult<ReportDto> =
        safeApiCall { api.report(episodeId, REPORT_LIMIT, REPORT_TARGET) }

    suspend fun readFile(uri: Uri): PickedFile? = withContext(Dispatchers.IO) {
        try {
            val bytes = context.contentResolver.openInputStream(uri)?.use { it.readBytes() }
                ?: return@withContext null
            PickedFile(displayName(uri), bytes)
        } catch (e: IOException) {
            null
        } catch (e: SecurityException) {
            null
        }
    }

    suspend fun analyze(
        file: PickedFile,
        title: String,
        season: Int?,
        number: Int?,
    ): ApiResult<EpisodeDto> {
        if (file.bytes.size > MAX_UPLOAD_BYTES) {
            return ApiResult.Error("Файл слишком большой (максимум 2 МБ)")
        }
        val textType = "text/plain; charset=utf-8".toMediaType()
        val filePart = MultipartBody.Part.createFormData(
            "file",
            file.name,
            file.bytes.toRequestBody("application/octet-stream".toMediaType()),
        )
        return safeApiCall(validationMessage = "В файле не найден текст субтитров") {
            api.analyze(
                filePart,
                title.toRequestBody(textType),
                season?.toString()?.toRequestBody(textType),
                number?.toString()?.toRequestBody(textType),
            )
        }
    }

    private fun displayName(uri: Uri): String {
        context.contentResolver
            .query(uri, arrayOf(OpenableColumns.DISPLAY_NAME), null, null, null)
            ?.use { cursor ->
                if (cursor.moveToFirst()) {
                    val index = cursor.getColumnIndex(OpenableColumns.DISPLAY_NAME)
                    if (index >= 0) return cursor.getString(index)
                }
            }
        return "subtitles.srt"
    }

    private companion object {
        const val MAX_UPLOAD_BYTES = 2_000_000
        const val REPORT_LIMIT = 50
        const val REPORT_TARGET = 0.95
    }
}