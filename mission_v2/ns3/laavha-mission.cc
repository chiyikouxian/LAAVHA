// Mission-v2: real NR/LTE/Wi-Fi, a shared logical upstream application and
// application-layer interface migration. This is NOT a protocol VHO implementation.
#include "ns3/applications-module.h"
#include "ns3/core-module.h"
#include "ns3/internet-module.h"
#include "ns3/lte-module.h"
#include "ns3/mobility-module.h"
#include "ns3/nr-module.h"
#include "ns3/point-to-point-module.h"
#include "ns3/wifi-module.h"
#include "mission-config.h"
#include <array>
#include <algorithm>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <string>
#include <sstream>
#include <vector>

using namespace ns3;

// A geometric obstruction and a frozen spatial shadow field act on the actual
// channel power, independently of policy actions. UAVs fly above the roof.
class SceneLoss : public PropagationLossModel
{
  public:
    double obstructionDb=mission_config::obstruction_db,shadowDb=0;
    double shadowLengthM=8,shadowCorrelation=.35;
    int linkIndex=0;
    double roofHeight=mission_config::building_high[2];
    uint32_t sceneSeed=100;
    static TypeId GetTypeId(){static TypeId t=TypeId("MissionSceneLoss").SetParent<PropagationLossModel>().AddConstructor<SceneLoss>();return t;}
    double ShadowLoss(const Vector& mobile) const
    {
        double common=0,independent=0;
        for(int k=1;k<=8;++k)
        {
            double spatial=mobile.x/(shadowLengthM*(.4+.15*k))
                          +mobile.y/(shadowLengthM*(.6+.17*k));
            common+=std::sin(spatial+sceneSeed*(.37+k*.11));
            independent+=std::sin(spatial+sceneSeed*(.61+k*.17)+(linkIndex+1)*(1.13+k*.73));
        }
        // Shared and link-specific fields are fixed before actions, continuous
        // in space and reciprocal. The parameter is a mixing power fraction,
        // not a promise of exact finite-trajectory sample correlation.
        return shadowDb*(std::sqrt(shadowCorrelation)*common
                         +std::sqrt(1-shadowCorrelation)*independent)/2.;
    }
  private:
    double DoCalcRxPower(double tx,Ptr<MobilityModel> a,Ptr<MobilityModel> b) const override
    {
        Vector p=a->GetPosition(),q=b->GetPosition();
        double enter=0,leave=1;
        std::array<double,3> origin{p.x,p.y,p.z},delta{q.x-p.x,q.y-p.y,q.z-p.z};
        auto low=mission_config::building_low,high=mission_config::building_high;
        high[2]=roofHeight;
        bool crosses=true;
        for(int k=0;k<3;++k)
        {
            if(std::abs(delta[k])<1e-9){if(origin[k]<low[k]||origin[k]>high[k])crosses=false;}
            else{double t1=(low[k]-origin[k])/delta[k],t2=(high[k]-origin[k])/delta[k];if(t1>t2)std::swap(t1,t2);enter=std::max(enter,t1);leave=std::min(leave,t2);}
        }
        crosses=crosses&&enter<=leave&&leave>=0&&enter<=1;
        Vector mobile=p.z>q.z?p:q;
        return tx-(crosses?obstructionDb:0)-ShadowLoss(mobile);
    }
    int64_t DoAssignStreams(int64_t) override{return 0;}
};

class MissionHeader : public Header
{
  public:
    uint32_t id=0;
    static TypeId GetTypeId() {static TypeId t=TypeId("MissionV2Header").SetParent<Header>().AddConstructor<MissionHeader>();return t;}
    TypeId GetInstanceTypeId() const override {return GetTypeId();}
    uint32_t GetSerializedSize() const override {return 4;}
    void Serialize(Buffer::Iterator i) const override {i.WriteHtonU32(id);}
    uint32_t Deserialize(Buffer::Iterator i) override {id=i.ReadNtohU32();return 4;}
    void Print(std::ostream& os) const override {os<<id;}
};

