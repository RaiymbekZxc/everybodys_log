package com.lexip.persona5metaapp

import android.app.AlarmManager
import android.app.PendingIntent
import android.appwidget.AppWidgetManager
import android.appwidget.AppWidgetProvider
import android.content.Context
import android.content.Intent
import android.icu.util.Calendar
import android.widget.RemoteViews
import android.content.ComponentName
import android.os.Build
import android.util.Log
import androidx.work.ExistingPeriodicWorkPolicy
import androidx.work.ExistingWorkPolicy
import androidx.work.OneTimeWorkRequestBuilder
import androidx.work.PeriodicWorkRequestBuilder
import androidx.work.WorkManager
import java.util.concurrent.TimeUnit

class PersonaDateWidgetProvider : AppWidgetProvider() {
    companion object {
        private const val WORK_WEATHER_ONCE = "weather_once"
        private const val WORK_WEATHER_PERIODIC = "weather_periodic"

        fun ensureWeatherWorkScheduled(context: Context){
            val workManager = WorkManager.getInstance(context)

            workManager.enqueueUniqueWork(
                WORK_WEATHER_ONCE,
                ExistingWorkPolicy.REPLACE,
                OneTimeWorkRequestBuilder<WeatherWorker>().build()
            )

            workManager.enqueueUniquePeriodicWork(
                WORK_WEATHER_PERIODIC,
                ExistingPeriodicWorkPolicy.KEEP,
                PeriodicWorkRequestBuilder<WeatherWorker>(30, TimeUnit.MINUTES).build()
            )
        }
        const val ACTION_UPDATE_WIDGET_DAILY = "com.lexip.UPDATE_WIDGET_DAILY"
        fun safeScheduleDailyUpdate(context: Context) {
            val alarmManager = context.getSystemService(Context.ALARM_SERVICE) as AlarmManager
            val calendar = Calendar.getInstance().apply {
                set(Calendar.HOUR_OF_DAY, 0)
                set(Calendar.MINUTE, 0)
                set(Calendar.SECOND, 0)
                add(Calendar.DAY_OF_MONTH, 1)
            }

            val intent = Intent(context, PersonaDateWidgetProvider::class.java).apply {
                action = ACTION_UPDATE_WIDGET_DAILY
            }
            val pendingIntent = PendingIntent.getBroadcast(
                context, 0, intent, PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
            )

            try {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                    if (alarmManager.canScheduleExactAlarms()) {
                        alarmManager.setExactAndAllowWhileIdle(
                            AlarmManager.RTC_WAKEUP,
                            calendar.timeInMillis,
                            pendingIntent
                        )
                    } else {
                        // Здесь можно вывести диалог с переходом в настройки
                        val settingsIntent = Intent(android.provider.Settings.ACTION_REQUEST_SCHEDULE_EXACT_ALARM)
                        settingsIntent.flags = Intent.FLAG_ACTIVITY_NEW_TASK
                        context.startActivity(settingsIntent)
                    }
                } else {
                    alarmManager.setExactAndAllowWhileIdle(
                        AlarmManager.RTC_WAKEUP,
                        calendar.timeInMillis,
                        pendingIntent
                    )
                }
            } catch (e: SecurityException) {
            }
        }

