package com.sublingo.app.data.repository

import com.sublingo.app.data.remote.AnswerRequest
import com.sublingo.app.data.remote.AnswerResultDto
import com.sublingo.app.data.remote.ApiResult
import com.sublingo.app.data.remote.ApiService
import com.sublingo.app.data.remote.ExerciseDto
import com.sublingo.app.data.remote.PlacementAnswerDto
import com.sublingo.app.data.remote.PlacementResultDto
import com.sublingo.app.data.remote.PlacementSubmitRequest
import com.sublingo.app.data.remote.PlacementWordDto
import com.sublingo.app.data.remote.safeApiCall
import kotlinx.serialization.json.Json

class LearningRepository(
    private val api: ApiService,
    private val json: Json,
) {
    suspend fun placementWords(): ApiResult<List<PlacementWordDto>> =
        safeApiCall(conflictMessage = "Недостаточно слов в базе. Сначала загрузите серию") {
            api.placementWords(PLACEMENT_SIZE)
        }

    suspend fun submitPlacement(
        answers: List<PlacementAnswerDto>,
    ): ApiResult<PlacementResultDto> =
        safeApiCall(validationMessage = "Слишком мало ответов") {
            api.placementSubmit(PlacementSubmitRequest(answers))
        }

    suspend fun nextExercise(episodeId: Int): ApiResult<ExerciseDto?> = safeApiCall {
        api.nextExercise(episodeId).use { body ->
            json.decodeFromString<ExerciseDto?>(body.string())
        }
    }

    suspend fun answer(
        exerciseId: Int,
        lemmaId: Int,
        responseMs: Int,
    ): ApiResult<AnswerResultDto> =
        safeApiCall(
            validationMessage = "Этого варианта нет в упражнении",
            conflictMessage = "Вы уже ответили на это упражнение",
        ) {
            api.answerExercise(exerciseId, AnswerRequest(lemmaId, responseMs))
        }

    private companion object {
        const val PLACEMENT_SIZE = 30
    }
}