from scapy.all import TCP, IP, UDP


def filter_generator(flt):
    if flt is None:
        return None

    def F(pkt):
        if 'ip' in flt:
            if IP not in pkt:
                return False
            for f in flt['ip']:
                if not getattr(pkt[IP], f) == flt['ip'][f]:
                    return False

        if 'tcp' in flt:
            if TCP not in pkt:
                return False
            for f in flt['tcp']:
                if not getattr(pkt[TCP], f) == flt['tcp'][f]:
                    return False

        if 'udp' in flt:
            if UDP not in pkt:
                return False
            for f in flt['udp']:
                if not getattr(pkt[UDP], f) == flt['udp'][f]:
                    return False

        return True
    return F
