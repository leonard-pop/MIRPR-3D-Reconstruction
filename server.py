from flask import Flask, request

# Flask Constructor
from GLTFfromSTL import generateGLTFfromSTL
from generateSTL import generateSTL
from processer.stl_to_GLTF_converter import convertSTLtoGLTF

app = Flask(__name__)


# decorator to associate
# a function with the url
@app.route("/")
def showHomePage():
    # response from the server
    return "Hello world from Flask v2"


@app.route("/debug", methods=["POST"])
def debug():
    text = request.form["sample"]
    print(text)
    return "received"


@app.route("/model", methods=["GET"])
def getModel():
    generateGLTFfromSTL()
    filename = "model/display_mesh.gltf"
    import codecs
    types_of_encoding = ["utf8", "cp1252"]
    for encoding_type in types_of_encoding:
        with codecs.open(filename, encoding=encoding_type, errors='replace') as file:
            content = file.read()
    return content


@app.route("/display_mesh.bin", methods=["GET"])
def getBin():
    filename = "model/display_mesh.bin"

    with(open(filename, 'rb')) as file:
        content = file.read()

    return content


@app.route("/converter", methods=["GET"])
def convert():
    convertSTLtoGLTF()

    return "done"


@app.route("/process", methods=["POST"])
def process():
    import base64
    IMAGE_FILES = []
    for i in range(1, 4):
        print(i)
        img_data = request.form["image{}".format(str(i))]
        print(img_data[:10])
        if len(img_data) > 0:
            with open("receivedImgs/recvdimg{}.png".format(str(i)), "wb") as fh:
                fh.write(base64.b64decode(img_data))
            IMAGE_FILES.append("receivedImgs/recvdimg{}.png".format(str(i)))
    print(IMAGE_FILES)

    generateSTL(IMAGE_FILES)
    return "received image"


if __name__ == "__main__":
    app.run(host="0.0.0.0")
