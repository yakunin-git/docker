#!/bin/bash

FILE="/etc/wireguard/wg0.conf"
if [[ -f "$FILE" ]]; then
  /usr/bin/wg-quick down wg0
  /usr/bin/wg-quick up wg0
  /opt/wireguard-ui
else
  /opt/wireguard-ui
fi
