from scapy.all import sniff

index = 1

# Function to display captured packets
def packet_callback(packet):
    global index
    print(f"\n\n Packet #{index}\n\n")
    packet.show()
    index += 1

# Start sniffing packets (you can specify an interface or use 'any' to capture from all interfaces)
print("Starting packet sniffing...\n")
sniff(iface="wlan0mon", prn=packet_callback)  # Capture 5 packets and call the callback function for each packet

