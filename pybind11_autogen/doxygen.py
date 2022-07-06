import re

import CppHeaderParser


def strip_doxygen_line(line):
    return re.sub("/// (@[a-z\[\]]*)?", "", line.strip()).strip()


def doxygen_to_docstring(doxygen, indent=""):

    brief = None
    extra = []
    params = []
    returns = []
    notes = []
    lines = doxygen.split("\n")
    for line in lines:
        if line.startswith("/// @param"):
            if line.startswith("/// @param[out]"):
                line = strip_doxygen_line(line)
                returns.append(line[line.index(" "):].strip())
            else:
                params.append(
                    re.sub(" ", ": ", strip_doxygen_line(line), count=1))
        elif line.startswith("/// @return"):
            returns.insert(0, strip_doxygen_line(line))
        elif line.startswith("/// @brief"):
            brief = strip_doxygen_line(line)
        elif line.startswith("/// @note"):
            notes.append(strip_doxygen_line(line))
        elif len(line.strip()) > 0:
            extra.append(strip_doxygen_line(line))

    # indent = " " * 0
    tab = " " * 4
    lines = []
    if brief is not None:
        lines.append(indent + brief)
        lines.append("")
    if notes:
        lines.append(f"{indent}Note{'s' if len(notes) > 1 else ''}:")
        lines.extend(f"{indent}{tab}{note}" for note in notes)
        lines.append("")
    if extra:
        lines.append(indent + "\n".join(extra))
        lines.append("")
    if params:
        lines.append(f"{indent}Parameters:")
        lines.append(f"{indent}{tab}" + f"\n{indent}{tab}".join(params))
        lines.append("")
    if returns:
        lines.append(f"{indent}Returns:")
        if len(returns) > 1:
            lines.append(f"{indent}{tab}Tuple of:")
        lines.extend(f"{indent}{tab}{r}" for r in returns)
        lines.append("")

    return "\n".join(lines)


def wrap_doxygen(doxygen, indent="", suffix=""):
    docstring = doxygen_to_docstring(doxygen, indent)
    if docstring.count("\n") > 1:
        docstring = f'''
{indent}R"ipc_Qu8mg5v7(
{docstring}\
{indent})ipc_Qu8mg5v7"'''
    else:
        docstring = f'"{docstring.strip()}"'
    docstring += suffix
    return docstring
