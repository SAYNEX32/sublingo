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
    val offline: Boolean = false,
)

class ReportViewModel(
    private val repository: EpisodeRepository,
    savedStateHandle: SavedStateHandle,
) : ViewModel() {
    private val episodeId: Int = checkNotNull(savedStateHandle.get<Int>("episodeId"))

    private val _state = MutableStateFlow(ReportUiState())
    val state: StateFlow<ReportUiState> = _state.asStateFlow()

    init {
        // Whatever is stored locally is shown immediately and updated live
        viewModelScope.launch {
            repository.observeReport(episodeId).collect { report ->
                _state.update {
                    it.copy(report = report, loading = if (report != null) false else it.loading)
                }
            }
        }
    }

    // Called on every screen resume, so the report refreshes after exercises
    fun load() {
        viewModelScope.launch {
            _state.update { it.copy(loading = it.report == null, error = null, offline = false) }
            when (val result = repository.refreshReport(episodeId)) {
                is ApiResult.Success -> _state.update { it.copy(loading = false) }
                is ApiResult.Error -> _state.update {
                    it.copy(loading = false, error = result.message, offline = it.report != null)
                }
            }
        }
    }
}