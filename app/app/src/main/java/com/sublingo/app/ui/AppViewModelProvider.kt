package com.sublingo.app.ui

import androidx.lifecycle.ViewModelProvider.AndroidViewModelFactory
import androidx.lifecycle.createSavedStateHandle
import androidx.lifecycle.viewmodel.CreationExtras
import androidx.lifecycle.viewmodel.initializer
import androidx.lifecycle.viewmodel.viewModelFactory
import com.sublingo.app.SubLingoApp
import com.sublingo.app.ui.auth.AuthViewModel
import com.sublingo.app.ui.episodes.EpisodesViewModel
import com.sublingo.app.ui.exercises.ExerciseViewModel
import com.sublingo.app.ui.placement.PlacementViewModel
import com.sublingo.app.ui.report.ReportViewModel

object AppViewModelProvider {
    val Factory = viewModelFactory {
        initializer { MainViewModel(subLingoApp().container.authRepository) }
        initializer { AuthViewModel(subLingoApp().container.authRepository) }
        initializer { EpisodesViewModel(subLingoApp().container.episodeRepository) }
        initializer {
            ReportViewModel(
                subLingoApp().container.episodeRepository,
                createSavedStateHandle(),
            )
        }
        initializer { PlacementViewModel(subLingoApp().container.learningRepository) }
        initializer {
            ExerciseViewModel(
                subLingoApp().container.learningRepository,
                createSavedStateHandle(),
            )
        }
    }
}

fun CreationExtras.subLingoApp(): SubLingoApp =
    this[AndroidViewModelFactory.APPLICATION_KEY] as SubLingoApp