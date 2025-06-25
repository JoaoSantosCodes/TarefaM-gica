package com.tarefamagica.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.compose.runtime.LaunchedEffect
import kotlinx.coroutines.delay
import androidx.compose.foundation.clickable
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import android.content.Context
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.SnackbarHost
import androidx.compose.runtime.getValue
import androidx.compose.runtime.setValue
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import kotlinx.coroutines.launch
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import android.app.Activity
import android.content.Intent
import androidx.activity.result.contract.ActivityResultContracts
import com.google.android.gms.auth.api.signin.GoogleSignIn
import com.google.android.gms.auth.api.signin.GoogleSignInAccount
import com.google.android.gms.auth.api.signin.GoogleSignInClient
import com.google.android.gms.auth.api.signin.GoogleSignInOptions
import com.google.android.gms.common.api.ApiException
import com.facebook.CallbackManager
import com.facebook.FacebookCallback
import com.facebook.FacebookException
import com.facebook.login.LoginManager
import com.facebook.login.LoginResult

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            TarefaMagicaTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    TarefaMagicaApp()
                }
            }
        }
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        val callbackManager = CallbackManager.Factory.create()
        callbackManager.onActivityResult(requestCode, resultCode, data)
    }
}

@Composable
fun TarefaMagicaTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        content = content
    )
}

@Composable
fun TarefaMagicaApp() {
    val navController = rememberNavController()
    NavHost(navController, startDestination = "splash") {
        composable("splash") { SplashScreen(navController) }
        composable("login") { LoginScreen(navController) }
        composable("cadastro") { CadastroScreen(navController) }
        composable("dashboard/{username}") { backStackEntry ->
            val username = backStackEntry.arguments?.getString("username") ?: "Usuário"
            DashboardScreen(navController, username)
        }
        composable("tarefas/{username}") { backStackEntry ->
            val username = backStackEntry.arguments?.getString("username") ?: "Usuário"
            TarefasScreen(navController, username)
        }
        composable("recompensas/{username}") { backStackEntry ->
            val username = backStackEntry.arguments?.getString("username") ?: "Usuário"
            RecompensasScreen(navController, username)
        }
    }
}

@Composable
fun SplashScreen(navController: NavController) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text(
            text = "TarefaMágica",
            fontSize = 32.sp,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.primary
        )
        Text(
            text = "App Educacional Gamificado",
            fontSize = 18.sp,
            color = MaterialTheme.colorScheme.onBackground,
            modifier = Modifier.padding(top = 8.dp)
        )
        Text(
            text = "Versão 1.0",
            fontSize = 14.sp,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            modifier = Modifier.padding(top = 16.dp)
        )
    }
    LaunchedEffect(Unit) {
        delay(2000)
        navController.navigate("login") {
            popUpTo("splash") { inclusive = true }
        }
    }
}

