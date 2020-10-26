import vtk
import sys


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
    iren.Start()



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

    xi, xf, yi, yf, zi, zf = polydata1.GetBounds()
    center = ((xf + xi)/2.0, (yf + yi)/2.0, (zf + zi)/2.0)
    diagonal_size = ((xf - xi)**2 + (yf - yi)**2.0 + (zf - zi)**2)**0.5
    polydata2 = create_sphere(center, diagonal_size * 0.23)

    polydata3 = apply_boolean_operation(polydata1, polydata2)

    show_polydatas([polydata3,])




if __name__ == "__main__":
    main()
