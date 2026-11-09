#ifndef LAAVHA_MSG_H
#define LAAVHA_MSG_H

#include <array>

// C++ -> Python: environment state
struct Cpp2PyStruct
{
    std::array<float, 150> metrics; // 3 nets * 10 steps * 5 indicators
    float velocity;                 // m/s
    float altitude;                 // m
    int current_net;                // 0=5G, 1=LTE, 2=WiFi
};

// Python -> C++: inference result
struct Py2CppStruct
{
    int target_net_id;   // 0=5G, 1=LTE, 2=WiFi
    float score_5g;
    float score_lte;
    float score_wifi;
};

#endif // LAAVHA_MSG_H
