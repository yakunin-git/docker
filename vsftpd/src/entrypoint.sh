#!/bin/sh

echo "$USERNAME:x:0:0:root:/ftp:/bin/sh" >> /etc/passwd && \
echo "$USERNAME:$USERPASSWORD" | chpasswd && \
chmod 0666 /tmp/vsftpd.log && chown root:root /tmp/vsftpd.log && \

/usr/sbin/vsftpd /etc/vsftpd/vsftpd.conf
