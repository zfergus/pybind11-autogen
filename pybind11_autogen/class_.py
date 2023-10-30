import CppHeaderParser

from .doxygen import wrap_doxygen
from .function import wrap_functions


def wrap_class(cclass: CppHeaderParser.CppHeaderParser.CppClass):
    indent = " " * 12

    parents = ", ".join(
        parent["class"] for parent in cclass["inherits"] if parent["access"] == "public")
    if parents != "":
        parents = ", " + parents

    code = [f'py::class_<{cclass["name"]}{parents}>(m, "{cclass["name"]}")']

    code.append(wrap_functions(
        [func for func in cclass["methods"]["public"] if not func["friend"]],
        prefix=f'{cclass["name"]}::',
        indent=indent,
        self=cclass["name"]))

    for prop in cclass["properties"]["public"]:
        docstring = wrap_doxygen(prop.get("doxygen", ""), indent=indent)
        args = [f'"{prop["name"]}"', f"&{cclass['name']}::{prop['name']}"]
        if docstring != '""':
            args.append(docstring)
        code.append(f".def_readwrite({', '.join(args)})")

    code.append(";")

    # Wrap friend functions
    code.append(wrap_functions(
        [func for func in cclass["methods"]["public"] if func["friend"]]))

    # Remove empty lines
    code = [line for line in code if line.strip() != ""]

    return "\n".join(code)
