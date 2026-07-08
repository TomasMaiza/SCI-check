#include <pybind11/pybind11.h>
#include "../external/Indirect_Predicates/include/indirect_predicates.h" 

namespace py = pybind11;

PYBIND11_MODULE(pyattene, m) {
    m.doc() = "Indirect Predicates Library (Marco Attene)";

    py::class_<genericPoint>(m, "GenericPoint"); // Generic Point class

    py::class_<explicitPoint2D, genericPoint>(m, "ExplicitPoint2D") // Explicit 2D point class
        .def(py::init<double, double>())
        .def("X", &explicitPoint2D::X)
        .def("Y", &explicitPoint2D::Y);

    py::class_<implicitPoint2D_SSI, genericPoint>(m, "ImplicitPoint2D_SSI") // Implicit 2D point class
        .def(py::init<const explicitPoint2D&, const explicitPoint2D&, const explicitPoint2D&, const explicitPoint2D&>());

    // orient2d_EEE and orient2d_IEE functions
    m.def("orient2d_EEE", &orient2d_EEE, "Predicado E-E-E 2D");
    m.def("orient2d_IEE", &orient2d_IEE, "Predicado I-E-E 2D");
}