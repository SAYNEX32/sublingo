package com.sublingo.app

import android.content.Context
import com.sublingo.app.data.local.TokenStore
import com.sublingo.app.data.remote.ApiConfig
import com.sublingo.app.data.remote.ApiService
import com.sublingo.app.data.remote.AuthInterceptor
import com.sublingo.app.data.repository.AuthRepository
import com.sublingo.app.data.repository.EpisodeRepository
import com.sublingo.app.data.repository.LearningRepository
import java.util.concurrent.TimeUnit
import kotlinx.serialization.json.Json
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.kotlinx.serialization.asConverterFactory

class AppContainer(context: Context) {
    private val tokenStore = TokenStore(context)

    private val json = Json { ignoreUnknownKeys = true }

    private val client = OkHttpClient.Builder()
        .addInterceptor(AuthInterceptor(tokenStore))
        .addInterceptor(
            HttpLoggingInterceptor().apply { level = HttpLoggingInterceptor.Level.BASIC }
        )
        .connectTimeout(15, TimeUnit.SECONDS)
        .readTimeout(120, TimeUnit.SECONDS)
        .build()

    private val retrofit = Retrofit.Builder()
        .baseUrl(ApiConfig.BASE_URL)
        .client(client)
        .addConverterFactory(json.asConverterFactory("application/json".toMediaType()))
        .build()

    private val api: ApiService = retrofit.create(ApiService::class.java)

    val authRepository = AuthRepository(api, tokenStore)
    val episodeRepository = EpisodeRepository(api, context.applicationContext)
    val learningRepository = LearningRepository(api, json)
}