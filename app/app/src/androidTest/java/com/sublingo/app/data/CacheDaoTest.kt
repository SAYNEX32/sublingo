package com.sublingo.app.data

import android.content.Context
import androidx.room.Room
import androidx.test.core.app.ApplicationProvider
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.sublingo.app.data.local.AppDatabase
import com.sublingo.app.data.local.CacheDao
import com.sublingo.app.data.local.EpisodeEntity
import com.sublingo.app.data.local.ReportEntity
import com.sublingo.app.data.local.ReportWordEntity
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.runBlocking
import org.junit.After
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class CacheDaoTest {
    private lateinit var db: AppDatabase
    private lateinit var dao: CacheDao

    @Before
    fun setUp() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        db = Room.inMemoryDatabaseBuilder(context, AppDatabase::class.java).build()
        dao = db.cacheDao()
    }

    @After
    fun tearDown() {
        db.close()
    }

    private fun episode(id: Int) = EpisodeEntity(id, "Show $id", null, null, 10, 5)

    private fun report(episodeId: Int) = ReportEntity(
        episodeId, "Show $episodeId", null, null, 10, 5,
        100, 20.0, 0.8, 0.95, 4.5, 2, 1L,
    )

    private fun word(episodeId: Int, position: Int, lemma: String) = ReportWordEntity(
        episodeId = episodeId, position = position, lemmaId = position + 1, lemma = lemma,
        pos = "NOUN", level = "B2", zipf = 3.5, count = 4, example = "An example.",
    )

    @Test
    fun replaceEpisodes_removesOldRows() = runBlocking {
        dao.replaceEpisodes(listOf(episode(1), episode(2)))
        dao.replaceEpisodes(listOf(episode(3)))
        assertEquals(listOf(3), dao.observeEpisodes().first().map { it.id })
    }

    @Test
    fun replaceReport_replacesWordsAndKeepsOrder() = runBlocking {
        dao.replaceReport(report(1), listOf(word(1, 1, "beta"), word(1, 0, "alpha")))
        dao.replaceReport(report(1), listOf(word(1, 0, "gamma"), word(1, 1, "delta")))
        assertEquals(listOf("gamma", "delta"), dao.observeReportWords(1).first().map { it.lemma })
    }

    @Test
    fun clearAllTables_emptiesTheCache() = runBlocking {
        dao.replaceEpisodes(listOf(episode(1)))
        dao.replaceReport(report(1), listOf(word(1, 0, "alpha")))
        db.clearAllTables()
        assertEquals(emptyList<EpisodeEntity>(), dao.observeEpisodes().first())
        assertNull(dao.observeReport(1).first())
        assertEquals(emptyList<ReportWordEntity>(), dao.observeReportWords(1).first())
    }
}