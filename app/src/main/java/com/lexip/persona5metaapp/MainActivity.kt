package com.lexip.persona5metaapp

import android.Manifest
import android.content.pm.PackageManager
import android.os.Bundle
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import android.webkit.WebView
import android.webkit.JavascriptInterface
import android.content.Context
import android.webkit.WebViewClient
import com.lexip.persona5metaapp.network.SessionManager

class MainActivity : AppCompatActivity() {

    private val locationPermissionLauncher =
        registerForActivityResult(ActivityResultContracts.RequestMultiplePermissions()) { result ->
            val coarseGranted = result[Manifest.permission.ACCESS_COARSE_LOCATION] == true
            val fineGranted = result[Manifest.permission.ACCESS_FINE_LOCATION] == true
        }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val webView = WebView(this)
        setContentView(webView)

        webView.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
            loadWithOverviewMode = true
            useWideViewPort = true
        }

        webView.webViewClient = WebViewClient()

        webView.addJavascriptInterface(
            WebAppInterface(this),
            "AndroidInterface"
        )

        webView.loadUrl("file:///android_asset/frontend/views/login.html")

        requestLocationPermissionsIfNeeded()
    }

    private fun requestLocationPermissionsIfNeeded() {
        val coarse = ContextCompat.checkSelfPermission(
            this,
            Manifest.permission.ACCESS_COARSE_LOCATION
        ) == PackageManager.PERMISSION_GRANTED

        val fine = ContextCompat.checkSelfPermission(
            this,
            Manifest.permission.ACCESS_FINE_LOCATION
        ) == PackageManager.PERMISSION_GRANTED

        if (!coarse && !fine) {
            locationPermissionLauncher.launch(
                arrayOf(
                    Manifest.permission.ACCESS_COARSE_LOCATION,
                    Manifest.permission.ACCESS_FINE_LOCATION
                )
            )
        }
    }
}

class WebAppInterface(private val context: Context) {
    @JavascriptInterface
    fun saveTokenToAndroid(token: String) {
        android.util.Log.d("PersonaWidget", "TOKEN FROM JS: $token")
        SessionManager.saveToken(context, token)
    }
}