struct Record
{
    double generated, received=-1, deadline;
    uint32_t bytes;
    int network, kind; // kind: probe=0,telemetry=1,video=2
    bool interruption=false;
};

class Mission
{
  public:
    double duration=mission_config::duration,period=mission_config::period,warmup=mission_config::warmup,interruption=mission_config::interruption,imagingMbps=mission_config::imaging_mbps;
    double offsetX=0,offsetY=0,offsetZ=0;
    double lteBackhaulMbps=6,nrTxDbm=23;
    double obstructionDb=mission_config::obstruction_db,shadowDb=0;
    double shadowLengthM=8,shadowCorrelation=.35;
    double roofHeight=mission_config::building_high[2];
    uint32_t seed=100;
    bool randomize=true;
    std::string output="mission-packets.csv",controller="pipe",scheduleFile="";
    int fixedNetwork=0;
    NodeContainer ue,sites;
    Ptr<Node> server;
    Ptr<LteHelper> lte;
    Ptr<NrHelper> nr;
    std::array<Ptr<Socket>,3> send;
    std::array<Ptr<SceneLoss>,3> sceneModels;
    std::array<Ipv4Address,3> destinations;
    std::array<double,3> sinr{{-50,-50,-50}},rx{{-150,-150,-150}},signalTime{{-1,-1,-1}};
    std::vector<Record> records;
    std::vector<int> schedule;
    int serving=0,handovers=0;
    double blockedUntil=-1;
    std::ofstream states;

    static std::pair<double,double> Motion(double t)
    {
        if(t<19.5)return {1600-30*t,30};
        if(t<20.5){double u=t-19.5;return {1015-30*u+12.5*u*u,30-25*u};}
        if(t<29.5)return {997.5-5*(t-20.5),5};
        if(t<30.5){double u=t-29.5;return {952.5-5*u-10*u*u,5+20*u};}
        return {937.5-25*(t-30.5),25};
    }

    void Position()
    {
        double t=Simulator::Now().GetSeconds()-warmup;
        auto [x,v]=Motion(std::max(0.,t));
        for(uint32_t n=0;n<ue.GetN();++n)
        {
            auto m=ue.Get(n)->GetObject<ConstantVelocityMobilityModel>();
            m->SetPosition(Vector(x+offsetX,1000+offsetY,100+offsetZ));
            m->SetVelocity(Vector(t<0?0:-v,0,0));
        }
        if(t<duration)Simulator::Schedule(MilliSeconds(20),&Mission::Position,this);
    }

    double Demand() const
    {
        double x=ue.Get(0)->GetObject<MobilityModel>()->GetPosition().x;
        return x>=950&&x<=1000?imagingMbps:mission_config::preview_mbps;
    }

    void Receive(Ptr<Socket> socket)
    {
        while(auto packet=socket->Recv())
        {
            MissionHeader header;
            if(packet->GetSize()<4)continue;
            packet->RemoveHeader(header);
            if(header.id<records.size()&&records[header.id].received<0)
                records[header.id].received=Simulator::Now().GetSeconds();
        }
    }

    void SendPacket(int network,int kind,uint32_t bytes,double deadline)
    {
        double now=Simulator::Now().GetSeconds();
        Record record{now,-1,deadline,bytes,network,kind,false};
        if(kind>0&&now<blockedUntil)record.interruption=true;
        records.push_back(record);
        if(record.interruption)return;
        auto packet=Create<Packet>(bytes);
        MissionHeader header;header.id=records.size()-1;packet->AddHeader(header);
        send[network]->Send(packet);
    }

    void Probe(int network)
    {
        if(Simulator::Now().GetSeconds()>=warmup+duration)return;
        SendPacket(network,0,256,.2);
        Simulator::Schedule(MilliSeconds(20),&Mission::Probe,this,network);
    }

