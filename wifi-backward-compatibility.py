import ns.core
import ns.network
import ns.applications
import ns.wifi
import ns.mobility
import ns.internet

wifi = ns.wifi.WifiHelper.Default ()

def convertstringtostandard (stringversion):
    standard = ns.wifi.WifiPhyStandard
    if stringversion == "80211a":
        standard = ns.wifi.WIFI_PHY_STANDARD_80211a

    elif stringversion =="80211b":
        standard = ns.wifi.WIFI_PHY_STANDARD_80211b

    elif stringversion == "80211g":
        standard = ns.wifi.WIFI_PHY_STANDARD_80211g

    elif stringversion == "80211_10Mhz":
        standard = ns.wifi.WIFI_PHY_STANDARD_80211_10MHZ

    elif stringversion == "80211_5Mhz":
        standard = ns.wifi.WIFI_PHY_STANDARD_80211_5MHZ

    elif stringversion == "holland":
        standard = ns.wifi.WIFI_PHY_STANDARD_holland

    elif stringversion == "80211n_2_4GHZ":
        standard = ns.wifi.WIFI_PHY_STANDARD_80211n_2_4GHZ

    elif stringversion == "80211n_5GHZ":
        standard = ns.wifi.WIFI_PHY_STANDARD_80211n_5GHZ                      

    elif stringversion == "80211ac":
        standard = ns.wifi.WIFI_PHY_STANDARD_80211ac

    else
        standard = ns.wifi.WIFI_PHY_STANDARD_UNSPECIFIED

    return standard


