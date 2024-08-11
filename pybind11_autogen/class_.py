import CppHeaderParser

from .doxygen import wrap_doxygen
from .function import wrap_functions


def wrap_property(Self, prop, indent=""):
    docstring = wrap_doxygen(prop.get("doxygen", ""), indent=indent)
    return f'.def_property("{prop["name"]}", &{Self}::{prop["name"]}, &{Self}::set_{prop["name"]}, {docstring})'


def wrap_as_property(Self, prop, indent=""):
    name = prop["name"]
    type = prop["type"]
    assertion = ""

    if "SparseVector" in type:
        type = type.replace("SparseVector", "SparseMatrix")
        assertion = f'assert_is_sparse_vector({name}, "{name}");'

    docstring = wrap_doxygen(prop.get("doxygen", ""), indent=indent)

    return f""".def_property("{name}",
    [](const {Self}& self) -> {type} {{ return self.{name}; }},
    []({Self}& self, const {type}& {name}) {{
        {assertion}
        self.{name} = {name};
    }},
    {docstring})"""


def wrap_class(class_: CppHeaderParser.CppHeaderParser.CppClass):
    indent = " " * 12

    parents = ", ".join(
        parent["class"] for parent in class_["inherits"] if parent["access"] == "public")
    if parents != "":
        parents = ", " + parents

    code = [f'py::class_<{class_["name"]}{parents}>(m, "{class_["name"]}")']

    ordinary_methods = [
        func
        for func in class_["methods"]["public"]
        if not func["friend"] and not func["override"] and (not func["constructor"] or not class_["abstract"])
    ]

    public_method_names = set(func["name"] for func in ordinary_methods)
    properties = [func for func in ordinary_methods if (
        "set_" + func["name"]) in public_method_names]
    property_names = set([func["name"] for func in properties])

    ordinary_methods = list(filter(
        lambda func: (func["name"] not in property_names and func["name"].replace(
            "set_", "") not in property_names),
        ordinary_methods))

    code.append(wrap_functions(
        ordinary_methods,
        prefix=f'{class_["name"]}::',
        indent=indent,
        self=class_["name"]))

    # Wrap properties
    for prop in properties:
        code.append(wrap_property(class_["name"], prop, indent))

    # Wrap read-write properties
    for prop in class_["properties"]["public"]:
        if "using" in prop["aliases"]:
            continue
        # pybind11 does not support Eigen::SparseVector
        if "SparseVector" in prop["type"]:
            code.append(wrap_as_property(class_["name"], prop, indent))
            continue
        docstring = wrap_doxygen(prop.get("doxygen", ""), indent=indent)
        args = [f'"{prop["name"]}"', f"&{class_['name']}::{prop['name']}"]
        if docstring != '""':
            args.append(docstring)
        code.append(f".def_readwrite({', '.join(args)})")

    code.append(";")

    # Wrap friend functions
    code.append(wrap_functions([
        func
        for func in class_["methods"]["public"]
        if func["friend"] and func["name"] != "AbslHashValue"
    ]))

    # Remove empty lines
    code = [line for line in code if line.strip() != ""]

    return "\n".join(code)
