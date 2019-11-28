# -*-  Mode: Python; -*-
# /*
#  * Copyright (c) 2019 NITK Surathkal
#  *
#  * This program is free software; you can redistribute it and/or modify
#  * it under the terms of the GNU General Public License version 2 as
#  * published by the Free Software Foundation;
#  *
#  * This program is distributed in the hope that it will be useful,
#  * but WITHOUT ANY WARRANTY; without even the implied warranty of
#  * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  * GNU General Public License for more details.
#  *
#  * You should have received a copy of the GNU General Public License
#  * along with this program; if not, write to the Free Software
#  * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#  *
#  * Ported to Python by: Sravani Mothe  <vpsravanitm909@gmail.com>
#  *                      KhanakSharma <vskhanaksharma@gmail.com>
#  */

import ns.core
import ns.applications
import ns.wifi
import ns.mobility
import ns.internet

# This is a simple example in order to show how to configure an IEEE 802.11ac Wi-Fi network.
#
# It ouputs the UDP or TCP goodput for every VHT bitrate value, which depends on the MCS value (0 to 9, where 9 is
# forbidden when the channel width is 20 MHz), the channel width (20, 40, 80 or 160 MHz) and the guard interval (long
# or short). The PHY bitrate is constant over all the simulation run. The user can also specify the distance between
# the access point and the station: the larger the distance the smaller the goodput.
#
# The simulation assumes a single station in an infrastructure network:
#
#  STA     AP
#    *     *
#    |     |
#   n1     n2
#
# Packets in this simulation aren't marked with a QosTag so they are considered
# belonging to BestEffort Access Class (AC_BE).

