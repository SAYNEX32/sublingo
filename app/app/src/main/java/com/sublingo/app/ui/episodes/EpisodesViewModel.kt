package com.sublingo.app.ui.episodes

import android.net.Uri
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.sublingo.app.data.remote.ApiResult
import com.sublingo.app.data.remote.EpisodeDto
import com.sublingo.app.data.repository.EpisodeRepository
import com.sublingo.app.data.repository.PickedFile
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class EpisodesUiState(
    val episodes: List<EpisodeDto> = emptyList(),
    val loading: Boolean = true,
    val error: String? = null,
    val message: String? = null,
    val pendingName: String? = null,
    val title: String = "",
    val season: String = "",
    val number: String = "",
    val uploading: Boolean = false,
    val uploadError: String? = null,
)

class EpisodesViewModel(private val repository: EpisodeRepository) : ViewModel() {
    private val _state = MutableStateFlow(EpisodesUiState())
    val state: StateFlow<EpisodesUiState> = _state.asStateFlow()

    private var pendingFile: PickedFile? = null

    init {
        refresh()
    }

    fun refresh() {
        viewModelScope.launch {
            _state.update { it.copy(loading = true, error = null) }
            when (val result = repository.list()) {
                is ApiResult.Success -> _state.update {
                    it.copy(episodes = result.value, loading = false)
                }
                is ApiResult.Error -> _state.update {
                    it.copy(loading = false, error = result.message)
                }
            }
        }
    }

    fun onFilePicked(uri: Uri) {
        viewModelScope.launch {
            val file = repository.readFile(uri)
            if (file == null) {
                _state.update { it.copy(message = "Не удалось прочитать файл") }
                return@launch
            }
            pendingFile = file
            _state.update {
                it.copy(
                    pendingName = file.name,
                    title = guessTitle(file.name),
                    season = "",
                    number = "",
                    uploadError = null,
                )
            }
        }
    }

    fun onTitleChange(value: String) = _state.update { it.copy(title = value, uploadError = null) }

    fun onSeasonChange(value: String) =
        _state.update { it.copy(season = value.filter(Char::isDigit).take(3)) }

    fun onNumberChange(value: String) =
        _state.update { it.copy(number = value.filter(Char::isDigit).take(3)) }

    fun cancelUpload() {
        pendingFile = null
        _state.update { it.copy(pendingName = null, uploadError = null) }
    }

    fun confirmUpload() {
        val file = pendingFile ?: return
        val current = _state.value
        if (current.uploading) return

        val title = current.title.trim()
        if (title.isEmpty()) {
            _state.update { it.copy(uploadError = "Введите название") }
            return
        }

        viewModelScope.launch {
            _state.update { it.copy(uploading = true, uploadError = null) }
            val result = repository.analyze(
                file = file,
                title = title,
                season = current.season.toIntOrNull(),
                number = current.number.toIntOrNull(),
            )
            when (result) {
                is ApiResult.Success -> {
                    pendingFile = null
                    _state.update {
                        it.copy(
                            pendingName = null,
                            uploading = false,
                            message = "Серия «$title» добавлена",
                        )
                    }
                    refresh()
                }
                is ApiResult.Error -> _state.update {
                    it.copy(uploading = false, uploadError = result.message)
                }
            }
        }
    }

    fun consumeMessage() = _state.update { it.copy(message = null) }

    private fun guessTitle(fileName: String): String =
        cleanTitle(fileName)
}

private val NOISE_REGEX = Regex(
    """(?i)\b(480p|720p|1080p|2160p|4k|bluray|brrip|bdrip|webrip|web-dl|hdrip|dvdrip|x264|x265|h264|h265|hevc|yify|yts|utf8|eng?)\b.*$"""
)
private val YEAR_REGEX = Regex("""\s*\(?\b(19|20)\d{2}\b\)?\s*$""")

private fun cleanTitle(fileName: String): String {
    val base = fileName.removeSuffix(".srt").replace('.', ' ').replace('_', ' ').trim()
    return base.replace(NOISE_REGEX, "").replace(YEAR_REGEX, "").trim().ifEmpty { base }
}