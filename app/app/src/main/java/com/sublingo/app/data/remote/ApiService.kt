package com.sublingo.app.data.remote

import okhttp3.MultipartBody
import okhttp3.RequestBody
import retrofit2.http.Body
import retrofit2.http.Field
import retrofit2.http.FormUrlEncoded
import retrofit2.http.GET
import retrofit2.http.Multipart
import retrofit2.http.POST
import retrofit2.http.Part
import retrofit2.http.Path
import retrofit2.http.Query

interface ApiService {
    @POST("auth/register")
    suspend fun register(@Body body: RegisterRequest): UserDto

    @FormUrlEncoded
    @POST("auth/login")
    suspend fun login(
        @Field("username") email: String,
        @Field("password") password: String,
    ): TokenDto

    @GET("auth/me")
    suspend fun me(): UserDto

    @GET("episodes")
    suspend fun episodes(): List<EpisodeDto>

    @Multipart
    @POST("episodes/analyze")
    suspend fun analyze(
        @Part file: MultipartBody.Part,
        @Part("title") title: RequestBody,
        @Part("season") season: RequestBody?,
        @Part("number") number: RequestBody?,
    ): EpisodeDto

    @GET("episodes/{id}/report")
    suspend fun report(
        @Path("id") id: Int,
        @Query("limit") limit: Int,
        @Query("target") target: Double,
    ): ReportDto
}