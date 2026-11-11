package com.sublingo.app.data.local

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import androidx.room.Transaction
import kotlinx.coroutines.flow.Flow

@Dao
abstract class CacheDao {
    @Query("SELECT * FROM episodes ORDER BY id DESC")
    abstract fun observeEpisodes(): Flow<List<EpisodeEntity>>

    @Query("DELETE FROM episodes")
    abstract suspend fun clearEpisodes()

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    abstract suspend fun insertEpisodes(items: List<EpisodeEntity>)

    @Transaction
    open suspend fun replaceEpisodes(items: List<EpisodeEntity>) {
        clearEpisodes()
        insertEpisodes(items)
    }

    @Query("SELECT * FROM reports WHERE episode_id = :episodeId")
    abstract fun observeReport(episodeId: Int): Flow<ReportEntity?>

    @Query("SELECT * FROM report_words WHERE episode_id = :episodeId ORDER BY position")
    abstract fun observeReportWords(episodeId: Int): Flow<List<ReportWordEntity>>

    @Query("DELETE FROM report_words WHERE episode_id = :episodeId")
    abstract suspend fun clearReportWords(episodeId: Int)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    abstract suspend fun insertReport(report: ReportEntity)

    @Insert
    abstract suspend fun insertReportWords(words: List<ReportWordEntity>)

    @Transaction
    open suspend fun replaceReport(report: ReportEntity, words: List<ReportWordEntity>) {
        clearReportWords(report.episodeId)
        insertReport(report)
        insertReportWords(words)
    }
}