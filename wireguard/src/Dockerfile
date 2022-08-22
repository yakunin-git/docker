FROM alpine

WORKDIR /opt

RUN apk --update add wget ifupdown iproute2 net-tools wireguard-tools && \
    rm -rf /var/lib/apt/lists/* && \
    rm /var/cache/apk/* && \
    wget https://github.com/ngoduykhanh/wireguard-ui/releases/download/v0.3.7/wireguard-ui-v0.3.7-linux-386.tar.gz && \
    tar -xvf wireguard-ui-v0.3.7-linux-386.tar.gz && rm wireguard-ui-v0.3.7-linux-386.tar.gz

COPY entrypoint.sh /entrypoint.sh
ENTRYPOINT /entrypoint.sh

CMD ["/entrypoint.sh"]
