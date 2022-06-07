FROM ubuntu:20.04
MAINTAINER "Yakunin V. Vasily" <vasily.yakunin@gmail.com>
LABEL maintaine "Yakunin V. Vasily" <vasily.yakunin@gmail.com>

ENV DEBIAN_FRONTEND noninteractive
RUN apt update && apt upgrade -y
RUN apt -y install bind9 bind9-utils dnsutils iputils-ping net-tools

RUN touch /var/log/bind.log && chown bind:bind /var/log/bind.log
RUN rm -rf /etc/bind && mkdir /etc/bind && mkdir /etc/bind/zone && chown -R bind:bind /etc/bind/

COPY ./conf/named.conf /etc/bind/named.conf
COPY ./zone/main.conf /etc/bind/zone/main.conf

CMD ["/usr/sbin/named", "-c", "/etc/bind/named.conf", "-p", "53", "-u", "bind", "-f"]
HEALTHCHECK CMD named-checkconf /etc/bind/named.conf || exit 1
