import cv2
import mediapipe as mp
import numpy as np
from stl import mesh
import pyvista as pv
import scipy as sp
import sys

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_face_mesh = mp.solutions.face_mesh

def getFaces(connections):
    faces = set()
    # for index, pair in enumerate(connections):
    #    for vertex in pair:
    #        for other_pair in connections[index + 1:]:
    #            new_face = [vertex, other_pair[0],
    #                    other_pair[1]]
    #            new_face.sort()
    #            faces.add(tuple(new_face))

    # print(faces)
    # sys.exit(1)

    return [[tri[0], tri[1], tri[2]] for tri in faces]


def getMeshFromPoints(points, connections):
    # points = np.array(points)
    # cloud = pv.PolyData(points)
    # print(len(points), end=" ")
    # mesh = cloud.delaunay_2d()
    # print(len(mesh.points))

    # mesh = cloud.delaunay_3d()
    # mesh = cloud.reconstruct_surface()

    # mesh.scale([1.0, 0.8, 1.0])
    # cloud.plot(point_size=15)

    mesh = pv.PolyData(points, lines=connections)
    return mesh


def mapPosition(pos, left, right):
    if pos <= left:
        return 0
    if pos >= right:
        return 1

    return (pos - left) / (right - left)


def interpolate(mesh_list, connections):
    # new_points = sum([mesh_data.points for mesh_data in mesh_list]) / len(mesh_list)

    point_collections = [mesh_data.points for mesh_data in mesh_list]
    mesh_bounds = mesh_list[1].bounds
    left = mesh_bounds[2]
    right = mesh_bounds[3]

    center = mesh_list[1].center[1]
    front_influence = (center - left) * 0.3

    new_points = []
    # print(f'Bounds: {left}, {center}, {right}')

    for samples in zip(*point_collections):
        # y coordinate of the point from the second mesh
        pos = samples[1][1]

        coef = [
            mapPosition(pos, center + front_influence, right),
            mapPosition(pos, left, center - front_influence) if pos <= center else
            1 - mapPosition(pos, center + front_influence, right),
            1 - mapPosition(pos, left, center - front_influence)]
        # print(f'Position {pos}, coefs: {coef}')

        # coef = [0, 1, 0]
        coef_sum = sum(coef)

        coords = []
        for i in range(3):
            total = 0
            for j in range(3):
                total += (samples[j][i] * coef[j])
            total /= coef_sum
            coords.append(total)

        new_points.append(coords)

    return getMeshFromPoints(new_points, connections)


def rotateMeshes(mesh_list):
    for element in mesh_list:
        element.rotate_x(-90, element.center)
        element.rotate_z(90, element.center)


def centerToFirst(mesh_list):
    dest = np.array(mesh_list[0].center)

    for element in mesh_list[1:]:
        element.translate(dest - np.array(element.center))


def scaleMeshes(mesh_list):
    for element in mesh_list:
        element.scale([10.0, 10.0, 10.0])


def triangulateMesh(input_mesh):
    input_mesh.rotate_y(-90, input_mesh.center)
    input_mesh.delaunay_2d(inplace=True, tol=0.0001)
    input_mesh.rotate_y(90, input_mesh.center)


