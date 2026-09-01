package com.allmedias.notifier

import android.content.Context
import android.service.notification.NotificationListenerService
import android.service.notification.StatusBarNotification
import android.util.Log
import org.json.JSONObject
import java.io.OutputStreamWriter
import java.net.HttpURLConnection
import java.net.URL
import kotlin.concurrent.thread

class NotificationListener : NotificationListenerService() {

    // Adicione ou remova os pacotes dos bancos que você quer capturar.
    private val pacotesMonitorados = listOf(
        "com.nu.production",       // Nubank
        "com.itau",                // Itaú
        "br.com.intermedium",      // Inter
        "br.com.bb.android",       // Banco do Brasil
        "com.whatsapp",            // WhatsApp (opcional, só para facilitar os testes iniciais)
        "com.google.android.gm"    // Gmail (opcional, para testes rápidos)
    )

    override fun onNotificationPosted(sbn: StatusBarNotification) {
        val packageName = sbn.packageName

        // Se o pacote da notificação não for um dos bancos acima, ignoramos e não gastamos CPU
        val isMonitorado = pacotesMonitorados.any { packageName.contains(it, ignoreCase = true) }
        
        if (isMonitorado) {
            val extras = sbn.notification.extras
            val title = extras.getString("android.title") ?: ""
            val text = extras.getCharSequence("android.text")?.toString() ?: ""

            // Monta o JSON perfeitinho pro Django ler
            val json = JSONObject().apply {
                put("app", packageName)
                put("title", title)
                put("text", text)
                put("timestamp", sbn.postTime)
            }

            Log.d("AllMediasNotifier", "Interceptado: $json")
            enviarParaDjango(json.toString())
        }
    }

    private fun enviarParaDjango(jsonPayload: String) {
        // Envia em segundo plano para não travar a leitura do celular
        thread {
            try {
                val prefs = getSharedPreferences("prefs", Context.MODE_PRIVATE)
                val urlString = prefs.getString("webhook_url", "") ?: ""
                
                if (urlString.isEmpty() || !urlString.startsWith("http")) return@thread

                val url = URL(urlString)
                val conn = url.openConnection() as HttpURLConnection
                conn.requestMethod = "POST"
                conn.setRequestProperty("Content-Type", "application/json; charset=UTF-8")
                conn.doOutput = true

                OutputStreamWriter(conn.outputStream).use { writer ->
                    writer.write(jsonPayload)
                    writer.flush()
                }

                val responseCode = conn.responseCode
                Log.d("AllMediasNotifier", "Webhook disparado! Código: $responseCode")
                conn.disconnect()
            } catch (e: Exception) {
                Log.e("AllMediasNotifier", "Erro ao disparar webhook: ${e.message}")
            }
        }
    }
}
