package com.lexip.persona5metaapp

import android.appwidget.AppWidgetManager
import android.content.ComponentName
import android.content.Context
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import com.google.android.gms.location.LocationServices
import kotlinx.coroutines.tasks.await
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

class WeatherWorker(
    appContext: Context,
    params: WorkerParameters
) : CoroutineWorker(appContext, params) {

    override suspend fun doWork(): Result {
        return try {

            val locationClient =
                LocationServices.getFusedLocationProviderClient(applicationContext)

            val location = try {
                locationClient.lastLocation.await()
            } catch (e: SecurityException) {
                null
            }

            if (location == null) {
                return Result.retry()
            }

            val lat = location.latitude
            val lon = location.longitude

            val retrofit = Retrofit.Builder()
                .baseUrl("https://api.open-meteo.com/")
                .addConverterFactory(GsonConverterFactory.create())
                .build()

            val api = retrofit.create(WeatherApi::class.java)

            val weather = api.getWeather(lat, lon)

            val weatherCode = weather.current?.weather_code ?: 0

            applicationContext
                .getSharedPreferences("weather", Context.MODE_PRIVATE)
                .edit()
                .putInt("code", weatherCode)
                .putFloat("lat", lat.toFloat())
                .putFloat("lon", lon.toFloat())
                .apply()

            val appWidgetManager =
                AppWidgetManager.getInstance(applicationContext)

            val componentName =
                ComponentName(applicationContext, PersonaDateWidgetProvider::class.java)

            val widgetIds =
                appWidgetManager.getAppWidgetIds(componentName)

            if (widgetIds.isNotEmpty()) {
                PersonaDateWidgetProvider.updateAllWidgets(
                    applicationContext,
                    appWidgetManager,
                    widgetIds
                )
            }

            Result.success()

        } catch (e: Exception) {
            e.printStackTrace()
            Result.retry()
        }
    }
}