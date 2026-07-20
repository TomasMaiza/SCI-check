cmake_minimum_required(VERSION 3.10)
project(PyAtteneBindings)

find_package(pybind11 REQUIRED)

include_directories(${CMAKE_CURRENT_SOURCE_DIR}/../external/Indirect_Predicates/include)

pybind11_add_module(pyattene bindings.cpp)

# esto manda el archivo .so a la carpeta de coverage_checker
set_target_properties(pyattene PROPERTIES LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/../coverage_checker)