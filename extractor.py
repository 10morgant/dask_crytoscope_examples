from scapy.all import sniff
from scapy.layers.http import HTTP, HTTPRequest
from scapy.sessions import TCPSession


def process_pcap(file_name):
    def proc(pkt):
        if HTTP in pkt:
            if HTTPRequest in pkt:
                print(pkt[HTTPRequest].Host.decode(), pkt[HTTPRequest].Path.decode())

    sniff(offline=file_name, session=TCPSession, store=False, prn=proc)


# Example usage
process_pcap('data/pcap.pcap')
