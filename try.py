import cv2
import mediapipe as mp
import numpy as np
from stl import mesh
import pyvista as pv

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_face_mesh = mp.solutions.face_mesh

IMAGE_FILES = [
    'data/A_17_-50.Jpg',
    'data/A_17_0.Jpg',
    'data/A_17_+50.Jpg'
]

point_output = []

drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)
# init FaceMesh object
with mp_face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5) as face_mesh:
    # go over given images
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
            mp_drawing.draw_landmarks(
                image=annotated_image,
                landmark_list=face_landmarks,
                connections=mp_face_mesh.FACEMESH_CONTOURS,
                landmark_drawing_spec=None,
                connection_drawing_spec=mp_drawing_styles
                    .get_default_face_mesh_contours_style())
            mp_drawing.draw_landmarks(
                image=annotated_image,
                landmark_list=face_landmarks,
                connections=mp_face_mesh.FACEMESH_IRISES,
                landmark_drawing_spec=None,
                connection_drawing_spec=mp_drawing_styles
                    .get_default_face_mesh_iris_connections_style())

        cv2.imwrite('output/annotated_image' + str(idx) + '.png', annotated_image)


def mapPosition(pos, left, right):
    if pos <= left:
        return 0
    if pos >= right:
        return 1

    return (pos - left) / (right - left)


def interpolate(points):
    # new_points = sum([mesh_data.points for mesh_data in mesh_list]) / len(mesh_list)

    point_collections = points
    mesh_bounds = mesh_list[1].bounds
    left = mesh_bounds[2]
    right = mesh_bounds[3]

    center = mesh_list[1].center[1]
    front_influence = (center - left) * 0.7

    new_points = []
    # print(f'Bounds: {left}, {center}, {right}')

    for samples in zip(*point_collections):
        pos = samples[1][1]
        coef = [
            mapPosition(pos, center + front_influence, right),
            mapPosition(pos, left, center - front_influence) if pos <= center else
            1 - mapPosition(pos, center + front_influence, right),
            1 - mapPosition(pos, left, center - front_influence)]
        # print(f'Position {pos}, coefs: {coef}')
        coef_sum = sum(coef)

        coords = []
        for i in range(3):
            total = 0
            for j in range(3):
                total += (samples[j][i] * coef[j]) / coef_sum
            coords.append(total)

        new_points.append(coords)

    new_points = np.array(new_points)
    cloud = pv.PolyData(new_points)
    mesh = cloud.delaunay_2d()

    # mesh.scale([1.0, 0.8, 1.0])
    return mesh


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


meshes = point_output  # [getMeshFromPoints(points) for points in point_output]

rotateMeshes(meshes)

# meshes[0].rotate_z(50, meshes[0].center)
# meshes[2].rotate_z(-50, meshes[2].center)

centerToFirst(meshes)
scaleMeshes(meshes)

new_mesh = interpolate(meshes)

# meshes[0].translate((0, 6, 6))
# meshes[1].translate((0, 0, 6))
# meshes[2].translate((0, -6, 6))

plotter = pv.Plotter()

# plotter.add_mesh(getMeshFromPoints(interpolate(point_output)))

# old_result = np.array(old_interpolate(point_output))
# old_mesh = getMeshFromPoints(old_result)
# new_mesh.translate((1, 0, 0))
#
# plotter.add_mesh(pv.Cube(bounds=new_mesh.bounds))
# plotter.add_mesh(pv.Cube(bounds=old_mesh.bounds))
#
# new_mesh.translate((0, 0, 1))
# old_mesh.translate((0, 0, 1))
# plotter.add_mesh(new_mesh)
# plotter.add_mesh(old_mesh)

plotter.add_mesh(meshes[0])
plotter.add_mesh(meshes[1])
plotter.add_mesh(meshes[2])
plotter.add_mesh(new_mesh)

# b = meshes[1].bounds
# s1 = pv.Sphere(center = (0, b[2], 0), radius = 0.1)
# s2 = pv.Sphere(center = (0, b[3], 0), radius = 0.1)
# box = pv.Cube(bounds = b)
#
# plotter.add_mesh(s1)
# plotter.add_mesh(s2)
# plotter.add_mesh(box)

plotter.show_axes()
plotter.show()
