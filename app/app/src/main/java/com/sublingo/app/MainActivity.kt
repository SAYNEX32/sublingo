package com.sublingo.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import com.sublingo.app.ui.SubLingoRoot
import com.sublingo.app.ui.theme.SubLingoTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            SubLingoTheme {
                SubLingoRoot()
            }
        }
    }
}