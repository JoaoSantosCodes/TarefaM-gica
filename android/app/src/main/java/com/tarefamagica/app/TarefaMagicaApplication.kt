package com.tarefamagica.app

import android.app.Application
import dagger.hilt.android.HiltAndroidApp
import timber.log.Timber

@HiltAndroidApp
class TarefaMagicaApplication : Application() {
    
    override fun onCreate() {
        super.onCreate()
        
        // Configurar logging
        if (BuildConfig.DEBUG) {
            Timber.plant(Timber.DebugTree())
        }
        
        // Inicializar componentes
        initializeApp()
    }
    
    private fun initializeApp() {
        Timber.d("TarefaMágica App inicializado")
        
        // Configurar criptografia
        SecurityManager.initialize(this)
        
        // Configurar notificações
        NotificationManager.initialize(this)
        
        // Configurar analytics
        AnalyticsManager.initialize(this)
    }
} 