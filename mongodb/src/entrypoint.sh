#!/usr/bin/bash
chown -R mongodb:mongodb /data
chown -R mongodb:mongodb /etc/ssl
su - mongodb -s /bin/bash -c '/usr/bin/mongod --config /etc/mongod.conf'
