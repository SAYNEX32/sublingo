package com.sublingo.app.ui.placement

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.sublingo.app.data.remote.ApiResult
import com.sublingo.app.data.remote.PlacementAnswerDto
import com.sublingo.app.data.remote.PlacementResultDto
import com.sublingo.app.data.remote.PlacementWordDto
import com.sublingo.app.data.repository.LearningRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class PlacementUiState(
    val loading: Boolean = true,
    val words: List<PlacementWordDto> = emptyList(),
    val index: Int = 0,
    val submitting: Boolean = false,
    val result: PlacementResultDto? = null,
    val error: String? = null,
)

class PlacementViewModel(private val repository: LearningRepository) : ViewModel() {
    private val _state = MutableStateFlow(PlacementUiState())
    val state: StateFlow<PlacementUiState> = _state.asStateFlow()

    private val answers = mutableListOf<PlacementAnswerDto>()

    init {
        load()
    }

    fun load() {
        viewModelScope.launch {
            answers.clear()
            _state.value = PlacementUiState()
            when (val result = repository.placementWords()) {
                is ApiResult.Success -> _state.update {
                    it.copy(loading = false, words = result.value)
                }
                is ApiResult.Error -> _state.update {
                    it.copy(loading = false, error = result.message)
                }
            }
        }
    }

    fun answer(known: Boolean) {
        val current = _state.value
        if (current.submitting || current.index >= current.words.size) return

        answers += PlacementAnswerDto(current.words[current.index].lemmaId, known)
        val next = current.index + 1
        _state.update { it.copy(index = next) }
        if (next >= current.words.size) submit()
    }

    fun retry() {
        if (_state.value.words.isEmpty()) load() else submit()
    }

    private fun submit() {
        viewModelScope.launch {
            _state.update { it.copy(submitting = true, error = null) }
            when (val result = repository.submitPlacement(answers.toList())) {
                is ApiResult.Success -> _state.update {
                    it.copy(submitting = false, result = result.value)
                }
                is ApiResult.Error -> _state.update {
                    it.copy(submitting = false, error = result.message)
                }
            }
        }
    }
}