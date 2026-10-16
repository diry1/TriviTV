package dev.trivitv.app

import android.annotation.SuppressLint
import android.app.Activity
import android.graphics.Color
import android.net.Uri
import android.os.Bundle
import android.os.Build
import android.webkit.WebChromeClient
import android.view.KeyEvent
import android.view.ViewGroup
import android.view.inputmethod.InputMethodManager
import android.content.Context
import android.webkit.WebResourceError
import android.webkit.WebResourceRequest
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.TextView

/** Development Android TV shell. The shared game and controller are served by the session server. */
class MainActivity : Activity() {
 private lateinit var web: WebView
 private lateinit var address: EditText
 private lateinit var status: TextView
 private var currentOrigin = ""
 @SuppressLint("SetJavaScriptEnabled")
 override fun onCreate(savedInstanceState: Bundle?) {
  super.onCreate(savedInstanceState)
  val root = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL; setBackgroundColor(Color.rgb(16,19,35)) }
  val toolbar = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL; setPadding(16,4,16,4) }
  address = EditText(this).apply {
   setSingleLine(true); textSize=12f; setTextColor(Color.WHITE)
   hint="Session server address"; contentDescription="Session server address"
   setText(getPreferences(Context.MODE_PRIVATE).getString("server", "http://10.0.2.2:3000"))
   inputType=android.text.InputType.TYPE_CLASS_TEXT or android.text.InputType.TYPE_TEXT_VARIATION_URI
  }
  val connect = Button(this).apply { text="Connect"; setOnClickListener { connectToServer() } }
  toolbar.addView(address, LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT,1f))
  toolbar.addView(connect)
  status=TextView(this).apply { text="Prototype • Menu on remote focuses server address"; textSize=10f; setTextColor(Color.LTGRAY); setPadding(16,0,16,4) }
  web=WebView(this).apply {
   setBackgroundColor(Color.rgb(16,19,35))
   settings.javaScriptEnabled=true
   settings.domStorageEnabled=true
   settings.allowFileAccess=false
   settings.allowContentAccess=false
   settings.mixedContentMode=android.webkit.WebSettings.MIXED_CONTENT_NEVER_ALLOW
   settings.setSupportMultipleWindows(false)
   webChromeClient=WebChromeClient()
   webViewClient=object : WebViewClient() {
    override fun shouldOverrideUrlLoading(view: WebView, request: WebResourceRequest): Boolean = origin(request.url) != currentOrigin
    override fun onPageFinished(view: WebView, url: String) { status.text="TriviTV prototype • Menu: server settings • Back: previous screen" }
    override fun onReceivedError(view: WebView, request: WebResourceRequest, error: WebResourceError) {
     if(request.isForMainFrame) status.text="Cannot reach the session server. Check its address and Wi-Fi, then Connect."
    }
   }
  }
  root.addView(toolbar); root.addView(status)
  root.addView(web,LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,0,1f))
  setContentView(root)
  if(Build.VERSION.SDK_INT >= 33) {
   onBackInvokedDispatcher.registerOnBackInvokedCallback(android.window.OnBackInvokedDispatcher.PRIORITY_DEFAULT) { handleBack() }
  }
  connectToServer()
 }
 private fun origin(uri: Uri): String = "${uri.scheme}://${uri.host}:${uri.port}"
 private fun connectToServer() {
  val value=address.text.toString().trim()
  val uri=Uri.parse(value)
  if(uri.scheme !in listOf("http","https") || uri.host.isNullOrBlank() || uri.userInfo != null) {
   status.text="Enter an http or https server address."; return
  }
  currentOrigin=origin(uri)
  getPreferences(Context.MODE_PRIVATE).edit().putString("server",value).apply()
  (getSystemService(Context.INPUT_METHOD_SERVICE) as InputMethodManager).hideSoftInputFromWindow(address.windowToken,0)
  web.loadUrl(value); web.requestFocus()
 }
 override fun dispatchKeyEvent(event: KeyEvent): Boolean {
  val activationKeys = listOf(KeyEvent.KEYCODE_DPAD_CENTER, KeyEvent.KEYCODE_ENTER, KeyEvent.KEYCODE_NUMPAD_ENTER, KeyEvent.KEYCODE_SPACE)
  if(event.action == KeyEvent.ACTION_DOWN && event.repeatCount > 0 && event.keyCode in activationKeys) return true
  if(event.keyCode == KeyEvent.KEYCODE_MEDIA_PLAY_PAUSE && ::web.isInitialized) {
   if(event.action == KeyEvent.ACTION_DOWN && event.repeatCount == 0) {
    web.evaluateJavascript("document.dispatchEvent(new KeyboardEvent('keydown', {key:'MediaPlayPause', bubbles:true}))", null)
   }
   return true
  }
  return super.dispatchKeyEvent(event)
 }
 override fun onKeyDown(keyCode: Int, event: KeyEvent): Boolean {
  if(keyCode==KeyEvent.KEYCODE_MENU) { address.requestFocus(); return true }
  return super.onKeyDown(keyCode,event)
 }
 @Deprecated("Legacy back navigation for the prototype")
 override fun onBackPressed() { handleBack() }
 private fun handleBack() { if(web.canGoBack()) web.goBack() else { address.requestFocus(); status.text="Use Connect to return to the game." } }
 override fun onDestroy() { web.destroy(); super.onDestroy() }
}
