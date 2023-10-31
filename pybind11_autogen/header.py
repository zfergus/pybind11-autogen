import CppHeaderParser

from .enum import wrap_enum
from .variable import wrap_variable
from .class_ import wrap_class
from .function import wrap_functions


def wrap_header(header, header_path, common_include=None):
    template = f"""\
{{includes}}

#include <{header_path}>

namespace py = pybind11;
{{namespaces}}

void define_{header_path.stem}(py::module_& m)
{{{{
{{code}}
}}}}
"""

    if common_include:
        includes = f"#include <{common_include}>"
    else:
        includes = """\
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/iostream.h>
#include <pybind11/operators.h>
#include <pybind11/eigen.h>
#include <pybind11/functional.h>"""

    code = []

    for enum in header.enums:
        if "name" not in enum:
            continue  # skip enum class
        code.append(wrap_enum(enum))
        code.append("")

    for var in header.variables:
        if "using" in var["aliases"]:
            continue
        code.append(wrap_variable(var))
        code.append("")

    for class_name in header.classes:
        code.append(wrap_class(header.classes[class_name]))
        code.append("")

    code.append(wrap_functions(header.functions, indent=" " * 8))

    namespaces = [
        f"using namespace {namespace};" for namespace in header.namespaces]

    return template.format(
        includes=includes,
        namespaces="\n".join(namespaces),
        code="\n".join(code))
