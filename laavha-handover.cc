/*
 * LAAVHA ns3-ai integration - Stage 3: WiFi + FlowMonitor Reintegration.
 *
 * Builds on the scheduled simulation skeleton:
 *   - UAV node with ConstantVelocityMobilityModel
 *   - AP ground node with WiFi STA-AP link (802.11g)
 *   - UDP traffic (UAV -> AP via OnOff/PacketSink)
 *   - WiFi Throughput: real (PacketSink interval rx bytes)
 *   - WiFi Delay/PLR: real (FlowMonitor) when flowmonMode=feed,
 *     synthetic otherwise.
 *   - WiFi SINR/RSRP: propagation proxy from UAV/AP MobilityModel positions.
 *   - 5G candidate uses proxy metrics (propagation + synthetic transport)
 *     until NR/5G-LENA module is integrated.
 *
 * FlowMonitor modes (CLI --flowmonMode):
 *   off  - no FlowMonitor installed
 *   log  - FlowMonitor installed, stats printed every 10 decisions,
 *          but model input metrics unchanged (default)
 *   feed - FlowMonitor delay/PLR fed into WiFi metric indices 2 and 4
 *
 * Metric order: 0=SINR, 1=RSRP, 2=Delay, 3=Throughput, 4=PLR
 */

#include "laavha_msg.h"

#include <ns3/ai-module.h>
#include <ns3/applications-module.h>
#include <ns3/command-line.h>
#include <ns3/constant-position-mobility-model.h>
#include <ns3/constant-velocity-mobility-model.h>
#include <ns3/flow-monitor-module.h>
#include <ns3/internet-module.h>
#include <ns3/lte-module.h>
#include <ns3/mobility-helper.h>
#include <ns3/node-container.h>
#include <ns3/nstime.h>
#include <ns3/point-to-point-module.h>
#include <ns3/rng-seed-manager.h>
#include <ns3/simulator.h>
#include <ns3/vector.h>
#include <ns3/wifi-module.h>

#include <array>
#include <cmath>
#include <iostream>

using namespace ns3;

NS_LOG_COMPONENT_DEFINE("LaavhaHandover");

// ---------------------------------------------------------------------------
// Simulation class
// ---------------------------------------------------------------------------
class LaavhaScheduledSimulation
{
  public:
    LaavhaScheduledSimulation()
        : m_msg(nullptr),
          m_currentNet(0),
          m_handoverCount(0),
          m_decisions(0),
          m_duration(5.0),
          m_period(0.1),
          m_initialSpeed(20.0),
          m_initialAltitude(100.0),
          m_initialPosOffsetX(0.0),
          m_initialPosOffsetY(0.0),
          m_flowmonMode("feed"),
          m_prevRxBytes(0),
          m_prevMetricTime(-1.0),
          m_lastWifiThroughput(0.0f),
          m_lastWifiSinr(20.0f),
          m_lastWifiRsrp(-60.0f),
          m_fmPrevTxPkts(0),
          m_fmPrevRxPkts(0),
          m_fmPrevLostPkts(0),
          m_fmPrevRxBytes(0),
          m_fmPrevDelaySum(0.0),
          m_fmPrevTime(-1.0),
          m_fmDelay(0.01f),
          m_fmThroughput(0.0f),
          m_fmPlr(0.0f),
          m_lastLteSinr(15.0f),
          m_lastLteRsrp(-80.0f),
          m_lastLteThroughput(0.0f),
          m_lteFmPrevTxPkts(0),
          m_lteFmPrevRxPkts(0),
          m_lteFmPrevRxBytes(0),
          m_lteFmPrevDelaySum(0.0),
          m_lteFmPrevTime(-1.0),
          m_lteFmDelay(0.01f),
          m_lteFmThroughput(0.0f),
          m_lteFmPlr(0.0f),
          m_5gFmPrevTxPkts(0),
          m_5gFmPrevRxPkts(0),
          m_5gFmPrevRxBytes(0),
          m_5gFmPrevDelaySum(0.0),
          m_5gFmPrevTime(-1.0),
          m_5gFmDelay(0.001f),
          m_5gFmThroughput(0.0f),
          m_5gFmPlr(0.0f),
          m_historyInitialized(false),
          m_numBackgroundNodes(0)
    {
    }

    void Configure(int argc, char* argv[])
    {
        uint32_t rngRun = 1;
        bool randomizeScenario = false;
        double positionJitter = 0.0;
        double altitudeJitter = 0.0;

        CommandLine cmd;
        cmd.AddValue("duration", "Simulation duration in seconds", m_duration);
        cmd.AddValue("period", "Decision period in seconds", m_period);
        cmd.AddValue("initialSpeed", "Initial UAV speed (m/s)", m_initialSpeed);
        cmd.AddValue("initialAltitude", "Initial UAV altitude (m)", m_initialAltitude);
        cmd.AddValue("flowmonMode", "FlowMonitor mode: off|log|feed", m_flowmonMode);
        cmd.AddValue("numBackgroundNodes",
                     "Number of background WiFi STA nodes with Gauss-Markov mobility",
                     m_numBackgroundNodes);
        cmd.AddValue("RngRun", "ns-3 RNG run number for reproducibility", rngRun);
        cmd.AddValue("randomizeScenario", "Enable random perturbations", randomizeScenario);
        cmd.AddValue("positionJitter", "Max x/y offset (m)", positionJitter);
        cmd.AddValue("altitudeJitter", "Max altitude offset (m)", altitudeJitter);
        cmd.Parse(argc, argv);

        RngSeedManager::SetRun(rngRun);

        if (randomizeScenario && (positionJitter > 0 || altitudeJitter > 0))
        {
            Ptr<UniformRandomVariable> rng = CreateObject<UniformRandomVariable>();
            if (positionJitter > 0)
            {
                m_initialPosOffsetX = rng->GetValue(-positionJitter, positionJitter);
                m_initialPosOffsetY = rng->GetValue(-positionJitter, positionJitter);
            }
            if (altitudeJitter > 0)
            {
                double altOff = rng->GetValue(-altitudeJitter, altitudeJitter);
                m_initialAltitude = std::max(10.0, m_initialAltitude + altOff);
            }
        }

        std::cout << "RngRun=" << rngRun
                  << " randomizeScenario=" << (randomizeScenario ? "true" : "false")
                  << " positionJitter=" << positionJitter
                  << " altitudeJitter=" << altitudeJitter << std::endl;
        std::cout << "Sampled initial: x_offset=" << m_initialPosOffsetX
                  << " y_offset=" << m_initialPosOffsetY
                  << " altitude=" << m_initialAltitude << std::endl;
    }

