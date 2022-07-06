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
    args = parser.parse_args()

    for header_file in args.headers:
        print(f"Generating bindings for {header_file}")

        header = CppHeaderParser.CppHeader(header_file)
        bindings = pybind11_autogen.wrap_header(header, header_file)

        bindings_file = pathlib.Path(
            re.sub("src", "python/src", str(header_file))).with_suffix(".cpp")
        print(f"Writing bindings to {bindings_file}")
        bindings_file.parent.mkdir(parents=True, exist_ok=True)
        with open(bindings_file, 'w') as f:
            f.write(bindings)
        subprocess.run(
            ["clang-format", str(bindings_file), "-i", "--style=file"])


if __name__ == "__main__":
    main()
