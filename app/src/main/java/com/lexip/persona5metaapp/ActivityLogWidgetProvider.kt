package com.lexip.persona5metaapp

import android.app.PendingIntent
import android.appwidget.AppWidgetManager
import android.appwidget.AppWidgetProvider
import android.content.Context
import android.content.Intent
import android.util.Log
import android.widget.RemoteViews

class ActivityLogWidgetProvider : AppWidgetProvider() {
    override fun onUpdate(
        context: Context,
        appWidgetManager: AppWidgetManager,
        appWidgetIds: IntArray
    ) {
        for (appWidgetId in appWidgetIds) {
            updateAppWidget(context, appWidgetManager, appWidgetId)
            Log.d("PersonaWidget", "Апдейт")
        }
    }

    private fun updateAppWidget(
        context: Context,
        appWidgetManager: AppWidgetManager,
        appWidgetId: Int
    ){
        val views = RemoteViews(context.packageName, R.layout.activity_log_widget)

        val emptyIntent = Intent().apply{
            action = "com.lexip.persona5metaapp.EMPTY_ACTION"
        }
        val pendingIntent = PendingIntent.getBroadcast(
            context,
            0,
            emptyIntent,
            PendingIntent.FLAG_IMMUTABLE
        )
        views.setOnClickPendingIntent(R.id.activity_log_root, pendingIntent)

        // Обновление процентов
        var productivity = 69
        var socialLife = 68
        var leisure = 67

        val currentProductivityPercent = "activity_log_productivity_${productivity}"
        val productivityResId = context.resources.getIdentifier(currentProductivityPercent, "drawable",context.packageName)

        val currentSocialLifePercent = "activity_log_sociallife_${socialLife}"
        val socialLifeResId = context.resources.getIdentifier(currentSocialLifePercent, "drawable",context.packageName)

        val currentLeisurePercent = "activity_log_leisure_${leisure}"
        val leisureResId = context.resources.getIdentifier(currentLeisurePercent, "drawable",context.packageName)

        if (productivityResId != 0 && socialLifeResId != 0 && leisureResId != 0){
            views.setImageViewResource(R.id.productivity_percent, productivityResId)
            views.setImageViewResource(R.id.social_life_percent, socialLifeResId)
            views.setImageViewResource(R.id.leisure_percent, leisureResId)
        }

        appWidgetManager.updateAppWidget(appWidgetId, views)
    }
}