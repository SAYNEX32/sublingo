package com.sublingo.app.data.remote

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class RegisterRequest(val email: String, val password: String)

@Serializable
data class UserDto(val id: Int, val email: String)

@Serializable
data class TokenDto(
    @SerialName("access_token") val accessToken: String,
    @SerialName("token_type") val tokenType: String = "bearer",
)

@Serializable
data class EpisodeDto(
    val id: Int,
    val title: String,
    val season: Int? = null,
    val number: Int? = null,
    @SerialName("subtitle_lines") val subtitleLines: Int = 0,
    @SerialName("word_count") val wordCount: Int = 0,
)

@Serializable
data class WordDto(
    @SerialName("lemma_id") val lemmaId: Int,
    val lemma: String,
    val pos: String,
    val level: String? = null,
    val zipf: Double = 0.0,
    val count: Int = 0,
    val example: String = "",
)

@Serializable
data class ReportDto(
    val episode: EpisodeDto,
    @SerialName("total_words") val totalWords: Int,
    @SerialName("unknown_occurrences") val unknownOccurrences: Double,
    val coverage: Double,
    val target: Double,
    @SerialName("vocab_threshold") val vocabThreshold: Double? = null,
    @SerialName("words_to_target") val wordsToTarget: Int? = null,
    @SerialName("to_learn") val toLearn: List<WordDto> = emptyList(),
)

@Serializable
data class PlacementWordDto(
    @SerialName("lemma_id") val lemmaId: Int,
    val lemma: String,
    val pos: String,
)

@Serializable
data class PlacementAnswerDto(
    @SerialName("lemma_id") val lemmaId: Int,
    val known: Boolean,
)

@Serializable
data class PlacementSubmitRequest(val answers: List<PlacementAnswerDto>)

@Serializable
data class PlacementResultDto(
    @SerialName("vocab_threshold") val vocabThreshold: Double,
    @SerialName("answers_used") val answersUsed: Int,
    @SerialName("known_count") val knownCount: Int,
)

@Serializable
data class OptionDto(
    @SerialName("lemma_id") val lemmaId: Int,
    val text: String,
)

@Serializable
data class ExerciseDto(
    val id: Int,
    val kind: String,
    val sentence: String,
    val options: List<OptionDto>,
    @SerialName("is_new") val isNew: Boolean,
)

@Serializable
data class AnswerRequest(
    @SerialName("lemma_id") val lemmaId: Int,
    @SerialName("response_ms") val responseMs: Int? = null,
)

@Serializable
data class AnswerResultDto(
    val correct: Boolean,
    @SerialName("correct_lemma_id") val correctLemmaId: Int,
    @SerialName("correct_lemma") val correctLemma: String,
    @SerialName("answer_form") val answerForm: String,
    val sentence: String,
    val status: String,
    @SerialName("interval_days") val intervalDays: Int,
    @SerialName("next_review") val nextReview: String,
)