### Wireguard based on Alpine linux

Use compose to startup server, before you start, you need edit sysctl.conf and enable ip forwarding.

```
> echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
> sysctl -p
```

After that, add iptables rules for NAT, where $eth0 is your WAN interface.

```
iptables -A FORWARD -j ACCEPT
iptables -t nat -A POSTROUTING -o $eth0 -j MASQUERADE
```

Now you redy to go. 
