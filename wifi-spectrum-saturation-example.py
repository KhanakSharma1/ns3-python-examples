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
import ns.network
import ns.applications
import ns.wifi
import ns.mobility
import ns.internet

'''
// This is a simple example of an IEEE 802.11n Wi-Fi network.
//
// The main use case is to enable and test SpectrumWifiPhy vs YansWifiPhy
// under saturation conditions (for max throughput).
//
// Network topology:
//
//  Wi-Fi 192.168.1.0
//
//   STA                  AP
//    * <-- distance -->  *
//    |                   |
//    n1                  n2
//
// Users may vary the following command-line arguments in addition to the
// attributes, global values, and default values typically available:
//
//    --simulationTime:  Simulation time in seconds [10]
//    --distance:        meters separation between nodes [50]
//    --index:           restrict index to single value between 0 and 31 [256]
//    --wifiType:        select ns3::SpectrumWifiPhy or ns3::YansWifiPhy [ns3::SpectrumWifiPhy]
//    --errorModelType:  select ns3::NistErrorRateModel or ns3::YansErrorRateModel [ns3::NistErrorRateModel]
//    --enablePcap:      enable pcap output [false]
//
// By default, the program will step through 64 index values, corresponding
// to the following MCS, channel width, and guard interval combinations:
//   index 0-7:    MCS 0-7, long guard interval, 20 MHz channel
//   index 8-15:   MCS 0-7, short guard interval, 20 MHz channel
//   index 16-23:  MCS 0-7, long guard interval, 40 MHz channel
//   index 24-31:  MCS 0-7, short guard interval, 40 MHz channel
//   index 32-39:    MCS 8-15, long guard interval, 20 MHz channel
//   index 40-47:   MCS 8-15, short guard interval, 20 MHz channel
//   index 48-55:  MCS 8-15, long guard interval, 40 MHz channel
//   index 56-63:  MCS 8-15, short guard interval, 40 MHz channel
// and send packets at a high rate using each MCS, using the SpectrumWifiPhy
// and the NistErrorRateModel, at a distance of 1 meter.  The program outputs
// results such as:
//
// wifiType: ns3::SpectrumWifiPhy distance: 1m
// index   MCS   width Rate (Mb/s) Tput (Mb/s) Received
//     0     0      20       6.5     5.96219    5063
//     1     1      20        13     11.9491   10147
//     2     2      20      19.5     17.9184   15216
//     3     3      20        26     23.9253   20317
//     ...
//
// selection of index values 32-63 will result in MCS selection 8-15
// involving two spatial streams

'''

