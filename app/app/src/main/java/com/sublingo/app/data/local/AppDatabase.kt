package com.sublingo.app.data.local

import androidx.room.Database
import androidx.room.RoomDatabase

@Database(
    entities = [EpisodeEntity::class, ReportEntity::class, ReportWordEntity::class],
    version = 1,
    exportSchema = true,
)
abstract class AppDatabase : RoomDatabase() {
    abstract fun cacheDao(): CacheDao
}