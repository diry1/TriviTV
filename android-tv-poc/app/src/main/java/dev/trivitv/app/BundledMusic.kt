package dev.trivitv.app

import android.app.Activity
import android.media.AudioAttributes
import android.media.MediaPlayer
import android.webkit.JavascriptInterface
import android.webkit.WebView
import org.json.JSONObject

/** Only packaged music assets are exposed; all MediaPlayer work stays on the UI thread. */
class BundledMusic(private val activity: Activity, private val web: WebView, private val local: () -> Boolean) {
 private var player: MediaPlayer? = null
 private var ready=false
 private var wanted=false
 private var foreground=true
 private var looping=false
 private var level=.42f
 private var path=""
 private val allowed=activity.assets.list("web/audio").orEmpty().filter { it.endsWith(".ogg") }.map { "audio/$it" }.toSet()
 private fun emit(event: String, value: Double=0.0, message: String="") {
  val args=listOf(event,path).joinToString(",") { JSONObject.quote(it) }
  web.evaluateJavascript("window.TriviTVAudio?.nativeEvent($args,$value,${JSONObject.quote(message)})",null)
 }
 private fun position()=if(ready)runCatching { player?.currentPosition?.div(1000.0)?:0.0 }.getOrDefault(0.0) else 0.0
 private fun begin() {
  if(!ready||!wanted||!foreground)return
  runCatching { player?.let { if(!it.isPlaying){it.start();emit("playing",position())} } }.onFailure { emit("error",message=it.message?:"Playback failed");clear() }
 }
 @JavascriptInterface fun load(source: String) { activity.runOnUiThread {
  if(!local()||source !in allowed)return@runOnUiThread
  clear();path=source
  try {
   val next=MediaPlayer();player=next
   next.setAudioAttributes(AudioAttributes.Builder().setUsage(AudioAttributes.USAGE_GAME).setContentType(AudioAttributes.CONTENT_TYPE_MUSIC).build())
   activity.assets.openFd("web/$source").use { next.setDataSource(it.fileDescriptor,it.startOffset,it.length) }
   next.setOnPreparedListener { current ->
    if(player===current){ready=true;current.isLooping=looping;current.setVolume(level,level);emit("prepared",current.duration/1000.0);begin()}
   }
   next.setOnCompletionListener { current -> if(player===current){wanted=false;emit("ended",position())} }
   next.setOnErrorListener { current,what,extra ->
    if(player===current){emit("error",message="Android audio error $what/$extra");clear()};true
   }
   next.prepareAsync()
  } catch(error: Exception) { emit("error",message=error.message?:"Cannot load bundled music");clear() }
 } }
 @JavascriptInterface fun play() { activity.runOnUiThread { if(local()){wanted=true;begin()} } }
 @JavascriptInterface fun pause() { activity.runOnUiThread { wanted=false;pausePlayer() } }
 @JavascriptInterface fun volume(value: Double) { activity.runOnUiThread { level=value.toFloat().coerceIn(0f,1f);if(ready)player?.setVolume(level,level) } }
 @JavascriptInterface fun loop(value: Boolean) { activity.runOnUiThread { looping=value;if(ready)player?.isLooping=value } }
 @JavascriptInterface fun seek(seconds: Double) { activity.runOnUiThread { if(ready&&seconds.isFinite())player?.seekTo((seconds*1000).toInt().coerceIn(0,player?.duration?:0)) } }
 private fun pausePlayer() { if(ready){runCatching { if(player?.isPlaying==true)player?.pause() };emit("paused",position())} }
 fun setForeground(value: Boolean) { foreground=value;if(value)begin() else pausePlayer() }
 fun clear() { ready=false;wanted=false;player?.apply { setOnPreparedListener(null);setOnCompletionListener(null);setOnErrorListener(null);release() };player=null }
}
