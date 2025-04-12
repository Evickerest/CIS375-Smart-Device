
from multiprocessing.connection import Listener

# Listen to port to get status of any Network Attacks
address = ("localhost", 6000)
listener = Listener(address)

print("Waiting for connection from packet sniffer...\n")
conn = listener.accept()

print("Connected to packet sniffer. Begin chating!\n\n")

try:
    while True:
        network_status = conn.recv()
        print(network_status)
except:

    print("bye")