def main(argv):
    cmd = ns.core.CommandLine ()
    cmd.udp = "True"
    cmd.useRts = "False"
    cmd.useExtendedBlockAck = "False";
    cmd.simulationTime = 10 # seconds
    cmd.distance = 1.0 # meters
    cmd.frequency = 5.0 # whether 2.4 or 5.0 GHz
    cmd.mcs = -1 # -1 indicates an unset value
    cmd.minExpectedThroughput = 0
    cmd.maxExpectedThroughput = 0
    cmd.minMcs = 0
    cmd.maxMcs = 11

    cmd.AddValue ("frequency", "Whether working in the 2.4 or 5.0 GHz band (other values gets rejected)")
    cmd.AddValue ("distance", "Distance in meters between the station and the access point")
    cmd.AddValue ("simulationTime", "Simulation time in seconds")
    cmd.AddValue ("udp", "UDP if set to 1, TCP otherwise")
    cmd.AddValue ("useExtendedBlockAck", "Enable/disable use of extended BACK")   
    cmd.AddValue ("mcs", "if set, limit testing to a specific MCS (0-11)")
    cmd.AddValue ("minExpectedThroughput", "if set, simulation fails if the lowest throughput is below this value")
    cmd.AddValue ("maxExpectedThroughput", "if set, simulation fails if the highest throughput is above this value")
    cmd.Parse (sys.argv)

    udp = cmd.udp
    useRts = cmd.useRts
    simulationTime = float(cmd.simulationTime)
    distance = float(cmd.distance)
    frequency = double(cmd.frequency)
    mcs = int(cmd.mcs)
    minExpectedThroughput = double(cmd.minExpectedThroughput)
    maxExpectedThroughput = double(cmd.maxExpectedThroughput)

    if useRts == "True":
        ns.core.Config.SetDefault ("ns3::WifiRemoteStationManager::RtsCtsThreshold", ns.core.StringValue ("0"))

 
    for l in range(0,12):
        prevThroughput[l] = 0

    print "MCS value" , "\t\t", "Channel width", "\t\t", "short GI","\t\t","Throughput" ,'\n'

    minMcs = int (cmd.minMcs)
    maxMcs = int (cmd.maxMcs)

    if mcs >= 0 and mcs <= 11:
        minMcs = mcs
        maxMcs = mcs

    ChannelWidth = 20
    gi = 3200
    for mcs in range(minMcs, maxMcs+1): # MCS
        index = 0
        previous = 0
        if frequency == 2.4:
            maxChannelWidth = 40
        else:
            maxChannelWidth = 160
        while ChannelWidth <= maxChannelWidth: #MHz
            while gi >= 800: #Nanoseconds
                if udp == "True": # 1500 byte IP packet
                    payloadSize = 1472 # bytes
                else:
                    payloadSize = 1448 # bytes
                    ns.core.Config.SetDefault ("ns3::TcpSocket::SegmentSize", ns.core.UintegerValue (payloadSize))

                wifiStaNode = ns.network.NodeContainer ()
                wifiStaNode.Create (1)
                wifiApNode = ns.network.NodeContainer ()
                wifiApNode.Create (1)

                channel = ns.wifi.YansWifiChannelHelper.Default ()
                phy = ns.wifi.YansWifiPhyHelper.Default ()
                phy.SetChannel (channel.Create ())

                # Set guard interval
                #phy.Set ("GuardInterval", ns.core.TimeValue (ns.core.NanoSeconds(gi)))


                mac = ns.wifi.WifiMacHelper.Default ()
                wifi = ns.wifi.WifiHelper.Default ()

                if frequency == 5.0:
                    wifi.SetStandard (ns.wifi.WIFI_PHY_STANDARD_80211ax_5GHZ)
                elif frequency == 2.4:
                    wifi.SetStandard (ns.wifi.WIFI_PHY_STANDARD_80211ax_2_4GHZ)
                    ns.core.Config.SetDefault ("ns3::LogDistancePropagationLossModel::ReferenceLoss", ns.core.DoubleValue (40.046))
                else:
                    print("Wrong frequency value!")
                    return 0

                
                mcsstr = str(mcs)
                oss = "HeMcs" + mcsstr 
                wifi.SetRemoteStationManager ("ns3::ConstantRateWifiManager", "DataMode", ns.core.StringValue (oss),"ControlMode", ns.core.StringValue (oss))

                ssid = ns.wifi.Ssid ("ns3-80211ax")
                mac.SetType ("ns3::StaWifiMac","Ssid", ns.wifi.SsidValue (ssid))


                staDevice = wifi.Install (phy, mac, wifiStaNode)

                mac.SetType ("ns3::ApWifiMac","EnableBeaconJitter", BooleanValue (false),
                             "Ssid", ns.wifi.SsidValue (ssid))

                apDevice = wifi.Install (phy, mac, wifiApNode)

                # Set channel width, guard interval and MPDU buffer size
                ns.core.Config.Set ("/NodeList/*/DeviceList/*/$ns3::WifiNetDevice/Phy/ChannelWidth", ns.core.UintegerValue (channelWidth))
                ns.core.Config.Set ("/NodeList/*/DeviceList/*/$ns3::WifiNetDevice/HeConfiguration/GuardInterval", ns.core.TimeValue (gi))
                if useExtendedBlockAck == "True":
                    ns.core.Config.Set ("/NodeList/*/DeviceList/*/$ns3::WifiNetDevice/HeConfiguration/MpduBufferSize", ns.core.UintegerValue (256))
                else:
                    ns.core.Config.Set ("/NodeList/*/DeviceList/*/$ns3::WifiNetDevice/HeConfiguration/MpduBufferSize", ns.core.UintegerValue (64))
                


                # mobility
                mobility = ns.mobility.MobilityHelper ()
                positionAlloc = ns.mobility.ListPositionAllocator ()
                positionAlloc.Add (ns.core.Vector (0.0, 0.0, 0.0))
                positionAlloc.Add (ns.core.Vector (distance, 0.0, 0.0))
                mobility.SetPositionAllocator (positionAlloc)

                mobility.SetMobilityModel ("ns3::ConstantPositionMobilityModel")

                mobility.Install (wifiApNode)
                mobility.Install (wifiStaNode)

                # Internet stack
                stack = ns.internet.InternetStackHelper ()
                stack.Install (wifiApNode)
                stack.Install (wifiStaNode)

                address = ns.internet.Ipv4AddressHelper ()

                address.SetBase (ns.network.Ipv4Address ("192.168.1.0"), ns.network.Ipv4Mask ("255.255.255.0"))

                staNodeInterface = address.Assign (staDevice)
                apNodeInterface = address.Assign (apDevice)

                # Setting applications
                serverApp = ns.network.ApplicationContainer ()
                if udp == "True": # UDP flow
                    port = 9
                    server = ns.applications.UdpServerHelper (port)
                    serverApp = server.Install (ns.network.NodeContainer (wifiStaNode.Get (0)))
                    serverApp.Start (ns.core.Seconds (0.0))
                    serverApp.Stop (ns.core.Seconds (simulationTime + 1))

                    client = ns.applications.UdpClientHelper (staNodeInterface.GetAddress (0), port)
                    client.SetAttribute ("MaxPackets", ns.core.UintegerValue (4294967295))
                    client.SetAttribute ("Interval", ns.core.TimeValue (ns.core.Time ("0.00001")))  # packets/s
                    client.SetAttribute ("PacketSize", ns.core.UintegerValue (payloadSize))

                    clientApp = client.Install (ns.network.NodeContainer (wifiApNode.Get (0)))
                    clientApp.Start (ns.core.Seconds (1.0))
                    clientApp.Stop (ns.core.Seconds (simulationTime + 1))
                else: # TCP flow
                    port = 50000
                    localAddress = ns.network.Address (ns.network.InetSocketAddress (ns.network.Ipv4Address.GetAny (), port))
                    packetSinkHelper = ns.applications.PacketSinkHelper ("ns3::TcpSocketFactory", localAddress)
                    serverApp = packetSinkHelper.Install (wifiStaNode.Get (0))
                    serverApp.Start (ns.core.Seconds (0.0))
                    serverApp.Stop (ns.core.Seconds (simulationTime + 1))

                    onoff = ns.applications.OnOffHelper ("ns3::TcpSocketFactory", ns.network.Ipv4Address.GetAny ())
                    onoff.SetAttribute ("OnTime",  ns.core.StringValue ("ns3::ConstantRandomVariable[Constant=1]"))
                    onoff.SetAttribute ("OffTime", ns.core.StringValue ("ns3::ConstantRandomVariable[Constant=0]"))
                    onoff.SetAttribute ("PacketSize", ns.core.UintegerValue (payloadSize))
                    onoff.SetAttribute ("DataRate", ns.network.DataRateValue (ns.network.DataRate (1000000000))) # bit/s
                    remoteAddress = ns.network.AddressValue (ns.network.InetSocketAddress (staNodeInterface.GetAddress (0), port))
                    onoff.SetAttribute ("Remote", remoteAddress)

                    apps = ns.network.ApplicationContainer ()
                    apps.Add (onoff.Install (wifiApNode.Get (0)))
                    apps.Start (ns.core.Seconds (1.0))
                    apps.Stop (ns.core.Seconds (simulationTime + 1))

                ns.internet.Ipv4GlobalRoutingHelper.PopulateRoutingTables ()

                ns.core.Simulator.Stop (ns.core.Seconds (simulationTime + 1))
                ns.core.Simulator.Run ()
                

                rxBytes = 0
                if udp == "True":
                    # UDP
                    rxBytes = payloadSize * ((serverApp.Get (0)).GetReceived ())
                else:
                    # TCP
                    rxBytes = (serverApp.Get (0)).GetTotalRx ()

                throughput = (rxBytes * 8) / (simulationTime * 1000000.0)
                ns.core.Simulator.Destroy ()
                print mcs , "\t\t\t" , channelWidth , "MHz\t\t\t" , gi , "ns\t\t\t" , throughput , " Mbit/s"

                # test first element
                if mcs == 0 and ChannelWidth == 20 and gi == 3200:
                    if throughput <minExpectedThroughput:
                        print("Obtained throughput " , throughput , " is not expected!")
                        sys.exit(1)

                # test last element
                if mcs == 11 and ChannelWidth == 160 and  gi == 800:
                    if maxExpectedThroughput > 0  and throughput > maxExpectedThroughput:
                        print ("Obtained throughput " , throughput , " is not expected!")
                        sys.exit(1)

                # test previous throughput is smaller (for the same mcs)
                if throughput > previous:
                    previous = throughput
                else:
                    print ("Obtained throughput " , throughput , " is not expected!")
                    sys.exit(1)

                # test previous throughput is smaller (for the same channel width and GI)
                if throughput > prevThroughput[index]:
                    prevThroughput[index] = throughput
                else:
                    print ("Obtained throughput " , throughput , " is not expected!")
                    sys.exit(1)

                index = index + 1
                gi = gi/2
            ChannelWidth = ChannelWidth * 2

    return 0

if __name__ == '__main__':
    import sys
    sys.exit (main (sys.argv))
