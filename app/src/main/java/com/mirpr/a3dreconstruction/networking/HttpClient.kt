package com.mirpr.a3dreconstruction.networking

import android.util.Log
import okhttp3.*
import java.io.IOException
import okhttp3.Response


/**
 *   created by Mohi on 12/9/2021
 */

interface HttpClientCallback{
    fun onFailure()
    fun onResponse(response: Response)
}

object HttpClient {
    private const val baseServerURL = "http://192.168.1.6:5000/"
    private val okHttpClient = OkHttpClient()

    fun sendImageToProcess(data: List<String>, httpClientCallback: HttpClientCallback){

        val requestBody = FormBody.Builder()
            .add("image1", data[0])
            .add("image2", data[1])
            .add("image3", data[2])
            .build()

        val request: Request = Request.Builder()
            .url("$baseServerURL/process")
            .post(requestBody)
            .build()

        // to access the response we get from the server
        // making call asynchronously
        return okHttpClient.newCall(request).enqueue(object : Callback {
            // called if server is unreachable
            override fun onFailure(call: Call, e: IOException) {
                e.message?.let { Log.d("Failure HTTP", it) }
               httpClientCallback.onFailure()
            }

            // called if we get a response from the server
            override fun onResponse(
                call: Call,
                response: Response
            ) {
                httpClientCallback.onResponse(response)
            }
        })
    }


}