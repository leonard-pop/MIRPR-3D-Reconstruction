package com.mirpr.a3dreconstruction

import android.graphics.Bitmap
import android.util.Log
import android.graphics.Color
import android.net.Uri

import androidx.lifecycle.MutableLiveData


/**
 *   created by Mohi on 10/21/2021
 */
class ImageProcessor {
    fun process(bitmap: Bitmap?, meshLiveData: MutableLiveData<Uri>) {
        Log.d("LOG_TAG","done extracting the bitmap")

        bitmap?.let {
            meshLiveData.postValue(doStuff(it))
        }

    }

    /**
     * Method for processing the bitmap of the picture
     * @return uri - the uri of the mesh file
     */
    private fun doStuff(bitmap: Bitmap): Uri {

//        var pixelMatrix = ""
//        for(i in 0..100) {
//            for (j in 0..100) {
//                val colour: Int = bitmap.getPixel(i, j)
//
//                val red = Color.red(colour)
//                val blue = Color.blue(colour)
//                val green = Color.green(colour)
//                val alpha = Color.alpha(colour)
//
//                pixelMatrix += " [$red, $blue, $green, $alpha]"
//            }
//            pixelMatrix += '\n'
//        }
//        Log.d("PIXEL_MATRIX", pixelMatrix)

        //Thread.sleep(2000)
        //return Uri.EMPTY
        return Uri.parse("https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Models/master/2.0/Avocado/glTF/Avocado.gltf")
    }
}