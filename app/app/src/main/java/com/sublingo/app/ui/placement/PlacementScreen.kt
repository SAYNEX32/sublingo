package com.sublingo.app.ui.placement

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import com.sublingo.app.data.remote.PlacementResultDto
import com.sublingo.app.ui.AppViewModelProvider
import java.util.Locale

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PlacementScreen(
    onDone: () -> Unit,
    viewModel: PlacementViewModel = viewModel(factory = AppViewModelProvider.Factory),
) {
    val state by viewModel.state.collectAsStateWithLifecycle()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Тест уровня") },
                navigationIcon = { TextButton(onClick = onDone) { Text("Назад") } },
            )
        },
    ) { padding ->
        Box(modifier = Modifier.padding(padding).fillMaxSize()) {
            val result = state.result
            when {
                result != null -> ResultContent(result, onDone)
                state.loading || state.submitting -> Column(
                    modifier = Modifier.align(Alignment.Center),
                    horizontalAlignment = Alignment.CenterHorizontally,
                ) {
                    CircularProgressIndicator()
                    Spacer(Modifier.height(12.dp))
                    Text(if (state.submitting) "Считаем результат" else "Загружаем слова")
                }
                state.error != null -> Column(
                    modifier = Modifier.align(Alignment.Center).padding(24.dp),
                    horizontalAlignment = Alignment.CenterHorizontally,
                ) {
                    Text(state.error ?: "", color = MaterialTheme.colorScheme.error)
                    Spacer(Modifier.height(8.dp))
                    Button(onClick = viewModel::retry) { Text("Повторить") }
                }
                state.index < state.words.size -> {
                    val word = state.words[state.index]
                    Column(
                        modifier = Modifier.fillMaxSize().padding(24.dp),
                        verticalArrangement = Arrangement.Center,
                        horizontalAlignment = Alignment.CenterHorizontally,
                    ) {
                        Text(
                            "${state.index + 1} из ${state.words.size}",
                            style = MaterialTheme.typography.labelLarge,
                        )
                        Spacer(Modifier.height(8.dp))
                        LinearProgressIndicator(
                            progress = { state.index.toFloat() / state.words.size },
                            modifier = Modifier.fillMaxWidth(),
                        )
                        Spacer(Modifier.height(48.dp))
                        Text(
                            "Вы знаете значение этого слова?",
                            style = MaterialTheme.typography.bodyLarge,
                        )
                        Spacer(Modifier.height(16.dp))
                        Text(
                            text = word.lemma,
                            style = MaterialTheme.typography.displaySmall,
                            fontWeight = FontWeight.SemiBold,
                        )
                        Text(posLabel(word.pos), style = MaterialTheme.typography.bodyMedium)
                        Spacer(Modifier.height(48.dp))
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(12.dp),
                        ) {
                            OutlinedButton(
                                onClick = { viewModel.answer(false) },
                                modifier = Modifier.weight(1f).height(52.dp),
                            ) { Text("Не знаю") }
                            Button(
                                onClick = { viewModel.answer(true) },
                                modifier = Modifier.weight(1f).height(52.dp),
                            ) { Text("Знаю") }
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun ResultContent(result: PlacementResultDto, onDone: () -> Unit) {
    Column(
        modifier = Modifier.fillMaxSize().padding(24.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Text("Ваш уровень", style = MaterialTheme.typography.bodyLarge)
        Text(levelLabel(result.vocabThreshold), style = MaterialTheme.typography.displaySmall)
        Spacer(Modifier.height(16.dp))
        Card(modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("Знакомых слов: ${result.knownCount} из ${result.answersUsed}")
                Text(
                    "Порог частотности: " +
                        String.format(Locale.US, "%.2f", result.vocabThreshold),
                    style = MaterialTheme.typography.bodySmall,
                )
                Spacer(Modifier.height(8.dp))
                Text(
                    "Оценка приблизительная. Отчёты по сериям уже учитывают её.",
                    style = MaterialTheme.typography.bodySmall,
                )
            }
        }
        Spacer(Modifier.height(24.dp))
        Button(onClick = onDone, modifier = Modifier.fillMaxWidth()) { Text("Готово") }
    }
}

private fun levelLabel(threshold: Double): String = when {
    threshold >= 4.6 -> "Начальный"
    threshold >= 4.0 -> "Базовый"
    threshold >= 3.4 -> "Средний"
    else -> "Продвинутый"
}

private fun posLabel(pos: String): String = when (pos) {
    "NOUN" -> "существительное"
    "VERB" -> "глагол"
    "ADJ" -> "прилагательное"
    "ADV" -> "наречие"
    else -> pos.lowercase()
}