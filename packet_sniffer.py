from scapy.all import sniff, Ether, IP, TCP, wrpcap  # Import from scapy.all

# Variable to store captured packets
captured_packets = []

# Callback function to process each captured packet
def packet_callback(packet):
    captured_packets.append(packet)  # Add the packet to the list
    print(f"Captured {len(captured_packets)} packets so far")

# Start sniffing (captures packets and processes them with the callback function)
sniff(count=10, prn=packet_callback)  # Capture 10 packets and pass them to the callback function

# After capture, you can print details about the captured packets
print(f"Total captured packets: {len(captured_packets)}")

# Optionally, save the captured packets to a PCAP file\
wrpcap("captured.pcap", captured_packets)

# Example: Show the first packet
if captured_packets:
    captured_packets[0].show()