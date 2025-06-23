package com.tarefamagica.ui

import android.os.Bundle
import android.view.View
import android.widget.ArrayAdapter
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import com.tarefamagica.R
import com.tarefamagica.databinding.ActivityAccessControlBinding
import com.tarefamagica.security.AccessManager
import kotlinx.coroutines.launch

class AccessControlActivity : AppCompatActivity() {
    
    private lateinit var binding: ActivityAccessControlBinding
    private lateinit var accessManager: AccessManager
    private lateinit var permissionsAdapter: PermissionsAdapter
    private lateinit var accessLogsAdapter: AccessLogsAdapter
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityAccessControlBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        accessManager = AccessManager(this)
        
        setupUI()
        setupListeners()
        loadUserData()
        loadPermissions()
        loadAccessLogs()
    }
    
    private fun setupUI() {
        // Configura RecyclerView de permissões
        permissionsAdapter = PermissionsAdapter()
        binding.rvPermissions.apply {
            layoutManager = LinearLayoutManager(this@AccessControlActivity)
            adapter = permissionsAdapter
        }
        
        // Configura RecyclerView de logs
        accessLogsAdapter = AccessLogsAdapter()
        binding.rvAccessLogs.apply {
            layoutManager = LinearLayoutManager(this@AccessControlActivity)
            adapter = accessLogsAdapter
        }
        
        // Configura spinner de permissões
        val permissions = AccessManager.Permission.values().map { it.value }
        val spinnerAdapter = ArrayAdapter(this, android.R.layout.simple_spinner_item, permissions)
        spinnerAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
        binding.spinnerPermission.setAdapter(spinnerAdapter)
    }
    
    private fun setupListeners() {
        // Botão atualizar permissões
        binding.btnRefreshPermissions.setOnClickListener {
            loadPermissions()
        }
        
        // Botão conceder permissão
        binding.btnGrantPermission.setOnClickListener {
            grantPermission()
        }
        
        // Botão revogar permissão
        binding.btnRevokePermission.setOnClickListener {
            revokePermission()
        }
        
        // Botão ver logs
        binding.btnViewLogs.setOnClickListener {
            loadAccessLogs()
        }
        
        // Botão desativar usuário
        binding.btnDeactivateUser.setOnClickListener {
            showDeactivateUserDialog()
        }
        
        // Botão sair
        binding.btnLogout.setOnClickListener {
            logout()
        }
    }
    
    private fun loadUserData() {
        val user = accessManager.getCurrentUser()
        if (user != null) {
            binding.tvUserId.text = user.userId
            binding.tvUserRole.text = user.role.value.capitalize()
            binding.tvUserStatus.text = if (user.isActive) "Ativo" else "Inativo"
            binding.tvUserStatus.setTextColor(
                if (user.isActive) getColor(R.color.success) else getColor(R.color.error)
            )
        } else {
            Toast.makeText(this, "Usuário não encontrado", Toast.LENGTH_SHORT).show()
            finish()
        }
    }
    
    private fun loadPermissions() {
        lifecycleScope.launch {
            try {
                val permissions = accessManager.getCurrentPermissions()
                permissionsAdapter.updatePermissions(permissions.toList())
                
                if (permissions.isEmpty()) {
                    binding.rvPermissions.visibility = View.GONE
                    // Mostrar mensagem de "Nenhuma permissão"
                } else {
                    binding.rvPermissions.visibility = View.VISIBLE
                }
            } catch (e: Exception) {
                Toast.makeText(this@AccessControlActivity, "Erro ao carregar permissões", Toast.LENGTH_SHORT).show()
            }
        }
    }
    
    private fun grantPermission() {
        val permissionValue = binding.spinnerPermission.text.toString()
        if (permissionValue.isEmpty()) {
            Toast.makeText(this, "Selecione uma permissão", Toast.LENGTH_SHORT).show()
            return
        }
        
        val permission = AccessManager.Permission.values().find { it.value == permissionValue }
        if (permission == null) {
            Toast.makeText(this, "Permissão inválida", Toast.LENGTH_SHORT).show()
            return
        }
        
        lifecycleScope.launch {
            try {
                val result = accessManager.grantPermission(permission)
                result.fold(
                    onSuccess = {
                        Toast.makeText(this@AccessControlActivity, "Permissão concedida com sucesso", Toast.LENGTH_SHORT).show()
                        loadPermissions()
                    },
                    onFailure = { exception ->
                        Toast.makeText(this@AccessControlActivity, "Erro: ${exception.message}", Toast.LENGTH_SHORT).show()
                    }
                )
            } catch (e: Exception) {
                Toast.makeText(this@AccessControlActivity, "Erro ao conceder permissão", Toast.LENGTH_SHORT).show()
            }
        }
    }
    
    private fun revokePermission() {
        val permissionValue = binding.spinnerPermission.text.toString()
        if (permissionValue.isEmpty()) {
            Toast.makeText(this, "Selecione uma permissão", Toast.LENGTH_SHORT).show()
            return
        }
        
        val permission = AccessManager.Permission.values().find { it.value == permissionValue }
        if (permission == null) {
            Toast.makeText(this, "Permissão inválida", Toast.LENGTH_SHORT).show()
            return
        }
        
        lifecycleScope.launch {
            try {
                val result = accessManager.revokePermission(permission)
                result.fold(
                    onSuccess = {
                        Toast.makeText(this@AccessControlActivity, "Permissão revogada com sucesso", Toast.LENGTH_SHORT).show()
                        loadPermissions()
                    },
                    onFailure = { exception ->
                        Toast.makeText(this@AccessControlActivity, "Erro: ${exception.message}", Toast.LENGTH_SHORT).show()
                    }
                )
            } catch (e: Exception) {
                Toast.makeText(this@AccessControlActivity, "Erro ao revogar permissão", Toast.LENGTH_SHORT).show()
            }
        }
    }
    
    private fun loadAccessLogs() {
        lifecycleScope.launch {
            try {
                val result = accessManager.getAccessLogs(days = 30)
                result.fold(
                    onSuccess = { logs ->
                        accessLogsAdapter.updateLogs(logs)
                        
                        if (logs.isEmpty()) {
                            binding.rvAccessLogs.visibility = View.GONE
                            // Mostrar mensagem de "Nenhum log encontrado"
                        } else {
                            binding.rvAccessLogs.visibility = View.VISIBLE
                        }
                    },
                    onFailure = { exception ->
                        Toast.makeText(this@AccessControlActivity, "Erro: ${exception.message}", Toast.LENGTH_SHORT).show()
                    }
                )
            } catch (e: Exception) {
                Toast.makeText(this@AccessControlActivity, "Erro ao carregar logs", Toast.LENGTH_SHORT).show()
            }
        }
    }
    
    private fun showDeactivateUserDialog() {
        AlertDialog.Builder(this)
            .setTitle("Desativar Usuário")
            .setMessage("Tem certeza que deseja desativar este usuário? Esta ação não pode ser desfeita.")
            .setPositiveButton("Desativar") { _, _ ->
                deactivateUser()
            }
            .setNegativeButton("Cancelar", null)
            .show()
    }
    
    private fun deactivateUser() {
        lifecycleScope.launch {
            try {
                val result = accessManager.deactivateCurrentUser()
                result.fold(
                    onSuccess = {
                        Toast.makeText(this@AccessControlActivity, "Usuário desativado com sucesso", Toast.LENGTH_SHORT).show()
                        finish()
                    },
                    onFailure = { exception ->
                        Toast.makeText(this@AccessControlActivity, "Erro: ${exception.message}", Toast.LENGTH_SHORT).show()
                    }
                )
            } catch (e: Exception) {
                Toast.makeText(this@AccessControlActivity, "Erro ao desativar usuário", Toast.LENGTH_SHORT).show()
            }
        }
    }
    
    private fun logout() {
        // Limpar dados locais e voltar para tela de login
        // Implementar conforme necessário
        finish()
    }
    
    // Adapters para RecyclerView
    inner class PermissionsAdapter : androidx.recyclerview.widget.RecyclerView.Adapter<PermissionsAdapter.ViewHolder>() {
        
        private var permissions = listOf<AccessManager.Permission>()
        
        fun updatePermissions(newPermissions: List<AccessManager.Permission>) {
            permissions = newPermissions
            notifyDataSetChanged()
        }
        
        override fun onCreateViewHolder(parent: android.view.ViewGroup, viewType: Int): ViewHolder {
            val view = android.view.LayoutInflater.from(parent.context)
                .inflate(R.layout.item_permission, parent, false)
            return ViewHolder(view)
        }
        
        override fun onBindViewHolder(holder: ViewHolder, position: Int) {
            val permission = permissions[position]
            holder.bind(permission)
        }
        
        override fun getItemCount() = permissions.size
        
        inner class ViewHolder(itemView: android.view.View) : androidx.recyclerview.widget.RecyclerView.ViewHolder(itemView) {
            
            private val tvPermissionName: android.widget.TextView = itemView.findViewById(R.id.tvPermissionName)
            private val tvPermissionDescription: android.widget.TextView = itemView.findViewById(R.id.tvPermissionDescription)
            private val ivPermissionIcon: android.widget.ImageView = itemView.findViewById(R.id.ivPermissionIcon)
            
            fun bind(permission: AccessManager.Permission) {
                tvPermissionName.text = permission.name.replace("_", " ").capitalize()
                tvPermissionDescription.text = getPermissionDescription(permission)
                ivPermissionIcon.setImageResource(getPermissionIcon(permission))
            }
            
            private fun getPermissionDescription(permission: AccessManager.Permission): String {
                return when (permission) {
                    AccessManager.Permission.READ_OWN_DATA -> "Ler dados próprios"
                    AccessManager.Permission.WRITE_OWN_DATA -> "Escrever dados próprios"
                    AccessManager.Permission.READ_CHILD_DATA -> "Ler dados da criança"
                    AccessManager.Permission.WRITE_CHILD_DATA -> "Escrever dados da criança"
                    AccessManager.Permission.CREATE_TRANSACTION -> "Criar transação"
                    AccessManager.Permission.APPROVE_TRANSACTION -> "Aprovar transação"
                    AccessManager.Permission.VIEW_TRANSACTION_HISTORY -> "Ver histórico de transações"
                    AccessManager.Permission.MANAGE_CONSENT -> "Gerenciar consentimento"
                    AccessManager.Permission.VIEW_CONSENT_HISTORY -> "Ver histórico de consentimento"
                    AccessManager.Permission.MANAGE_USERS -> "Gerenciar usuários"
                    AccessManager.Permission.VIEW_LOGS -> "Ver logs do sistema"
                    AccessManager.Permission.MANAGE_SYSTEM -> "Gerenciar sistema"
                }
            }
            
            private fun getPermissionIcon(permission: AccessManager.Permission): Int {
                return when (permission) {
                    AccessManager.Permission.READ_OWN_DATA,
                    AccessManager.Permission.READ_CHILD_DATA -> R.drawable.ic_read
                    AccessManager.Permission.WRITE_OWN_DATA,
                    AccessManager.Permission.WRITE_CHILD_DATA -> R.drawable.ic_write
                    AccessManager.Permission.CREATE_TRANSACTION,
                    AccessManager.Permission.APPROVE_TRANSACTION -> R.drawable.ic_payment
                    AccessManager.Permission.VIEW_TRANSACTION_HISTORY -> R.drawable.ic_history
                    AccessManager.Permission.MANAGE_CONSENT -> R.drawable.ic_consent
                    AccessManager.Permission.VIEW_CONSENT_HISTORY -> R.drawable.ic_history
                    AccessManager.Permission.MANAGE_USERS -> R.drawable.ic_people
                    AccessManager.Permission.VIEW_LOGS -> R.drawable.ic_logs
                    AccessManager.Permission.MANAGE_SYSTEM -> R.drawable.ic_settings
                }
            }
        }
    }
    
    inner class AccessLogsAdapter : androidx.recyclerview.widget.RecyclerView.Adapter<AccessLogsAdapter.ViewHolder>() {
        
        private var logs = listOf<AccessManager.AccessLog>()
        
        fun updateLogs(newLogs: List<AccessManager.AccessLog>) {
            logs = newLogs
            notifyDataSetChanged()
        }
        
        override fun onCreateViewHolder(parent: android.view.ViewGroup, viewType: Int): ViewHolder {
            val view = android.view.LayoutInflater.from(parent.context)
                .inflate(R.layout.item_access_log, parent, false)
            return ViewHolder(view)
        }
        
        override fun onBindViewHolder(holder: ViewHolder, position: Int) {
            val log = logs[position]
            holder.bind(log)
        }
        
        override fun getItemCount() = logs.size
        
        inner class ViewHolder(itemView: android.view.View) : androidx.recyclerview.widget.RecyclerView.ViewHolder(itemView) {
            
            private val tvAction: android.widget.TextView = itemView.findViewById(R.id.tvAction)
            private val tvResource: android.widget.TextView = itemView.findViewById(R.id.tvResource)
            private val tvTimestamp: android.widget.TextView = itemView.findViewById(R.id.tvTimestamp)
            private val tvSuccess: android.widget.TextView = itemView.findViewById(R.id.tvSuccess)
            private val ivStatusIcon: android.widget.ImageView = itemView.findViewById(R.id.ivStatusIcon)
            
            fun bind(log: AccessManager.AccessLog) {
                tvAction.text = log.action.replace("_", " ").capitalize()
                tvResource.text = log.resource
                tvTimestamp.text = formatTimestamp(log.timestamp)
                tvSuccess.text = if (log.success) "Sucesso" else "Falha"
                tvSuccess.setTextColor(
                    if (log.success) getColor(R.color.success) else getColor(R.color.error)
                )
                ivStatusIcon.setImageResource(
                    if (log.success) R.drawable.ic_success else R.drawable.ic_error
                )
            }
            
            private fun formatTimestamp(timestamp: String): String {
                // Implementar formatação de timestamp
                return timestamp
            }
        }
    }
} 