package com.allmedias.notifier

import android.app.Activity
import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.provider.Settings
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast

class MainActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Criando a interface diretamente no código para você não precisar mexer com arquivos XML de layout!
        val layout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(60, 100, 60, 60)
        }

        val title = TextView(this).apply {
            text = "Ponte de Notificações - AllMedias"
            textSize = 22f
            setPadding(0, 0, 0, 80)
        }

        val urlInput = EditText(this).apply {
            hint = "Digite a URL do Webhook (Django)"
            val prefs = getSharedPreferences("prefs", Context.MODE_PRIVATE)
            setText(prefs.getString("webhook_url", "https://seu-django.com/webhook/"))
        }

        val saveButton = Button(this).apply {
            text = "Salvar URL do Webhook"
            setOnClickListener {
                getSharedPreferences("prefs", Context.MODE_PRIVATE)
                    .edit()
                    .putString("webhook_url", urlInput.text.toString())
                    .apply()
                Toast.makeText(this@MainActivity, "URL Salva com sucesso!", Toast.LENGTH_SHORT).show()
            }
        }

        val permButton = Button(this).apply {
            text = "Abrir Configuração de Permissão"
            setOnClickListener {
                // Abre a tela nativa do Android para habilitar a escuta de notificações
                startActivity(Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS))
            }
        }

        layout.addView(title)
        layout.addView(urlInput)
        layout.addView(saveButton)
        
        val espaco = TextView(this).apply { setPadding(0, 50, 0, 50) }
        layout.addView(espaco)
        
        layout.addView(permButton)

        setContentView(layout)
    }
}
