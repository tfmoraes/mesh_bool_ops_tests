import sys

import numpy as np
import pymeshfix
import vtk
from vtk.util import numpy_support
from pymeshfix import _meshfix


def show_polydatas(polydatas, colors=[]):
    renderer = vtk.vtkRenderer()

    for i, polydata in enumerate(polydatas):
        try:
            color = colors[i]
        except IndexError:
            color = (1.0, 1.0, 1.0)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(polydata)

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(color)

        renderer.AddActor(actor)

    ren_win = vtk.vtkRenderWindow()
    ren_win.AddRenderer(renderer)

    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(ren_win)
    iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
    iren.Start()


def save_polydata(polydata, filename):
    if filename.lower().endswith(".stl"):
        writer = vtk.vtkSTLWriter()
    elif filename.lower().endswith(".ply"):
        writer = vtk.vtkPLYWriter()
    else:
        print("File must be STL or PLY")
        sys.exit(0)
    writer.SetInputData(polydata)
    writer.SetFileName(filename)
    writer.Write()


def polydata_to_numpy(polydata):
    vertices = numpy_support.vtk_to_numpy(polydata.GetPoints().GetData())
    vertices.shape = -1, 3

    faces = numpy_support.vtk_to_numpy(polydata.GetPolys().GetData())
    faces.shape = -1, 4

    return vertices, faces


def numpy_to_polydata(vertices, faces):
    _faces = np.empty_like(faces, shape=(faces.shape[0], 4), dtype=np.int64)
    _faces[:, 0] = 3
    _faces[:, 1:] = faces

    points = vtk.vtkPoints()
    points.SetData(numpy_support.numpy_to_vtk(vertices))

    id_triangles = numpy_support.numpy_to_vtkIdTypeArray(_faces)
    triangles = vtk.vtkCellArray()
    triangles.SetCells(_faces.shape[0], id_triangles)

    polydata = vtk.vtkPolyData()
    polydata.SetPoints(points)
    polydata.SetPolys(triangles)

    return polydata


def fix_polydata(polydata):
    vertices, faces = polydata_to_numpy(polydata)
    #  meshfix = pymeshfix.MeshFix(vertices, faces[:, 1:])
    #  meshfix.repair()
    tin = _meshfix.PyTMesh()
    tin.load_array(vertices, faces[:, 1:])

    tin.fill_small_boundaries()
    print('There are {:d} boundaries'.format(tin.boundaries()))


    # Clean (removes self intersections)
    # tin.clean(max_iters=10, inner_loops=3)
    # Check mesh for holes again
    # print('There are {:d} boundaries'.format(tin.boundaries()))

    clean_vertices, clean_faces = tin.return_arrays()
    fixed_polydata = numpy_to_polydata(clean_vertices, clean_faces)
    return fixed_polydata


def apply_boolean_operation(polydata1, polydata2, operation="difference"):
    boolean_operator = vtk.vtkBooleanOperationPolyDataFilter()
    if operation == "union":
        boolean_operator.SetOperationToUnion()
    elif operation == "intersection":
        boolean_operator.SetOperationToIntersection()
    elif operation == "difference":
        boolean_operator.SetOperationToDifference()
    else:
        print("Unknow operation")
        sys.exit(0)

    boolean_operator.SetInputData(0, polydata1)
    boolean_operator.SetInputData(1, polydata2)
    boolean_operator.Update()

    return boolean_operator.GetOutput()


def create_sphere(center, radius):
    sphere_source = vtk.vtkSphereSource()
    sphere_source.SetCenter(center)
    sphere_source.SetRadius(radius)
    sphere_source.Update()
    return sphere_source.GetOutput()


def main():
    input_file = sys.argv[1]

    if input_file.lower().endswith(".stl"):
        reader = vtk.vtkSTLReader()
    elif input_file.lower().endswith(".ply"):
        reader = vtk.vtkPLYReader()
    else:
        print("File must be STL or PLY")
        sys.exit(0)

    reader.SetFileName(input_file)
    reader.Update()

    polydata1 = reader.GetOutput()
    polydata1 = fix_polydata(polydata1)

    xi, xf, yi, yf, zi, zf = polydata1.GetBounds()
    center = ((xf + xi) / 2.0, (yf + yi) / 2.0, (zf + zi) / 2.0)
    diagonal_size = ((xf - xi) ** 2 + (yf - yi) ** 2.0 + (zf - zi) ** 2) ** 0.5
    polydata2 = create_sphere(center, diagonal_size * 0.23)

    polydata3 = apply_boolean_operation(polydata1, polydata2)

    show_polydatas(
        [polydata3,]
    )


if __name__ == "__main__":
    main()
