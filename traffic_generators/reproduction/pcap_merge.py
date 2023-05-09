from scapy.all import PcapReader, PcapWriter

import argparse

parser = argparse.ArgumentParser(description="Merge pcap together")

parser.add_argument(
    "-i"
    "--inputs",
    type=str,
    nargs='+',
    dest='inputs',
    required=True,
    help="PCAPs list you want to merge (in order)",
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
print(args)

pcapWriter = PcapWriter(args.output, linktype=1)
for path in args.inputs:
    for pkt in PcapReader(path):
        pcapWriter.write(pkt)
pcapWriter.flush()
pcapWriter.close()