@Composable
fun LoginScreen(navController: NavController) {
    val context = androidx.compose.ui.platform.LocalContext.current
    var username = androidx.compose.runtime.remember { androidx.compose.runtime.mutableStateOf("") }
    var password = androidx.compose.runtime.remember { androidx.compose.runtime.mutableStateOf("") }
    var error = androidx.compose.runtime.remember { androidx.compose.runtime.mutableStateOf("") }
    val snackbarHostState = remember { SnackbarHostState() }
    // Estados e variáveis para social login
    val activity = context as? Activity
    val googleSignInClient = remember {
        GoogleSignIn.getClient(
            context,
            GoogleSignInOptions.Builder(GoogleSignInOptions.DEFAULT_SIGN_IN)
                .requestEmail()
                .build()
        )
    }
    val callbackManager = remember { CallbackManager.Factory.create() }
    val googleLauncher = androidx.activity.compose.rememberLauncherForActivityResult(
        contract = ActivityResultContracts.StartActivityForResult()
    ) { result ->
        val task = GoogleSignIn.getSignedInAccountFromIntent(result.data)
        try {
            val account = task.getResult(ApiException::class.java)
            // Sucesso: navegue para o dashboard
            navController.navigate("dashboard/${'$'}{account.email ?: "GoogleUser"}") {
                popUpTo("login") { inclusive = true }
            }
        } catch (e: Exception) {
            error.value = "Falha no login com Google."
        }
    }
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text("Login", fontSize = 24.sp, fontWeight = FontWeight.Bold)
        androidx.compose.material3.OutlinedTextField(
            value = username.value,
            onValueChange = { username.value = it },
            label = { Text("Usuário") },
            modifier = Modifier.padding(top = 16.dp)
        )
        androidx.compose.material3.OutlinedTextField(
            value = password.value,
            onValueChange = { password.value = it },
            label = { Text("Senha") },
            modifier = Modifier.padding(top = 8.dp),
            visualTransformation = androidx.compose.ui.text.input.PasswordVisualTransformation()
        )
        if (error.value.isNotEmpty()) {
            Text(error.value, color = MaterialTheme.colorScheme.error, modifier = Modifier.padding(top = 8.dp))
        }
        androidx.compose.material3.Button(
            onClick = {
                if (username.value.isBlank() || password.value.isBlank()) {
                    error.value = "Preencha usuário e senha."
                } else {
                    val prefs = context.getSharedPreferences("auth", Context.MODE_PRIVATE)
                    val savedUser = prefs.getString("user", null)
                    val savedPass = prefs.getString("pass", null)
                    if (savedUser == username.value && savedPass == password.value) {
                        error.value = ""
                        navController.navigate("dashboard/${'$'}{username.value}") {
                            popUpTo("login") { inclusive = true }
                        }
                    } else {
                        error.value = "Usuário ou senha inválidos."
                    }
                }
            },
            modifier = Modifier.padding(top = 16.dp)
        ) {
            Text("Entrar")
        }
        // Botão de login com Google
        androidx.compose.material3.Button(
            onClick = {
                if (activity != null) {
                    val signInIntent = googleSignInClient.signInIntent
                    googleLauncher.launch(signInIntent)
                }
            },
            modifier = Modifier
                .padding(top = 16.dp)
                .fillMaxWidth()
        ) {
            Text("Entrar com Google")
        }
        // Botão de login com Facebook
        androidx.compose.material3.Button(
            onClick = {
                LoginManager.getInstance().logInWithReadPermissions(activity, listOf("email", "public_profile"))
                LoginManager.getInstance().registerCallback(callbackManager,
                    object : FacebookCallback<LoginResult> {
                        override fun onSuccess(result: LoginResult) {
                            navController.navigate("dashboard/FacebookUser") {
                                popUpTo("login") { inclusive = true }
                            }
                        }
                        override fun onCancel() {
                            error.value = "Login com Facebook cancelado."
                        }
                        override fun onError(errorFB: FacebookException) {
                            error.value = "Falha no login com Facebook."
                        }
                    })
            },
            modifier = Modifier
                .padding(top = 8.dp)
                .fillMaxWidth()
        ) {
            Text("Entrar com Facebook")
        }
        androidx.compose.material3.TextButton(
            onClick = { navController.navigate("cadastro") },
            modifier = Modifier.padding(top = 8.dp)
        ) {
            Text("Não tem conta? Cadastre-se")
        }
        SnackbarHost(hostState = snackbarHostState)
    }
}

