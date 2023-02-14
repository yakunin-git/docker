FROM ubuntu:latest

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get upgrade -y && apt install wget gnupg gnupg2  gnupg1 netcat -y && \
    wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | apt-key add - && \
    echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/6.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-6.0.list && \
    apt-get update && apt-get install -y mongodb-org && apt-get purge wget gnupg gnupg2  gnupg1 -y && \
    mkdir /home/mongodb &&  mkdir /etc/ssl/mongodb/ && mkdir /data && \
    chown -R mongodb:mongodb /data && chown -R mongodb:mongodb /home/mongodb/ && \
    rm -rf /var/cache/apt

COPY entrypoint.sh /entrypoint.sh

ENTRYPOINT /entrypoint.sh
CMD ["tail", "-f", "/var/log/mongodb/mongod.log"]
