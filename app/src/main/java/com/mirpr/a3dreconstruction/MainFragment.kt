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
    // layout for displaying loading info
    private lateinit var generatingLayout: RelativeLayout

    private lateinit var file: File
    private lateinit var uri: Uri

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

        // subscribe to viewmodel livedata
        viewModel.meshLiveData.observe(viewLifecycleOwner, {
            // when an Uri is posted to the livedata, the mesh corresponding to it is displayed
            generatingLayout.visibility = View.GONE
            if(it!=Uri.EMPTY) {
                displaySTL(it)
            }else{
                Toast.makeText(requireContext(), "Something went horribly wrong!", Toast.LENGTH_SHORT).show()
            }
        })
    }

    // send intent for taking a picture
    private val takeImageResult = registerForActivityResult(ActivityResultContracts.TakePicture()) { isSuccess ->
        if (isSuccess) {
            latestTmpUri?.let { uri ->
                image.setImageURI(uri)
                // do other stuff with the Uri
                Log.d(TAG, uri.toString())

                generatingLayout.visibility = View.VISIBLE
                viewModel.send(requireActivity().contentResolver, uri)

            }
        }
    }


    // sent intent for selecting picture from camera - might use this later as well
    private val selectImageFromGalleryResult = registerForActivityResult(ActivityResultContracts.GetContent()) { uri: Uri? ->
        uri?.let { image.setImageURI(uri) }
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

    // might be used later
    private fun selectImageFromGallery() = selectImageFromGalleryResult.launch("image/*")


    private fun getTmpFileUri(): Uri {
        val tmpFile = File.createTempFile("tmp_image_file", ".png", requireActivity().cacheDir).apply {
            createNewFile()
            deleteOnExit()
        }

        return FileProvider.getUriForFile(requireContext().applicationContext, "${BuildConfig.APPLICATION_ID}.provider", tmpFile)
    }

    // method for viewing a 3D model (uses the Google AR thingy stuff app)
    private fun displaySTL(uri: Uri){
        val sceneViewerIntent = Intent(Intent.ACTION_VIEW)
        sceneViewerIntent.data = uri

        sceneViewerIntent.setPackage("com.google.android.googlequicksearchbox")
        startActivity(sceneViewerIntent)
    }
}