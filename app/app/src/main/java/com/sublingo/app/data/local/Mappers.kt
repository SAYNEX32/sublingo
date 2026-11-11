package com.sublingo.app.data.local

import com.sublingo.app.data.remote.EpisodeDto
import com.sublingo.app.data.remote.ReportDto
import com.sublingo.app.data.remote.WordDto

fun EpisodeDto.toEntity() = EpisodeEntity(id, title, season, number, subtitleLines, wordCount)

fun EpisodeEntity.toDto() = EpisodeDto(id, title, season, number, subtitleLines, wordCount)

fun ReportDto.toEntity(updatedAt: Long) = ReportEntity(
    episodeId = episode.id,
    title = episode.title,
    season = episode.season,
    number = episode.number,
    subtitleLines = episode.subtitleLines,
    wordCount = episode.wordCount,
    totalWords = totalWords,
    unknownOccurrences = unknownOccurrences,
    coverage = coverage,
    target = target,
    vocabThreshold = vocabThreshold,
    wordsToTarget = wordsToTarget,
    updatedAt = updatedAt,
)

fun ReportDto.wordEntities(): List<ReportWordEntity> = toLearn.mapIndexed { index, word ->
    ReportWordEntity(
        episodeId = episode.id,
        position = index,
        lemmaId = word.lemmaId,
        lemma = word.lemma,
        pos = word.pos,
        level = word.level,
        zipf = word.zipf,
        count = word.count,
        example = word.example,
    )
}

fun ReportEntity.toDto(words: List<ReportWordEntity>) = ReportDto(
    episode = EpisodeDto(episodeId, title, season, number, subtitleLines, wordCount),
    totalWords = totalWords,
    unknownOccurrences = unknownOccurrences,
    coverage = coverage,
    target = target,
    vocabThreshold = vocabThreshold,
    wordsToTarget = wordsToTarget,
    toLearn = words.sortedBy { it.position }.map {
        WordDto(it.lemmaId, it.lemma, it.pos, it.level, it.zipf, it.count, it.example)
    },
)