    void Telemetry()
    {
        if(Simulator::Now().GetSeconds()>=warmup+duration)return;
        SendPacket(serving,1,200,.05);
        Simulator::Schedule(MilliSeconds(25),&Mission::Telemetry,this);
    }

    void Video()
    {
        if(Simulator::Now().GetSeconds()>=warmup+duration)return;
        for(int i=0;i<8;++i)SendPacket(serving,2,1024,.2);
        Simulator::Schedule(Seconds(8*1024*8/(Demand()*1e6)),&Mission::Video,this);
    }

    void LteSignal(uint16_t,uint16_t,double rsrp,double,uint8_t)
    {
        rx[1]=10*std::log10(std::max(rsrp,1e-18))+30;
    }
    void LteUplinkSinr(uint16_t,uint16_t,double linearSinr,uint8_t)
    {sinr[1]=10*std::log10(std::max(linearSinr,1e-15));signalTime[1]=Simulator::Now().GetSeconds();}
    void NrUplinkSinr(uint64_t,SpectrumValue& linearSinr,SpectrumValue&)
    {
        double sum=0;int active=0;
        for(auto it=linearSinr.ConstValuesBegin();it!=linearSinr.ConstValuesEnd();++it)
            if(*it>0){sum+=*it;++active;}
        if(active){sinr[0]=10*std::log10(sum/active);signalTime[0]=Simulator::Now().GetSeconds();}
    }
    void NrRsrp(uint16_t,uint16_t,uint16_t,double rsrp,uint8_t)
    {rx[0]=rsrp;}
    void WifiSignal(Ptr<const Packet>,uint16_t,WifiTxVector,MpduInfo,SignalNoiseDbm s,uint16_t)
    {rx[2]=s.signal;sinr[2]=s.signal-s.noise;signalTime[2]=Simulator::Now().GetSeconds();}

    void Decision(uint32_t step)
    {
        double now=Simulator::Now().GetSeconds();
        std::array<std::array<double,5>,3> metrics;
        std::array<double,3> valid{},loss{},latency{};
        // Matured probe cohorts only. Arrival counts never substitute for loss.
        for(int n=0;n<3;++n)
        {
            int generated=0,received=0;double delay=0;
            for(auto it=records.rbegin();it!=records.rend();++it)
            {
                if(it->generated<now-.7)break;
                if(it->kind!=0||it->network!=n||it->generated>now-.2)continue;
                ++generated;
                if(it->received>=0&&it->received-it->generated<=it->deadline)
                {++received;delay+=1000*(it->received-it->generated);}
            }
            loss[n]=generated?1.-double(received)/generated:1.;
            latency[n]=received?delay/received:1000.;valid[n]=received>0;
            double bandwidth=n==1?10.:20.;
            double efficiency=n==2?.45:.35;
            double capacity=bandwidth*efficiency*std::log2(1+std::pow(10.,std::clamp(sinr[n],-50.,80.)/10));
            // Capacity is a disclosed PHY-based estimate, not observed payload goodput.
            if(n==1)capacity=std::min(capacity,lteBackhaulMbps);
            capacity*=1-loss[n];
            if(now-signalTime[n]>.5)capacity=0.;
            metrics[n]={sinr[n],rx[n],latency[n],capacity,loss[n]};
        }
        auto pos=ue.Get(0)->GetObject<MobilityModel>()->GetPosition();
        std::ostringstream message;message<<std::setprecision(10);
        message<<"{\"step\":"<<step<<",\"time\":"<<step*period<<",\"current_net\":"<<serving
               <<",\"speed\":"<<Motion(step*period).second<<",\"altitude\":"<<pos.z
               <<",\"position\":["<<pos.x<<","<<pos.y<<","<<pos.z<<"],\"demand\":"<<Demand()<<",\"metrics\":[";
        for(int n=0;n<3;++n){if(n)message<<",";message<<"[";for(int k=0;k<5;++k){if(k)message<<",";message<<metrics[n][k];}message<<"]";}
        message<<"],\"delay_valid\":["<<valid[0]<<","<<valid[1]<<","<<valid[2]<<"],\"signal_age_s\":[";
        for(int n=0;n<3;++n){if(n)message<<",";message<<(signalTime[n]<0?1e9:std::max(0.,now-signalTime[n]));}
        message<<"],\"shadow_loss_db\":[";
        for(int n=0;n<3;++n){if(n)message<<",";message<<sceneModels[n]->ShadowLoss(pos);}
        message<<"]}";
        states<<message.str()<<"\n";states.flush();
        int target=serving;
        if(controller=="pipe")
        {
            std::cout<<"STATE "<<message.str()<<std::endl;
            NS_ABORT_MSG_IF(!(std::cin>>target),"Controller closed its action stream");
        }
        else if(controller=="fixed")target=fixedNetwork;
        else if(controller=="schedule")
        {NS_ABORT_MSG_IF(step>=schedule.size(),"Schedule shorter than mission");target=schedule[step];}
        NS_ABORT_MSG_IF(target<0||target>2,"Invalid network action");
        // A controller cannot start another migration during its own interruption.
        if(target!=serving&&now+1e-8>=blockedUntil)
        {++handovers;serving=target;blockedUntil=now+interruption;}
        if((step+1)*period<duration-1e-7)Simulator::Schedule(Seconds(period),&Mission::Decision,this,step+1);
    }