def main(argv):
    payloadSize = 1472 # Bytes
    cmd = ns.core.CommandLine()
    cmd.simulationTime = 9  # seconds
    cmd.apVersion = "80211a"  #
    cmd.staVersion = "80211n_5GHZ"; #
    cmd.apRaa = "Minstrel"  #
    cmd.staRaa = "MinstrelHt"  #
    cmd.apHasTraffic = 0 # Enable/disable traffic on the AP
    cmd.staHasTraffic = 1 # Enable/disable traffic on the Station

    cmd.AddValue("simulationTime", "Simulation time in seconds")
    cmd.AddValue("apVersion", "The standard version used by the AP: 80211a, 80211b, 80211g, 80211_10MHZ, 80211_5MHZ, holland, 80211n_2_4GHZ, 80211n_5GHZ or 80211ac")
    cmd.AddValue("staVersion", "The standard version used by the station: 80211a, 80211b, 80211g, 80211_10MHZ, 80211_5MHZ, holland, 80211n_2_4GHZ, 80211n_5GHZ or 80211ac")
    cmd.AddValue("apRaa", "Rate adaptation algorithm used by the AP")
    cmd.AddValue("staRaa", "Rate adaptation algorithm used by the station")
    cmd.AddValue("apHasTraffic", "Enable/disable traffic on the AP")
    cmd.AddValue("staHasTraffic", "Enable/disable traffic on the station")
    cmd.Parse(sys.argv)


    simulationTime = float(cmd.simulationTime)
    apVersion: str = cmd.apVersion
    staVersion: str = cmd.staVersion
    apRaa: str = cmd.apRaa
    staRaa: str =  cmd.staRaa
    apHasTraffic = cmd.apHasTraffic
    staHasTraffic = cmd.staHasTraffic


    # Create nodes
    wifiStaNodes = ns.network.NodeContainer()
    wifiStaNodes.Create(1)
    wifiApNode = ns.network.NodeContainer()
    wifiApNode.Create(1)

    # Create wireless channel
    channel = ns.wifi.YansWifiChannelHelper.Default()
    phy = ns.wifi.YansWifiPhyHelper.Default()
    phy.SetChannel(channel.Create())  # wireless range limited to 5 meters!

    # Default IEEE 802.11n (2.4 GHz)
    mac = ns.wifi.HtWifiMacHelper.Default()
    wifi = ns.wifi.WifiHelper.Default()
    ssid = ns.wifi.Ssid("ns3")

    wifi.SetStandard(convertstringtostandard(staVersion))
    wifi.SetRemoteStationManager("ns3::" + staRaa + "WifiManager")

    # Install PHY and MAC

    mac.SetType("ns3::StaWifiMac", "Ssid", ns.wifi.SsidValue(ssid))

    staDevices = ns.network.NetDeviceContainer()
    staDevices = wifi.Install(phy, mac, wifiStaNodes)

    mac.SetType("ns3::ApWifiMac", "Ssid", ns.wifi.SsidValue(ssid))

    apDevice = ns.network.NetDeviceContainer()
    apDevice = wifi.Install(phy, mac, wifiApNode)

    #  Workaround needed as long as we do not fully support channel bonding
    if staVersion == "80211ac":
        ns.core.Config.Set ("/NodeList/*/DeviceList/*/$ns3::WifiNetDevice/Phy/ChannelWidth", ns.core.UintegerValue (20))
        ns.core.Config.Set("/NodeList/0/DeviceList/*/$ns3::WifiNetDevice/Phy/Frequency", ns.core.UintegerValue(5180))

    if apVersion =="80211ac":
        ns.core.Config.Set("/NodeList/*/DeviceList/*/$ns3::WifiNetDevice/Phy/ChannelWidth", ns.core.UintegerValue(20))
        ns.core.Config.Set("/NodeList/0/DeviceList/*/$ns3::WifiNetDevice/Phy/Frequency", ns.core.UintegerValue(5180))

    # Mobility
    mobility = ns.mobility.MobilityHelper()
    positionAlloc = ns.mobility.ListPositionAllocator()

    positionAlloc.Add(ns.core.Vector3D(0.0, 0.0, 0.0))
    positionAlloc.Add(ns.core.Vector3D(5.0, 0.0, 0.0))
    mobility.SetPositionAllocator(positionAlloc)

    mobility.SetMobilityModel("ns3::ConstantPositionMobilityModel")
    mobility.Install(wifiApNode)
    mobility.Install(wifiStaNodes)

    # Internet stack
    stack = ns.internet.InternetStackHelper()
    stack.Install(wifiApNode)
    stack.Install(wifiStaNodes)

    address = ns.internet.Ipv4AddressHelper()
    address.SetBase(ns.network.Ipv4Address("192.168.1.0"), ns.network.Ipv4Mask("255.255.255.0"))

    staNodeInterface = ns.internet.Ipv4InterfaceContainer()
    staNodeInterface = address.Assign(staDevices)

    apNodeInterface = ns.internet.Ipv4InterfaceContainer()
    apNodeInterface = address.Assign(apDevice)

    # Setting applications

    apServer = ns.applications.UdpServerHelper(9) # AP server port
    apserverApp = apServer.Install(wifiStaNodes.Get(0))
    apserverApp.Start(ns.core.Seconds(0.0))
    apserverApp.Stop(ns.core.Seconds(simulationTime + 1))

    staServer = ns.applications.UdpServerHelper(5001) # Station server port
    staServerApp = staServer.Install(wifiStaNodes.Get(0))
    staServerApp.Start(ns.core.Seconds(0.0));
    staServerApp.Stop(ns.core.Seconds(simulationTime + 1));

    if apHasTraffic == 1:
        apClient = ns.applications.UdpClientHelper(staNodeInterface.GetAddress(0), 5001);
        apClient.SetAttribute("MaxPackets", ns.core.UintegerValue(4294967295))
        apClient.SetAttribute("Interval", ns.core.TimeValue(ns.core.Time("0.00001"))) # Packets / Second
        apClient.SetAttribute("PacketSize", ns.core.UintegerValue(payloadSize)) # Bytes
        apClientApp = apClient.Install(wifiApNode.Get(0))
        apClientApp.Start(ns.core.Seconds(1.0))
        apClientApp.Stop(ns.core.Seconds(simulationTime + 1))

    if staHasTraffic == 1:
        staClient = ns.applications.UdpClientHelper(apNodeInterface.GetAddress(0), 9)
        staClient.SetAttribute("MaxPackets", ns.core.UintegerValue(4294967295))
        staClient.SetAttribute("Interval", ns.core.TimeValue(ns.core.Time("0.00001"))) # Packets / Second
        staClient.SetAttribute("PacketSize", ns.core.UintegerValue(payloadSize)) # Bytes
        staClientApp = staClient.Install(wifiStaNodes.Get(0))
        staClientApp.Start(ns.core.Seconds(1.0))
        staClientApp.Stop(ns.core.Seconds(simulationTime + 1))

    # Populate routing table
    ns.internet.Ipv4GlobalRoutingHelper.PopulateRoutingTables()

    # Set simulation time and launch simulation
    ns.core.Simulator.Stop(ns.core.Seconds(simulationTime + 1))
    ns.core.Simulator.Run()


    error = False

    if apHasTraffic == 1:
        rxBytes = payloadSize * (staServerApp.Get(0).GetReceived())
        throughput = (rxBytes * 8) / (simulationTime * 1000000.0); # Mbit / s
        print("AP Throughput:", throughput, "Mbit/s")

        if throughput == 0:
            error = True

    if staHasTraffic == 1:
        rxBytes = payloadSize * (apServerApp.Get(0)).GetReceived()
        throughput = (rxBytes * 8) / (simulationTime * 1000000.0) # Mbit / s
        print("STA Throughput:", throughput, "Mbit/s")

        if throughput == 0:
                error = True

        ns.core.Simulator.Destroy()
    if error == True:
        sys.exit(1)

    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))