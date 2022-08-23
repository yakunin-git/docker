### Wireguard based on Alpine linux

I wrote this docker compose after I needed to install wireguard on my server. I did not want to install it on the system, so I chose docker. Ubuntu seemed too large image size for me. Alpine linux is my favorite. That is why this image is assembled on it.

I wanted to have a web interface to control wireguard, and I found this great project: [https://github.com/EmbarkStudios/wg-ui](https://github.com/EmbarkStudios/wg-ui)


It's time to prepare your system, you need to run the container in network - host mode. It is also necessary edit sysctl.conf in order for you to be able to route traffic.

```
> echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
> sysctl -p
```

After that, add iptables rules for NAT, where $eth0 is your WAN interface.

```
iptables -A FORWARD -j ACCEPT
iptables -t nat -A POSTROUTING -o $eth0 -j MASQUERADE
```

Of course, it's better to use specific networks, sources, and destinations when writing rules for iptables. I leave this behind the scenes. You can use this solution, but it is not entirely correct in terms of building rules.


After starting the project, go through the browser to the address: http://127.0.0.1:5000 The default username and password is admin:admin


You can change all the settings according to the project documentation, I left a link to it above.


Now, we are ready to start.

```
docker compose up --build --detach
```
