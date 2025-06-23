package com.tarefamagica.ui.consent

import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.tarefamagica.R
import com.tarefamagica.databinding.ActivityParentalConsentBinding
import com.tarefamagica.security.ConsentManager
import kotlinx.coroutines.launch

class ParentalConsentActivity : AppCompatActivity() {
    
    private lateinit var binding: ActivityParentalConsentBinding
    private val consentManager by lazy { ConsentManager(applicationContext) }
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        binding = ActivityParentalConsentBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        setupViews()
        checkConsentStatus()
    }
    
    private fun setupViews() {
        binding.apply {
            // Botão de conceder consentimento
            btnGrantConsent.setOnClickListener {
                if (validateFields()) {
                    requestConsent()
                }
            }
            
            // Botão de revogar consentimento
            btnRevokeConsent.setOnClickListener {
                revokeConsent()
            }
            
            // Checkbox de termos
            checkboxTerms.setOnCheckedChangeListener { _, isChecked ->
                btnGrantConsent.isEnabled = isChecked
            }
        }
    }
    
    private fun checkConsentStatus() {
        val hasConsent = consentManager.hasActiveConsent()
        updateUI(hasConsent)
    }
    
    private fun validateFields(): Boolean {
        binding.apply {
            var isValid = true
            
            // Validar nome do responsável
            if (editParentName.text.isNullOrBlank()) {
                editParentName.error = "Nome do responsável é obrigatório"
                isValid = false
            }
            
            // Validar nome da criança
            if (editChildName.text.isNullOrBlank()) {
                editChildName.error = "Nome da criança é obrigatório"
                isValid = false
            }
            
            // Validar termos
            if (!checkboxTerms.isChecked) {
                Toast.makeText(
                    this@ParentalConsentActivity,
                    "Você precisa aceitar os termos",
                    Toast.LENGTH_SHORT
                ).show()
                isValid = false
            }
            
            return isValid
        }
    }
    
    private fun requestConsent() {
        binding.progressBar.visibility = View.VISIBLE
        
        lifecycleScope.launch {
            try {
                val result = consentManager.requestConsent(
                    userId = getCurrentUserId(), // Implementar método para obter ID do usuário
                    childId = generateChildId(), // Implementar método para gerar ID da criança
                    parentName = binding.editParentName.text.toString(),
                    childName = binding.editChildName.text.toString()
                )
                
                result.fold(
                    onSuccess = { response ->
                        // Consentimento solicitado com sucesso
                        grantConsent()
                    },
                    onFailure = { exception ->
                        showError("Erro ao solicitar consentimento: ${exception.message}")
                    }
                )
            } catch (e: Exception) {
                showError("Erro inesperado: ${e.message}")
            } finally {
                binding.progressBar.visibility = View.GONE
            }
        }
    }
    
    private fun grantConsent() {
        lifecycleScope.launch {
            try {
                val result = consentManager.grantConsent(getCurrentUserId())
                
                result.fold(
                    onSuccess = {
                        updateUI(true)
                        showSuccess("Consentimento concedido com sucesso!")
                    },
                    onFailure = { exception ->
                        showError("Erro ao conceder consentimento: ${exception.message}")
                    }
                )
            } catch (e: Exception) {
                showError("Erro inesperado: ${e.message}")
            }
        }
    }
    
    private fun revokeConsent() {
        lifecycleScope.launch {
            try {
                val result = consentManager.revokeConsent(getCurrentUserId())
                
                result.fold(
                    onSuccess = {
                        updateUI(false)
                        showSuccess("Consentimento revogado com sucesso!")
                    },
                    onFailure = { exception ->
                        showError("Erro ao revogar consentimento: ${exception.message}")
                    }
                )
            } catch (e: Exception) {
                showError("Erro inesperado: ${e.message}")
            }
        }
    }
    
    private fun updateUI(hasConsent: Boolean) {
        binding.apply {
            // Formulário
            formContainer.visibility = if (hasConsent) View.GONE else View.VISIBLE
            
            // Botões
            btnGrantConsent.visibility = if (hasConsent) View.GONE else View.VISIBLE
            btnRevokeConsent.visibility = if (hasConsent) View.VISIBLE else View.GONE
            
            // Status
            textConsentStatus.text = if (hasConsent) {
                "✅ Consentimento ativo"
            } else {
                "⚠️ Consentimento pendente"
            }
        }
    }
    
    private fun showError(message: String) {
        Toast.makeText(this, message, Toast.LENGTH_LONG).show()
    }
    
    private fun showSuccess(message: String) {
        Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
    }
    
    // Métodos auxiliares (implementar conforme necessidade)
    private fun getCurrentUserId(): String {
        // TODO: Implementar obtenção do ID do usuário logado
        return "user_123"
    }
    
    private fun generateChildId(): String {
        // TODO: Implementar geração de ID único para criança
        return "child_${System.currentTimeMillis()}"
    }
} 