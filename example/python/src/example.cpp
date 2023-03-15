#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/iostream.h>
#include <pybind11/operators.h>

#include <example.hpp>

namespace py = pybind11;
using namespace example;

void define_example(py::module_& m)
{
    py::enum_<Colors>(m, "Colors", "Default colors for the example.")
        .value("RED", Colors::RED, "")
        .value("BLUE", Colors::BLUE, "")
        .value("PURPLE", Colors::PURPLE, "")
        .value("AZURE", Colors::AZURE, "")
        .export_values();

    m.attr(
        "PI", "Ratio between the circumference of a circle and its diameter.") =
        py::cast(PI);

    m.attr(
        "MeaningOfLife",
        "Adams, D. (1989). The Hitchhiker's Guide to the Galaxy. Harmony.") =
        py::cast(MeaningOfLife);

    py::class_<ExampleClass>(m, "ExampleClass")
        .def("do_something", &ExampleClass::do_something, "Do that something.")
        .def(
            "put_value", &ExampleClass::put_value,
            R"ipc_Qu8mg5v7(
            Put a value into vals.

            Parameters:
                i: The value to put into vals.
            )ipc_Qu8mg5v7",
            py::arg("i"));

    py::class_<RGB>(m, "RGB")
        .def_readwrite("r", &RGB::r, "red")
        .def_readwrite("g", &RGB::g, "green")
        .def_readwrite("b", &RGB::b, "blue");

    m.def(
        "foo", &foo,
        R"ipc_Qu8mg5v7(
        Function that computes something.

        Parameters:
            x: The input.

        Returns:
            The output.
        )ipc_Qu8mg5v7",
        py::arg("x"));
}
