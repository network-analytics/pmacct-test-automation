# Tests ordered by category

## 1XX - IPFIX/NFv9/sFLOW
- 100: IPFIXv10-CISCO
- 101: NFv9-CISCO-cust_primitives
- 102: NFv9-CISCO-f2rd-pretag-sampling-reload
- 103: IPFIXv10-CISCO-JSON_encoding
- 104: IPFIXv10-IPv6-CISCO-sampling_option
- 110: IPFIXv10-NFv9-multiple-sources
- 111: IPFIXv10-NFv9-IPv6-IPv4-mix_sources

## 2XX - BMP
- 200: BMP-HUAWEI-locrib_instance
- 201: BMP-CISCO-rd_instance
- 202: BMP-CISCO-HUAWEI-multiple-sources
- 203: BMP-HUAWEI-dump
- 204: BMP-CISCO-peer_down
- 205: BMP-6wind-FRR-peer_down

## 3XX - BGP
- 300: BGP-IPv6-CISCO-extNH_enc
- 301: BGP-CISCO-pretag
- 302: BGP-IPv6-multiple-sources

## 4XX - IPFIX/NFv9 + BMP
- 400: IPFIXv10-BMP-CISCO-SRv6-multiple-sources
- 401: IPFIXv10-BMP-IPv6-CISCO-MPLS-multiple-sources

## 5XX - IPFIX/NFv9 + BGP
- 500: IPFIXv10-BGP-CISCO-SRv6
- 501: IPFIXv10-BGP-IPv6-CISCO-MPLS
- 502: IPFIXv10-BGP-IPv6-lcomms         [TODO: add]

## 9XX - Miscellaneous
- 900: kafka-connection-loss
- 901: redis-connection-loss
- 902: log-rotation-signal              [TODO: fix or remove]
