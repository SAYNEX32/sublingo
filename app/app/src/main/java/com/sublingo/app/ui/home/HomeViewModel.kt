package com.sublingo.app.ui.home

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.sublingo.app.data.remote.ApiResult
import com.sublingo.app.data.repository.AuthRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class HomeUiState(
    val email: String? = null,
    val error: String? = null,
)

class HomeViewModel(private val repository: AuthRepository) : ViewModel() {
    private val _state = MutableStateFlow(HomeUiState())
    val state: StateFlow<HomeUiState> = _state.asStateFlow()

    init {
        load()
    }

    fun load() {
        viewModelScope.launch {
            _state.update { it.copy(error = null) }
            when (val result = repository.currentUser()) {
                is ApiResult.Success -> _state.update { it.copy(email = result.value.email) }
                is ApiResult.Error -> _state.update { it.copy(error = result.message) }
            }
        }
    }
}