    void Run()
    {
        SetupMsgInterface();
        SetupNodes();
        SetupBackgroundNodes();  // create background STA nodes (before network setup)
        SetupNetwork();
        SetupLte();
        Setup5gProxy();
        SetupTraffic();
        SetupLteTraffic();
        Setup5gProxyTraffic();
        SetupBackgroundTraffic();

        if (m_flowmonMode != "off")
        {
            SetupFlowMonitor();
        }

        std::cout << "=== LAAVHA ns3-ai integration - Stage 3 ===" << std::endl;
        std::cout << "Duration: " << m_duration << "s, period: " << m_period
                  << "s" << std::endl;
        std::cout << "UAV init pos: " << m_mobility->GetPosition()
                  << ", init vel: " << m_mobility->GetVelocity() << std::endl;
        std::cout << "AP pos: " << m_apNode.Get(0)->GetObject<MobilityModel>()->GetPosition()
                  << std::endl;
        std::cout << "flowmonMode=" << m_flowmonMode << std::endl;
        if (m_flowmonMode == "feed")
        {
            std::cout << "  WiFi: Throughput=real(PacketSink), Delay/PLR=real(FlowMonitor), "
                      << "SINR/RSRP=real(propagation proxy)" << std::endl;
            std::cout << "  LTE:  Throughput/Delay/PLR=real(FlowMonitor), "
                      << "SINR/RSRP=real(propagation proxy)" << std::endl;
        }
        else if (m_flowmonMode == "log")
        {
            std::cout << "  WiFi: Throughput=real(PacketSink), Delay/PLR=synthetic "
                      << "(FlowMonitor logged only), SINR/RSRP=real(propagation proxy)"
                      << std::endl;
            std::cout << "  LTE:  Throughput=real(FlowMonitor logged), "
                      << "SINR/RSRP=real(propagation proxy)" << std::endl;
        }
        else
        {
            std::cout << "  WiFi: Throughput=real(PacketSink), "
                      << "SINR/RSRP=real(propagation proxy), Delay/PLR=synthetic" << std::endl;
            std::cout << "  LTE:  SINR/RSRP=real(propagation proxy), "
                      << "Delay/Throughput/PLR=synthetic" << std::endl;
        }
        std::cout << "  5G: SINR/RSRP=proxy(propagation), Delay/Throughput/PLR="
                  << (m_flowmonMode == "feed" ? "proxy(FlowMonitor on P2P)"
                                              : "synthetic")
                  << " (NOT real NR)" << std::endl;
        std::cout << "  Override: --ns3-arg flowmonMode=off|log" << std::endl;

        Simulator::Schedule(Seconds(m_duration * 0.5),
                            &LaavhaScheduledSimulation::UpdateVelocity,
                            this);

        Simulator::Schedule(Seconds(0.0),
                            &LaavhaScheduledSimulation::DecisionStep,
                            this);

        Simulator::Stop(Seconds(m_duration + 0.001));
        Simulator::Run();

        PrintSummary();
    }

  private:
    // -----------------------------------------------------------------------
    // Setup helpers
    // -----------------------------------------------------------------------
    void SetupMsgInterface()
    {
        auto interface = Ns3AiMsgInterface::Get();
        interface->SetIsMemoryCreator(false);
        interface->SetUseVector(false);
        interface->SetHandleFinish(true);
        m_msg = interface->GetInterface<Cpp2PyStruct, Py2CppStruct>();
    }

    void SetupNodes()
    {
        m_uavNodes.Create(1);
        MobilityHelper mobility;
        mobility.SetMobilityModel("ns3::ConstantVelocityMobilityModel");
        mobility.Install(m_uavNodes);

        Ptr<ConstantVelocityMobilityModel> cvmm =
            m_uavNodes.Get(0)->GetObject<ConstantVelocityMobilityModel>();
        cvmm->SetPosition(Vector(m_initialPosOffsetX, m_initialPosOffsetY, m_initialAltitude));
        cvmm->SetVelocity(Vector(m_initialSpeed, 0.0, 0.0));
        m_mobility = cvmm;
    }

    void SetupNetwork()
    {
        // AP node at ground level, directly below UAV start
        m_apNode.Create(1);
        MobilityHelper apMobility;
        apMobility.SetMobilityModel("ns3::ConstantPositionMobilityModel");
        apMobility.Install(m_apNode);
        m_apNode.Get(0)->GetObject<ConstantPositionMobilityModel>()->SetPosition(
            Vector(0.0, 0.0, 100.0));

        // WiFi channel and PHY
        YansWifiChannelHelper channel = YansWifiChannelHelper::Default();
        YansWifiPhyHelper phy;
        phy.SetChannel(channel.Create());

        WifiHelper wifi;
        wifi.SetStandard(WIFI_STANDARD_80211g);
        // Use default rate control (Aarf) for simplicity

        WifiMacHelper mac;
        Ssid ssid = Ssid("laavha-net");

        mac.SetType("ns3::ApWifiMac", "Ssid", SsidValue(ssid));
        NetDeviceContainer apDev = wifi.Install(phy, mac, m_apNode);

        mac.SetType("ns3::StaWifiMac", "Ssid", SsidValue(ssid));
        NetDeviceContainer staDev = wifi.Install(phy, mac, m_uavNodes);

        // Install STA devices on background nodes (same BSS, same channel)
        NetDeviceContainer bgDevs;
        if (m_backgroundStaNodes.GetN() > 0)
        {
            bgDevs = wifi.Install(phy, mac, m_backgroundStaNodes);
        }

        // Internet stack
        InternetStackHelper internet;
        internet.Install(m_uavNodes);
        internet.Install(m_apNode);
        if (m_backgroundStaNodes.GetN() > 0)
        {
            internet.Install(m_backgroundStaNodes);
        }

        // IP addressing for all WiFi nodes (UAV + background STAs)
        // All nodes on the same subnet to avoid GlobalRouter confusion
        NetDeviceContainer allDev;
        allDev.Add(apDev.Get(0));
        allDev.Add(staDev.Get(0));
        for (uint32_t i = 0; i < bgDevs.GetN(); ++i)
        {
            allDev.Add(bgDevs.Get(i));
        }
        Ipv4AddressHelper ipv4("10.1.1.0", "255.255.255.0");
        m_ipIfs = ipv4.Assign(allDev); // m_ipIfs[0]=AP, m_ipIfs[1]=UAV-STA, [2+]=bg-STAs
        // Store background node IP indices for traffic setup
        m_bgIpIfs = Ipv4InterfaceContainer();
        for (uint32_t i = 0; i < bgDevs.GetN(); ++i)
        {
            m_bgIpIfs.Add(m_ipIfs.Get(2 + i));
        }

        Ipv4GlobalRoutingHelper::PopulateRoutingTables();
    }

