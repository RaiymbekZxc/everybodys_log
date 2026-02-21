package com.lexip.persona5metaapp

data class WeatherResponse(
    val current: CurrentWeather?
)

data class CurrentWeather(
    val weather_code: Int
)
