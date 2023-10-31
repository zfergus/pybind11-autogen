import CppHeaderParser

from .doxygen import wrap_doxygen
from .function import wrap_functions


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
        if not func["friend"] and not func["override"]
    ]

    code.append(wrap_functions(
        ordinary_methods,
        prefix=f'{class_["name"]}::',
        indent=indent,
        self=class_["name"]))

    for prop in class_["properties"]["public"]:
        if "using" in prop["aliases"]:
            continue
        docstring = wrap_doxygen(prop.get("doxygen", ""), indent=indent)
        args = [f'"{prop["name"]}"', f"&{class_['name']}::{prop['name']}"]
        if docstring != '""':
            args.append(docstring)
        code.append(f".def_readwrite({', '.join(args)})")

    code.append(";")

    # Wrap friend functions
    code.append(wrap_functions(
        [func for func in class_["methods"]["public"] if func["friend"] and func["name"] != "AbslHashValue"]))

    # Remove empty lines
    code = [line for line in code if line.strip() != ""]

    return "\n".join(code)