@Composable
fun CadastroScreen(navController: NavController) {
    val context = androidx.compose.ui.platform.LocalContext.current
    var username = androidx.compose.runtime.remember { androidx.compose.runtime.mutableStateOf("") }
    var password = androidx.compose.runtime.remember { androidx.compose.runtime.mutableStateOf("") }
    var confirm = androidx.compose.runtime.remember { androidx.compose.runtime.mutableStateOf("") }
    var error = androidx.compose.runtime.remember { androidx.compose.runtime.mutableStateOf("") }
    val snackbarHostState = remember { SnackbarHostState() }
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text("Cadastro", fontSize = 24.sp, fontWeight = FontWeight.Bold)
        androidx.compose.material3.OutlinedTextField(
            value = username.value,
            onValueChange = { username.value = it },
            label = { Text("Usuário") },
            modifier = Modifier.padding(top = 16.dp)
        )
        androidx.compose.material3.OutlinedTextField(
            value = password.value,
            onValueChange = { password.value = it },
            label = { Text("Senha") },
            modifier = Modifier.padding(top = 8.dp),
            visualTransformation = androidx.compose.ui.text.input.PasswordVisualTransformation()
        )
        androidx.compose.material3.OutlinedTextField(
            value = confirm.value,
            onValueChange = { confirm.value = it },
            label = { Text("Confirmar Senha") },
            modifier = Modifier.padding(top = 8.dp),
            visualTransformation = androidx.compose.ui.text.input.PasswordVisualTransformation()
        )
        if (error.value.isNotEmpty()) {
            Text(error.value, color = MaterialTheme.colorScheme.error, modifier = Modifier.padding(top = 8.dp))
        }
        androidx.compose.material3.Button(
            onClick = {
                if (username.value.isBlank() || password.value.isBlank() || confirm.value.isBlank()) {
                    error.value = "Preencha todos os campos."
                } else if (password.value != confirm.value) {
                    error.value = "As senhas não coincidem."
                } else {
                    val prefs = context.getSharedPreferences("auth", Context.MODE_PRIVATE)
                    prefs.edit().putString("user", username.value).putString("pass", password.value).apply()
                    error.value = ""
                    navController.navigate("login") {
                        popUpTo("cadastro") { inclusive = true }
                    }
                }
            },
            modifier = Modifier.padding(top = 16.dp)
        ) {
            Text("Cadastrar")
        }
        androidx.compose.material3.TextButton(
            onClick = { navController.navigate("login") },
            modifier = Modifier.padding(top = 8.dp)
        ) {
            Text("Já tem conta? Fazer login")
        }
        SnackbarHost(hostState = snackbarHostState)
    }
}

@Composable
fun DashboardScreen(navController: NavController, username: String) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text("Bem-vindo, $username!", fontSize = 22.sp, fontWeight = FontWeight.Bold)
        androidx.compose.material3.Button(
            onClick = { navController.navigate("tarefas/$username") },
            modifier = Modifier.padding(top = 24.dp)
        ) { Text("Ver Tarefas") }
        androidx.compose.material3.Button(
            onClick = { navController.navigate("recompensas/$username") },
            modifier = Modifier.padding(top = 12.dp)
        ) { Text("Ver Recompensas") }
        androidx.compose.material3.Button(
            onClick = { navController.navigate("login") },
            modifier = Modifier.padding(top = 32.dp)
        ) { Text("Sair") }
    }
}

@Composable
fun TarefasScreen(navController: NavController, username: String) {
    val context = androidx.compose.ui.platform.LocalContext.current
    val gson = Gson()
    val prefs = context.getSharedPreferences("tarefas_$username", Context.MODE_PRIVATE)
    val scope = rememberCoroutineScope()
    var tarefas = remember { mutableStateListOf<String>() }
    var novaTarefa by remember { androidx.compose.runtime.mutableStateOf("") }
    val snackbarHostState = remember { SnackbarHostState() }

    // Carregar tarefas salvas
    LaunchedEffect(Unit) {
        val json = prefs.getString("tarefas", null)
        if (json != null) {
            val type = object : TypeToken<List<String>>() {}.type
            tarefas.clear()
            tarefas.addAll(gson.fromJson(json, type))
        } else {
            tarefas.clear()
            tarefas.addAll(listOf("Arrumar a cama", "Lavar a louça", "Fazer lição de casa"))
        }
    }

    fun salvarTarefas() {
        prefs.edit().putString("tarefas", gson.toJson(tarefas)).apply()
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        Text("Tarefas de $username", fontSize = 20.sp, fontWeight = FontWeight.Bold)
        androidx.compose.material3.OutlinedTextField(
            value = novaTarefa,
            onValueChange = { novaTarefa = it },
            label = { Text("Nova tarefa") },
            modifier = Modifier.padding(top = 8.dp)
        )
        androidx.compose.material3.Button(
            onClick = {
                if (novaTarefa.isNotBlank()) {
                    tarefas.add(novaTarefa)
                    salvarTarefas()
                    novaTarefa = ""
                    scope.launch { snackbarHostState.showSnackbar("Tarefa adicionada!") }
                }
            },
            modifier = Modifier.padding(top = 8.dp)
        ) { Text("Adicionar Tarefa") }
        LazyColumn(modifier = Modifier.weight(1f).padding(top = 16.dp)) {
            items(tarefas) { tarefa ->
                androidx.compose.material3.Card(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(bottom = 8.dp)
                        .clickable {
                            tarefas.remove(tarefa)
                            salvarTarefas()
                            scope.launch { snackbarHostState.showSnackbar("Tarefa concluída!") }
                        },
                ) {
                    Text(tarefa, modifier = Modifier.padding(16.dp))
                }
            }
        }
        androidx.compose.material3.Button(
            onClick = { navController.navigate("dashboard/$username") },
            modifier = Modifier.padding(top = 8.dp)
        ) { Text("Voltar ao Dashboard") }
        SnackbarHost(hostState = snackbarHostState)
    }
}

