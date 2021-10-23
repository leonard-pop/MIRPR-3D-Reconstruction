package com.mirpr.a3dreconstruction

import android.content.ContentResolver
import android.net.Uri
import androidx.lifecycle.ViewModel

import android.provider.MediaStore
import androidx.lifecycle.MutableLiveData


class MainViewModel : ViewModel() {


    private val imageProcessor = ImageProcessor()
    val meshLiveData = MutableLiveData<Uri>()
    /**
     * Method for passing the Uri of the taken picture to be processed
     */
    fun send(contentResolver: ContentResolver, uri: Uri) {
        //TODO process image
        // we need to determine what the next step is
        // get image bitmap - do stuff with image - return the mesh?

        // launch processing on new thread so it doesn't block the UI thread
        Thread{
            imageProcessor.process(MediaStore.Images.Media.getBitmap(contentResolver , uri), meshLiveData)
        }.start()
    }


}