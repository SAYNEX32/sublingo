package com.sublingo.app.data.local

import androidx.room.ColumnInfo
import androidx.room.Entity
import androidx.room.ForeignKey
import androidx.room.Index
import androidx.room.PrimaryKey

@Entity(tableName = "episodes")
data class EpisodeEntity(
    @PrimaryKey val id: Int,
    val title: String,
    val season: Int?,
    val number: Int?,
    @ColumnInfo(name = "subtitle_lines") val subtitleLines: Int,
    @ColumnInfo(name = "word_count") val wordCount: Int,
)

@Entity(tableName = "reports")
data class ReportEntity(
    @PrimaryKey @ColumnInfo(name = "episode_id") val episodeId: Int,
    val title: String,
    val season: Int?,
    val number: Int?,
    @ColumnInfo(name = "subtitle_lines") val subtitleLines: Int,
    @ColumnInfo(name = "word_count") val wordCount: Int,
    @ColumnInfo(name = "total_words") val totalWords: Int,
    @ColumnInfo(name = "unknown_occurrences") val unknownOccurrences: Double,
    val coverage: Double,
    val target: Double,
    @ColumnInfo(name = "vocab_threshold") val vocabThreshold: Double?,
    @ColumnInfo(name = "words_to_target") val wordsToTarget: Int?,
    @ColumnInfo(name = "updated_at") val updatedAt: Long,
)

@Entity(
    tableName = "report_words",
    foreignKeys = [
        ForeignKey(
            entity = ReportEntity::class,
            parentColumns = ["episode_id"],
            childColumns = ["episode_id"],
            onDelete = ForeignKey.CASCADE,
        ),
    ],
    indices = [Index("episode_id")],
)
data class ReportWordEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    @ColumnInfo(name = "episode_id") val episodeId: Int,
    val position: Int,
    @ColumnInfo(name = "lemma_id") val lemmaId: Int,
    val lemma: String,
    val pos: String,
    val level: String?,
    val zipf: Double,
    val count: Int,
    val example: String,
)