def main(argv):
    channelWidth = 0
    cmd = ns.core.CommandLine()
    cmd.simulationTime = 10  # seconds
    cmd.distance = 1.0
    cmd.index = 256
    cmd.wifiType = "ns3::SpectrumWifiPhy"
    cmd.errorModelType = "ns3::NistErrorRateModel"
    cmd.enablePcap = False

    cmd.AddValue("simulationTime", "Simulation time in seconds")
    cmd.AddValue("distance", "meters separation between nodes")
    cmd.AddValue("index", "restrict index to single value between 0 and 63")
    cmd.AddValue("wifiType", "select ns3::SpectrumWifiPhy or ns3::YansWifiPhy")
    cmd.AddValue("errorModelType", "select ns3::NistErrorRateModel or ns3::YansErrorRateModel")
    cmd.AddValue("enablePcap", "enable pcap output")
    cmd.Parse(sys.argv)

    simulationTime = float(cmd.simulationTime)
    distance = int(cmd.distance)
    index = int(cmd.index)
    wifiType: str = cmd.wifiType
    errorModelType: str = cmd.errorModelType
    enablePcap = bool(cmd.enablePcap)

    startIndex = 0
    stopIndex = 63

    if index < 64:
        startIndex = index
        stopIndex = index

    print("wifiType",wifiType, "distance:", distance, "m")
    print("index","width","Rate (Mb/s)", "Tput (Mb/s)","Received ")

    i = startIndex
    while i < stopIndex:
        print("Current Index:", i)
        payloadSize = 1472 # 1500 bytes IPv4

        wifiStaNode = ns.network.NodeContainer()
        wifiStaNode.Create(1)
        wifiApNode = ns.network.NodeContainer()
        wifiApNode.Create(1)

        phy = ns.wifi.YansWifiHelper.Default()
        spectrumPhy = ns.wifi.SpectrumWifiPhyHelper.Default()

        if wifiType == "ns3::YansWifiPhy":
        	channel = ns.wifi.YansWifiChannelHelper.Default ()
			channel.AddPropagationLoss ("ns3::FriisPropagationLossModel")
			channel.SetPropagationDelay ("ns3::ConstantSpeedPropagationDelayModel")
			phy.SetChannel (channel.Create ())
          	phy.Set ("TxPowerStart", ns.core.DoubleValue (1))
          	phy.Set ("TxPowerEnd", ns.core.DoubleValue (1))

            if i > 31 and i <=39:
                phy.Set ("Antennas", ns.core.UintegerValue (2))
              	phy.Set ("MaxSupportedTxSpatialStreams", ns.core.UintegerValue (2))
              	phy.Set ("MaxSupportedRxSpatialStreams", ns.core.UintegerValue (2))
            elif i > 39 and i <= 47:
                phy.Set ("Antennas", ns.core.UintegerValue (2))
              	phy.Set ("MaxSupportedTxSpatialStreams", ns.core.UintegerValue (2))
              	phy.Set ("MaxSupportedRxSpatialStreams", ns.core.UintegerValue (2))
            elif i > 47 and i <= 55:
                phy.Set ("Antennas", ns.core.UintegerValue (2))
              	phy.Set ("MaxSupportedTxSpatialStreams", ns.core.UintegerValue (2))
              	phy.Set ("MaxSupportedRxSpatialStreams", ns.core.UintegerValue (2))
            elif i > 55 and i <= 63:
                phy.Set ("Antennas", ns.core.UintegerValue (2))
              	phy.Set ("MaxSupportedTxSpatialStreams", ns.core.UintegerValue (2))
              	phy.Set ("MaxSupportedRxSpatialStreams", ns.core.UintegerValue (2))
        elif wifiType == "ns3::SpectrumWifiPhy":
        	channel1 = ns.wifi.SpectrumWifiChannelHelper.Default ()
        	channel1.AddPropagationLoss ("ns3::FriisPropagationLossModel")
			channel1.SetPropagationDelay ("ns3::ConstantSpeedPropagationDelayModel")
			spectrumPhy.SetChannel (channel1.Create ())
			spectrumPhy.Set ("Frequency", ns.core.UintegerValue (5180)); # channel 36 at 20 MHz 
			spectrumPhy.Set ("TxPowerStart", ns.core.DoubleValue (1));
			spectrumPhy.Set ("TxPowerEnd", ns.core.DoubleValue (1));
            
          	
        	###########################################
        	'''
        	spectrumChannel = ns.wifi.MultiModelSpectrumChannel()
        	lossModel = ns.wifi.FriisPropagationLossModel()
        	delayModel = ns.wifi.ConstantSpeedPropagationDelayModel()
        	spectrumPhy.SetChannel (spectrumChannel);
			spectrumPhy.SetErrorRateModel (errorModelType);
			spectrumPhy.Set ("Frequency", ns.core.UintegerValue (5180)); 
			spectrumPhy.Set ("TxPowerStart", ns.core.DoubleValue (1));
			spectrumPhy.Set ("TxPowerEnd", ns.core.DoubleValue (1));

			'''            
            ###########################################

            if i > 31 and i <=39:
                spectrumPhy.Set ("Antennas", ns.core.UintegerValue (2))
              	spectrumPhy.Set ("MaxSupportedTxSpatialStreams", ns.core.UintegerValue (2))
              	spectrumPhy.Set ("MaxSupportedRxSpatialStreams", ns.core.UintegerValue (2))
            elif i > 39 and i <= 47:
                spectrumPhy.Set ("Antennas", ns.core.UintegerValue (2))
              	spectrumPhy.Set ("MaxSupportedTxSpatialStreams", ns.core.UintegerValue (2))
              	spectrumPhy.Set ("MaxSupportedRxSpatialStreams", ns.core.UintegerValue (2))
            elif i > 47 and i <= 55:
                spectrumPhy.Set ("Antennas", ns.core.UintegerValue (2))
              	spectrumPhy.Set ("MaxSupportedTxSpatialStreams", ns.core.UintegerValue (2))
              	spectrumPhy.Set ("MaxSupportedRxSpatialStreams", ns.core.UintegerValue (2))
            elif i > 55 and i <= 63:
                spectrumPhy.Set ("Antennas", ns.core.UintegerValue (2))
              	spectrumPhy.Set ("MaxSupportedTxSpatialStreams", ns.core.UintegerValue (2))
              	spectrumPhy.Set ("MaxSupportedRxSpatialStreams", ns.core.UintegerValue (2))
        else
            print("Unsupported WiFi type ", wifiType)
            sys.exit(1)

        wifi = ns.wifi.WifiHelper.Default ()
        wifi.SetStandard (ns.wifi.WIFI_PHY_STANDARD_80211n_5GHZ)
        mac = ns.wifi.HtWifiMacHelper.Default ()

        ssid = ns.wifi.Ssid ("ns3-80211n")

		if i == 0:
		    DataRate = "HtMcs0"
		    datarate = 6.5
		elif i == 1:
		    DataRate = "HtMcs1"
		    datarate = 13
		elif i == 2:
		    DataRate = "HtMcs2"
		    datarate = 19.5
		elif i == 3:
		    DataRate = "HtMcs3"
		    datarate = 26
		elif i == 4:
		    DataRate = "HtMcs4"
		    datarate = 39
		elif i == 5:
		    DataRate = "HtMcs5"
		    datarate = 52
		elif i == 6:
		    DataRate = "HtMcs6"
		    datarate = 58.5
		elif i == 7:
		    DataRate = "HtMcs7"
		    datarate = 65
		elif i == 8:
		    DataRate = "HtMcs0"
		    datarate = 7.2
		elif i == 9:
		    DataRate = "HtMcs1"
		    datarate = 14.4
		elif i == 10:
		    DataRate = "HtMcs2"
		    datarate = 21.7
		elif i == 11:
		    DataRate = "HtMcs3"
		    datarate = 28.9
		elif i == 12:
		    DataRate = "HtMcs4"
		    datarate = 43.3
		elif i == 13:
		    DataRate = "HtMcs5"
		    datarate = 57.8
		elif i == 14:
		    DataRate = "HtMcs6"
		    datarate = 65
		elif i == 15:
		    DataRate = "HtMcs7"
		    datarate = 72.2
		elif i == 16:
		    DataRate = "HtMcs0"
		    datarate = 13.5
		elif i == 17:
		    DataRate = "HtMcs1"
		    datarate = 27
		elif i == 18:
		    DataRate = "HtMcs2"
		    datarate = 40.5
		elif i == 19:
		    DataRate = "HtMcs3"
		    datarate = 54
		elif i == 20:
		    DataRate = "HtMcs4"
		    datarate = 81
		elif i == 21:
		    DataRate = "HtMcs5"
		    datarate = 108
		elif i == 22:
		    DataRate = "HtMcs6"
		    datarate = 121.5
		elif i == 23:
		    DataRate = "HtMcs7"
		    datarate = 135
		elif i == 24:
		    DataRate = "HtMcs0"
		    datarate = 15
		elif i == 25:
		    DataRate = "HtMcs1"
		    datarate = 30
		elif i == 26:
		    DataRate = "HtMcs2"
		    datarate = 45
		elif i == 27:
		    DataRate = "HtMcs3"
		    datarate = 60
		elif i == 28:
		    DataRate = "HtMcs4"
		    datarate = 90
		elif i == 29:
		    DataRate = "HtMcs5"
		    datarate = 120
		elif i == 30:
		    DataRate = "HtMcs6"
		    datarate = 135
		elif i == 31:
		    DataRate = "HtMcs7"
		    datarate = 150
		elif i == 32:
		    DataRate = "HtMcs8"
		    datarate = 13
		elif i == 33:
		    DataRate = "HtMcs9"
		    datarate = 26
		elif i == 34:
		    DataRate = "HtMcs10"
		    datarate = 39
		elif i == 35:
		    DataRate = "HtMcs11"
		    datarate = 52
		elif i == 36:
		    DataRate = "HtMcs12"
		    datarate = 78
		elif i == 37:
		    DataRate = "HtMcs13"
		    datarate = 104
		elif i == 38:
		    DataRate = "HtMcs14"
		    datarate = 117
		elif i == 39:
		    DataRate = "HtMcs15"
		    datarate = 130
		elif i == 40:
		    DataRate = "HtMcs8"
		    datarate = 14.4
		elif i == 41:
		    DataRate = "HtMcs9"
		    datarate = 28.9
		elif i == 42:
		    DataRate = "HtMcs10"
		    datarate = 43.3
		elif i == 43:
		    DataRate = "HtMcs11"
		    datarate = 57.8
		elif i == 44:
		    DataRate = "HtMcs12"
		    datarate = 86.7
		elif i == 45:
		    DataRate = "HtMcs13"
		    datarate = 115.6
		elif i == 46:
		    DataRate = "HtMcs14"
		    datarate = 130.3
		elif i == 47:
		    DataRate = "HtMcs15"
		    datarate = 144.4
		elif i == 48:
		    DataRate = "HtMcs8"
		    datarate = 27
		elif i == 49:
		    DataRate = "HtMcs9"
		    datarate = 54
		elif i == 50:
		    DataRate = "HtMcs10"
		    datarate = 81
		elif i == 51:
		    DataRate = "HtMcs11"
		    datarate = 108
		elif i == 52:
		    DataRate = "HtMcs12"
		    datarate = 162
		elif i == 53:
		    DataRate = "HtMcs13"
		    datarate = 216
		elif i == 54:
		    DataRate = "HtMcs14"
		    datarate = 243
		elif i == 55:
		    DataRate = "HtMcs15"
		    datarate = 270
		elif i == 56:
		    DataRate = "HtMcs8"
		    datarate = 30
		elif i == 57:
		    DataRate = "HtMcs9"
		    datarate = 60
		elif i == 58:
		    DataRate = "HtMcs10"
		    datarate = 90
		elif i == 59:
		    DataRate = "HtMcs11"
		    datarate = 120
		elif i == 60:
		    DataRate = "HtMcs12"
		    datarate = 180
		elif i == 61:
		    DataRate = "HtMcs13"
		    datarate = 240
		elif i == 62:
		    DataRate = "HtMcs14"
		    datarate = 270
		elif i == 63:
		    DataRate = "HtMcs15"
		    datarate = 300
		else
		    print("Illegal index i ", i)
		    sys.exit(1)

        
        wifi.SetRemoteStationManager ("ns3::ConstantRateWifiManager", "DataMode", ns.core.StringValue (DataRate), "ControlMode", ns.core.StringValue (DataRate))

        staDevice = ns.network.NetDeviceContainer ()
		apDevice = ns.network.NetDeviceContainer ()

        if wifiType == "ns3::YansWifiPhy":
            
            mac.SetType ("ns3::StaWifiMac",	"Ssid", ns.wifi.SsidValue (ssid))
            staDevice = wifi.Install (phy, mac, wifiStaNod)
            mac.SetType ("ns3::ApWifiMac",	"Ssid", ns.wifi.SsidValue (ssid))
            apDevice = wifi.Install (phy, mac, wifiApNode)


        elif wifiType == "ns3::SpectrumWifiPhy":
            
            mac.SetType ("ns3::StaWifiMac",	"Ssid", ns.wifi.SsidValue (ssid))
            staDevice = wifi.Install (spectrumPhy, mac, wifiStaNod)
            mac.SetType ("ns3::ApWifiMac",	"Ssid", ns.wifi.SsidValue (ssid))
            apDevice = wifi.Install (spectrumPhy, mac, wifiApNode)



        if i <= 7 or (31 < i <= 39):
            
            ns.core.Config.Set ("/NodeList/*/DeviceList/*/$ns3::WifiNetDevice/Phy/ChannelWidth", ns.core.UintegerValue (20))
    		ns.core.Config.Set ("/NodeList/*/DeviceList/*/$ns3::WifiNetDevice/HtConfiguration/ShortGuardIntervalSupported", ns.core.BooleanValue ("false"))
    
        elif (7 < i <= 15) or (39 < i <= 47):
            
            ns.core.Config.Set ("/NodeList/*/DeviceList/*/$ns3::WifiNetDevice/Phy/ChannelWidth", ns.core.UintegerValue (20))
    		ns.core.Config.Set ("/NodeList/*/DeviceList/*/$ns3::WifiNetDevice/HtConfiguration/ShortGuardIntervalSupported", ns.core.BooleanValue ("true"))
    
        elif (15 < i <= 23) or (47 < i <= 55):
            
            ns.core.Config.Set ("/NodeList/*/DeviceList/*/$ns3::WifiNetDevice/Phy/ChannelWidth", ns.core.UintegerValue (40))
    		ns.core.Config.Set ("/NodeList/*/DeviceList/*/$ns3::WifiNetDevice/HtConfiguration/ShortGuardIntervalSupported", ns.core.BooleanValue ("false"))
    
        else
            
            ns.core.Config.Set ("/NodeList/*/DeviceList/*/$ns3::WifiNetDevice/Phy/ChannelWidth", ns.core.UintegerValue (40))
    		ns.core.Config.Set ("/NodeList/*/DeviceList/*/$ns3::WifiNetDevice/HtConfiguration/ShortGuardIntervalSupported", ns.core.BooleanValue ("true"))
    

		#Mobility
		mobility = ns.mobility.MobilityHelper ()
		positionAlloc = ns.mobility.ListPositionAllocator ()

		positionAlloc.Add (ns.core.Vector (0.0, 0.0, 0.0))
		positionAlloc.Add (ns.core.Vector (distance, 0.0, 0.0))
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
		staNodeInterface = address.Assign (staDevice)

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
		client.SetAttribute ("Interval", ns.core.TimeValue (ns.core.Time ("0.00002")))#packets/s
		client.SetAttribute ("PacketSize", ns.core.UintegerValue (1472))#bytes

		clientApp = client.Install (wifiApNode.Get (0))
		clientApp.Start (ns.core.Seconds (1.0))
		clientApp.Stop (ns.core.Seconds (simulationTime + 1))

		if enablePcap == "True":			
		    phy.EnablePcap ("wifi-spectrum-saturation-example-", apDevice)

		#Set simulation time and launch simulation
		ns.core.Simulator.Stop (ns.core.Seconds (simulationTime + 1))
		ns.core.Simulator.Run ()



		j = (i % 8) + 8 * (i / 32)  
		totalPacketsThrough = serverApp.Get (0).GetReceived ()
		throughput = totalPacketsThrough * payloadSize * 8 / (simulationTime * 1000000.0) # Mbit/s
		print(i,j,channelWidth,datarate,throughput,totalPacketsThrough)


		ns.core.Simulator.Destroy ()
	i = i+1

	return 0

if __name__ == '__main__':
    import sys
    sys.exit (main (sys.argv))