package com.mirpr.a3dreconstruction

import android.net.Uri
import androidx.lifecycle.ViewModel

import android.util.Log
import androidx.lifecycle.MutableLiveData
import com.mirpr.a3dreconstruction.networking.HttpClient
import com.mirpr.a3dreconstruction.networking.HttpClientCallback
import okhttp3.Response

class MainViewModel : ViewModel() {
    val meshLiveData = MutableLiveData<Uri>()
    /**
     * Method for passing the Uri of the taken picture to be processed
     */
    fun send(data: List<String>) {
        Thread{
            Log.d("Mohi",data.toString())
            HttpClient.sendImageToProcess(data, object: HttpClientCallback {
                override fun onFailure() {
                    Log.d("Mohi","fail")
                }

                override fun onResponse(response: Response) {
                    Log.d("Mohi","$response")
                }

            })
        }.start()
    }

}