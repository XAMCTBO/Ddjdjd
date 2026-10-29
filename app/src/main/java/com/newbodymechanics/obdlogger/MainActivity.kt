package com.newbodymechanics.obdlogger

import android.annotation.SuppressLint
import android.os.Bundle
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.appcompat.app.AppCompatActivity

/**
 * Thin native shell. All the UI, gauges, parsing and recording logic lives in
 * obd-logger.html (bundled as an asset, see app/src/main/assets/). This class
 * only supplies what a browser can't: classic Bluetooth (SPP) and a BLE path
 * that isn't limited by Web Bluetooth's browser restrictions.
 *
 * Bundled as an asset for now (no hosting needed to get this working). Once
 * the page is hosted somewhere with HTTPS, switch LOGGER_URL below to that
 * address instead -- then updating the page doesn't need a new APK build.
 */
class MainActivity : AppCompatActivity() {

    private val LOGGER_URL = "file:///android_asset/obd-logger.html"
    // private val LOGGER_URL = "https://yoursite.com/obd/obd-logger.html"

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val webView = findViewById<WebView>(R.id.webview)
        webView.settings.javaScriptEnabled = true
        webView.settings.domStorageEnabled = true
        // The page loads from file:// (bundled asset); these let its cloud-sync
        // fetch() calls still reach your https:// server.
        @Suppress("DEPRECATION")
        webView.settings.allowUniversalAccessFromFileURLs = true
        @Suppress("DEPRECATION")
        webView.settings.allowFileAccessFromFileURLs = true
        webView.webViewClient = WebViewClient()

        val bridge = BtBridge(this, webView)
        webView.addJavascriptInterface(bridge, "AndroidBT")

        webView.loadUrl(LOGGER_URL)
    }

    override fun onRequestPermissionsResult(
        requestCode: Int, permissions: Array<out String>, grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        // The page checks AndroidBT.hasPermission() again after the user retries,
        // so nothing else is needed here.
    }
}