@Composable
fun RecompensasScreen(navController: NavController, username: String) {
    val context = androidx.compose.ui.platform.LocalContext.current
    val gson = Gson()
    val prefs = context.getSharedPreferences("recompensas_$username", Context.MODE_PRIVATE)
    val scope = rememberCoroutineScope()
    var recompensas = remember { mutableStateListOf<String>() }
    var novaRecompensa by remember { androidx.compose.runtime.mutableStateOf("") }
    val snackbarHostState = remember { SnackbarHostState() }

    // Carregar recompensas salvas
    LaunchedEffect(Unit) {
        val json = prefs.getString("recompensas", null)
        if (json != null) {
            val type = object : TypeToken<List<String>>() {}.type
            recompensas.clear()
            recompensas.addAll(gson.fromJson(json, type))
        } else {
            recompensas.clear()
            recompensas.addAll(listOf("Moeda de Ouro", "Adesivo Especial", "Dia sem tarefas"))
        }
    }

    fun salvarRecompensas() {
        prefs.edit().putString("recompensas", gson.toJson(recompensas)).apply()
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        Text("Recompensas de $username", fontSize = 20.sp, fontWeight = FontWeight.Bold)
        androidx.compose.material3.OutlinedTextField(
            value = novaRecompensa,
            onValueChange = { novaRecompensa = it },
            label = { Text("Nova recompensa") },
            modifier = Modifier.padding(top = 8.dp)
        )
        androidx.compose.material3.Button(
            onClick = {
                if (novaRecompensa.isNotBlank()) {
                    recompensas.add(novaRecompensa)
                    salvarRecompensas()
                    novaRecompensa = ""
                    scope.launch { snackbarHostState.showSnackbar("Recompensa adicionada!") }
                }
            },
            modifier = Modifier.padding(top = 8.dp)
        ) { Text("Adicionar Recompensa") }
        LazyColumn(modifier = Modifier.weight(1f).padding(top = 16.dp)) {
            items(recompensas) { recompensa ->
                androidx.compose.material3.Card(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(bottom = 8.dp)
                        .clickable {
                            recompensas.remove(recompensa)
                            salvarRecompensas()
                            scope.launch { snackbarHostState.showSnackbar("Recompensa resgatada!") }
                        },
                ) {
                    Text(recompensa, modifier = Modifier.padding(16.dp))
                }
            }
        }
        androidx.compose.material3.Button(
            onClick = { navController.navigate("dashboard/$username") },
            modifier = Modifier.padding(top = 8.dp)
        ) { Text("Voltar ao Dashboard") }
        SnackbarHost(hostState = snackbarHostState)
    }
}

@Preview(showBackground = true)
@Composable
fun TarefaMagicaAppPreview() {
    TarefaMagicaTheme {
        TarefaMagicaApp()
    }
}