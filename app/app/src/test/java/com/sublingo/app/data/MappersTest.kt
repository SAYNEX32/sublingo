package com.sublingo.app.data

import com.sublingo.app.data.local.toDto
import com.sublingo.app.data.local.toEntity
import com.sublingo.app.data.local.wordEntities
import com.sublingo.app.data.remote.EpisodeDto
import com.sublingo.app.data.remote.ReportDto
import com.sublingo.app.data.remote.WordDto
import org.junit.Assert.assertEquals
import org.junit.Test

class MappersTest {
    private val report = ReportDto(
        episode = EpisodeDto(7, "Oppenheimer", null, null, 2885, 907),
        totalWords = 19097,
        unknownOccurrences = 1008.0,
        coverage = 0.9472,
        target = 0.95,
        vocabThreshold = 4.8,
        wordsToTarget = 4,
        toLearn = listOf(
            WordDto(1, "atomic", "ADJ", "B2", 3.98, 35, "The atomic program."),
            WordDto(2, "hydrogen", "NOUN", "B2", 3.98, 18, "We use hydrogen."),
        ),
    )

    @Test
    fun episode_survives_round_trip() {
        val episode = report.episode
        assertEquals(episode, episode.toEntity().toDto())
    }

    @Test
    fun word_positions_follow_list_order() {
        assertEquals(listOf(0, 1), report.wordEntities().map { it.position })
    }

    @Test
    fun report_survives_round_trip_even_if_words_come_back_unordered() {
        val entity = report.toEntity(updatedAt = 1L)
        val shuffled = report.wordEntities().reversed()
        assertEquals(report, entity.toDto(shuffled))
    }
}