package com.lexip.persona5metaapp

import android.app.PendingIntent
import android.appwidget.AppWidgetManager
import android.appwidget.AppWidgetProvider
import android.content.Context
import android.content.Intent
import android.util.Log
import android.widget.RemoteViews
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import com.lexip.persona5metaapp.network.SessionManager

class ActivityLogWidgetProvider : AppWidgetProvider() {

    override fun onUpdate(
        context: Context,
        appWidgetManager: AppWidgetManager,
        appWidgetIds: IntArray
    ) {
        for (appWidgetId in appWidgetIds) {
            updateAppWidget(context, appWidgetManager, appWidgetId)
            Log.d("PersonaWidget", "Запрос обновления данных для ID: $appWidgetId")
        }
    }

    private fun updateAppWidget(
        context: Context,
        appWidgetManager: AppWidgetManager,
        appWidgetId: Int
    ) {
        val views = RemoteViews(context.packageName, R.layout.activity_log_widget)

        val emptyIntent = Intent().apply {
            action = "com.lexip.persona5metaapp.EMPTY_ACTION"
        }

        val pendingIntent = PendingIntent.getBroadcast(
            context,
            0,
            emptyIntent,
            PendingIntent.FLAG_IMMUTABLE
        )

        views.setOnClickPendingIntent(R.id.activity_log_root, pendingIntent)

        CoroutineScope(Dispatchers.IO).launch {
            try {
                val savedToken = getSavedToken(context)

                if (savedToken.isBlank()) {
                    Log.e(
                        "PersonaWidget",
                        "Token is empty. User is not logged in Android SharedPreferences."
                    )
                    return@launch
                }

                val retrofit = Retrofit.Builder()
                    .baseUrl("https://everybodys-log.onrender.com/")
                    .addConverterFactory(GsonConverterFactory.create())
                    .build()

                val api = retrofit.create(ActivityApiService::class.java)

                val token = "Bearer $savedToken"
                val info = api.getActivityInfo(token)

                val productivity = info.productivity.percentage ?: 0
                val socialLife = info.socialLife.percentage ?: 0
                val leisure = info.leisure.percentage ?: 0

                val prodResId = context.resources.getIdentifier(
                    "activity_log_productivity_$productivity",
                    "drawable",
                    context.packageName
                )

                val socialResId = context.resources.getIdentifier(
                    "activity_log_sociallife_$socialLife",
                    "drawable",
                    context.packageName
                )

                val leisureResId = context.resources.getIdentifier(
                    "activity_log_leisure_$leisure",
                    "drawable",
                    context.packageName
                )

                if (prodResId != 0) {
                    views.setImageViewResource(R.id.productivity_percent, prodResId)
                }

                if (socialResId != 0) {
                    views.setImageViewResource(R.id.social_life_percent, socialResId)
                }

                if (leisureResId != 0) {
                    views.setImageViewResource(R.id.leisure_percent, leisureResId)
                }

                appWidgetManager.updateAppWidget(appWidgetId, views)

                Log.d("PersonaWidget", "Виджет успешно обновлен данными из API")

            } catch (e: Exception) {
                Log.e("PersonaWidget", "Ошибка при обновлении виджета: ${e.message}")
            }
        }
    }

    private fun getSavedToken(context: Context): String {
        return SessionManager.getToken(context)
    }
}