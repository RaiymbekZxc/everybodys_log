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
        appWidgetManager.updateAppWidget(appWidgetId, views)
    }
}