    void SetupTraffic()
    {
        uint16_t port = 9;
        // PacketSink on AP (server)
        PacketSinkHelper sink("ns3::UdpSocketFactory",
                              InetSocketAddress(Ipv4Address::GetAny(), port));
        ApplicationContainer sinkApp = sink.Install(m_apNode.Get(0));
        m_sinkApp = sinkApp.Get(0);
        sinkApp.Start(Seconds(0.1));
        sinkApp.Stop(Seconds(m_duration));

        // OnOff on UAV (client), sends to AP
        OnOffHelper onoff("ns3::UdpSocketFactory",
                          InetSocketAddress(m_ipIfs.GetAddress(0), port));
        onoff.SetAttribute("PacketSize", UintegerValue(1024));
        onoff.SetAttribute("DataRate", StringValue("500kbps"));
        onoff.SetConstantRate(DataRate("500kbps"));
        ApplicationContainer clientApp = onoff.Install(m_uavNodes.Get(0));
        clientApp.Start(Seconds(0.2));
        clientApp.Stop(Seconds(m_duration));
    }

    void SetupFlowMonitor()
    {
        m_flowMonitor = m_flowHelper.InstallAll();
    }

    void SetupLte()
    {
        // LTE helper + EPC
        m_lteHelper = CreateObject<LteHelper>();
        Ptr<PointToPointEpcHelper> epcHelper = CreateObject<PointToPointEpcHelper>();
        m_lteHelper->SetEpcHelper(epcHelper);

        // PGW and remote host
        Ptr<Node> pgw = epcHelper->GetPgwNode();
        m_remoteHost.Create(1);
        InternetStackHelper internet;
        internet.Install(m_remoteHost);

        PointToPointHelper p2ph;
        p2ph.SetDeviceAttribute("DataRate", DataRateValue(DataRate("100Gb/s")));
        p2ph.SetChannelAttribute("Delay", TimeValue(MilliSeconds(5)));
        NetDeviceContainer internetDevices = p2ph.Install(pgw, m_remoteHost.Get(0));

        Ipv4AddressHelper ipv4h("1.0.0.0", "255.0.0.0");
        ipv4h.Assign(internetDevices);

        Ipv4StaticRoutingHelper ipv4RoutingHelper;
        Ptr<Ipv4StaticRouting> remoteHostRouting =
            ipv4RoutingHelper.GetStaticRouting(
                m_remoteHost.Get(0)->GetObject<Ipv4>());
        remoteHostRouting->AddNetworkRouteTo(
            Ipv4Address("7.0.0.0"), Ipv4Mask("255.0.0.0"), 1);

        // eNB node
        m_enbNode.Create(1);
        MobilityHelper enbMobility;
        enbMobility.SetMobilityModel("ns3::ConstantPositionMobilityModel");
        enbMobility.Install(m_enbNode);
        m_enbNode.Get(0)->GetObject<ConstantPositionMobilityModel>()->SetPosition(
            Vector(700.0, 0.0, 30.0));

        // LTE UE node (parallel to UAV, same mobility)
        m_lteUeNode.Create(1);
        MobilityHelper ueMobility;
        ueMobility.SetMobilityModel("ns3::ConstantVelocityMobilityModel");
        ueMobility.Install(m_lteUeNode);
        Ptr<ConstantVelocityMobilityModel> ueMob =
            m_lteUeNode.Get(0)->GetObject<ConstantVelocityMobilityModel>();
        ueMob->SetPosition(m_mobility->GetPosition());
        ueMob->SetVelocity(m_mobility->GetVelocity());
        m_lteMobility = ueMob;

        // Install LTE devices
        NetDeviceContainer enbDevs = m_lteHelper->InstallEnbDevice(m_enbNode);
        NetDeviceContainer ueDevs = m_lteHelper->InstallUeDevice(m_lteUeNode);

        // IP stack on UE + assign address
        internet.Install(m_lteUeNode);
        m_lteUeIpIfs = epcHelper->AssignUeIpv4Address(ueDevs);

        Ptr<Ipv4StaticRouting> ueRouting =
            ipv4RoutingHelper.GetStaticRouting(
                m_lteUeNode.Get(0)->GetObject<Ipv4>());
        ueRouting->SetDefaultRoute(epcHelper->GetUeDefaultGatewayAddress(), 1);

        m_lteHelper->Attach(ueDevs.Get(0), enbDevs.Get(0));
    }

    void SetupLteTraffic()
    {
        uint16_t ltePort = 10;
        // PacketSink on LTE UE (downlink receiver)
        PacketSinkHelper lteSink("ns3::UdpSocketFactory",
                                 InetSocketAddress(Ipv4Address::GetAny(), ltePort));
        ApplicationContainer lteSinkApp = lteSink.Install(m_lteUeNode.Get(0));
        m_lteSinkApp = lteSinkApp.Get(0);
        lteSinkApp.Start(Seconds(0.1));
        lteSinkApp.Stop(Seconds(m_duration));

        // OnOff from remote host → LTE UE (downlink)
        OnOffHelper lteOnoff("ns3::UdpSocketFactory",
                             InetSocketAddress(m_lteUeIpIfs.GetAddress(0), ltePort));
        lteOnoff.SetAttribute("PacketSize", UintegerValue(1024));
        lteOnoff.SetAttribute("DataRate", StringValue("500kbps"));
        lteOnoff.SetConstantRate(DataRate("500kbps"));
        ApplicationContainer lteClientApp = lteOnoff.Install(m_remoteHost.Get(0));
        lteClientApp.Start(Seconds(0.5));
        lteClientApp.Stop(Seconds(m_duration));
    }

