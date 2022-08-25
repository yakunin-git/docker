FROM alpine

WORKDIR /etc/bind
COPY named.conf /etc/bind/named.conf

RUN apk --update add bind bind-tools bind-dnssec-tools nano  && \
    rm -rf /var/lib/apt/lists/* && \
    rm /var/cache/apk/* && \
    touch /var/log/bind.log && \
    chown named:named /var/log/bind.log

CMD ["/usr/sbin/named", "-c", "/etc/bind/named.conf", "-p", "53", "-u", "named", "-f"]
