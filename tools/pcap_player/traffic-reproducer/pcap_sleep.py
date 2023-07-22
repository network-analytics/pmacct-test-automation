from scapy.all import PcapReader, PcapWriter, EDecimal

import argparse

parser = argparse.ArgumentParser(description="Set max sleep time between two packets")

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

parser.add_argument(
    "-s"
    "--maxsleep",
    type=int,
    dest='maxsleep',
    required=True,
    help="Max sleep time in seconds",
)

args = parser.parse_args()


pcapWriter = PcapWriter(args.output, linktype=1)
pcapReader = PcapReader(args.input)

max_sleep = EDecimal(args.maxsleep)
prev_time = None
time_offset = EDecimal(0)
packetIndex = 0
for packet in pcapReader:
    packetIndex += 1
    if prev_time is not None and packet.time - prev_time > max_sleep:
        print(f"Packet {packetIndex}: {prev_time} - {packet.time} ({prev_time-packet.time}) > {max_sleep}")
        time_offset += (packet.time - prev_time) - max_sleep

    if packetIndex % 5000 == 0:
        print(f"Processed packet {packetIndex}. Offset: {time_offset}. Diff {packet.time - prev_time}s")

    prev_time = packet.time
    packet.time = packet.time - time_offset
    # pcapWriter.write(packet)



print('Flushing writer')
pcapWriter.flush()
print('Closing writer')
pcapWriter.close()
print('Closing reader')
pcapReader.close()