    void Setup5gProxy()
    {
        // 5G proxy: point-to-point link simulating a 5G backhaul.
        // NOT real NR — uses P2P with low latency to emulate 5G transport.
        m_5gProxyNodes.Create(2); // [0]=proxy-UE, [1]=proxy-gNB/server
        InternetStackHelper internet;
        internet.Install(m_5gProxyNodes);

        MobilityHelper mob;
        mob.SetMobilityModel("ns3::ConstantPositionMobilityModel");
        mob.Install(m_5gProxyNodes);
        // proxy-UE follows UAV position conceptually
        m_5gProxyNodes.Get(0)->GetObject<ConstantPositionMobilityModel>()->SetPosition(
            m_mobility->GetPosition());
        // proxy-gNB at hypothetical gNB location (eastern edge of 2km area)
        m_5gProxyNodes.Get(1)->GetObject<ConstantPositionMobilityModel>()->SetPosition(
            Vector(1400.0, 0.0, 30.0));

        PointToPointHelper p2p;
        p2p.SetDeviceAttribute("DataRate", DataRateValue(DataRate("10Gbps")));
        p2p.SetChannelAttribute("Delay", TimeValue(MilliSeconds(1)));
        NetDeviceContainer devs = p2p.Install(m_5gProxyNodes);

        Ipv4AddressHelper ipv4("9.0.0.0", "255.255.255.0");
        m_5gProxyIpIfs = ipv4.Assign(devs);

        std::cout << "[5G proxy] topology: P2P link 9.0.0.1 <-> 9.0.0.2, "
                  << "1ms delay, 10Gbps. NOT real NR." << std::endl;
        std::cout << "[5G proxy] flow classification: dst in 9.0.0.0/8"
                  << std::endl;
    }

    void Setup5gProxyTraffic()
    {
        uint16_t port5g = 5000;
        // PacketSink on proxy-UE (receiver)
        PacketSinkHelper sink5g("ns3::UdpSocketFactory",
                                InetSocketAddress(Ipv4Address::GetAny(), port5g));
        ApplicationContainer sinkApp5g = sink5g.Install(m_5gProxyNodes.Get(0));
        m_5gSinkApp = sinkApp5g.Get(0);
        sinkApp5g.Start(Seconds(0.1));
        sinkApp5g.Stop(Seconds(m_duration));

        // OnOff from proxy-gNB/server → proxy-UE (downlink)
        OnOffHelper onoff5g("ns3::UdpSocketFactory",
                            InetSocketAddress(m_5gProxyIpIfs.GetAddress(0), port5g));
        onoff5g.SetAttribute("PacketSize", UintegerValue(1024));
        onoff5g.SetAttribute("DataRate", StringValue("2Mbps"));
        onoff5g.SetConstantRate(DataRate("2Mbps"));
        ApplicationContainer clientApp5g = onoff5g.Install(m_5gProxyNodes.Get(1));
        clientApp5g.Start(Seconds(0.3));
        clientApp5g.Stop(Seconds(m_duration));
    }

    // -----------------------------------------------------------------------
    // Background nodes (Gauss-Markov mobility, thesis Section 3.5)
    // -----------------------------------------------------------------------
    void SetupBackgroundNodes()
    {
        if (m_numBackgroundNodes == 0)
            return;

        m_backgroundStaNodes.Create(m_numBackgroundNodes);

        // Random positions within 2000m x 2000m area, altitude 50-150m
        // (thesis Table 3-2: area 2000m*2000m*200m)
        // Using ConstantPositionMobilityModel for stability; node density
        // creates WiFi contention/congestion as more nodes are added.
        MobilityHelper bgMobility;
        bgMobility.SetMobilityModel("ns3::ConstantPositionMobilityModel");
        bgMobility.SetPositionAllocator(
            "ns3::RandomBoxPositionAllocator",
            "X", StringValue("ns3::UniformRandomVariable[Min=0|Max=2000]"),
            "Y", StringValue("ns3::UniformRandomVariable[Min=-1000|Max=1000]"),
            "Z", StringValue("ns3::UniformRandomVariable[Min=50|Max=150]"));
        bgMobility.Install(m_backgroundStaNodes);

        std::cout << "[LAAVHA] Created " << m_numBackgroundNodes
                  << " background STA nodes (random positions, area 2000x2000m)"
                  << std::endl;
    }

    void SetupBackgroundTraffic()
    {
        if (m_numBackgroundNodes == 0)
            return;

        // Each background node sends light UDP traffic to AP, creating
        // realistic WiFi contention/congestion as node count increases
        uint16_t basePort = 20;
        for (uint32_t i = 0; i < m_numBackgroundNodes; ++i)
        {
            OnOffHelper onoff("ns3::UdpSocketFactory",
                InetSocketAddress(m_ipIfs.GetAddress(0), basePort + i));
            onoff.SetAttribute("PacketSize", UintegerValue(1024));
            onoff.SetAttribute("DataRate", StringValue("30kbps"));
            onoff.SetConstantRate(DataRate("30kbps"));
            ApplicationContainer app = onoff.Install(m_backgroundStaNodes.Get(i));
            app.Start(Seconds(0.5 + i * 0.01));  // stagger starts
            app.Stop(Seconds(m_duration));
        }

        std::cout << "[LAAVHA] Background traffic: " << m_numBackgroundNodes
                  << " nodes × 30kbps UDP to AP" << std::endl;
    }

    // -----------------------------------------------------------------------
    // Simulation events
    // -----------------------------------------------------------------------
    void UpdateVelocity()
    {
        Vector newVel(m_initialSpeed * 0.75, 0.0, 5.0);
        m_mobility->SetVelocity(newVel);
        if (m_lteMobility)
        {
            m_lteMobility->SetVelocity(newVel);
        }
    }

