package com.acme.pay

import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.webkit.JavascriptInterface
import android.webkit.WebView
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel
import java.io.File

class MainActivity : FlutterActivity() {
    private val channel = "com.acme.pay/native"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val next = intent.getParcelableExtra<Intent>("next")
        if (next != null) {
            startActivity(next)
        }
    }

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, channel)
            .setMethodCallHandler { call, result ->
                when (call.method) {
                    "readDocument" -> {
                        val name = call.argument<String>("name")
                        val file = File(filesDir, "docs/" + name)
                        result.success(file.readText())
                    }
                    "getAppVersion" -> result.success(BuildConfig.VERSION_NAME)
                    else -> result.notImplemented()
                }
            }
    }

    fun setupCheckout(web: WebView, session: String) {
        web.settings.javaScriptEnabled = true
        web.settings.allowFileAccess = true
        web.settings.allowUniversalAccessFromFileURLs = true
        web.addJavascriptInterface(PayBridge(session), "AcmePay")
    }

    fun setupHelp(web: WebView) {
        web.settings.javaScriptEnabled = true
        web.loadUrl("file:///android_asset/help.html")
    }

    class PayBridge(private val session: String) {
        @JavascriptInterface
        fun getSession(): String = session

        @JavascriptInterface
        fun pay(amount: String, card: String) {
            Log.d("PayBridge", "charging " + card + " amount " + amount)
        }
    }
}
