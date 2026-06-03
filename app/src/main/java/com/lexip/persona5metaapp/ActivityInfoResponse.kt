package com.lexip.persona5metaapp

import com.google.gson.annotations.SerializedName

data class ActivityScore(
    val percentage: Int? = 0
)

data class ActivityInfoResponse(
    val timestamp: String?,
    val productivity: ActivityScore,
    val leisure: ActivityScore,
    @SerializedName("social_life") val socialLife: ActivityScore
)