    void DecisionStep()
    {
        double now = Simulator::Now().GetSeconds();
        int stepIndex = m_decisions;

        Vector v = m_mobility->GetVelocity();
        Vector p = m_mobility->GetPosition();

        Cpp2PyStruct* env = m_msg->GetCpp2PyStruct();
        env->velocity = std::sqrt(v.x * v.x + v.y * v.y + v.z * v.z);
        env->altitude = p.z;
        env->current_net = m_currentNet;

        UpdateMetrics(now, p, env);

        m_msg->CppSendBegin();
        m_msg->CppSendEnd();

        m_msg->CppRecvBegin();
        int targetNet = m_msg->GetPy2CppStruct()->target_net_id;
        float s5g = m_msg->GetPy2CppStruct()->score_5g;
        float slte = m_msg->GetPy2CppStruct()->score_lte;
        float swifi = m_msg->GetPy2CppStruct()->score_wifi;
        m_msg->CppRecvEnd();

        m_decisions++;

        // Query FlowMonitor AFTER CppRecvEnd (safe point - not blocking)
        if (m_flowmonMode != "off")
        {
            QueryFlowMonitor(now);
            QueryLteFlowMonitor(now);
            Query5gFlowMonitor(now);
        }

        // Periodic log (every 10 decisions)
        if (stepIndex % 10 == 0 && m_prevMetricTime > 0)
        {
            std::cout << "[WiFi signal] sinr=" << m_lastWifiSinr
                      << "dB rsrp=" << m_lastWifiRsrp
                      << "dBm source=propagation-proxy" << std::endl;
            std::cout << "[WiFi real] t=" << now << "s thrpt=" << m_lastWifiThroughput
                      << " Mbps (PacketSink)";
            if (m_flowmonMode != "off")
            {
                std::cout << " | [FlowMonitor] delay=" << m_fmDelay
                          << "s thrpt=" << m_fmThroughput
                          << "Mbps plr=" << m_fmPlr;
            }
            std::cout << std::endl;
            std::cout << "[LTE signal] sinr=" << m_lastLteSinr
                      << "dB rsrp=" << m_lastLteRsrp
                      << "dBm source=propagation-proxy" << std::endl;
            std::cout << "[LTE real] t=" << now << "s thrpt=" << m_lastLteThroughput
                      << " Mbps";
            if (m_flowmonMode != "off")
            {
                std::cout << " | [FlowMonitor] delay=" << m_lteFmDelay
                          << "s plr=" << m_lteFmPlr;
            }
            std::cout << std::endl;
            std::cout << "[5G proxy] t=" << now << "s thrpt=" << m_5gFmThroughput
                      << " Mbps";
            if (m_flowmonMode != "off")
            {
                std::cout << " | [FlowMonitor] delay=" << m_5gFmDelay
                          << "s plr=" << m_5gFmPlr;
            }
            std::cout << " (NOT real NR)" << std::endl;
        }

        std::cout << "Decision " << stepIndex << " (t=" << now << "s): "
                  << "vel=" << env->velocity << " alt=" << env->altitude
                  << " pos=" << p << " cur=" << m_currentNet
                  << " -> target=" << targetNet << " scores=[" << s5g << ","
                  << slte << "," << swifi << "]";

        if (targetNet != m_currentNet)
        {
            m_handoverCount++;
            std::cout << " *** HANDOVER " << m_currentNet << " -> " << targetNet
                      << " ***";
            m_currentNet = targetNet;
        }
        std::cout << std::endl;

        if (now + m_period < m_duration)
        {
            Simulator::Schedule(Seconds(m_period),
                                &LaavhaScheduledSimulation::DecisionStep,
                                this);
        }
    }

    // -----------------------------------------------------------------------
    // Metrics
    // -----------------------------------------------------------------------
    void UpdateMetrics(double now, Vector pos, Cpp2PyStruct* env)
    {
        ComputeWifiMetrics(now);

        // Current-step metrics for each of the 3 networks
        std::array<float, 5> m5g = Proxy5gMetrics(now, pos);
        std::array<float, 5> mLte = LteMetrics(now, pos);
        std::array<float, 5> mWifi = WiFiMetrics(now, pos);

        if (!m_historyInitialized)
        {
            InitializeMetricHistory(now, pos);
            m_historyInitialized = true;
        }
        else
        {
            ShiftAndAppendHistory(0, m5g);
            ShiftAndAppendHistory(1, mLte);
            ShiftAndAppendHistory(2, mWifi);
        }

        FlattenHistory(env);
    }

    void ComputeWifiMetrics(double now)
    {
        // Use PacketSink rx bytes for real WiFi throughput.
        // SINR, RSRP, Delay, PLR remain synthetic.
        Ptr<PacketSink> sink = DynamicCast<PacketSink>(m_sinkApp);
        if (!sink)
        {
            return;
        }

        uint64_t rxBytes = sink->GetTotalRx();

        if (m_prevMetricTime < 0)
        {
            m_prevRxBytes = rxBytes;
            m_prevMetricTime = now;
            return;
        }

        double deltaTime = now - m_prevMetricTime;
        uint64_t dRxBytes = rxBytes - m_prevRxBytes;

        if (deltaTime > 0)
        {
            m_lastWifiThroughput =
                static_cast<float>(dRxBytes * 8.0 / deltaTime / 1e6); // Mbps
        }
        else
        {
            m_lastWifiThroughput = 0.0f;
        }

        // Delay and PLR remain synthetic for now
        m_prevRxBytes = rxBytes;
        m_prevMetricTime = now;
    }

