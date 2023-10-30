import re

import CppHeaderParser

from .doxygen import wrap_doxygen

cpp_to_python_magic = {
    "operator+": "__add__",
    "operator–": "__sub__",
    "operator*": "__mul__",
    "operator/": "__truediv__",
    "operator//": "__floordiv__",
    "operator%": "__mod__",
    "operator**": "__pow__",
    "operator>>": "__rshift__",
    "operator<<": "__lshift__",
    "operator&": "__and__",
    "operator|": "__or__",
    "operator^": "__xor__",
    "operator<": "__lt__",
    "operator>": "__gt__",
    "operator<=": "__le__",
    "operator>=": "__ge__",
    "operator==": "__eq__",
    "operator!=": "__ne__",
    "operator-=": "__isub__",
    "operator+=": "__iadd__",
    "operator*=": "__imul__",
    "operator/=": "__idiv__",
    "operator//=": "__ifloordiv__",
    "operator%=": "__imod__",
    "operator**=": "__ipow__",
    "operator>>=": "__irshift__",
    "operator<<=": "__ilshift__",
    "operator&=": "__iand__",
    "operator|=": "__ior__",
    "operator^=": "__ixor__",
    # "operator–": "__neg__",
    # "operator+": "__pos__",
    "operator~": "__invert__",
    "operator()": "__call__",
    "operator[]": "__getitem__",
    "size": "__len__",
}


def fix_scientific_notation(s):
    if re.match(r"^[0-9.]+e - [0-9]+$", s):
        return s.replace("e - ", "e-")
    return s


def wrap_parameter_default(param):
    if "default" in param and ":" in param["default"]:
        param["default"] = re.sub(r"\s*:\s*", ":", param["default"])
    return f'={fix_scientific_notation(param["default"])}' if "default" in param else ""


def wrap_parameters(params: list[CppHeaderParser.CppHeaderParser.CppVariable]):
    return ", ".join(f'py::arg("{param["name"].lstrip("_")}"){wrap_parameter_default(param)}' for param in params)


def is_out_param(param):
    return not param["type"].startswith("const ") and param["type"].endswith('&')


def has_output_parameters(params: list[CppHeaderParser.CppHeaderParser.CppVariable]):
    return any(is_out_param(p) for p in params)


def find_overloaded_functions(functions):
    overloaded = set()
    defined = set()
    for func in functions:
        if func["name"] in defined:
            overloaded.add(func["name"])
        defined.add(func["name"])
    return overloaded


def generate_lambda_function(func, self=None):
    in_params = [param for param in func["parameters"]
                 if not is_out_param(param)]
    out_params = [param for param in func["parameters"] if is_out_param(param)]
    args = ", ".join(param["name"] for param in func["parameters"])

    lambda_params = ",".join(
        ([f"{self}& self"] if self else [])
        + [f'{p["type"]} {p["name"]}{wrap_parameter_default(p)}' for p in in_params])
    return_param_decls = "\n".join(
        f'{p["type"][:-1]} {p["name"]};' for p in out_params)

    func["rtnType"] = func["rtnType"].replace("[ [ noreturn ] ]", "").strip()
    if func["rtnType"] not in ["static void", "void"]:
        return_decl = f"{func['rtnType']} r = "
        out_params.insert(0, {"name": "r", "type": func['rtnType']})
    else:
        return_decl = ""

    if len(out_params) == 0:
        return_statement = ""
    elif len(out_params) == 1:
        return_statement = f"return {out_params[0]['name']};"
    else:
        return_statement = f"return std::make_tuple({','.join(p['name'] for p in out_params)});"

    if func["static"]:
        caller = f"{func['parent']['name']}::"
    else:
        caller = "self." if self else ""

    return f"""\
[]({lambda_params}) {{
    {return_param_decls}
    {return_decl}{caller}{func["name"]}({args});
    {return_statement}
}}
"""


def wrap_function(func, prefix="", indent="", overloaded=False, self=None, name=None):
    has_params = (any([not is_out_param(p) for p in func["parameters"]])
                  and not re.match("^function<.*", func["name"]))
    docstring = wrap_doxygen(func.get("doxygen", ""), indent=indent, suffix="")

    if re.match("^(function|)<.*", func["name"]):
        name = func["debug"].split(">")[1].strip().split()[0]
        args = [f'"{name}"', f"&{prefix}{name}"]
        if docstring != '""':
            args.append(docstring)
        print(args)
        return f".def_readwrite({', '.join(args)})"

    params = wrap_parameters(
        [p for p in func["parameters"] if not is_out_param(p)])
    param_types = ", ".join([p["type"]
                            for p in func["parameters"] if not is_out_param(p)])

    if func["constructor"]:
        args = [f'py::init<{param_types}>()' if param_types else "py::init()"]
        if docstring != '""':
            args.append(docstring)
        if has_params:
            args.append(params)
        return f".def({', '.join(args)})"

    if has_output_parameters(func["parameters"]):
        func_address = generate_lambda_function(func, None if func["static"] else self)
    else:
        func_address = f'&{prefix}{func["name"]}'
        if overloaded:
            func_address = f"py::overload_cast<{param_types}>({func_address})"

    if name is None:
        name = func["name"]

    args = [f'"{name}"', func_address]
    if "&" in func["rtnType"]:
        args.append("py::return_value_policy::reference")
    if docstring != '""':
        args.append(docstring)
    if has_params:
        args.append(params)

    return f'.def{"_static" if func["static"] else ""}({", ".join(args)})'


def wrap_functions(functions, prefix="", indent="", self=None):
    overloaded_functions = find_overloaded_functions(functions)
    code = []
    for func in functions:
        if func["destructor"]:
            continue
        name = cpp_to_python_magic.get(func["name"], None)
        code.append(
            ("" if self else "m")
            + wrap_function(
                func, prefix=prefix, indent=indent,
                overloaded=(
                    func["name"] in overloaded_functions and not func["constructor"]),
                self=self,
                name=name)
            + ("" if self else ";\n")
        )
    return "\n".join(code)