    Ipv4Address Backhaul(Ptr<Node> gateway,const std::string& subnet,const std::string& rate,double delay)
    {
        PointToPointHelper p;p.SetDeviceAttribute("DataRate",StringValue(rate));
        p.SetChannelAttribute("Delay",TimeValue(Seconds(delay)));
        auto dev=p.Install(gateway,server);Ipv4AddressHelper ip;ip.SetBase(subnet.c_str(),"255.255.255.0");
        return ip.Assign(dev).GetAddress(1);
    }

    Ptr<SceneLoss> ConfigureScene(int network)
    {
        auto scene=CreateObject<SceneLoss>();
        scene->obstructionDb=obstructionDb;scene->shadowDb=shadowDb;
        scene->shadowLengthM=shadowLengthM;scene->shadowCorrelation=shadowCorrelation;
        scene->sceneSeed=seed;scene->roofHeight=roofHeight;scene->linkIndex=network;
        sceneModels[network]=scene;
        return scene;
    }

    void Setup()
    {
        RngSeedManager::SetSeed(12345);RngSeedManager::SetRun(seed);
        if(randomize){auto r=CreateObject<UniformRandomVariable>();r->SetStream(10);offsetX=r->GetValue(-30,30);offsetY=r->GetValue(-30,30);offsetZ=r->GetValue(-10,10);}
        ue.Create(3);sites.Create(3);server=CreateObject<Node>();
        MobilityHelper mobile;mobile.SetMobilityModel("ns3::ConstantVelocityMobilityModel");mobile.Install(ue);
        MobilityHelper fixed;fixed.SetMobilityModel("ns3::ConstantPositionMobilityModel");fixed.Install(sites);
        for(int n=0;n<3;++n){auto p=mission_config::sites[n];sites.Get(n)->GetObject<MobilityModel>()->SetPosition(Vector(p[0],p[1],p[2]));}
        Position();InternetStackHelper internet;internet.Install(ue);internet.Install(server);internet.Install(sites.Get(2));
        Ipv4StaticRoutingHelper routes;
        // Wi-Fi uplink and a routed connection to the same destination server.
        YansWifiChannelHelper channel;channel.SetPropagationDelay("ns3::ConstantSpeedPropagationDelayModel");
        channel.AddPropagationLoss("ns3::LogDistancePropagationLossModel","Exponent",DoubleValue(3.),"ReferenceLoss",DoubleValue(40.));
        auto wifiChannel=channel.Create();
        // YansWifiChannel exposes its loss chain through the setter; use the
        // same engineering log-distance law as its primary propagation model.
        auto wifiLoss=CreateObject<LogDistancePropagationLossModel>();wifiLoss->SetAttribute("Exponent",DoubleValue(mission_config::pathloss[2]));wifiLoss->SetAttribute("ReferenceLoss",DoubleValue(mission_config::reference_loss[2]));
        auto wifiScene=ConfigureScene(2);
        wifiLoss->SetNext(wifiScene);wifiChannel->SetPropagationLossModel(wifiLoss);
        YansWifiPhyHelper phy;phy.SetChannel(wifiChannel);
        phy.Set("TxPowerStart",DoubleValue(20));phy.Set("TxPowerEnd",DoubleValue(20));
        phy.Set("ChannelSettings",StringValue("{1, 20, BAND_2_4GHZ, 0}"));
        WifiHelper wifi;wifi.SetStandard(WIFI_STANDARD_80211n);wifi.SetRemoteStationManager("ns3::MinstrelHtWifiManager");
        WifiMacHelper mac;Ssid ssid("mission-v2");
        mac.SetType("ns3::ApWifiMac","Ssid",SsidValue(ssid));auto ap=wifi.Install(phy,mac,sites.Get(2));
        mac.SetType("ns3::StaWifiMac","Ssid",SsidValue(ssid));auto sta=wifi.Install(phy,mac,ue.Get(2));
        wifi.AssignStreams(ap,100);wifi.AssignStreams(sta,200);
        Ipv4AddressHelper ip;ip.SetBase("10.1.0.0","255.255.255.0");NetDeviceContainer w;w.Add(ap);w.Add(sta);auto wi=ip.Assign(w);
        auto wr=routes.GetStaticRouting(ue.Get(2)->GetObject<Ipv4>());wr->SetDefaultRoute(wi.GetAddress(0),1);
        destinations[2]=Backhaul(sites.Get(2),"10.2.0.0","100Mbps",.001);
        DynamicCast<WifiNetDevice>(ap.Get(0))->GetPhy()->TraceConnectWithoutContext("MonitorSnifferRx",MakeCallback(&Mission::WifiSignal,this));
        // LTE/EPC, with a declared six-Mbps shared backhaul limit.
        auto epc=CreateObject<PointToPointEpcHelper>();lte=CreateObject<LteHelper>();lte->SetEpcHelper(epc);
        lte->SetEnbDeviceAttribute("DlBandwidth",UintegerValue(50));lte->SetEnbDeviceAttribute("UlBandwidth",UintegerValue(50));
        lte->SetAttribute("PathlossModel",TypeIdValue(LogDistancePropagationLossModel::GetTypeId()));
        lte->SetPathlossModelAttribute("Exponent",DoubleValue(mission_config::pathloss[1]));lte->SetPathlossModelAttribute("ReferenceLoss",DoubleValue(mission_config::reference_loss[1]));
        auto enb=lte->InstallEnbDevice(NodeContainer(sites.Get(1)));auto ld=lte->InstallUeDevice(NodeContainer(ue.Get(1)));
        auto lteScene=ConfigureScene(1);
        lte->GetUplinkSpectrumChannel()->AddPropagationLossModel(lteScene);
        lte->AssignStreams(enb,300);lte->AssignStreams(ld,400);epc->AssignUeIpv4Address(ld);
        routes.GetStaticRouting(ue.Get(1)->GetObject<Ipv4>())->SetDefaultRoute(epc->GetUeDefaultGatewayAddress(),1);
        lte->Attach(ld.Get(0),enb.Get(0));
        destinations[1]=Backhaul(epc->GetPgwNode(),"11.1.0.0",std::to_string(lteBackhaulMbps)+"Mbps",.005);
        DynamicCast<LteUeNetDevice>(ld.Get(0))->GetPhy()->TraceConnectWithoutContext("ReportCurrentCellRsrpSinr",MakeCallback(&Mission::LteSignal,this));
        DynamicCast<LteEnbNetDevice>(enb.Get(0))->GetPhy()->TraceConnectWithoutContext("ReportUeSinr",MakeCallback(&Mission::LteUplinkSinr,this));
        // Real 5G-LENA NR stack with an explicit SISO engineering channel.
        // Avoid extrapolating terrestrial TR38.901 UE-height formulas to 100 m.
        auto nrEpc=CreateObject<NrPointToPointEpcHelper>();nr=CreateObject<NrHelper>();nr->SetEpcHelper(nrEpc);
        auto bf=CreateObject<IdealBeamformingHelper>();bf->SetAttribute("BeamformingMethod",TypeIdValue(DirectPathBeamforming::GetTypeId()));nr->SetBeamformingHelper(bf);
        nr->SetUePhyAttribute("TxPower",DoubleValue(nrTxDbm));
        nr->SetGnbAntennaAttribute("NumRows",UintegerValue(2));nr->SetGnbAntennaAttribute("NumColumns",UintegerValue(2));
        nr->SetUeAntennaAttribute("NumRows",UintegerValue(1));nr->SetUeAntennaAttribute("NumColumns",UintegerValue(1));
        CcBwpCreator creator;CcBwpCreator::SimpleOperationBandConf bandConf(3.5e9,20e6,1);
        auto band=creator.CreateOperationBandContiguousCc(bandConf);
        auto spectrum=CreateObject<MultiModelSpectrumChannel>();
        auto nrLoss=CreateObject<LogDistancePropagationLossModel>();nrLoss->SetAttribute("Exponent",DoubleValue(mission_config::pathloss[0]));nrLoss->SetAttribute("ReferenceLoss",DoubleValue(mission_config::reference_loss[0]));
        auto nrScene=ConfigureScene(0);
        // Match NrChannelHelper's zero propagation-delay scheduling convention.
        nrLoss->SetNext(nrScene);spectrum->AddPropagationLossModel(nrLoss);
        auto bwps=CcBwpCreator::GetAllBwps({band});bwps.at(0).get()->SetChannel(spectrum);
        auto gd=nr->InstallGnbDevice(NodeContainer(sites.Get(0)),bwps);
        auto nd=nr->InstallUeDevice(NodeContainer(ue.Get(0)),bwps);nr->AssignStreams(gd,500);nr->AssignStreams(nd,600);
        NrHelper::GetGnbPhy(gd.Get(0),0)->SetAttribute("Numerology",UintegerValue(1));
        NrHelper::GetGnbPhy(gd.Get(0),0)->SetAttribute("TxPower",DoubleValue(30.));
        nrEpc->AssignUeIpv4Address(nd);routes.GetStaticRouting(ue.Get(0)->GetObject<Ipv4>())->SetDefaultRoute(nrEpc->GetUeDefaultGatewayAddress(),1);
        nr->AttachToClosestGnb(nd,gd);
        destinations[0]=Backhaul(nrEpc->GetPgwNode(),"12.1.0.0","100Mbps",.001);
        NrHelper::GetGnbPhy(gd.Get(0),0)->TraceConnectWithoutContext("UlSinrTrace",MakeCallback(&Mission::NrUplinkSinr,this));
        NrHelper::GetUePhy(nd.Get(0),0)->TraceConnectWithoutContext("ReportRsrp",MakeCallback(&Mission::NrRsrp,this));
        auto sink=Socket::CreateSocket(server,UdpSocketFactory::GetTypeId());sink->Bind(InetSocketAddress(Ipv4Address::GetAny(),9000));sink->SetRecvCallback(MakeCallback(&Mission::Receive,this));
        for(int n=0;n<3;++n)
        {
            send[n]=Socket::CreateSocket(ue.Get(n),UdpSocketFactory::GetTypeId());
            send[n]->Connect(InetSocketAddress(destinations[n],9000));
            Simulator::Schedule(Seconds(.8),&Mission::Probe,this,n);
        }
        if(controller=="schedule")
        {std::ifstream f(scheduleFile);int net;while(f>>net)schedule.push_back(net);NS_ABORT_MSG_IF(schedule.empty(),"Empty schedule");}
        states.open(output+".states.jsonl");NS_ABORT_MSG_IF(!states,"Cannot open state output");
        Simulator::Schedule(Seconds(warmup),&Mission::Decision,this,0);
        Simulator::Schedule(Seconds(warmup+.001),&Mission::Telemetry,this);
        Simulator::Schedule(Seconds(warmup+.002),&Mission::Video,this);
    }

