from scapy.all import sniff
from scapy.layers.dot11 import AKMSuite, Dot11, Dot11Beacon, Dot11CCMP, Dot11Elt, Dot11EltCountry, Dot11EltCountryConstraintTriplet, Dot11QoS, RadioTap, Dot11FCS, Dot11Deauth, Dot11Disas, Dot11ProbeResp, Dot11EltRSN, Dot11Elt
from scapy.layers.eap import EAPOL, EAPOL_KEY
from sklearn.preprocessing import StandardScaler, RobustScaler
from multiprocessing.connection import Client
from pickle import  load
import pandas as pd

pd.set_option("display.max_colwidth", None)
pd.set_option("display.max_columns", None)

packet_number = 1
last_packet_time = 0.0
data = []

# columns_subset = ['frame.len', 'frame.time_delta', 'radiotap.channel.flags.cck',
#        'radiotap.channel.flags.ofdm', 'radiotap.channel.freq', 
#        'radiotap.length', 'radiotap.rxflags', 'wlan.duration', 'wlan.fc.ds', 
#        'wlan.fc.frag', 'wlan.fc.order', 'wlan.fc.moredata', 'wlan.fc.protected',
#        'wlan.fc.pwrmgt', 'wlan.fc.type', 'wlan.fc.retry', 'wlan.fc.subtype',
#        'wlan.ra', 'wlan.ta', 'wlan_radio.frequency']
columns_subset = ['frame.len', 'frame.time_delta', 'radiotap.channel.flags.cck',
       'radiotap.channel.flags.ofdm', 'radiotap.channel.freq', 
       'radiotap.length', 'radiotap.rxflags', 'wlan.duration', 'wlan.fc.ds', 
       'wlan.fc.frag', 'wlan.fc.order', 'wlan.fc.moredata', 'wlan.fc.protected',
       'wlan.fc.pwrmgt', 'wlan.fc.type', 'wlan.fc.retry', 'wlan.fc.subtype']

def expand(x):
    yield x
    while x.payload:
        x = x.payload
        yield x

model = load(open("./models/model3.pkl", "rb"))
results = []

# Open up port
address = ("localhost", 6000)
conn = Client(address)

