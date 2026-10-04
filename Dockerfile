FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    iproute2 \
    iputils-ping \
    traceroute \
    dnsutils \
    tcpdump \
    tshark \
    net-tools \
    curl \
    wget \
    nano \
    vim \
    coreutils \
    python3 \
    && rm -rf /var/lib/apt/lists/*

# Allow tshark/Wireshark packet capture without requiring an interactive prompt
RUN setcap cap_net_raw,cap_net_admin=eip /usr/bin/dumpcap || true

WORKDIR /lab

COPY scripts/ /lab/scripts/
COPY consultar_puertos.py /lab/consultar_puertos.py
RUN sed -i 's/\r$//' /lab/scripts/check_port.sh && chmod +x /lab/scripts/check_port.sh

CMD ["/bin/bash"]
