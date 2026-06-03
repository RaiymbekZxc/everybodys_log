package com.lexip.persona5metaapp

import com.lexip.persona5metaapp.ActivityInfoResponse
import retrofit2.http.GET
import retrofit2.http.Header

interface ActivityApiService {
    @GET("/api/activity/info")
    suspend fun getActivityInfo(
        @Header("Authorization") token: String
    ): ActivityInfoResponse
}