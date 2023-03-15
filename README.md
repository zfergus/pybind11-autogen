# pybind11-autogen

[![License](https://img.shields.io/github/license/zfergus/pybind11-autogen.svg?color=blue)](https://github.com/zfergus/pybind11-autogen/blob/main/LICENSE)

Automatically generate pybind11 source from a C++ header.

## Usage

```
usage: main.py [-h] [-i INCLUDE_ROOT] headers [headers ...]

Automatically Generate pybind11 bindings from C++ header(s)

positional arguments:
  headers               C++ header file(s) to generate bindings for

options:
  -h, --help            show this help message and exit
  -i INCLUDE_ROOT, --include-root INCLUDE_ROOT
                        Root include path
```

### Example

```
cd example
python ../main.py include/example.hpp -i include
```

This will create a `example.cpp` file in `example/python/src` containing the bindings for the contents of `example.hpp`.

## Known Issues

* `enum class` are parsed as classes, not enums
* inline doxygen comments (e.g., `///< @brief A brief description`) are not parsed correctly

If you find any other issues, please open an issue on GitHub.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details