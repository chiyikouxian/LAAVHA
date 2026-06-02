#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/mobility-module.h"
#include "ns3/lte-module.h"
#include "ns3/wifi-module.h"
#include "ns3/internet-module.h"
#include "ns3/ai-module.h" // 必须安装并包含 ns3-ai

using namespace ns3;

// 1. 定义与 Python 共享的数据结构 (必须与 Python 端严格一致)
struct HandoverInfo {
    float metrics[15]; // 3网络 * 5指标 (SINR, RSRP, Delay, Thr, PLR)
    float velocity;
    float altitude;
} packed;

struct HandoverDecision {
    int target_net_id; // 0: 5G, 1: LTE, 2: WiFi
} packed;

class LaavhaSimulation {
public:
    LaavhaSimulation() {
        // 初始化 ns3-ai 接口，ID 为 1234
        m_aiInterface = CreateObject<Ns3AIRL<HandoverInfo, HandoverDecision>>(1234);
        m_currentNet = 0; 
    }

    void SetupScenario() {
        // 创建节点
        NodeContainer uavNode;
        uavNode.Create(1);
        
        NodeContainer enbNodes;
        enbNodes.Create(3); // 3个基站代表3种网络覆盖

        // 设置移动模型：无人机水平匀速移动，高度 100m
        MobilityHelper mobility;
        Ptr<ListPositionAllocator> positionAlloc = CreateObject<ListPositionAllocator>();
        positionAlloc->Add(Vector(0.0, 0.0, 100.0)); // 起点
        mobility.SetPositionAllocator(positionAlloc);
        mobility.SetMobilityModel("ns3::ConstantVelocityMobilityModel");
        mobility.Install(uavNode);
        uavNode.Get(0)->GetObject<ConstantVelocityMobilityModel>()->SetVelocity(Vector(20.0, 0.0, 0.0));

        // 基站位置
        mobility.SetMobilityModel("ns3::ConstantPositionMobilityModel");
        mobility.Install(enbNodes);

        // 2. 安装网络协议栈 (这里简化，实际需安装 LteHelper, WifiHelper 等)
        InternetStackHelper stack;
        stack.Install(uavNode);

        // 启动定时决策逻辑
        Simulator::Schedule(Seconds(1.0), &LaavhaSimulation::CollectAndDecide, this, uavNode.Get(0));
    }

    void CollectAndDecide(Ptr<Node> node) {
        HandoverInfo info;
        
        // 3. 采集数据 (实际需从各网络设备的 Phy 层获取)
        for (int i = 0; i < 15; ++i) {
            info.metrics[i] = (float)rand() / (float)RAND_MAX; // 演示用随机数，实际请替换为 Trace 数据
        }
        
        Ptr<ConstantVelocityMobilityModel> mob = node->GetObject<ConstantVelocityMobilityModel>();
        info.velocity = mob->GetVelocity().x;
        info.altitude = mob->GetPosition().z;

        // 4. 调用 Python 模型获取决策
        auto decision = m_aiInterface->Predict(info);

        // 5. 执行切换逻辑
        if (decision.target_net_id != m_currentNet) {
            NS_LOG_UNCOND("Time: " << Simulator::Now().GetSeconds() 
                          << "s | Handover triggered to Net: " << decision.target_net_id);
            m_currentNet = decision.target_net_id;
            // 此处应调用具体网络接口的切换函数，例如：
            // SwitchApplicationFlow(node, m_currentNet);
        }

        // 每 0.1 秒运行一次决策周期
        Simulator::Schedule(Seconds(0.1), &LaavhaSimulation::CollectAndDecide, this, node);
    }

private:
    Ptr<Ns3AIRL<HandoverInfo, HandoverDecision>> m_aiInterface;
    int m_currentNet;
};

int main(int argc, char *argv[]) {
    CommandLine cmd;
    cmd.Parse(argc, argv);

    LaavhaSimulation sim;
    sim.SetupScenario();

    Simulator::Stop(Seconds(100.0));
    Simulator::Run();
    Simulator::Destroy();
    return 0;
}