    void QueryFlowMonitor(double now)
    {
        if (!m_flowMonitor)
        {
            return;
        }
        m_flowMonitor->CheckForLostPackets();
        auto stats = m_flowMonitor->GetFlowStats();

        uint64_t txPkts = 0, rxPkts = 0, lostPkts = 0, rxBytes = 0;
        double delaySum = 0.0;

        for (auto& [fid, f] : stats)
        {
            if (f.txPackets > 0)
            {
                txPkts += f.txPackets;
                rxPkts += f.rxPackets;
                lostPkts += f.lostPackets;
                rxBytes += f.rxBytes;
                delaySum += f.delaySum.GetSeconds();
            }
        }

        if (m_fmPrevTime < 0)
        {
            m_fmPrevTxPkts = txPkts;
            m_fmPrevRxPkts = rxPkts;
            m_fmPrevLostPkts = lostPkts;
            m_fmPrevRxBytes = rxBytes;
            m_fmPrevDelaySum = delaySum;
            m_fmPrevTime = now;
            return;
        }

        double dt = now - m_fmPrevTime;
        uint64_t dTx = txPkts - m_fmPrevTxPkts;
        uint64_t dRx = rxPkts - m_fmPrevRxPkts;
        uint64_t dRxB = rxBytes - m_fmPrevRxBytes;
        double dDelay = delaySum - m_fmPrevDelaySum;

        if (dRx > 0 && dt > 0)
        {
            m_fmDelay = static_cast<float>(dDelay / dRx);
            m_fmThroughput = static_cast<float>(dRxB * 8.0 / dt / 1e6);
        }
        else if (dt > 0)
        {
            m_fmThroughput = 0.0f;
        }

        if (dTx > 0)
        {
            double plr = static_cast<double>(dTx - dRx) / dTx;
            m_fmPlr = static_cast<float>(std::max(0.0, std::min(1.0, plr)));
        }
        else
        {
            m_fmPlr = 0.0f;
        }

        m_fmPrevTxPkts = txPkts;
        m_fmPrevRxPkts = rxPkts;
        m_fmPrevLostPkts = lostPkts;
        m_fmPrevRxBytes = rxBytes;
        m_fmPrevDelaySum = delaySum;
        m_fmPrevTime = now;
    }

    std::array<float, 5> Proxy5gMetrics(double now, Vector pos)
    {
        // 5G proxy: propagation-based SINR/RSRP from hypothetical gNB position.
        // Transport metrics from FlowMonitor on P2P proxy flow (NOT real NR).
        constexpr double gnbX = 1400.0, gnbY = 0.0, gnbZ = 30.0;
        constexpr double txPowerDbm = 30.0;    // macro gNB
        constexpr double noiseFloorDbm = -95.0;
        constexpr double refLossDb = 32.4;     // free-space at 1m, 3.5 GHz
        constexpr double pathLossExp = 2.8;    // urban macro mmWave-like

        double dx = pos.x - gnbX;
        double dy = pos.y - gnbY;
        double dz = pos.z - gnbZ;
        double dist = std::sqrt(dx * dx + dy * dy + dz * dz);
        if (dist < 1.0)
            dist = 1.0;

        double pathLossDb = refLossDb + 10.0 * pathLossExp * std::log10(dist);
        double rxPowerDbm = txPowerDbm - pathLossDb;
        double sinrDb = rxPowerDbm - noiseFloorDbm;

        double timeFrac = now / m_duration;
        double noise = std::sin(now * 3.0 + 2.0) * 0.02;

        float delay = 2.0f + 8.0f * (float)timeFrac + std::abs((float)noise);
        float thrpt = 500.0f - 300.0f * (float)timeFrac + (float)noise;
        float plr = 0.005f + 0.05f * (float)timeFrac + std::abs((float)noise);

        if (m_flowmonMode == "feed")
        {
            delay = m_5gFmDelay * 1000.0f; // s -> ms
            thrpt = m_5gFmThroughput;      // Mbps from FlowMonitor
            plr = m_5gFmPlr;
        }

        return {
            /* SINR */ static_cast<float>(sinrDb),
            /* RSRP */ static_cast<float>(rxPowerDbm),
            /* Delay */ delay,
            /* Thrpt */ thrpt,
            /* PLR */ plr,
        };
    }

    std::array<float, 5> LteMetrics(double now, Vector /*pos*/)
    {
        double noise = std::sin(now * 3.0 + 3.0) * 0.02;

        float delay = 15.0f + (float)noise;
        float plr = 0.03f + std::abs((float)noise);

        if (m_flowmonMode == "feed")
        {
            delay = m_lteFmDelay * 1000.0f; // s -> ms
            plr = m_lteFmPlr;
        }

        ComputeLteSignal();

        return {
            /* SINR */ m_lastLteSinr,
            /* RSRP */ m_lastLteRsrp,
            /* Delay */ delay,
            /* Thrpt */ m_lastLteThroughput,
            /* PLR */ plr,
        };
    }

    void ComputeLteSignal()
    {
        // Propagation proxy for LTE (2 GHz band, macro-cell parameters)
        constexpr double txPowerDbm = 23.0;
        constexpr double noiseFloorDbm = -100.0;
        constexpr double refLossDb = 38.0;  // free-space at 1m, 2 GHz
        constexpr double pathLossExp = 3.5; // urban macro

        Vector uePos = m_lteMobility->GetPosition();
        Vector enbPos = m_enbNode.Get(0)->GetObject<MobilityModel>()->GetPosition();

        double dx = uePos.x - enbPos.x;
        double dy = uePos.y - enbPos.y;
        double dz = uePos.z - enbPos.z;
        double dist = std::sqrt(dx * dx + dy * dy + dz * dz);
        if (dist < 1.0)
        {
            dist = 1.0;
        }

        double pathLossDb = refLossDb + 10.0 * pathLossExp * std::log10(dist);
        double rxPowerDbm = txPowerDbm - pathLossDb;
        double sinrDb = rxPowerDbm - noiseFloorDbm;

        m_lastLteRsrp = static_cast<float>(rxPowerDbm);
        m_lastLteSinr = static_cast<float>(sinrDb);
    }

