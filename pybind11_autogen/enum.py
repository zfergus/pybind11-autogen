import CppHeaderParser

from pybind11_autogen.doxygen import wrap_doxygen


def wrap_enum(enum):
    code = [
        f'py::enum_<{enum["name"]}>(m, "{enum["name"]}", {wrap_doxygen(enum.get("doxygen", ""))})']
    for value in enum["values"]:
        code.append(
            f'.value("{value["name"]}", {enum["name"]}::{value["name"]}, {wrap_doxygen(value.get("doxygen", ""))})')
    code.append(".export_values();")
    return "\n".join(code)
