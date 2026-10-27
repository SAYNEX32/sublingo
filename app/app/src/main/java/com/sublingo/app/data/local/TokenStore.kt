package com.sublingo.app.data.local

import android.content.Context
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.map

private val Context.sessionDataStore by preferencesDataStore(name = "session")

class TokenStore(private val context: Context) {
    private val tokenKey = stringPreferencesKey("access_token")

    val token: Flow<String?> = context.sessionDataStore.data.map { it[tokenKey] }

    suspend fun current(): String? = token.first()

    suspend fun save(token: String) {
        context.sessionDataStore.edit { it[tokenKey] = token }
    }

    suspend fun clear() {
        context.sessionDataStore.edit { it.remove(tokenKey) }
    }
}