from scapy.all import sniff
from scapy.layers.dot11 import AKMSuite, Dot11, Dot11Beacon, Dot11CCMP, Dot11Elt, Dot11EltCountry, Dot11EltCountryConstraintTriplet, Dot11QoS, RadioTap, Dot11FCS, Dot11Deauth, Dot11Disas, Dot11ProbeResp, Dot11EltRSN, Dot11Elt
from scapy.layers.eap import EAP, EAPOL, EAPOL_KEY

packet_number = 1
last_packet_time = 0.0
data = []

def expand(x):
    yield x
    while x.payload:
        x = x.payload
        yield x

# Function to display captured packets
def packet_callback(packet):
    # Ensure we are reading 802.11 Packet
    if (type(packet) != RadioTap): return

    datum = {}

    global packet_number, last_packet_time
    
    datum["frame.encap_type"] = 23 # 802.11
    datum["frame.len"] = len(packet)
    datum["frame.number"] = packet_number
    datum["frame.time"] = packet.time
    datum["frame.time_delta"] = 0.0 if packet_number == 1 else float(packet.time) - last_packet_time

    last_packet_time = packet.time
    packet_number += 1

    datum["radiotap.channel.flags.cck"] = 1 if "CCK" in packet.ChannelFlags else 0
    datum["radiotap.channel.flags.ofdm"] = 1 if "OFDM" in packet.ChannelFlags else 0
    datum["radiotap.channel.freq"] = packet.ChannelFrequency
    datum["radiotap.datarate"] = packet.Rate 
    datum["radiotap.dbm_antsignal"] = f"{packet.dBm_AntSignal}{packet.dBm_AntSignal}{packet.dBm_AntSignal}"
    datum["radiotap.lengthc"] = packet.len 
    datum["radiotap.mactime"] = packet.mac_timestamp
    datum["radiotap.present.tsft"] = f"{1 if "TSFT" in packet.present else 0}-0-0"
    datum["radiotap.rxflags"] = f"0x{(packet.RXFlags.value):#0{8}}"
    datum["radiorap.timestamp.ts"] = packet.timestamp
    datum["radiodap.vendor_oui"] = None


    # (len bytes * 8 bits) / (Rate mbps) * 1000000 us
    packetLength = len(packet) or 0 
    packetRate = packet.Rate or 1 
    datum["wlan_radio.duration"] = packetLength * 8 / packetRate  

    wlanTag = []
    wlanTagLength = []

    l = list(expand(packet))
    for layer in l:
        if isinstance(layer, Dot11Elt):
            wlanTag.append("1")
            wlanTagLength.append(str(layer.len))

            # If beacon
            if (layer.ID == 0):
                datum["wlan.ssid"] = layer.info


    if len(wlanTag) > 0:
        datum["wlan.tag"] = "-".join(wlanTag)
    else:
        datum["wlan.tag"] = None 

    if len(wlanTagLength) > 0:
        datum["wlan.tag.length"] = "-".join(wlanTagLength)
    else:
        datum["wlan.tag.length"] = None 

    if Dot11Deauth in packet:
        deauth = packet[Dot11Deauth]

        datum["wlan.fixed.reason_code"] = deauth.reason 

    if Dot11Disas in packet:
        disas = packet[Dot11Disas]

        datum["wlan.fixed.reason_code"] = disas.reason 

    if Dot11EltRSN in packet:
        rsn = packet[Dot11EltRSN]

        # fix in data prepartation
        datum["wlan.rsn.capabilities.mfpc"] = 1.0 if rsn.mfp_capable == 1 else 0.0
        datum["wlan.rsn.ie.pmkid"] = rsn.pmkids 

    if EAPOL_KEY in packet:
        eap = packet[EAPOL_KEY]

        datum["wlan_rsna_eapol.keydes.data"] = eap.key_data
        datum["wlan_rsna_eapol.keydes.data_len"] = eap.key_data_length
        datum["wlan_rsna_eapol.keydes.key_info.key_mic"] = 1.0 if eap.has_key_mic & 0x1 else 0.0
        datum["wlan_rsna_eapol.keydes.keydes.nonce"] = eap.key_nonce
        datum["eapol.keydes.key_len"] = eap.key_length
        datum["eapol.keydes.replay_counter"] = eap.key_replay_counter

    if EAPOL in packet:
        eap = packet[EAPOL]

        datum["eapol.len"] = eap.len
        datum["eapol.type"] = eap.type

    if Dot11Beacon in packet:
        beacon = packet[Dot11Beacon]

        datum["wlan.fixed.beacon"] = beacon.beacon_interval
        datum["wlan.fixed.capabilities.ess"] = 1.0 if "ESS" in beacon.cap else 0.0
        datum["wlan.fixed.capabilities.ibss"] = 1.0 if "IBSS" in beacon.cap else 0.0
        datum["wlan.fixed.timestamp"] = beacon.timestamp 

    if Dot11FCS in packet:
        dot11 = packet[Dot11]

        datum["wlan.duration"] = dot11.ID
        datum["wlan.analysis.kck"] = None 
        datum["wlan.analysis.kek"] = None 
        datum["wlan.fc.ds"] = f"0x{(dot11.FCfield.value & 0x3):#0{8}}"

        # Calculate addresses based on tods and fromds
        tods = 1 if "to-DS" in dot11.FCfield else 0
        fromds = 1 if "from-DS" in dot11.FCfield else 0

        if tods == 0 and fromds == 0:
            datum["wlan.da"] = dot11.addr1 
            datum["wlan.ra"] = dot11.addr1
            datum["wlan.sa"] = dot11.addr2
            datum["wlan.ta"] = dot11.addr2
            datum["wlan.bssid"] = dot11.addr3
        elif tods == 0 and fromds == 1:
            datum["wlan.ra"] = dot11.addr1 
            datum["wlan.da"] = dot11.addr1
            datum["wlan.bssid"] = dot11.addr2
            datum["wlan.ta"] = dot11.addr2
            datum["wlan.sa"] = dot11.addr3
        elif tods == 1 and fromds == 0:
            datum["wlan.bssid"] = dot11.addr1
            datum["wlan.ra"] = dot11.addr1 
            datum["wlan.ta"] = dot11.addr2 
            datum["wlan.sa"] = dot11.addr2
            datum["wlan.da"] = dot11.addr3
        elif tods == 1 and fromds == 1:
            datum["wlan.ra"] = dot11.addr1 
            datum["wlan.ta"] = dot11.addr2
            datum["wlan.da"] = dot11.addr3
            datum["wlan.sa"] = dot11.addr4 

        datum["wlan.fc.frag"] = 1 if "MF" in dot11.FCfield else 0
        datum["wlan.fc.order"] = 1 if "order" in dot11.FCfield else 0
        datum["wlan.fc.moredata"] = 1 if "MD" in dot11.FCfield else 0
        datum["wlan.fc.protected"] = 1 if "protected" in dot11.FCfield else 0
        datum["wlan.fc.pwrmgt"] = 1 if "pw-mgt" in dot11.FCfield else 0
        datum["wlan.fc.retry"] = 1 if "retry" in dot11.FCfield else 0

        datum["wlan.fc.subtype"] = dot11.subtype 
        datum["wlan.fc.type"] = dot11.type
        datum["wlan.fc.type"] = dot11.type
        datum["wlan.fcs.bad_checksum"] = None
        if dot11.SC:
            datum["wlan.seq"] = (dot11.SC & 0xFFF)
        else:
            datum["wlan.seq"] = None 


    data.append(datum)



# Start sniffing packets (you can specify an interface or use 'any' to capture from all interfaces)
print("Starting packet sniffing...\n")
sniff(iface="wlan0mon", count=10, prn=packet_callback)  # Capture 5 packets and call the callback function for each packet

for i, datum in enumerate(data):
    print(f"\n --- Data {i} ----\n")
    for key, value in datum.items():
        print(f"\t{key}: {value}")




