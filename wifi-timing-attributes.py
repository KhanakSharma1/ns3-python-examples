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

# This example shows how to set Wi-Fi timing parameters through WifiMac attributes.
# 
# Example: set slot time to 20 microseconds, while keeping other values as defined in the simulation script:
#
#          ./waf --pyrun "examples/wireless/wifi-timing-attributes.py --slot=20"
#
# Network topology:
#
#  Wifi 192.168.1.0
#
#       AP
#  *    *
#  |    |
#  n1   n2

def main (argv):
    cmd = ns.core.CommandLine ()
    cmd.slot = 9 # slot time in microseconds
    cmd.sifs = 10 # SIFS duration in microseconds
    cmd.ackTimeout = 88 # ACK timeout duration in microseconds
    cmd.ctsTimeout = 88 # CTS timeout duration in microseconds
    cmd.rifs = 2 # RIFS duration in microseconds
    cmd.basicBlockAckTimeout = 286 # Basic Block ACK timeout duration in microseconds
    cmd.compressedBlockAckTimeout = 112 # Compressed Block ACK timeout duration in microseconds
    cmd.simulationTime = 10 # simulation time in seconds
        
    cmd.AddValue ("slot", "Slot time in microseconds")
    cmd.AddValue ("sifs", "SIFS duration in microseconds")
    cmd.AddValue ("ackTimeout", "ACK timeout duration in microseconds")
    cmd.AddValue ("ctsTimeout", "CTS timeout duration in microseconds")
    cmd.AddValue ("rifs", "RIFS duration in microseconds")
    cmd.AddValue ("basicBlockAckTimeoutTimeout", "Basic Block ACK timeout duration in microseconds")
    cmd.AddValue ("compressedBlockAckTimeoutTimeout", "Compressed Block ACK timeout duration in microseconds")
    cmd.AddValue ("simulationTime", "Simulation time in seconds")
    cmd.Parse (sys.argv);

    slot = int (cmd.slot)
    sifs = int (cmd.sifs)
    nMpdusackTimeout = int (cmd.ackTimeout)
    ctsTimeout = int (cmd.ctsTimeout)
    rifs = int (cmd.rifs)
    basicBlockAckTimeout = int (cmd.basicBlockAckTimeout)
    compressedBlockAckTimeout = int (cmd.compressedBlockAckTimeout)
    simulationTime = cmd.simulationTime
    
    #Since default reference loss is defined for 5 GHz, it needs to be changed when operating at 2.4 GHz
    ns.core.Config.SetDefault ("ns3::LogDistancePropagationLossModel::ReferenceLoss", ns.core.DoubleValue (40.046))    
    
    #Create nodes
    wifiStaNodes = ns.network.NodeContainer ()
    wifiStaNodes.Create (1)
    wifiApNode = ns.network.NodeContainer ()
    wifiApNode.Create (1)
    
    #Create wireless channel
    channel = ns.wifi.YansWifiChannelHelper.Default ()
    phy = ns.wifi.YansWifiPhyHelper.Default ()
    phy.SetChannel (channel.Create ()) # wireless range limited to 5 meters!

    
    #Default IEEE 802.11n (2.4 GHz)
    wifi = ns.wifi.WifiHelper.Default ()
    wifi.SetStandard (ns.wifi.WIFI_PHY_STANDARD_80211n_2_4GHZ)
    wifi.SetRemoteStationManager ("ns3::ConstantRateWifiManager", "DataMode", ns.core.StringValue ("HtMcs7"), "ControlMode", ns.core.StringValue ("HtMcs0"))
    mac = ns.wifi.HtWifiMacHelper.Default ()


    #Install PHY and MAC
    ssid = ns.wifi.Ssid ("ns3-wifi")
    mac.SetType ("ns3::StaWifiMac",
                "Ssid", ns.wifi.SsidValue (ssid))


    staDevices = ns.network.NetDeviceContainer ()
    staDevices = wifi.Install (phy, mac, wifiStaNodes)

    mac.SetType ("ns3::ApWifiMac",
                "Ssid", ns.wifi.SsidValue (ssid))

    apDevice = ns.network.NetDeviceContainer ()
    apDevice = wifi.Install (phy, mac, wifiApNode)


    #Once install is done, we overwrite the standard timing values
    ns.core.Config.Set ("/NodeList/*/DeviceList/*/$ns3::WifiNetDevice/Mac/Slot", ns.core.TimeValue (ns.core.MicroSeconds (slot)))
    ns.core.Config.Set ("/NodeList/*/DeviceList/*/$ns3::WifiNetDevice/Mac/Sifs", ns.core.TimeValue (ns.core.MicroSeconds (sifs)))
    ns.core.Config.Set ("/NodeList/*/DeviceList/*/$ns3::WifiNetDevice/Mac/AckTimeout", ns.core.TimeValue (ns.core.MicroSeconds (ackTimeout)))
    ns.core.Config.Set ("/NodeList/*/DeviceList/*/$ns3::WifiNetDevice/Mac/CtsTimeout", ns.core.TimeValue (ns.core.MicroSeconds (ctsTimeout)))
    ns.core.Config.Set ("/NodeList/*/DeviceList/*/$ns3::WifiNetDevice/Mac/Rifs", ns.core.TimeValue (ns.core.MicroSeconds (rifs)))
    ns.core.Config.Set ("/NodeList/*/DeviceList/*/$ns3::WifiNetDevice/Mac/BasicBlockAckTimeout", ns.core.TimeValue (ns.core.MicroSeconds (basicBlockAckTimeout)))
    ns.core.Config.Set ("/NodeList/*/DeviceList/*/$ns3::WifiNetDevice/Mac/compressedBlockAckTimeout", ns.core.TimeValue (ns.core.MicroSeconds (compressedBlockAckTimeout)))

    #Mobility
    mobility = ns.mobility.MobilityHelper ()
    positionAlloc = ns.mobility.ListPositionAllocator ()

    positionAlloc.Add (ns.core.Vector3D (0.0, 0.0, 0.0))
    positionAlloc.Add (ns.core.Vector3D (1.0, 0.0, 0.0))
    mobility.SetPositionAllocator (positionAlloc)

    mobility.SetMobilityModel ("ns3::ConstantPositionMobilityModel")
    mobility.Install (wifiApNode)
    mobility.Install (wifiStaNodes)

    #Internet stack
    stack = ns.internet.InternetStackHelper ()
    stack.Install (wifiApNode)
    stack.Install (wifiStaNodes)

    address = ns.internet.Ipv4AddressHelper ()
    address.SetBase (ns.network.Ipv4Address ("192.168.1.0"), ns.network.Ipv4Mask ("255.255.255.0"))

    staNodeInterface = ns.internet.Ipv4InterfaceContainer ()
    staNodeInterface = address.Assign (staDevices)

    apNodeInterface = ns.internet.Ipv4InterfaceContainer ()
    apNodeInterface = address.Assign (apDevice)

    #Setting applications
    port = 9 
    server = ns.applications.UdpServerHelper (port)
    serverApp = server.Install (wifiStaNode.Get (0))
    serverApp.Start (ns.core.Seconds (0.0))
    serverApp.Stop (ns.core.Seconds (simulationTime + 1))
      
    client = ns.applications.UdpClientHelper (staNodeInterface.GetAddress (0), port)
    client.SetAttribute ("MaxPackets", ns.core.UintegerValue (4294967295))
    client.SetAttribute ("Interval", ns.core.TimeValue (ns.core.Time ("0.00001")))#packets/s
    client.SetAttribute ("PacketSize", ns.core.UintegerValue (1472))#bytes
  
    clientApp = client.Install (wifiApNode.Get (0))
    clientApp.Start (ns.core.Seconds (1.0))
    clientApp.Stop (ns.core.Seconds (simulationTime + 1))
    
    #Populate routing table
    #need to be done ###############
    ns.internet.Ipv4GlobalRoutingHelper.PopulateRoutingTables()

    #Set simulation time and launch simulation
    ns.core.Simulator.Stop (ns.core.Seconds (simulationTime + 1))
    ns.core.Simulator.Run ()
    
      
    totalPacketsThrough = serverApp.Get (0).GetReceived ()
    throughput = totalPacketsThrough * 1472 * 8 / (simulationTime * 1000000.0) # Mbit/s
    print ("Throughput:", throughput,"Mbit/s")
  
    ns.core.Simulator.Destroy ()

    return 0

if __name__ == '__main__':
    import sys
    sys.exit (main (sys.argv))