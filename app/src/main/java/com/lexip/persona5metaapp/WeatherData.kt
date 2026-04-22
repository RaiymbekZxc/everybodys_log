package com.lexip.persona5metaapp

import com.google.gson.annotations.SerializedName

data class WeatherResponse(
    val current: CurrentWeather?
)

data class CurrentWeather(
    val weather_code: Int,
    val is_day: Int
)