    void QueryLteFlowMonitor(double now)
    {
        if (!m_flowMonitor)
        {
            return;
        }
        m_flowMonitor->CheckForLostPackets();
        Ptr<Ipv4FlowClassifier> classifier =
            DynamicCast<Ipv4FlowClassifier>(m_flowHelper.GetClassifier());
        auto stats = m_flowMonitor->GetFlowStats();

        uint64_t txPkts = 0, rxPkts = 0, rxBytes = 0;
        double delaySum = 0.0;

        for (auto& [fid, f] : stats)
        {
            if (f.txPackets == 0)
                continue;
            Ipv4FlowClassifier::FiveTuple t = classifier->FindFlow(fid);
            // LTE UE is in 7.0.0.0/8 subnet
            if ((t.destinationAddress.Get() & 0xFF000000) == 0x07000000)
            {
                txPkts += f.txPackets;
                rxPkts += f.rxPackets;
                rxBytes += f.rxBytes;
                delaySum += f.delaySum.GetSeconds();
            }
        }

        if (m_lteFmPrevTime < 0)
        {
            m_lteFmPrevTxPkts = txPkts;
            m_lteFmPrevRxPkts = rxPkts;
            m_lteFmPrevRxBytes = rxBytes;
            m_lteFmPrevDelaySum = delaySum;
            m_lteFmPrevTime = now;
            return;
        }

        double dt = now - m_lteFmPrevTime;
        uint64_t dTx = txPkts - m_lteFmPrevTxPkts;
        uint64_t dRx = rxPkts - m_lteFmPrevRxPkts;
        uint64_t dRxB = rxBytes - m_lteFmPrevRxBytes;
        double dDelay = delaySum - m_lteFmPrevDelaySum;

        if (dRx > 0 && dt > 0)
        {
            m_lteFmDelay = static_cast<float>(dDelay / dRx);
            m_lteFmThroughput = static_cast<float>(dRxB * 8.0 / dt / 1e6);
            m_lastLteThroughput = m_lteFmThroughput;
        }
        else if (dt > 0)
        {
            m_lteFmThroughput = 0.0f;
            m_lastLteThroughput = 0.0f;
        }

        if (dTx > 0)
        {
            double plr = static_cast<double>(dTx - dRx) / dTx;
            m_lteFmPlr = static_cast<float>(std::max(0.0, std::min(1.0, plr)));
        }
        else
        {
            m_lteFmPlr = 0.0f;
        }

        m_lteFmPrevTxPkts = txPkts;
        m_lteFmPrevRxPkts = rxPkts;
        m_lteFmPrevRxBytes = rxBytes;
        m_lteFmPrevDelaySum = delaySum;
        m_lteFmPrevTime = now;
    }

    void Query5gFlowMonitor(double now)
    {
        if (!m_flowMonitor)
        {
            return;
        }
        m_flowMonitor->CheckForLostPackets();
        Ptr<Ipv4FlowClassifier> classifier =
            DynamicCast<Ipv4FlowClassifier>(m_flowHelper.GetClassifier());
        auto stats = m_flowMonitor->GetFlowStats();

        uint64_t txPkts = 0, rxPkts = 0, rxBytes = 0;
        double delaySum = 0.0;

        for (auto& [fid, f] : stats)
        {
            if (f.txPackets == 0)
                continue;
            Ipv4FlowClassifier::FiveTuple t = classifier->FindFlow(fid);
            // 5G proxy UE is in 9.0.0.0/8 subnet
            if ((t.destinationAddress.Get() & 0xFF000000) == 0x09000000)
            {
                txPkts += f.txPackets;
                rxPkts += f.rxPackets;
                rxBytes += f.rxBytes;
                delaySum += f.delaySum.GetSeconds();
            }
        }

        if (m_5gFmPrevTime < 0)
        {
            m_5gFmPrevTxPkts = txPkts;
            m_5gFmPrevRxPkts = rxPkts;
            m_5gFmPrevRxBytes = rxBytes;
            m_5gFmPrevDelaySum = delaySum;
            m_5gFmPrevTime = now;
            return;
        }

        double dt = now - m_5gFmPrevTime;
        uint64_t dTx = txPkts - m_5gFmPrevTxPkts;
        uint64_t dRx = rxPkts - m_5gFmPrevRxPkts;
        uint64_t dRxB = rxBytes - m_5gFmPrevRxBytes;
        double dDelay = delaySum - m_5gFmPrevDelaySum;

        if (dRx > 0 && dt > 0)
        {
            m_5gFmDelay = static_cast<float>(dDelay / dRx);
            m_5gFmThroughput = static_cast<float>(dRxB * 8.0 / dt / 1e6);
        }
        else if (dt > 0)
        {
            m_5gFmThroughput = 0.0f;
        }

        if (dTx > 0)
        {
            double plr = static_cast<double>(dTx - dRx) / dTx;
            m_5gFmPlr = static_cast<float>(std::max(0.0, std::min(1.0, plr)));
        }
        else
        {
            m_5gFmPlr = 0.0f;
        }

        m_5gFmPrevTxPkts = txPkts;
        m_5gFmPrevRxPkts = rxPkts;
        m_5gFmPrevRxBytes = rxBytes;
        m_5gFmPrevDelaySum = delaySum;
        m_5gFmPrevTime = now;
    }

    std::array<float, 5> WiFiMetrics(double now, Vector /*pos*/)
    {
        double timeFrac = now / m_duration;
        double noise = std::sin(now * 3.0 + 0.5) * 0.02;

        float delay = 20.0f - 10.0f * (float)timeFrac + (float)noise;
        float plr = 0.05f - 0.03f * (float)timeFrac + std::abs((float)noise);

        if (m_flowmonMode == "feed")
        {
            delay = m_fmDelay * 1000.0f; // convert s -> ms for model scale
            plr = m_fmPlr;
        }

        ComputeWifiSignal();

        return {
            /* SINR */ m_lastWifiSinr,
            /* RSRP */ m_lastWifiRsrp,
            /* Delay */ delay,
            /* Thrpt */ m_lastWifiThroughput, // REAL from PacketSink
            /* PLR */ plr,
        };
    }

    void ComputeWifiSignal()
    {
        // Propagation proxy: log-distance path loss from UAV to AP.
        // Parameters for 802.11g at 2.4 GHz (thesis Table 3-2: TX power 20dBm,
        // transmission range ~200m).
        constexpr double txPowerDbm = 20.0;    // thesis: 20 dBm
        constexpr double noiseFloorDbm = -93.0; // thermal noise at 20 MHz BW
        constexpr double refLossDb = 40.0;     // free-space loss at 1m, 2.4 GHz
        constexpr double pathLossExp = 3.0;    // urban/suburban exponent

        Vector uavPos = m_mobility->GetPosition();
        Vector apPos = m_apNode.Get(0)->GetObject<MobilityModel>()->GetPosition();

        double dx = uavPos.x - apPos.x;
        double dy = uavPos.y - apPos.y;
        double dz = uavPos.z - apPos.z;
        double dist = std::sqrt(dx * dx + dy * dy + dz * dz);

        if (dist < 1.0)
        {
            dist = 1.0;
        }

        double pathLossDb = refLossDb + 10.0 * pathLossExp * std::log10(dist);
        double rxPowerDbm = txPowerDbm - pathLossDb;
        double sinrDb = rxPowerDbm - noiseFloorDbm;

        m_lastWifiRsrp = static_cast<float>(rxPowerDbm);
        m_lastWifiSinr = static_cast<float>(sinrDb);
    }

