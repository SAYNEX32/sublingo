package com.sublingo.app.ui

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.safeDrawingPadding
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import com.sublingo.app.ui.auth.AuthScreen

@Composable
fun SubLingoRoot(
    mainViewModel: MainViewModel = viewModel(factory = AppViewModelProvider.Factory),
) {
    val session by mainViewModel.session.collectAsStateWithLifecycle()

    Surface(
        modifier = Modifier.fillMaxSize(),
        color = MaterialTheme.colorScheme.background,
    ) {
        Box(modifier = Modifier.fillMaxSize().safeDrawingPadding()) {
            when (session) {
                SessionState.Loading -> CircularProgressIndicator(
                    modifier = Modifier.align(Alignment.Center)
                )
                SessionState.LoggedOut -> AuthScreen()
                SessionState.LoggedIn -> AppNavHost(onLogout = mainViewModel::logout)
            }
        }
    }
}