FROM alpine:latest

COPY vsftpd.conf /etc/vsftpd/vsftpd.conf
COPY entrypoint.sh /entrypoint.sh

RUN apk add --no-cache --update vsftpd && \
    (rm "/tmp/"* 2>/dev/null || true) && (rm -rf /var/cache/apk/* 2>/dev/null || true)

ENTRYPOINT /entrypoint.sh
CMD ["/usr/sbin/vsftpd", "/etc/vsftpd/vsftpd.conf"]
