package com.sublingo.app.ui.exercises

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import com.sublingo.app.data.remote.AnswerResultDto
import com.sublingo.app.data.remote.ExerciseDto
import com.sublingo.app.ui.AppViewModelProvider

private enum class OptionMode { Idle, Correct, Wrong, Dimmed }

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ExerciseScreen(
    onBack: () -> Unit,
    viewModel: ExerciseViewModel = viewModel(factory = AppViewModelProvider.Factory),
) {
    val state by viewModel.state.collectAsStateWithLifecycle()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Упражнения") },
                navigationIcon = { TextButton(onClick = onBack) { Text("Назад") } },
                actions = {
                    if (state.answered > 0) {
                        Text(
                            "${state.correctCount} из ${state.answered}",
                            modifier = Modifier.padding(end = 16.dp),
                        )
                    }
                },
            )
        },
    ) { padding ->
        Box(modifier = Modifier.padding(padding).fillMaxSize()) {
            val exercise = state.exercise
            when {
                exercise != null -> ExerciseContent(
                    state = state,
                    exercise = exercise,
                    onChoose = viewModel::choose,
                    onNext = viewModel::loadNext,
                )
                state.loading -> CircularProgressIndicator(
                    modifier = Modifier.align(Alignment.Center)
                )
                state.finished -> Column(
                    modifier = Modifier.align(Alignment.Center).padding(24.dp),
                    horizontalAlignment = Alignment.CenterHorizontally,
                ) {
                    Text("На сегодня всё", style = MaterialTheme.typography.headlineSmall)
                    Spacer(Modifier.height(8.dp))
                    Text(
                        "Новых слов и повторений сейчас нет. " +
                            "Загляните позже или загрузите ещё одну серию.",
                        style = MaterialTheme.typography.bodyMedium,
                    )
                    if (state.answered > 0) {
                        Spacer(Modifier.height(8.dp))
                        Text("Верных ответов: ${state.correctCount} из ${state.answered}")
                    }
                    Spacer(Modifier.height(16.dp))
                    Button(onClick = onBack) { Text("К отчёту") }
                }
                else -> Column(
                    modifier = Modifier.align(Alignment.Center).padding(24.dp),
                    horizontalAlignment = Alignment.CenterHorizontally,
                ) {
                    Text(state.error ?: "", color = MaterialTheme.colorScheme.error)
                    Spacer(Modifier.height(8.dp))
                    Button(onClick = viewModel::loadNext) { Text("Повторить") }
                }
            }
        }
    }
}

@Composable
private fun ExerciseContent(
    state: ExerciseUiState,
    exercise: ExerciseDto,
    onChoose: (Int) -> Unit,
    onNext: () -> Unit,
) {
    val result = state.result

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(20.dp),
    ) {
        Text(
            text = if (exercise.isNew) "Новое слово" else "Повторение",
            style = MaterialTheme.typography.labelLarge,
            color = MaterialTheme.colorScheme.primary,
        )
        Spacer(Modifier.height(8.dp))
        Text(
            "Выберите слово, которое подходит в пропуск",
            style = MaterialTheme.typography.bodyMedium,
        )
        Spacer(Modifier.height(12.dp))
        Card(modifier = Modifier.fillMaxWidth()) {
            Text(
                text = exercise.sentence,
                modifier = Modifier.padding(16.dp),
                style = MaterialTheme.typography.titleMedium,
            )
        }
        Spacer(Modifier.height(16.dp))

        exercise.options.forEach { option ->
            val mode = when {
                result == null -> OptionMode.Idle
                option.lemmaId == result.correctLemmaId -> OptionMode.Correct
                option.lemmaId == state.chosenId -> OptionMode.Wrong
                else -> OptionMode.Dimmed
            }
            OptionButton(text = option.text, mode = mode, onClick = { onChoose(option.lemmaId) })
            Spacer(Modifier.height(8.dp))
        }

        state.error?.let {
            Text(it, color = MaterialTheme.colorScheme.error)
        }

        if (result != null) {
            Spacer(Modifier.height(8.dp))
            FeedbackCard(result)
            Spacer(Modifier.height(12.dp))
            Button(onClick = onNext, modifier = Modifier.fillMaxWidth()) { Text("Дальше") }
        }
    }
}

@Composable
private fun OptionButton(text: String, mode: OptionMode, onClick: () -> Unit) {
    val colors = when (mode) {
        OptionMode.Correct -> ButtonDefaults.buttonColors(
            containerColor = Color(0xFF2E7D32),
            contentColor = Color.White,
        )
        OptionMode.Wrong -> ButtonDefaults.buttonColors(
            containerColor = Color(0xFFC62828),
            contentColor = Color.White,
        )
        OptionMode.Dimmed -> ButtonDefaults.filledTonalButtonColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f),
        )
        OptionMode.Idle -> ButtonDefaults.filledTonalButtonColors()
    }
    Button(
        onClick = onClick,
        colors = colors,
        modifier = Modifier.fillMaxWidth().heightIn(min = 52.dp),
    ) {
        Text(text, style = MaterialTheme.typography.titleMedium)
    }
}

@Composable
private fun FeedbackCard(result: AnswerResultDto) {
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = if (result.correct) "Верно!"
                else "Неверно. Правильный ответ: ${result.correctLemma}",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.SemiBold,
            )
            Spacer(Modifier.height(4.dp))
            Text(result.sentence, style = MaterialTheme.typography.bodyMedium)
            Spacer(Modifier.height(4.dp))
            Text(
                text = when {
                    result.status == "known" -> "Слово выучено"
                    result.intervalDays == 0 -> "Повторим это слово через несколько минут"
                    else -> "Следующий повтор через ${result.intervalDays} " +
                        pluralDays(result.intervalDays)
                },
                style = MaterialTheme.typography.bodySmall,
            )
        }
    }
}

private fun pluralDays(n: Int): String {
    val mod10 = n % 10
    val mod100 = n % 100
    return when {
        mod10 == 1 && mod100 != 11 -> "день"
        mod10 in 2..4 && mod100 !in 12..14 -> "дня"
        else -> "дней"
    }
}