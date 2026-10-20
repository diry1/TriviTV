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
import android.content.Intent
import android.content.ActivityNotFoundException
import android.webkit.WebResourceError
import android.webkit.WebResourceRequest
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.LinearLayout

/** Android TV proof of concept wrapping the existing browser-local game. */
class MainActivity : Activity() {
 private lateinit var web: WebView
 private var currentOrigin = ""
 private val liveUrl = "https://trivitv-ua-europe-test.jauntysloth128.chatgpt.site/"
 private val localUrl = "https://appassets.androidplatform.net/"
 private var offline = false
 private var loaded = false
 private var generation = 0
 private var menuDialog: android.app.AlertDialog? = null
 @SuppressLint("SetJavaScriptEnabled")
 override fun onCreate(savedInstanceState: Bundle?) {
  super.onCreate(savedInstanceState)
  val root = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL; setBackgroundColor(Color.rgb(16,19,35)) }
  window.decorView.systemUiVisibility = android.view.View.SYSTEM_UI_FLAG_FULLSCREEN or android.view.View.SYSTEM_UI_FLAG_HIDE_NAVIGATION or android.view.View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
  web=WebView(this).apply {
   setBackgroundColor(Color.rgb(16,19,35))
   settings.javaScriptEnabled=true
   settings.domStorageEnabled=true
   settings.textZoom=100
   settings.useWideViewPort=true
   settings.loadWithOverviewMode=true
   settings.setSupportZoom(false)
   settings.allowFileAccess=false
   settings.allowContentAccess=false
   settings.mixedContentMode=android.webkit.WebSettings.MIXED_CONTENT_NEVER_ALLOW
   settings.setSupportMultipleWindows(false)
   webChromeClient=WebChromeClient()
   webViewClient=object : WebViewClient() {
    override fun shouldOverrideUrlLoading(view: WebView, request: WebResourceRequest): Boolean {
     if(origin(request.url) == currentOrigin) return false
     if(request.hasGesture() && request.isForMainFrame && request.url.scheme in listOf("http", "https")) {
      try { startActivity(Intent(Intent.ACTION_VIEW, request.url)) }
      catch (_: ActivityNotFoundException) { android.widget.Toast.makeText(this@MainActivity,"Джерела та ліцензію наведено в Credits.",android.widget.Toast.LENGTH_LONG).show() }
     }
     return true
    }
    override fun onPageFinished(view: WebView, url: String) {
     loaded = true
     web.requestFocus()
     web.evaluateJavascript("(()=>{const s=document.createElement('style');s.textContent='.language-picker{display:none!important}';document.head.appendChild(s);setTimeout(()=>{if(document.activeElement===document.body)document.querySelector('button:not(:disabled),a')?.focus()},500)})()",null)
    }
    override fun shouldInterceptRequest(view: WebView, request: WebResourceRequest): android.webkit.WebResourceResponse? {
     if(request.url.host != "appassets.androidplatform.net" || request.url.scheme != "https") return null
     val path = if(request.url.path=="/") "index.html" else request.url.path.orEmpty().removePrefix("/")
     if(path.split('/').any { it==".." || it.isBlank() } || path.contains('\\')) return missing()
     return try {
      val mime=when(path.substringAfterLast('.')) { "js"->"text/javascript";"css"->"text/css";"json"->"application/json";"txt"->"text/plain";else->"text/html" }
      android.webkit.WebResourceResponse(mime,"UTF-8",200,"OK",mapOf("Cache-Control" to "no-cache"),assets.open("web/$path"))
     } catch (_: Exception) { missing() }
    }
    override fun onReceivedHttpError(view: WebView, request: WebResourceRequest, response: android.webkit.WebResourceResponse) {
     if(request.isForMainFrame && !offline && response.statusCode>=400)web.post { openGame(true) }
    }
    override fun onReceivedError(view: WebView, request: WebResourceRequest, error: WebResourceError) {
     if(request.isForMainFrame && !offline) web.post { openGame(true) }
    }
   }
  }
  // The game occupies the full TV screen. Settings are reached with Back/Menu.
  root.addView(web,LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,0,1f))
  setContentView(root)
  if(Build.VERSION.SDK_INT >= 33) {
   onBackInvokedDispatcher.registerOnBackInvokedCallback(android.window.OnBackInvokedDispatcher.PRIORITY_DEFAULT) { handleBack() }
  }
  connectToServer()
 }
 private fun origin(uri: Uri): String = "${uri.scheme}://${uri.host}:${uri.port}"
 private fun missing() = android.webkit.WebResourceResponse("text/plain","UTF-8",404,"Not Found",emptyMap(),java.io.ByteArrayInputStream("Not found".toByteArray()))
 private fun connectToServer() { openGame(false) }
 private fun openGame(local: Boolean) {
  generation++; val epoch=generation; offline=local; loaded=false
  val url=if(local)localUrl else liveUrl
  currentOrigin=origin(Uri.parse(url));web.stopLoading();web.loadUrl(url+"?language=uk");web.requestFocus()
  if(!local)web.postDelayed({ if(generation==epoch && !loaded)openGame(true) },12000)
 }
 private fun showMenu() {
  if(menuDialog?.isShowing==true)return
  menuDialog=android.app.AlertDialog.Builder(this)
   .setTitle("TriviTV POC · "+if(offline)"Локальна версія" else "Онлайн")
   .setItems(arrayOf("Продовжити","Оновити сторінку","Онлайн: остання версія","Локальна версія: 916 запитань","Вийти")) { _, item ->
    when(item) {1->web.reload();2->openGame(false);3->openGame(true);4->finish()};web.requestFocus()
   }.create()
  menuDialog?.show()
 }
 override fun dispatchKeyEvent(event: KeyEvent): Boolean {
  if(menuDialog?.isShowing==true)return super.dispatchKeyEvent(event)
  if(event.keyCode==KeyEvent.KEYCODE_MENU){if(event.action==KeyEvent.ACTION_DOWN && event.repeatCount==0)showMenu();return true}
  val key=when(event.keyCode){
   KeyEvent.KEYCODE_DPAD_UP->"ArrowUp";KeyEvent.KEYCODE_DPAD_DOWN->"ArrowDown"
   KeyEvent.KEYCODE_DPAD_LEFT->"ArrowLeft";KeyEvent.KEYCODE_DPAD_RIGHT->"ArrowRight"
   KeyEvent.KEYCODE_DPAD_CENTER,KeyEvent.KEYCODE_ENTER,KeyEvent.KEYCODE_NUMPAD_ENTER->"Enter"
   KeyEvent.KEYCODE_MEDIA_PLAY_PAUSE->"MediaPlayPause";else->null
  }
  if(key!=null){
   if(event.action==KeyEvent.ACTION_DOWN && !(key in listOf("Enter","MediaPlayPause") && event.repeatCount>0)){
    val script="(()=>{if(window.TriviTVRemote){window.TriviTVRemote.key('$key',${event.repeatCount>0});return;}if('$key'==='Enter'){const a=document.activeElement;if(a && a!==document.body && a.click && !a.disabled)a.click();return;}document.dispatchEvent(new KeyboardEvent('keydown',{key:'$key',bubbles:true,cancelable:true,repeat:${event.repeatCount>0}}))})()"
    web.evaluateJavascript(script,null)
   };return true
  }
  return super.dispatchKeyEvent(event)
 }
 @Deprecated("Legacy back navigation for the prototype")
 @SuppressLint("GestureBackNavigation") // API 33+ is handled by the registered OnBackInvokedCallback above.
 override fun onBackPressed() { handleBack() }
 private fun handleBack() {
  web.evaluateJavascript("Boolean(window.TriviTVRemote && (document.body.dataset.screen==='settings'||document.body.dataset.screen==='credits'||document.querySelector('.tv-dialog')))") { handled ->
   if(handled=="true")web.evaluateJavascript("window.TriviTVRemote.back()",null) else showMenu()
  }
 }
 override fun onDestroy() { menuDialog?.dismiss();web.destroy(); super.onDestroy() }
}