def generateSTL(IMAGE_FILES):
    point_output = []

    drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)
    with mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5) as face_mesh:
        # print(len(mp_face_mesh.FACEMESH_TESSELATION))
        # print(mp_face_mesh.FACEMESH_TESSELATION)
        for idx, file in enumerate(IMAGE_FILES):
            image = cv2.imread(file)
            # Convert the BGR image to RGB before processing.
            results = face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            # results = face_mesh.process(image);

            # Print and draw face mesh landmarks on the image.
            if not results.multi_face_landmarks:
                continue
            annotated_image = image.copy()

            for face_landmarks in results.multi_face_landmarks:
                # print('face_landmarks:', face_landmarks)

                landmarks = face_landmarks.landmark

                # Write landmarks to STL
                # face_mesh = mesh.Mesh(np.zeros(len(landmarks), dtype=mesh.Mesh.dtype))
                point_list = []

                for i, coords in enumerate(landmarks):
                    point_list.append([coords.x, coords.y, coords.z])

                point_output.append(point_list)

                # Draw annotations
                mp_drawing.draw_landmarks(
                    image=annotated_image,
                    landmark_list=face_landmarks,
                    connections=mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=mp_drawing_styles
                        .get_default_face_mesh_tesselation_style())
                # mp_drawing.draw_landmarks(
                #    image=annotated_image,
                #    landmark_list=face_landmarks,
                #    connections=mp_face_mesh.FACEMESH_CONTOURS,
                #    landmark_drawing_spec=None,
                #    connection_drawing_spec=mp_drawing_styles
                #    .get_default_face_mesh_contours_style())
                # mp_drawing.draw_landmarks(
                #    image=annotated_image,
                #    landmark_list=face_landmarks,
                #    connections=mp_face_mesh.FACEMESH_IRISES,
                #    landmark_drawing_spec=None,
                #    connection_drawing_spec=mp_drawing_styles
                #    .get_default_face_mesh_iris_connections_style())

            cv2.imwrite('output/annotated_image' + str(idx) + '.png', annotated_image)

    connections = [[2, pair[0], pair[1]] for pair in mp_face_mesh.FACEMESH_TESSELATION]
    faces = getFaces(connections)
    meshes = [getMeshFromPoints(points, connections) for points in point_output]

    rotateMeshes(meshes)
    scaleMeshes(meshes)

    meshes[0].rotate_z(50, meshes[0].center)
    meshes[2].rotate_z(-50, meshes[2].center)

    centerToFirst(meshes)

    new_mesh = interpolate(meshes, connections)

    triangulateMesh(new_mesh)

    # new_mesh.smooth(100, inplace = True, convergence = 0.01)
    # new_mesh.subdivide(2, inplace = True, subfilter = 'loop')
    # new_mesh.smooth(100, inplace = True, convergence = 0.01)

    for element in meshes:
        triangulateMesh(element)

    meshes[0].translate((0, 6, 6))
    meshes[1].translate((0, 0, 6))
    meshes[2].translate((0, -6, 6))

    plotter = pv.Plotter()

    new_mesh = new_mesh.extract_all_edges()

    # new_mesh.extrude_rotate(resolution=1, dradius=0.005,
    #        angle=0.1, inplace=True)
    #
    # new_mesh.rotate_x(90, new_mesh.center)

    # new_mesh.extrude_rotate(resolution=1, dradius=0.005,
    #        angle=0.1, capping=True, inplace=True)

    new_mesh.tube(radius=0.02, inplace=True)
    # sphere = pv.Sphere(center=new_mesh.center, radius=5)
    # new_mesh = new_mesh.boolean_union(sphere)

    # new_mesh.rotate_z(-90, new_mesh.center)

    # print("Manifold: " + str(new_mesh.is_manifold))
    # new_mesh.triangulate(inplace=True)
    # new_mesh = new_mesh.subdivide(5)
    # new_mesh.smooth(1000, inplace=True)
    # new_mesh.subdivide(1, 'butterfly', inplace=True)

    # plotter.add_mesh(meshes[0])
    # plotter.add_mesh(meshes[1])
    # plotter.add_mesh(meshes[2])
    # plotter.add_mesh(new_mesh, show_edges=False)
    #
    # plotter.show_axes()
    # plotter.show()

    # new_mesh.flip_normals()
    new_mesh.translate(np.array([0, 0, 0]) - new_mesh.center)
    new_mesh.rotate_x(-90)
    new_mesh.save("output/mesh.stl")
    print("the mesh was generated")


if __name__ == "__main__":
    # IMAGE_FILES = [
    #     'data/A_02_-50.Jpg',
    #     'data/A_02_0.Jpg',
    #     'data/A_02_+50.Jpg']
    IMAGE_FILES = [
        'receivedImgs/recvdimg3.png',
        'receivedImgs/recvdimg2.png',
        'receivedImgs/recvdimg1.png',
    ]
    generateSTL(IMAGE_FILES)
