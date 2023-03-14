import CppHeaderParser

from .enum import wrap_enum
from .class_ import wrap_class
from .function import wrap_functions


def wrap_header(header, header_path):
    template = f"""\
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/iostream.h>
#include <pybind11/operators.h>

#include <ipc/{header_path.parent.name}/{header_path.name}>

namespace py = pybind11;
using namespace ipc;

void define_{header_path.stem}(py::module_& m)
{{{{
{{}}
}}}}
"""

    code = []

    for enum in header.enums:
        code.append(wrap_enum(enum))
        code.append("")

    for class_name in header.classes:
        code.append(wrap_class(header.classes[class_name]))
        code.append("")

    code.append(wrap_functions(header.functions, indent=" " * 8))

    return template.format("\n".join(code))
