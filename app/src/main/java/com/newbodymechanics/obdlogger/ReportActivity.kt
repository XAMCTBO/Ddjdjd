package com.newbodymechanics.obdlogger

import android.annotation.SuppressLint
import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.print.PrintAttributes
import android.print.PrintManager
import android.webkit.JavascriptInterface
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.appcompat.app.AppCompatActivity

/**
 * Shows an AI diagnostic report in its own screen, so opening it doesn't unload
 * the logger page (and its live Bluetooth session). Android WebView ignores
 * window.print(), so the report's "PDF / Print" button calls AndroidPrint.print(),
 * which hands the page to the system print dialog (which includes "Save as PDF").
 */
class ReportActivity : AppCompatActivity() {

    private lateinit var webView: WebView

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        webView = WebView(this)
        setContentView(webView)
        title = "Diagnostic report"
        webView.settings.javaScriptEnabled = true
        webView.webViewClient = WebViewClient()
        // Only the print helper is exposed here - NOT the Bluetooth bridge.
        webView.addJavascriptInterface(PrintBridge(), "AndroidPrint")
        webView.loadUrl(intent.getStringExtra(EXTRA_URL) ?: return finish())
    }

    inner class PrintBridge {
        @JavascriptInterface
        fun print() {
            runOnUiThread {
                val pm = getSystemService(Context.PRINT_SERVICE) as PrintManager
                pm.print("OBD diagnostic report", webView.createPrintDocumentAdapter("obd-report"),
                    PrintAttributes.Builder().setMediaSize(PrintAttributes.MediaSize.ISO_A4).build())
            }
        }
    }

    companion object {
        const val EXTRA_URL = "url"

        fun open(context: Context, url: String) {
            context.startActivity(Intent(context, ReportActivity::class.java).putExtra(EXTRA_URL, url))
        }
    }
}