        fun updateAllWidgets(
            applicationContext: Context,
            appWidgetManager: AppWidgetManager,
            widgetIds: IntArray
        ) {
            for (widgetId in widgetIds) {
                PersonaDateWidgetProvider().updateAppWidget(applicationContext, appWidgetManager, widgetId)
            }
        }
    }

    override fun onUpdate(
        context: Context,
        appWidgetManager: AppWidgetManager,
        appWidgetIds: IntArray
    ) {
        for (appWidgetId in appWidgetIds) {
            updateAppWidget(context, appWidgetManager, appWidgetId)
            Log.d("PersonaWidget", "Апдейт")
        }
        ensureWeatherWorkScheduled(context)
        safeScheduleDailyUpdate(context)
    }

    override fun onReceive(context: Context, intent: Intent) {
        Log.d("PersonaWidget", "onReceive ВХОД: ${intent.action}")
        super.onReceive(context, intent)

        val appWidgetManager = AppWidgetManager.getInstance(context)
        val componentName = ComponentName(context, PersonaDateWidgetProvider::class.java)
        val appWidgetIds = appWidgetManager.getAppWidgetIds(componentName)

        when (intent.action) {
            Intent.ACTION_TIME_CHANGED,
            Intent.ACTION_TIMEZONE_CHANGED,
            ACTION_UPDATE_WIDGET_DAILY -> {
                Log.d("PersonaWidget", "onReceive обновление для ${intent.action}")
                onUpdate(context, appWidgetManager, appWidgetIds)
            }
        }
    }

    private fun updateAppWidget(
        context: Context,
        appWidgetManager: AppWidgetManager,
        appWidgetId: Int
    ) {
        val views = RemoteViews(context.packageName, R.layout.persona_date_widget)
        val rightNow = Calendar.getInstance()

        // День
        val day = rightNow.get(Calendar.DAY_OF_MONTH)
        val currentDayBottom = "d${day}b"
        val currentDay = "d${day}"
        val currentDayTop = "d${day}t"

        val dayBottomResId = context.resources.getIdentifier(currentDayBottom, "drawable", context.packageName)
        val dayResId = context.resources.getIdentifier(currentDay, "drawable", context.packageName)
        val dayTopResId = context.resources.getIdentifier(currentDayTop, "drawable", context.packageName)

        if (dayBottomResId != 0 && dayResId != 0 && dayTopResId != 0){
            views.setImageViewResource(R.id.day_bottom, dayBottomResId)
            views.setImageViewResource(R.id.day, dayResId)
            views.setImageViewResource(R.id.day_top, dayTopResId)
        }

        // Месяц
        val month = rightNow.get(Calendar.MONTH)
        var currentMonthBottom = "m${month+1}b"
        var currentMonth = "m${month+1}"
        var currentMonthTop = "m${month+1}t"
        if (day >= 10){
            currentMonthBottom = "mm${month+1}b"
            currentMonth = "mm${month+1}"
            currentMonthTop = "mm${month+1}t"
        }

        val monthBottomResId = context.resources.getIdentifier(currentMonthBottom, "drawable", context.packageName)
        val monthResId = context.resources.getIdentifier(currentMonth, "drawable", context.packageName)
        val monthTopResId = context.resources.getIdentifier(currentMonthTop, "drawable", context.packageName)

        if (monthBottomResId != 0 && monthResId != 0 && monthTopResId != 0){
            views.setImageViewResource(R.id.month_bottom, monthBottomResId)
            views.setImageViewResource(R.id.month, monthResId)
            views.setImageViewResource(R.id.month_top, monthTopResId)
        }

        // День недели
        val week = rightNow.get(Calendar.DAY_OF_WEEK)
        var currentWeekBottom = "w${week}b"
        var currentWeek = "w${week}"
        var currentWeekTop = "w${week}t"

        val weekBottomResId = context.resources.getIdentifier(currentWeekBottom, "drawable", context.packageName)
        val weekResId = context.resources.getIdentifier(currentWeek, "drawable", context.packageName)
        val weekTopResId = context.resources.getIdentifier(currentWeekTop, "drawable", context.packageName)

        if (weekBottomResId != 0 && weekResId != 0 && weekTopResId != 0){
            views.setImageViewResource(R.id.week_bottom, weekBottomResId)
            views.setImageViewResource(R.id.week, weekResId)
            views.setImageViewResource(R.id.week_top, weekTopResId)
        }

        // Иконка погоды
        val prefs = context.getSharedPreferences("weather", Context.MODE_PRIVATE)
        val code = prefs.getInt("code", 0)
        val isDay = prefs.getInt("is_day", 1)
        var weather = when (code) {
            0, 1 -> "sun"
            2, 3, 45, 48 -> "cloud"
            51, 53, 55, 56, 57, 61, 63, 65, 80, 81, 82, 95, 96, 99 -> "rain"
            71, 73, 75, 77, 85, 86 -> "snow"
            else -> "sun"
            // 56, 57 — Freezing drizzle
            // 66, 67 — Freezing rain
            // 96, 99 — Thunderstorm with hail
            // 45, 48 — Fog / Depositing rime fog
        }

        if (weather == "sun" && isDay == 0) weather = "moon"
        Log.d("PersonaWidget", "Loaded: code=$code, isDay=$isDay")

        var currentWeather = "w${weather}"
        if (rightNow.get(Calendar.DAY_OF_MONTH) >= 10) currentWeather = "ww${weather}"

        val weatherResId1 = context.resources.getIdentifier("${currentWeather}1", "drawable", context.packageName)
        val weatherResId2 = context.resources.getIdentifier("${currentWeather}2", "drawable", context.packageName)
        val weatherResId3 = context.resources.getIdentifier("${currentWeather}3", "drawable", context.packageName)

        if (weatherResId1 != 0 && weatherResId2 != 0 && weatherResId3 != 0){
            views.setImageViewResource(R.id.weather1, weatherResId1)
            views.setImageViewResource(R.id.weather2, weatherResId2)
            views.setImageViewResource(R.id.weather3, weatherResId3)
        }

        appWidgetManager.updateAppWidget(appWidgetId, views)
    }
}
