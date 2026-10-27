package com.sublingo.app.ui.auth

import android.util.Patterns
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.sublingo.app.data.remote.ApiResult
import com.sublingo.app.data.repository.AuthRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class AuthUiState(
    val email: String = "",
    val password: String = "",
    val isRegister: Boolean = false,
    val loading: Boolean = false,
    val error: String? = null,
)

class AuthViewModel(private val repository: AuthRepository) : ViewModel() {
    private val _state = MutableStateFlow(AuthUiState())
    val state: StateFlow<AuthUiState> = _state.asStateFlow()

    fun onEmailChange(value: String) {
        _state.update { it.copy(email = value, error = null) }
    }

    fun onPasswordChange(value: String) {
        _state.update { it.copy(password = value, error = null) }
    }

    fun toggleMode() {
        _state.update { it.copy(isRegister = !it.isRegister, error = null) }
    }

    fun submit() {
        val current = _state.value
        if (current.loading) return

        val email = current.email.trim()
        if (!Patterns.EMAIL_ADDRESS.matcher(email).matches()) {
            _state.update { it.copy(error = "Введите корректный email") }
            return
        }
        if (current.isRegister && current.password.length < 8) {
            _state.update { it.copy(error = "Пароль должен содержать минимум 8 символов") }
            return
        }

        viewModelScope.launch {
            _state.update { it.copy(loading = true, error = null) }
            val result = if (current.isRegister) {
                repository.register(email, current.password)
            } else {
                repository.login(email, current.password)
            }
            _state.update {
                when (result) {
                    is ApiResult.Success -> it.copy(loading = false, password = "")
                    is ApiResult.Error -> it.copy(loading = false, error = result.message)
                }
            }
        }
    }
}