    void Finish()
    {
        std::ofstream csv(output);csv<<"id,network,kind,generated_s,received_s,deadline_s,bytes,on_time,interruption_drop\n";
        uint64_t bytes=0;int tele=0,teleOk=0,video=0,videoOk=0;
        for(size_t id=0;id<records.size();++id)
        {
            auto&r=records[id];bool ontime=r.received>=0&&r.received-r.generated<=r.deadline+1e-8;
            csv<<id<<","<<r.network<<","<<r.kind<<","<<std::setprecision(12)<<r.generated-warmup<<","<<(r.received<0?-1:r.received-warmup)<<","<<r.deadline<<","<<r.bytes<<","<<ontime<<","<<r.interruption<<"\n";
            if(r.kind==1){++tele;teleOk+=ontime;}
            if(r.kind==2){++video;videoOk+=ontime;if(ontime)bytes+=r.bytes;}
        }
        std::cout<<"SUMMARY {\"handovers\":"<<handovers<<",\"telemetry_packets\":"<<tele<<",\"telemetry_on_time\":"<<teleOk
                 <<",\"video_packets\":"<<video<<",\"video_on_time\":"<<videoOk<<",\"video_on_time_mbps\":"<<bytes*8./duration/1e6<<"}"<<std::endl;
    }
};

