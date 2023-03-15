#pragma once

#include <vector>
#include <string>

namespace example {

/// @brief Default colors for the example.
enum Colors { RED, BLUE, PURPLE, AZURE };

/// @brief Ratio between the circumference of a circle and its diameter.
const double PI = 3.14;

/// @ref Adams, D. (1989). The Hitchhiker's Guide to the Galaxy. Harmony.
constexpr int MeaningOfLife = 42;

/// @brief Function that computes something.
/// @param x The input.
/// @return The output.
double foo(double x);

/// @brief Class that does something.
class ExampleClass {
public:
    /// @brief Do that something.
    void do_something();

    /// @brief Put a value into vals.
    /// @param i The value to put into vals.
    inline void put_value(int i) { vals.push_back(i); }

private:
    /// @brief A vector of values.
    std::vector<int> vals;
};

struct RGB {
    /// @brief red
    short r = 0;
    /// @brief green
    short g = 0;
    /// @brief blue
    short b = 0;
};

} // namespace example