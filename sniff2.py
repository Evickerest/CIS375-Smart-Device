from scapy.all import sniff
from scapy.layers.dot11 import Dot11, RadioTap
from scapy.layers.eap import EAPOL
from datetime import datetime

def extract_features(packet):
    features = {}

    # Frame-level features
    features['frame.encap_type'] = packet.getfieldval('type') if packet.haslayer(Dot11) else None
    features['frame.len'] = len(packet)
    features['frame.number'] = packet.number if hasattr(packet, 'number') else None
    features['frame.time'] = datetime.fromtimestamp(float(packet.time)).strftime('%Y-%m-%d %H:%M:%S')
    features['frame.time_epoch'] = packet.time
    features['frame.time_delta'] = packet.time_delta if hasattr(packet, 'time_delta') else None
    features['frame.time_delta_displayed'] = features['frame.time_delta']
    features['frame.time_relative'] = packet.time_relative if hasattr(packet, 'time_relative') else None

    # Radiotap features
    if packet.haslayer(RadioTap):
        radiotap = packet.getlayer(RadioTap)
        features['radiotap.channel.flags.cck'] = 'CCK' in radiotap.ChannelFlags if hasattr(radiotap, 'ChannelFlags') else None
        features['radiotap.channel.flags.ofdm'] = 'OFDM' in radiotap.ChannelFlags if hasattr(radiotap, 'ChannelFlags') else None
        features['radiotap.channel.freq'] = radiotap.ChannelFrequency if hasattr(radiotap, 'ChannelFrequency') else None
        features['radiotap.datarate'] = radiotap.Rate if hasattr(radiotap, 'Rate') else None
        features['radiotap.dbm_antsignal'] = radiotap.dBm_AntSignal if hasattr(radiotap, 'dBm_AntSignal') else None
        features['radiotap.length'] = radiotap.len if hasattr(radiotap, 'len') else None
        features['radiotap.mactime'] = radiotap.MACTimestamp if hasattr(radiotap, 'MACTimestamp') else None
        features['radiotap.present.tsft'] = 'TSFT' in radiotap.present if hasattr(radiotap, 'present') else None
        features['radiotap.rxflags'] = radiotap.RXFlags if hasattr(radiotap, 'RXFlags') else None
        features['radiotap.timestamp.ts'] = radiotap.timestamp if hasattr(radiotap, 'timestamp') else None
        features['radiotap.vendor_oui'] = radiotap.vendor_oui if hasattr(radiotap, 'vendor_oui') else None

    # 802.11 (WLAN) features
    if packet.haslayer(Dot11):
        dot11 = packet.getlayer(Dot11)
        features['wlan.duration'] = dot11.duration if hasattr(dot11, 'duration') else None
        features['wlan.bssid'] = dot11.addr3 if hasattr(dot11, 'addr3') else None
        features['wlan.da'] = dot11.addr1 if hasattr(dot11, 'addr1') else None
        features['wlan.sa'] = dot11.addr2 if hasattr(dot11, 'addr2') else None
        features['wlan.ta'] = dot11.addr2 if hasattr(dot11, 'addr2') else None
        features['wlan.ra'] = dot11.addr1 if hasattr(dot11, 'addr1') else None
        features['wlan.seq'] = dot11.SC if hasattr(dot11, 'SC') else None
        features['wlan.fc.ds'] = dot11.FCfield & 0x03 if hasattr(dot11, 'FCfield') else None
        features['wlan.fc.frag'] = dot11.FCfield & 0x04 if hasattr(dot11, 'FCfield') else None
        features['wlan.fc.order'] = dot11.FCfield & 0x80 if hasattr(dot11, 'FCfield') else None
        features['wlan.fc.moredata'] = dot11.FCfield & 0x20 if hasattr(dot11, 'FCfield') else None
        features['wlan.fc.protected'] = dot11.FCfield & 0x40 if hasattr(dot11, 'FCfield') else None
        features['wlan.fc.pwrmgt'] = dot11.FCfield & 0x10 if hasattr(dot11, 'FCfield') else None
        features['wlan.fc.type'] = dot11.type if hasattr(dot11, 'type') else None
        features['wlan.fc.retry'] = dot11.FCfield & 0x08 if hasattr(dot11, 'FCfield') else None
        features['wlan.fc.subtype'] = dot11.subtype if hasattr(dot11, 'subtype') else None
        features['wlan.fcs.bad_checksum'] = dot11.fcs_bad if hasattr(dot11, 'fcs_bad') else None
        features['wlan.fixed.timestamp'] = dot11.timestamp if hasattr(dot11, 'timestamp') else None
        features['wlan.ssid'] = dot11.info.decode() if hasattr(dot11, 'info') else None
        features['wlan.tag'] = dot11.ID if hasattr(dot11, 'ID') else None
        features['wlan.tag.length'] = dot11.len if hasattr(dot11, 'len') else None

    # EAPOL features
    if packet.haslayer(EAPOL):
        eapol = packet.getlayer(EAPOL)
        features['eapol.len'] = eapol.len if hasattr(eapol, 'len') else None
        features['eapol.type'] = eapol.type if hasattr(eapol, 'type') else None

    return features

# Sniff a single packet for demonstration purposes
packet = sniff(co)[0]
features = extract_features(packet)

# Print the extracted features
for feature, value in features.items():
    print(f"{feature}: {value}") 

