package com.sublingo.app.ui.report

import androidx.lifecycle.SavedStateHandle
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.sublingo.app.data.remote.ApiResult
import com.sublingo.app.data.remote.ReportDto
import com.sublingo.app.data.repository.EpisodeRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class ReportUiState(
    val loading: Boolean = true,
    val report: ReportDto? = null,
    val error: String? = null,
)

class ReportViewModel(
    private val repository: EpisodeRepository,
    savedStateHandle: SavedStateHandle,
) : ViewModel() {
    private val episodeId: Int = checkNotNull(savedStateHandle.get<Int>("episodeId"))

    private val _state = MutableStateFlow(ReportUiState())
    val state: StateFlow<ReportUiState> = _state.asStateFlow()

    init {
        load()
    }

    fun load() {
        viewModelScope.launch {
            _state.update { it.copy(loading = true, error = null) }
            when (val result = repository.report(episodeId)) {
                is ApiResult.Success -> _state.update {
                    it.copy(loading = false, report = result.value)
                }
                is ApiResult.Error -> _state.update {
                    it.copy(loading = false, error = result.message)
                }
            }
        }
    }
}