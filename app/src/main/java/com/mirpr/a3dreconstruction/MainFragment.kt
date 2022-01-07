package com.mirpr.a3dreconstruction

import android.net.Uri
import androidx.lifecycle.ViewModelProvider
import android.os.Bundle
import android.util.Log
import androidx.fragment.app.Fragment
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.ImageView
import androidx.activity.result.contract.ActivityResultContracts
import androidx.core.content.FileProvider
import java.io.File

import androidx.lifecycle.lifecycleScope
import android.content.Intent
import android.widget.RelativeLayout
import android.widget.Toast
import java.io.InputStream
import java.io.ByteArrayOutputStream

import android.util.Base64

class MainFragment : Fragment() {

    companion object {
        fun newInstance() = MainFragment()
        const val TAG = "LOG_TAG"
    }

    private lateinit var viewModel: MainViewModel
    // view for displaying the taken image
    private lateinit var image: ImageView
    // button for taking a photo
    private lateinit var buttonTakePhoto: Button
    private lateinit var buttonShow3D: Button
    // layout for displaying loading info
    private lateinit var generatingLayout: RelativeLayout
    private lateinit var file: File
    private lateinit var uri: Uri

    private var noTakenImages = 0

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        return inflater.inflate(R.layout.main_fragment, container, false)
    }


    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        viewModel = ViewModelProvider(this).get(MainViewModel::class.java)
        image = view.findViewById(R.id.image)
        buttonTakePhoto = view.findViewById(R.id.button_take_photo)
        buttonShow3D = view.findViewById(R.id.button_show_3d)
        generatingLayout = view.findViewById(R.id.generating_layout)

        // create the file where the image will be stored
        file = File(requireActivity().filesDir, "picFromCamera")

        // get the uri for the file
        uri = FileProvider.getUriForFile(
            requireContext(),
            requireActivity().packageName + ".provider",
            file
        )

        // set listener to button
        buttonTakePhoto.setOnClickListener {
            takeImage()
        }
        buttonShow3D.setOnClickListener {
            displaySTL()
        }

        // subscribe to viewmodel livedata
        viewModel.meshLiveData.observe(viewLifecycleOwner, {
            // when an Uri is posted to the livedata, the mesh corresponding to it is displayed
            generatingLayout.visibility = View.GONE
            if(it!=Uri.EMPTY) {
                displaySTL()
            }else{
                Toast.makeText(requireContext(), "Something went horribly wrong!", Toast.LENGTH_SHORT).show()
            }
        })
    }

    private var imageList = arrayListOf<String>()

    // send intent for taking a picture
    private val takeImageResult = registerForActivityResult(ActivityResultContracts.TakePicture()) { isSuccess ->
        if (isSuccess) {
            latestTmpUri?.let { uri ->
                image.setImageURI(uri)
                // do other stuff with the Uri
                Log.d(TAG, uri.toString())
                val iStream: InputStream? = requireActivity().contentResolver.openInputStream(uri)
                val inputData: ByteArray? = iStream?.let { it1 -> getBytes(it1) }
                val data = Base64.encodeToString(inputData, Base64.DEFAULT)
                imageList.add(data)
                noTakenImages++
                if(noTakenImages<3){
                    takeImage()
                }else{
                    noTakenImages=0
                    viewModel.send(imageList)
                    imageList= arrayListOf()
                }
                generatingLayout.visibility = View.VISIBLE
            }
        }
    }

    private fun getBytes(inputStream: InputStream): ByteArray {
        val byteBuffer = ByteArrayOutputStream()
        val bufferSize = 1024
        val buffer = ByteArray(bufferSize)
        var len = 0
        while (inputStream.read(buffer).also { len = it } != -1) {
            byteBuffer.write(buffer, 0, len)
        }
        return byteBuffer.toByteArray()
    }

    private var latestTmpUri: Uri? = null

    // launches the take picture flow
    private fun takeImage() {
        lifecycleScope.launchWhenStarted {
            getTmpFileUri().let { uri ->
                latestTmpUri = uri
                takeImageResult.launch(uri)
            }
        }
    }

    private fun getTmpFileUri(): Uri {
        val tmpFile = File.createTempFile("tmp_image_file", ".png", requireActivity().cacheDir).apply {
            createNewFile()
            deleteOnExit()
        }

        return FileProvider.getUriForFile(requireContext().applicationContext, "${BuildConfig.APPLICATION_ID}.provider", tmpFile)
    }

    // method for viewing a 3D model (uses the Google AR thingy stuff app)
    private fun displaySTL(){
        val sceneViewerIntent = Intent(Intent.ACTION_VIEW)

        // the GLTF file is obtain remotely from the server
        sceneViewerIntent.data =
            Uri.parse("https://arvr.google.com/scene-viewer/1.0")
                .buildUpon()
                .appendQueryParameter("file","http://192.168.1.6:5000/model")
                .appendQueryParameter("mode", "3d_only")
                .build()
        Log.d("MIRPR_DEBUG_TAG",sceneViewerIntent.data.toString())
        sceneViewerIntent.setPackage("com.google.ar.core")

        startActivity(sceneViewerIntent)
    }
}