int main(int argc,char**argv)
{
    Mission m;CommandLine cmd;
    cmd.AddValue("seed","External random run",m.seed);cmd.AddValue("duration","Mission seconds excluding warmup/drain",m.duration);
    cmd.AddValue("period","Decision seconds",m.period);cmd.AddValue("warmup","Stationary link warmup",m.warmup);
    cmd.AddValue("interruption","Application migration interruption, not measured protocol delay",m.interruption);
    cmd.AddValue("imagingMbps","Shared upstream video demand during imaging",m.imagingMbps);
    cmd.AddValue("nrTxDbm","NR UE transmit power",m.nrTxDbm);cmd.AddValue("lteBackhaulMbps","LTE backhaul allocation",m.lteBackhaulMbps);
    cmd.AddValue("obstructionDb","Loss for a ray intersecting the declared building",m.obstructionDb);cmd.AddValue("shadowDb","Policy-independent spatial shadow field strength",m.shadowDb);
    cmd.AddValue("shadowLengthM","Spatial shadow scale in meters",m.shadowLengthM);
    cmd.AddValue("shadowCorrelation","Shared shadow mixing power fraction",m.shadowCorrelation);
    cmd.AddValue("buildingHeight","Roof height for geometry sensitivity",m.roofHeight);
    cmd.AddValue("randomize","Initial position/height perturbation",m.randomize);
    cmd.AddValue("output","Packet CSV path",m.output);cmd.AddValue("controller","pipe|fixed|schedule",m.controller);
    cmd.AddValue("fixedNetwork","Fixed network index",m.fixedNetwork);cmd.AddValue("scheduleFile","Integer actions for schedule control",m.scheduleFile);
    cmd.Parse(argc,argv);
    NS_ABORT_MSG_IF(m.shadowLengthM<=0||m.shadowCorrelation<0||m.shadowCorrelation>1||m.shadowDb<0,"Invalid spatial shadow parameters");
    m.Setup();Simulator::Stop(Seconds(m.warmup+m.duration+1.));Simulator::Run();m.Finish();Simulator::Destroy();
}
