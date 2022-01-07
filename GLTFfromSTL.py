import pygltflib
import numpy as np
from stl import mesh
from math import sqrt


def normalize(vector):
    norm = 0
    for i in range(0, len(vector)):
        norm += vector[i] * vector[i]
    norm = sqrt(norm)
    for i in range(0, len(vector)):
        vector[i] = vector[i] / norm

    return vector


def generateGLTFfromSTL():
    stl_mesh = mesh.Mesh.from_file('output/mesh.stl')

    stl_points = []
    for i in range(0, len(stl_mesh.points)):  # Convert points into correct numpy array
        stl_points.append([stl_mesh.points[i][0], stl_mesh.points[i][1], stl_mesh.points[i][2]])
        stl_points.append([stl_mesh.points[i][3], stl_mesh.points[i][4], stl_mesh.points[i][5]])
        stl_points.append([stl_mesh.points[i][6], stl_mesh.points[i][7], stl_mesh.points[i][8]])

    points = np.array(
        stl_points,
        dtype="float32",
    )

    stl_normals = []
    for i in range(0, len(stl_mesh.normals)):  # Convert points into correct numpy array
        normal_vector = [stl_mesh.normals[i][0], stl_mesh.normals[i][1], stl_mesh.normals[i][2]]
        normal_vector = normalize(normal_vector)
        stl_normals.append(normal_vector)
        stl_normals.append(normal_vector)
        stl_normals.append(normal_vector)

    normals = np.array(
        stl_normals,
        dtype="float32"
    )

    points_binary_blob = points.tobytes()
    normals_binary_blob = normals.tobytes()

    gltf = pygltflib.GLTF2(
        scene=0,
        scenes=[pygltflib.Scene(nodes=[0])],
        nodes=[pygltflib.Node(mesh=0)],
        meshes=[
            pygltflib.Mesh(
                primitives=[
                    pygltflib.Primitive(
                        attributes=pygltflib.Attributes(POSITION=0, NORMAL=1), indices=None
                    )
                ]
            )
        ],
        accessors=[
            pygltflib.Accessor(
                bufferView=0,
                componentType=pygltflib.FLOAT,
                count=len(points),
                type=pygltflib.VEC3,
                max=points.max(axis=0).tolist(),
                min=points.min(axis=0).tolist(),
            ),
            pygltflib.Accessor(
                bufferView=1,
                componentType=pygltflib.FLOAT,
                count=len(normals),
                type=pygltflib.VEC3,
                max=None,
                min=None,
            ),
        ],
        bufferViews=[
            pygltflib.BufferView(
                buffer=0,
                byteOffset=0,
                byteLength=len(points_binary_blob),
                target=pygltflib.ARRAY_BUFFER,
            ),
            pygltflib.BufferView(
                buffer=0,
                byteOffset=len(points_binary_blob),
                byteLength=len(normals_binary_blob),
                target=pygltflib.ARRAY_BUFFER,
            ),
        ],
        buffers=[
            pygltflib.Buffer(
                byteLength=len(points_binary_blob) + len(normals_binary_blob)
            )
        ],
    )
    gltf.set_binary_blob(points_binary_blob + normals_binary_blob)
    gltf.save("model/display_mesh.gltf")