    // -----------------------------------------------------------------------
    // 10-step metric history buffer
    // -----------------------------------------------------------------------
    void InitializeMetricHistory(double now, Vector pos)
    {
        auto m5g = Proxy5gMetrics(now, pos);
        auto mLte = LteMetrics(now, pos);
        auto mWifi = WiFiMetrics(now, pos);

        for (int t = 0; t < 10; ++t)
        {
            m_metricHistory[0][t] = m5g;
            m_metricHistory[1][t] = mLte;
            m_metricHistory[2][t] = mWifi;
        }
    }

    void ShiftAndAppendHistory(int net, const std::array<float, 5>& metrics)
    {
        // Shift left: t=0 discarded, t=1..9 move to 0..8
        for (int t = 0; t < 9; ++t)
        {
            m_metricHistory[net][t] = m_metricHistory[net][t + 1];
        }
        m_metricHistory[net][9] = metrics;
    }

    void FlattenHistory(Cpp2PyStruct* env)
    {
        for (int net = 0; net < 3; ++net)
        {
            for (int t = 0; t < 10; ++t)
            {
                int base = net * 50 + t * 5;
                env->metrics[base + 0] = m_metricHistory[net][t][0];
                env->metrics[base + 1] = m_metricHistory[net][t][1];
                env->metrics[base + 2] = m_metricHistory[net][t][2];
                env->metrics[base + 3] = m_metricHistory[net][t][3];
                env->metrics[base + 4] = m_metricHistory[net][t][4];
            }
        }
    }

    // -----------------------------------------------------------------------
    // Summary
    // -----------------------------------------------------------------------
    void PrintSummary()
    {
        std::cout << "\n=== Summary ===" << std::endl;
        std::cout << "handover_count: " << m_handoverCount << std::endl;
        std::cout << "final_net: " << m_currentNet << std::endl;
        std::cout << "decisions: " << m_decisions << std::endl;
        std::cout << "=== LAAVHA stage 3 complete ===" << std::endl;
    }

    // -----------------------------------------------------------------------
    // Members
    // -----------------------------------------------------------------------
    Ns3AiMsgInterfaceImpl<Cpp2PyStruct, Py2CppStruct>* m_msg;
    NodeContainer m_uavNodes;
    Ptr<ConstantVelocityMobilityModel> m_mobility;

    // WiFi network
    NodeContainer m_apNode;
    Ipv4InterfaceContainer m_ipIfs;
    Ptr<Application> m_sinkApp; // PacketSink for real throughput

    // Simulation state
    int m_currentNet;
    int m_handoverCount;
    int m_decisions;
    double m_duration;
    double m_period;
    double m_initialSpeed;
    double m_initialAltitude;
    double m_initialPosOffsetX;
    double m_initialPosOffsetY;

    // FlowMonitor
    std::string m_flowmonMode;
    FlowMonitorHelper m_flowHelper;
    Ptr<FlowMonitor> m_flowMonitor;

    // Interval tracking for real WiFi throughput (PacketSink)
    uint64_t m_prevRxBytes;
    double m_prevMetricTime;
    float m_lastWifiThroughput;

    // WiFi signal metrics (propagation proxy)
    float m_lastWifiSinr;
    float m_lastWifiRsrp;

    // WiFi FlowMonitor interval tracking
    uint64_t m_fmPrevTxPkts;
    uint64_t m_fmPrevRxPkts;
    uint64_t m_fmPrevLostPkts;
    uint64_t m_fmPrevRxBytes;
    double m_fmPrevDelaySum;
    double m_fmPrevTime;
    float m_fmDelay;
    float m_fmThroughput;
    float m_fmPlr;

    // LTE network
    Ptr<LteHelper> m_lteHelper;
    NodeContainer m_enbNode;
    NodeContainer m_lteUeNode;
    NodeContainer m_remoteHost;
    Ptr<ConstantVelocityMobilityModel> m_lteMobility;
    Ipv4InterfaceContainer m_lteUeIpIfs;
    Ptr<Application> m_lteSinkApp;

    // LTE signal metrics (propagation proxy)
    float m_lastLteSinr;
    float m_lastLteRsrp;
    float m_lastLteThroughput;

    // LTE FlowMonitor interval tracking
    uint64_t m_lteFmPrevTxPkts;
    uint64_t m_lteFmPrevRxPkts;
    uint64_t m_lteFmPrevRxBytes;
    double m_lteFmPrevDelaySum;
    double m_lteFmPrevTime;
    float m_lteFmDelay;
    float m_lteFmThroughput;
    float m_lteFmPlr;

    // 5G proxy network (P2P link, NOT real NR)
    NodeContainer m_5gProxyNodes;
    Ipv4InterfaceContainer m_5gProxyIpIfs;
    Ptr<Application> m_5gSinkApp;

    // 5G proxy FlowMonitor interval tracking
    uint64_t m_5gFmPrevTxPkts;
    uint64_t m_5gFmPrevRxPkts;
    uint64_t m_5gFmPrevRxBytes;
    double m_5gFmPrevDelaySum;
    double m_5gFmPrevTime;
    float m_5gFmDelay;
    float m_5gFmThroughput;
    float m_5gFmPlr;

    // 10-step history buffer [network][timestep][indicator]
    std::array<std::array<std::array<float, 5>, 10>, 3> m_metricHistory;
    bool m_historyInitialized;

    // Background congestion nodes (thesis Section 3.5: node count 50-350)
    uint32_t m_numBackgroundNodes;
    NodeContainer m_backgroundStaNodes;
    Ipv4InterfaceContainer m_bgIpIfs;
};

// ---------------------------------------------------------------------------
// main
// ---------------------------------------------------------------------------
int
main(int argc, char* argv[])
{
    LaavhaScheduledSimulation sim;
    sim.Configure(argc, argv);
    sim.Run();
    return 0;
}
