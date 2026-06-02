/*
 * pybind11 binding for LAAVHA handover message interface.
 */

#include "laavha_msg.h"

#include <ns3/ai-module.h>

#include <iostream>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

PYBIND11_MODULE(ns3ai_laavha_handover_py, m)
{
    py::class_<Cpp2PyStruct>(m, "PyCpp2PyStruct")
        .def(py::init<>())
        .def_readwrite("metrics", &Cpp2PyStruct::metrics)
        .def_readwrite("velocity", &Cpp2PyStruct::velocity)
        .def_readwrite("altitude", &Cpp2PyStruct::altitude)
        .def_readwrite("current_net", &Cpp2PyStruct::current_net);

    py::class_<Py2CppStruct>(m, "PyPy2CppStruct")
        .def(py::init<>())
        .def_readwrite("target_net_id", &Py2CppStruct::target_net_id)
        .def_readwrite("score_5g", &Py2CppStruct::score_5g)
        .def_readwrite("score_lte", &Py2CppStruct::score_lte)
        .def_readwrite("score_wifi", &Py2CppStruct::score_wifi);

    py::class_<ns3::Ns3AiMsgInterfaceImpl<Cpp2PyStruct, Py2CppStruct>>(
        m, "Ns3AiMsgInterfaceImpl")
        .def(py::init<bool,
                      bool,
                      bool,
                      uint32_t,
                      const char*,
                      const char*,
                      const char*,
                      const char*>())
        .def("PyRecvBegin",
             &ns3::Ns3AiMsgInterfaceImpl<Cpp2PyStruct, Py2CppStruct>::PyRecvBegin)
        .def("PyRecvEnd",
             &ns3::Ns3AiMsgInterfaceImpl<Cpp2PyStruct, Py2CppStruct>::PyRecvEnd)
        .def("PySendBegin",
             &ns3::Ns3AiMsgInterfaceImpl<Cpp2PyStruct, Py2CppStruct>::PySendBegin)
        .def("PySendEnd",
             &ns3::Ns3AiMsgInterfaceImpl<Cpp2PyStruct, Py2CppStruct>::PySendEnd)
        .def("PyGetFinished",
             &ns3::Ns3AiMsgInterfaceImpl<Cpp2PyStruct, Py2CppStruct>::PyGetFinished)
        .def("GetCpp2PyStruct",
             &ns3::Ns3AiMsgInterfaceImpl<Cpp2PyStruct, Py2CppStruct>::GetCpp2PyStruct,
             py::return_value_policy::reference)
        .def("GetPy2CppStruct",
             &ns3::Ns3AiMsgInterfaceImpl<Cpp2PyStruct, Py2CppStruct>::GetPy2CppStruct,
             py::return_value_policy::reference);
}
