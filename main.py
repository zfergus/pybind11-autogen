import argparse
import re
import pathlib
import subprocess

import CppHeaderParser

import pybind11_autogen


def main():
    parser = argparse.ArgumentParser(
        description="Automatically Generate pybind11 bindings from C++ header(s)")
    parser.add_argument(
        "headers", nargs="+", help="C++ header file(s) to generate bindings for", type=pathlib.Path)
    parser.add_argument(
        "-i", "--include-root", help="Root include path", type=pathlib.Path, default=None)
    parser.add_argument(
        "-c", "--common-include", help="Common include file", type=pathlib.Path, default=None)
    args = parser.parse_args()

    for header_file in args.headers:
        print(f"Generating bindings for {header_file}")

        with open(header_file, 'r') as f:
            header_file_contents = f.read()
        header_file_contents += "\n"  # trailing comment causes parsing error

        header = CppHeaderParser.CppHeader(
            header_file_contents, argType="string")

        if not any((header.enums, header.variables, header.classes, header.functions)):
            print(f"Skipping {header_file} - no enums, variables, classes, or functions")
            continue

        rel_header_file = header_file.relative_to(args.include_root) if args.include_root else header_file
        bindings = pybind11_autogen.wrap_header(header, rel_header_file, common_include=args.common_include)

        bindings_file = pathlib.Path(
            "python", "src", *rel_header_file.parts[1:]).with_suffix(".cpp")
        print(f"Writing bindings to {bindings_file}")
        bindings_file.parent.mkdir(parents=True, exist_ok=True)
        with open(bindings_file, 'w') as f:
            f.write(bindings)
        subprocess.run(
            ["clang-format", str(bindings_file), "-i", "--style=file"])


if __name__ == "__main__":
    main()
