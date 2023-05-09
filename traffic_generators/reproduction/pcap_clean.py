from scapy.all import PcapReader, PcapWriter, TCP, IP

import argparse

parser = argparse.ArgumentParser(description="Filter TCP same seq")

parser.add_argument(
    "-i"
    "--input",
    type=str,
    dest='input',
    required=True,
    help="PCAP input",
)

parser.add_argument(
    "-o"
    "--output",
    type=str,
    dest='output',
    required=True,
    help="PCAP output",
)

args = parser.parse_args()


pcapWriter = PcapWriter(args.output, linktype=1)
pcapReader = PcapReader(args.input)


min_len = None
min_sec = 60

if min_len is None and min_sec is None:
    raise Exception('min_len or min_sec should not be None')

seqs = {} # key: 5-tuple (proto always = TCP) + sequence number. Value: packet to write
overlaps = {} # key: 5-tuple (proto always = TCP) + sequence number. Value: [packet index]. Scope: store packet index with a same seq
last_seq_by_conn = {} # last sequence number seen by 5 tuple (proto always = TCP)
window = [] # keep the sequence number (for TCP packet, and the generated number for non-TCP)
packet_index = 0
written_packets = 0
non_tcp_packet = 0
for packet in pcapReader:
    packet_index += 1
    if packet_index % 5000 == 0:
        print(f'Processed {packet_index} packet\twritten: {written_packets}\tqueue len:{len(window)}\tnon TCP written: {non_tcp_packet}')

    if TCP not in packet:
        generated_id = f'g{packet_index}'
        window.append(generated_id)
        seqs[generated_id] = packet
        overlaps[generated_id] = []
        non_tcp_packet += 1
        continue

    tcp = packet[TCP]
    ip = packet[IP]
    ip_src, ip_dst = ip.src, ip.dst
    port_src, port_dst = tcp.sport, tcp.dport
    seq = tcp.seq

    conn = (ip_src, ip_dst, port_src, port_dst)
    key = (ip_src, ip_dst, port_src, port_dst, seq)

    if key not in seqs:
        window.append(key)
        overlaps[key] = []
    else:
        print(f'[{conn}]: seq ({seq}) found twice: {overlaps[key] + [packet_index]}')

    seqs[key] = packet
    overlaps[key].append(packet_index)

    if conn in last_seq_by_conn and last_seq_by_conn[conn] > seq:
        print(f'[{packet_index}]: SEQ number ({seq}) is smaller than the last received: {last_seq_by_conn[conn]}')

    last_seq_by_conn[conn] = seq

    while (min_len is not None and len(window) > min_len) \
    or (min_sec is not None and float(seqs[window[-1]].time - seqs[window[0]].time) > min_sec):
        written_packets += 1
        cached_key = window.pop(0)
        pcapWriter.write(seqs[cached_key])
        del seqs[cached_key]
        del overlaps[cached_key]


while len(window) > 0:
    packet_index += 1
    cached_key = window.pop(0)
    pcapWriter.write(seqs[cached_key])
    del seqs[cached_key]
    del overlaps[cached_key]

    if packet_index % 5000 == 0:
        print(f'Processed {packet_index} packet\twriting remaining ({len(window)} packets')

print('Flushing writer')
pcapWriter.flush()
print('Closing writer')
pcapWriter.close()
print('Closing reader')
pcapReader.close()
