package com.sublingo.app.ui

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.sublingo.app.data.repository.AuthRepository
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch

sealed interface SessionState {
    data object Loading : SessionState
    data object LoggedOut : SessionState
    data object LoggedIn : SessionState
}

class MainViewModel(private val repository: AuthRepository) : ViewModel() {
    val session: StateFlow<SessionState> = repository.tokenFlow
        .map { token -> if (token == null) SessionState.LoggedOut else SessionState.LoggedIn }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), SessionState.Loading)

    fun logout() {
        viewModelScope.launch { repository.logout() }
    }
}