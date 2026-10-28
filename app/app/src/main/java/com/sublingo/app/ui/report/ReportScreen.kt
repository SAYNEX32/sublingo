package com.sublingo.app.ui.report

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
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
import com.sublingo.app.data.remote.ReportDto
import com.sublingo.app.data.remote.WordDto
import com.sublingo.app.ui.AppViewModelProvider
import java.util.Locale
import kotlin.math.roundToInt

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ReportScreen(
    onBack: () -> Unit,
    viewModel: ReportViewModel = viewModel(factory = AppViewModelProvider.Factory),
) {
    val state by viewModel.state.collectAsStateWithLifecycle()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(state.report?.episode?.title ?: "Отчёт") },
                navigationIcon = { TextButton(onClick = onBack) { Text("Назад") } },
            )
        },
    ) { padding ->
        Box(modifier = Modifier.padding(padding).fillMaxSize()) {
            val report = state.report
            when {
                state.loading -> CircularProgressIndicator(
                    modifier = Modifier.align(Alignment.Center)
                )
                report != null -> ReportContent(report)
                else -> Column(
                    modifier = Modifier.align(Alignment.Center).padding(24.dp),
                    horizontalAlignment = Alignment.CenterHorizontally,
                ) {
                    Text(state.error ?: "", color = MaterialTheme.colorScheme.error)
                    Spacer(Modifier.height(8.dp))
                    Button(onClick = viewModel::load) { Text("Повторить") }
                }
            }
        }
    }
}

@Composable
private fun ReportContent(report: ReportDto) {
    val percent = String.format(Locale.getDefault(), "%.1f%%", report.coverage * 100)
    val targetPercent = (report.target * 100).roundToInt()

    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        item {
            Column {
                Text("Вы понимаете примерно", style = MaterialTheme.typography.bodyMedium)
                Text(percent, style = MaterialTheme.typography.displayMedium)
                Spacer(Modifier.height(8.dp))
                LinearProgressIndicator(
                    progress = { report.coverage.toFloat().coerceIn(0f, 1f) },
                    modifier = Modifier.fillMaxWidth(),
                )
                Spacer(Modifier.height(12.dp))
                val toGo = report.wordsToTarget
                Text(
                    text = if (toGo != null) {
                        "Чтобы понимать $targetPercent% слов, выучите $toGo ${pluralWords(toGo)}"
                    } else {
                        "Вы уже понимаете $targetPercent% слов этой серии"
                    },
                    style = MaterialTheme.typography.titleMedium,
                )
                if (report.vocabThreshold == null) {
                    Spacer(Modifier.height(4.dp))
                    Text(
                        text = "Оценка приблизительная: пройдите тест уровня, и она станет точнее",
                        style = MaterialTheme.typography.bodySmall,
                    )
                }
                Spacer(Modifier.height(16.dp))
                Text("Слова для изучения", style = MaterialTheme.typography.titleLarge)
            }
        }
        items(report.toLearn, key = { it.lemmaId }) { word -> WordCard(word) }
    }
}

@Composable
private fun WordCard(word: WordDto) {
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(modifier = Modifier.padding(12.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    text = word.lemma,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.SemiBold,
                )
                Spacer(Modifier.width(8.dp))
                Text(
                    text = listOfNotNull(word.pos, word.level).joinToString(" · "),
                    style = MaterialTheme.typography.labelMedium,
                )
                Spacer(Modifier.weight(1f))
                Text("×${word.count}", style = MaterialTheme.typography.labelLarge)
            }
            if (word.example.isNotBlank()) {
                Spacer(Modifier.height(4.dp))
                Text(word.example, style = MaterialTheme.typography.bodySmall)
            }
        }
    }
}

private fun pluralWords(n: Int): String {
    val mod10 = n % 10
    val mod100 = n % 100
    return when {
        mod10 == 1 && mod100 != 11 -> "слово"
        mod10 in 2..4 && mod100 !in 12..14 -> "слова"
        else -> "слов"
    }
}