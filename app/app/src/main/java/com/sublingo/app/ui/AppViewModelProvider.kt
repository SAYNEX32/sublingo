package com.sublingo.app.ui

import androidx.lifecycle.ViewModelProvider.AndroidViewModelFactory
import androidx.lifecycle.viewmodel.CreationExtras
import androidx.lifecycle.viewmodel.initializer
import androidx.lifecycle.viewmodel.viewModelFactory
import com.sublingo.app.SubLingoApp
import com.sublingo.app.ui.auth.AuthViewModel
import com.sublingo.app.ui.home.HomeViewModel

object AppViewModelProvider {
    val Factory = viewModelFactory {
        initializer { MainViewModel(subLingoApp().container.authRepository) }
        initializer { AuthViewModel(subLingoApp().container.authRepository) }
        initializer { HomeViewModel(subLingoApp().container.authRepository) }
    }
}

fun CreationExtras.subLingoApp(): SubLingoApp =
    this[AndroidViewModelFactory.APPLICATION_KEY] as SubLingoApp