# Function to display captured packets
def packet_callback(packet):
    global packet_number, last_packet_time
    datum = pd.DataFrame()

    datum["frame.encap_type"] = [23] # 802.11
    datum["frame.len"] = [len(packet)]
    datum["frame.number"] = [packet_number]
    datum["frame.time"] = [packet.time]
    datum["frame.time_delta"] = [0.0 if packet_number == 1 else float(packet.time) - last_packet_time]

    last_packet_time = packet.time
    packet_number += 1

    datum["radiotap.channel.flags.cck"] = 1 if "CCK" in packet.ChannelFlags else 0
    datum["radiotap.channel.flags.ofdm"] = 1 if "OFDM" in packet.ChannelFlags else 0
    datum["radiotap.channel.freq"] = packet.ChannelFrequency
    datum["radiotap.datarate"] = packet.Rate 
    datum["radiotap.length"] = packet.len 
    datum["radiotap.mactime"] = packet.mac_timestamp
    datum["radiotap.present.tsft"] = f"{1 if "TSFT" in packet.present else 0}-0-0"
    datum["radiotap.rxflags"] = packet.RXFlags.value
    datum["radiotap.timestamp.ts"] = packet.timestamp


    # (len bytes * 8 bits) / (Rate mbps) * 1000000 us
    packetLength = len(packet) or 0 
    packetRate = packet.Rate or 1 
    datum["wlan_radio.duration"] = packetLength * 8 / packetRate  
    wlanTag = []
    wlanTagLength = []

    datum["wlan.ssid"] = 0

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
        datum["wlan.tag"] = 0

    if len(wlanTagLength) > 0:
        datum["wlan.tag.length"] = "-".join(wlanTagLength)
    else:
        datum["wlan.tag.length"] = 0

    if Dot11Deauth in packet:
        deauth = packet[Dot11Deauth]

        datum["wlan.fixed.reason_code"] = deauth.reason 
    else:
        datum["wlan.fixed.reason_code"] = 0


    if Dot11Disas in packet:
        disas = packet[Dot11Disas]

        datum["wlan.fixed.reason_code"] = disas.reason 
    else:
        datum["wlan.fixed.reason_code"] = 0

    if Dot11EltRSN in packet:
        rsn = packet[Dot11EltRSN]

        # fix in data prepartation
        datum["wlan.rsn.capabilities.mfpc"] = 1.0 if rsn.mfp_capable == 1 else 0.0
        datum["wlan.rsn.ie.pmkid"] = rsn.pmkids 
    else:
        datum["wlan.rsn.capabilities.mfpc"] = 0
        datum["wlan.rsn.ie.pmkid"] = 0

    if EAPOL_KEY in packet:
        eap = packet[EAPOL_KEY]

        datum["wlan_rsna_eapol.keydes.data"] = eap.key_data
        datum["wlan_rsna_eapol.keydes.data_len"] = eap.key_data_length
        datum["wlan_rsna_eapol.keydes.key_info.key_mic"] = 1.0 if eap.has_key_mic & 0x1 else 0.0
        datum["wlan_rsna_eapol.keydes.keydes.nonce"] = eap.key_nonce
        datum["eapol.keydes.key_len"] = eap.key_length
        datum["eapol.keydes.replay_counter"] = eap.key_replay_counter
    else:
        datum["wlan_rsna_eapol.keydes.data"] = 0
        datum["wlan_rsna_eapol.keydes.data_len"] = 0
        datum["wlan_rsna_eapol.keydes.key_info.key_mic"] = 0
        datum["wlan_rsna_eapol.keydes.nonce"] = 0
        datum["eapol.keydes.key_len"] = 0
        datum["eapol.keydes.replay_counter"] = 0

    if EAPOL in packet:
        eap = packet[EAPOL]

        datum["eapol.len"] = eap.len
        datum["eapol.type"] = eap.type
    else:
        datum["eapol.len"] = 0
        datum["eapol.type"] = 0

    if Dot11Beacon in packet:
        beacon = packet[Dot11Beacon]

        datum["wlan.fixed.beacon"] = beacon.beacon_interval
        datum["wlan.fixed.capabilities.ess"] = 1.0 if "ESS" in beacon.cap else 0.0
        datum["wlan.fixed.capabilities.ibss"] = 1.0 if "IBSS" in beacon.cap else 0.0
        datum["wlan.fixed.timestamp"] = beacon.timestamp 
    else:
        datum["wlan.fixed.beacon"] = 0
        datum["wlan.fixed.capabilities.ess"] = 0
        datum["wlan.fixed.capabilities.ibss"] = 0
        datum["wlan.fixed.timestamp"] = 0

    if Dot11FCS in packet:
        dot11 = packet[Dot11]

        datum["wlan.duration"] = dot11.ID
        datum["wlan.analysis.kck"] = None 
        datum["wlan.analysis.kek"] = None 
        datum["wlan.fc.ds"] = dot11.FCfield.value 

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

        # if (dot11.subtype == 12 and dot11.type == 0):
        #     print("Deauth frame!")

        datum["wlan.fc.subtype"] = dot11.subtype 
        datum["wlan.fc.type"] = dot11.type
        datum["wlan.fc.type"] = dot11.type
        datum["wlan.fcs.bad_checksum"] = 0
        if dot11.SC:
            datum["wlan.seq"] = (dot11.SC & 0xFFF)
        else:
            datum["wlan.seq"] = 0
    else:
        datum["wlan.duration"] = 0
        datum["wlan.analysis.kck"] = 0
        datum["wlan.analysis.kek"] = 0
        datum["wlan.fc.ds"] = 0
        datum["wlan.da"] = 0
        datum["wlan.ra"] = 0
        datum["wlan.sa"] = 0
        datum["wlan.ta"] = 0
        datum["wlan.bssid"] = 0
        datum["wlan.fc.frag"] = 0
        datum["wlan.fc.order"] = 0
        datum["wlan.fc.moredata"] = 0
        datum["wlan.fc.protected"] = 0
        datum["wlan.fc.pwrmgt"] = 0
        datum["wlan.fc.retry"] = 0
        datum["wlan.fc.subtype"] = 0
        datum["wlan.fc.type"] = 0
        datum["wlan.fc.type"] = 0
        datum["wlan.fcs.bad_checksum"] = 0
        datum["wlan.seq"] = 0

    datum = datum[columns_subset]

    # scaler = RobustScaler()
    # datum = scaler.fit_transform(datum)

    # print(datum)

    result = model.predict(datum)[0]
    print(result)
    results.append(result)

    # Every 100th packet send the results to chat model:
    if packet_number % 100 == 0:
        string = ""
        for ele in set(results[packet_number - 100: packet_number + 1]):
            string += f"Break down of packets #{packet_number - 100} to #{packet_number + 1}"
            string += f"Packet of Type {ele} occured {results[packet_number - 100: packet_number + 1].count(ele)} times\n"
        conn.send(string)

# Start sniffing packets (you can specify an interface or use 'any' to capture from all interfaces)
print("Starting packet sniffing...\n")

input("Waiting for input to start...\n")

try:
    sniff(iface="wlan0mon", prn=packet_callback)  # Capture 5 packets and call the callback function for each packetS
except KeyboardInterrupt:
    pass

print("\n\nResults: ")
for e in set(results):
    print(f"\tLabel {e} occured {results.count(e)} times")


conn.close()
