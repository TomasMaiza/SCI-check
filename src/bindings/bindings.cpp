#include <pybind11/pybind11.h>
#include "../external/Indirect_Predicates/include/implicit_point.h" 

namespace py = pybind11;

PYBIND11_MODULE(pyattene, m) {
    m.doc() = "Indirect Predicates Library (Marco Attene)";

    py::class_<genericPoint>(m, "GenericPoint"); // Generic Point class

    // structs 2d
    py::class_<explicitPoint2D, genericPoint>(m, "ExplicitPoint2D") // Explicit 2D point class
        .def(py::init<double, double>())
        .def("X", &explicitPoint2D::X)
        .def("Y", &explicitPoint2D::Y);

    py::class_<implicitPoint2D_SSI, genericPoint>(m, "ImplicitPoint2D_SSI") // Implicit 2D point class
        .def(py::init<const genericPoint&, const genericPoint&, const genericPoint&, const genericPoint&>());

    // structs 3d
    py::class_<explicitPoint3D, genericPoint>(m, "ExplicitPoint3D") 
        .def(py::init<double, double, double>())
        .def("X", &explicitPoint3D::X)
        .def("Y", &explicitPoint3D::Y)
        .def("Z", &explicitPoint3D::Z);

    // Para C3: Intersección Línea-Plano LPI (Edge vs Face)
    py::class_<implicitPoint3D_LPI, genericPoint>(m, "ImplicitPoint3D_LPI") 
        .def(py::init<const genericPoint&, const genericPoint&, 
                      const genericPoint&, const genericPoint&, const genericPoint&>(),
             "Interseccion Linea-Plano (LPI). Args: p, q (linea), r, s, t (plano)");

    // Para nueva C4: Intersección de 3 Planos (Face vs Face vs Face)
    py::class_<implicitPoint3D_TPI, genericPoint>(m, "ImplicitPoint3D_TPI") 
        .def(py::init<const genericPoint&, const genericPoint&, const genericPoint&, 
                      const genericPoint&, const genericPoint&, const genericPoint&, 
                      const genericPoint&, const genericPoint&, const genericPoint&>(),
             "Interseccion Tres-Planos (TPI). Args: v1,v2,v3 (pl1), w1,w2,w3 (pl2), u1,u2,u3 (pl3)");


    // Predicados
    m.def("orient2d_EEE", &orient2d_EEE, "Predicado E-E-E 2D");
    m.def("orient2d_IEE", &orient2d_IEE, "Predicado I-E-E 2D");
    m.def("orient3d", &genericPoint::orient3D, "Predicado Orient3D dinámico",
          py::arg("a"), py::arg("b"), py::arg("c"), py::arg("d"));
}