package com.sublingo.app.ui.exercises

import android.os.SystemClock
import androidx.lifecycle.SavedStateHandle
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.sublingo.app.data.remote.AnswerResultDto
import com.sublingo.app.data.remote.ApiResult
import com.sublingo.app.data.remote.ExerciseDto
import com.sublingo.app.data.repository.LearningRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class ExerciseUiState(
    val loading: Boolean = true,
    val exercise: ExerciseDto? = null,
    val chosenId: Int? = null,
    val result: AnswerResultDto? = null,
    val finished: Boolean = false,
    val error: String? = null,
    val answered: Int = 0,
    val correctCount: Int = 0,
)

class ExerciseViewModel(
    private val repository: LearningRepository,
    savedStateHandle: SavedStateHandle,
) : ViewModel() {
    private val episodeId: Int = checkNotNull(savedStateHandle.get<Int>("episodeId"))

    private val _state = MutableStateFlow(ExerciseUiState())
    val state: StateFlow<ExerciseUiState> = _state.asStateFlow()

    private var shownAt = 0L

    init {
        loadNext()
    }

    fun loadNext() {
        viewModelScope.launch {
            _state.update {
                it.copy(
                    loading = true,
                    exercise = null,
                    chosenId = null,
                    result = null,
                    error = null,
                )
            }
            when (val result = repository.nextExercise(episodeId)) {
                is ApiResult.Success -> {
                    val exercise = result.value
                    if (exercise == null) {
                        _state.update { it.copy(loading = false, finished = true) }
                    } else {
                        shownAt = SystemClock.elapsedRealtime()
                        _state.update { it.copy(loading = false, exercise = exercise) }
                    }
                }
                is ApiResult.Error -> _state.update {
                    it.copy(loading = false, error = result.message)
                }
            }
        }
    }

    fun choose(lemmaId: Int) {
        val current = _state.value
        val exercise = current.exercise ?: return
        if (current.chosenId != null) return

        _state.update { it.copy(chosenId = lemmaId, error = null) }
        val elapsed = (SystemClock.elapsedRealtime() - shownAt).coerceIn(0L, 600_000L).toInt()

        viewModelScope.launch {
            when (val result = repository.answer(exercise.id, lemmaId, elapsed)) {
                is ApiResult.Success -> _state.update {
                    it.copy(
                        result = result.value,
                        answered = it.answered + 1,
                        correctCount = it.correctCount + if (result.value.correct) 1 else 0,
                    )
                }
                is ApiResult.Error -> _state.update {
                    it.copy(chosenId = null, error = result.message)
                }
            }
        }
    }
}