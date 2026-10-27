package com.sublingo.app.ui

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.imePadding
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Scaffold
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import com.sublingo.app.ui.auth.AuthScreen
import com.sublingo.app.ui.home.HomeScreen

@Composable
fun SubLingoRoot(
    mainViewModel: MainViewModel = viewModel(factory = AppViewModelProvider.Factory),
) {
    val session by mainViewModel.session.collectAsStateWithLifecycle()

    Scaffold(modifier = Modifier.fillMaxSize()) { innerPadding ->
        Box(
            modifier = Modifier
                .padding(innerPadding)
                .imePadding()
                .fillMaxSize()
        ) {
            when (session) {
                SessionState.Loading -> CircularProgressIndicator(
                    modifier = Modifier.align(Alignment.Center)
                )
                SessionState.LoggedOut -> AuthScreen()
                SessionState.LoggedIn -> HomeScreen(onLogout = mainViewModel::logout)
            }
        }
    }
}