package com.tarefamagica.app.data.security

import android.content.Context
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import java.io.File
import java.io.FileInputStream
import java.io.FileOutputStream
import java.security.KeyStore
import java.security.SecureRandom
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey
import javax.crypto.spec.GCMParameterSpec
import javax.crypto.spec.SecretKeySpec
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class DataProtection @Inject constructor(
    private val context: Context
) {
    
    private val keyStore = KeyStore.getInstance("AndroidKeyStore").apply {
        load(null)
    }
    
    private val keyAlias = "TarefaMagicaKey"
    private val algorithm = "AES/GCM/NoPadding"
    
    init {
        createKeyIfNeeded()
    }
    
    private fun createKeyIfNeeded() {
        if (!keyStore.containsAlias(keyAlias)) {
            val keyGenerator = KeyGenerator.getInstance(
                KeyProperties.KEY_ALGORITHM_AES,
                "AndroidKeyStore"
            )
            
            val keyGenParameterSpec = KeyGenParameterSpec.Builder(
                keyAlias,
                KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
            )
                .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                .setUserAuthenticationRequired(false)
                .setRandomizedEncryptionRequired(true)
                .build()
            
            keyGenerator.init(keyGenParameterSpec)
            keyGenerator.generateKey()
        }
    }
    
    fun encryptData(data: String): EncryptedData {
        val secretKey = keyStore.getKey(keyAlias, null) as SecretKey
        val cipher = Cipher.getInstance(algorithm)
        cipher.init(Cipher.ENCRYPT_MODE, secretKey)
        
        val encryptedBytes = cipher.doFinal(data.toByteArray())
        val iv = cipher.iv
        
        return EncryptedData(
            encryptedData = encryptedBytes,
            iv = iv
        )
    }
    
    fun decryptData(encryptedData: EncryptedData): String {
        val secretKey = keyStore.getKey(keyAlias, null) as SecretKey
        val cipher = Cipher.getInstance(algorithm)
        val spec = GCMParameterSpec(128, encryptedData.iv)
        cipher.init(Cipher.DECRYPT_MODE, secretKey, spec)
        
        val decryptedBytes = cipher.doFinal(encryptedData.encryptedData)
        return String(decryptedBytes)
    }
    
    fun encryptFile(inputFile: File, outputFile: File) {
        val data = inputFile.readBytes()
        val encryptedData = encryptData(String(data))
        
        outputFile.writeBytes(encryptedData.encryptedData + encryptedData.iv)
    }
    
    fun decryptFile(inputFile: File, outputFile: File) {
        val encryptedBytes = inputFile.readBytes()
        val dataSize = encryptedBytes.size - 12 // 12 bytes for IV
        
        val data = encryptedBytes.copyOfRange(0, dataSize)
        val iv = encryptedBytes.copyOfRange(dataSize, encryptedBytes.size)
        
        val encryptedData = EncryptedData(data, iv)
        val decryptedData = decryptData(encryptedData)
        
        outputFile.writeBytes(decryptedData.toByteArray())
    }
    
    fun secureDelete(file: File) {
        if (file.exists()) {
            // Sobrescrever com dados aleatórios
            val random = SecureRandom()
            val fileSize = file.length()
            val randomData = ByteArray(fileSize.toInt())
            random.nextBytes(randomData)
            
            FileOutputStream(file).use { fos ->
                fos.write(randomData)
                fos.flush()
                fos.fd.sync()
            }
            
            // Deletar o arquivo
            file.delete()
        }
    }
    
    fun createSecureBackup(data: String, backupName: String): File {
        val backupDir = File(context.filesDir, "secure_backups")
        if (!backupDir.exists()) {
            backupDir.mkdirs()
        }
        
        val backupFile = File(backupDir, "$backupName.enc")
        val encryptedData = encryptData(data)
        
        backupFile.writeBytes(encryptedData.encryptedData + encryptedData.iv)
        return backupFile
    }
    
    fun restoreSecureBackup(backupFile: File): String {
        val encryptedBytes = backupFile.readBytes()
        val dataSize = encryptedBytes.size - 12
        
        val data = encryptedBytes.copyOfRange(0, dataSize)
        val iv = encryptedBytes.copyOfRange(dataSize, encryptedBytes.size)
        
        val encryptedData = EncryptedData(data, iv)
        return decryptData(encryptedData)
    }
    
    fun listSecureBackups(): List<File> {
        val backupDir = File(context.filesDir, "secure_backups")
        return if (backupDir.exists()) {
            backupDir.listFiles()?.filter { it.extension == "enc" } ?: emptyList()
        } else {
            emptyList()
        }
    }
    
    fun deleteSecureBackup(backupFile: File) {
        secureDelete(backupFile)
    }
    
    fun wipeAllData() {
        // Deletar todos os arquivos do app
        context.filesDir.deleteRecursively()
        context.cacheDir.deleteRecursively()
        
        // Limpar shared preferences
        context.getSharedPreferences("app_prefs", Context.MODE_PRIVATE)
            .edit()
            .clear()
            .apply()
    }
}

data class EncryptedData(
    val encryptedData: ByteArray,
    val iv: ByteArray
) {
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (javaClass != other?.javaClass) return false
        
        other as EncryptedData
        
        if (!encryptedData.contentEquals(other.encryptedData)) return false
        if (!iv.contentEquals(other.iv)) return false
        
        return true
    }
    
    override fun hashCode(): Int {
        var result = encryptedData.contentHashCode()
        result = 31 * result + iv.contentHashCode()
        return result
    }
} 